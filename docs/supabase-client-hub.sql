-- Northern Peak Systems: Client Hub (2026-10-25). Run once in Supabase -> SQL Editor (safe to re-run).
-- project_stage drives the progress tracker customers see: setup -> build -> review -> live.
-- It moves to 'build' automatically when the setup form is submitted; move it to 'review' and 'live'
-- yourself in Table Editor -> nps_customers. team_note shows as "Latest from our team" in the Hub.
alter table public.nps_customers
  add column if not exists project_stage text not null default 'setup',
  add column if not exists team_note text,
  add column if not exists site_url text;

alter table public.nps_customers drop constraint if exists nps_customers_project_stage_check;
alter table public.nps_customers add constraint nps_customers_project_stage_check
  check (project_stage in ('setup', 'build', 'review', 'live'));
