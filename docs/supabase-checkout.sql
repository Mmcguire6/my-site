-- Northern Peak Systems: self-serve checkout + onboarding records.
-- Paste into Supabase -> SQL Editor -> Run (safe to run more than once).
-- Row-level security is ON with no policies, so only the server (service key) can read or write.

create table if not exists public.nps_customers (
  id uuid primary key default gen_random_uuid(),
  stripe_subscription_id text not null unique,
  stripe_customer_id text,
  stripe_checkout_session_id text unique,
  plan text not null check (plan in ('base', 'peak')),
  email text,
  name text,
  phone text,
  subscription_status text,
  cancel_at_period_end boolean not null default false,
  current_period_end timestamptz,
  last_payment_at timestamptz,
  onboarding_status text not null default 'awaiting_information'
    check (onboarding_status in ('awaiting_information', 'in_progress', 'complete')),
  onboarding_data jsonb not null default '{}'::jsonb,
  onboarding_started_at timestamptz,
  onboarding_completed_at timestamptz,
  attribution jsonb not null default '{}'::jsonb,
  -- once-only steps (claimed atomically so retries never repeat them)
  welcome_sent_at timestamptz,
  team_notified_at timestamptz,
  ghl_purchase_sent_at timestamptz,
  onboarding_notified_at timestamptz,
  ghl_onboarding_sent_at timestamptz,
  link_sent_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists nps_customers_email_idx on public.nps_customers (email);
create index if not exists nps_customers_customer_idx on public.nps_customers (stripe_customer_id);

create table if not exists public.nps_stripe_events (
  id text primary key,                 -- Stripe event ID (evt_...)
  type text not null,
  livemode boolean not null default false,
  status text not null default 'processing' check (status in ('processing', 'done', 'failed')),
  attempts integer not null default 1,
  steps_done text[] not null default '{}',
  error text,
  alerted boolean not null default false,
  received_at timestamptz not null default now(),
  processed_at timestamptz,
  updated_at timestamptz not null default now()
);

create or replace function public.nps_touch_updated_at() returns trigger
language plpgsql as $$ begin new.updated_at = now(); return new; end $$;

drop trigger if exists nps_customers_touch on public.nps_customers;
create trigger nps_customers_touch before update on public.nps_customers
  for each row execute function public.nps_touch_updated_at();

alter table public.nps_customers enable row level security;
alter table public.nps_stripe_events enable row level security;
revoke all on public.nps_customers from anon, authenticated;
revoke all on public.nps_stripe_events from anon, authenticated;

-- Handy view for the team: who still owes setup information.
create or replace view public.nps_onboarding_queue
with (security_invoker = true) as
  select created_at, plan, email, name, subscription_status, onboarding_status,
         onboarding_data ->> 'business_name' as business_name, onboarding_completed_at
  from public.nps_customers
  order by created_at desc;
revoke all on public.nps_onboarding_queue from anon, authenticated;
