-- Northern Peak Systems: email additions (2026-10-24). Run once in Supabase -> SQL Editor (safe to re-run).
alter table public.nps_customers
  add column if not exists cancel_at timestamptz,
  add column if not exists customer_confirm_sent_at timestamptz,
  add column if not exists reminder_1_sent_at timestamptz,
  add column if not exists reminder_2_sent_at timestamptz,
  add column if not exists cancel_confirm_sent_at timestamptz;
