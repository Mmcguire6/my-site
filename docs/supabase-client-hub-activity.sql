-- Client Hub activity dates (2026-10-24). Run once in Supabase -> SQL Editor.
-- Stamps when a project moves to build / review / live and when the team note changes, so the
-- customer's activity timeline and progress tracker can show real dates. Works for edits made in
-- the Table Editor as well as by the site.

alter table public.nps_customers
  add column if not exists build_at timestamptz,
  add column if not exists review_at timestamptz,
  add column if not exists live_at timestamptz,
  add column if not exists team_note_at timestamptz;

create or replace function public.nps_customers_stage_times()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  if new.project_stage is distinct from old.project_stage then
    if new.project_stage = 'build' and new.build_at is null then new.build_at := now(); end if;
    if new.project_stage = 'review' and new.review_at is null then new.review_at := now(); end if;
    if new.project_stage = 'live' and new.live_at is null then new.live_at := now(); end if;
  end if;
  if new.team_note is distinct from old.team_note then
    new.team_note_at := case when coalesce(btrim(new.team_note), '') = '' then null else now() end;
  end if;
  return new;
end;
$$;

drop trigger if exists nps_customers_stage_times on public.nps_customers;
create trigger nps_customers_stage_times
  before update on public.nps_customers
  for each row execute function public.nps_customers_stage_times();

-- customers who submitted setup before this existed started their build then
update public.nps_customers
  set build_at = onboarding_completed_at
  where build_at is null and onboarding_completed_at is not null;
