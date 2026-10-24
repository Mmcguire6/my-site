# Self-serve checkout and onboarding: setup and operations

**Flow:** Get Started → Stripe Checkout (server-created session, server-side price) → Stripe confirms payment →
webhook records the customer in Supabase → welcome email with a private setup link + team notice + GoHighLevel
event → customer fills in the setup form on `/welcome.html` → team notice + GoHighLevel event → we build.

Book a Demo is unchanged (`/book` → Google Calendar). Both paths stay on every key page.

Billing policy (decided 2026-10-22): **first month charged at checkout**, renews monthly, cancel with 30 days'
written notice. Terms, FAQ and pricing copy say this.

## What lives where

| Piece | File |
| --- | --- |
| Start a checkout (`/api/checkout?plan=`, `/start/base`, `/start/peak`) | `netlify/functions/checkout.js` |
| Stripe webhook (`/api/stripe-webhook`) | `netlify/functions/stripe-webhook.js` |
| Onboarding API (`/api/onboarding`: verify, load, save, submit, resend, portal) | `netlify/functions/onboarding.js` |
| Shared code (Stripe, Supabase, emails, GHL, signed links, plans) | `netlify/lib/*.js` |
| Onboarding page | `welcome.html` |
| Database tables | `docs/supabase-checkout.sql` |
| One-time Stripe setup (prices, portal, webhook) | `scripts/stripe-setup.mjs` |
| Local server with functions | `scripts/dev-server.mjs` |
| Automated tests (no credentials needed) | `scripts/test-checkout.mjs` |

## 1. Supabase (once)

Supabase → SQL Editor → paste `docs/supabase-checkout.sql` → Run. It creates `nps_customers`,
`nps_stripe_events` and the `nps_onboarding_queue` view, with row-level security on and no public access.
Submissions are visible in Table Editor → `nps_customers` (answers are in `onboarding_data`).

## 2. Stripe, test mode first

1. In **the NPS Stripe account** (not CloseCombat), copy the test secret key into `my-site/.env.local`:
   `STRIPE_SECRET_KEY=sk_test_...`
2. `node scripts/stripe-setup.mjs` creates (or finds) the two products and CAD monthly prices and a Customer
   Portal configuration, and prints `STRIPE_PRICE_BASE`, `STRIPE_PRICE_PEAK`, `STRIPE_PORTAL_CONFIGURATION`.
   Re-running never duplicates anything (prices are found by lookup key).
3. Stripe dashboard settings to check:
   - Settings → Branding: logo, colours, business name (shown on Checkout and receipts).
   - Settings → Customer emails: turn on successful-payment receipts and failed-payment emails if you want Stripe to send them.
   - Settings → Public details: statement descriptor, support email/phone.
   - **Tax:** prices are $97 / $297 with no GST/HST added. If NPS is GST-registered, decide whether prices are
     tax-inclusive or set up Stripe Tax before going live.
4. Webhook: `node scripts/stripe-setup.mjs --webhook https://northernpeaksystems.ca/api/stripe-webhook`
   creates the endpoint with the right events. Its signing secret is written to `.env.local` as
   `STRIPE_WEBHOOK_SECRET` (never printed). Copy it into Netlify.

## 3. Netlify environment variables

| Variable | Required | Value |
| --- | --- | --- |
| `STRIPE_SECRET_KEY` | yes | `sk_test_...` now, `sk_live_...` at launch |
| `STRIPE_WEBHOOK_SECRET` | yes | `whsec_...` from step 2.4 (test and live endpoints have different secrets) |
| `STRIPE_PRICE_BASE` / `STRIPE_PRICE_PEAK` | yes | price IDs from step 2.2 (test and live IDs differ) |
| `STRIPE_PORTAL_CONFIGURATION` | optional | `bpc_...`; turns on the "Manage billing" button |
| `SUPABASE_URL` | yes | `https://<ref>.supabase.co` |
| `SUPABASE_SERVICE_KEY` | yes | Supabase secret (service role) key |
| `ONBOARDING_TOKEN_SECRET` | yes | 64 random hex chars: `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"` |
| `RESEND_API_KEY` | yes (already set) | used by the contact form too |
| `GHL_WEBHOOK_URL` | optional | GoHighLevel inbound-webhook URL (section 4) |
| `TO_EMAIL` / `FROM_EMAIL` | optional | team inbox / sender (defaults: matt@ / noreply@northernpeaksystems.ca) |
| `SITE_URL` | optional | defaults to Netlify's `URL`; set it on a test deploy so Stripe returns to that deploy |

Until these are set, Get Started sends people back to the pricing page with "Online checkout isn't available
right now. Book a demo or call…", so nothing breaks.

## 4. GoHighLevel (inbound webhook)

Create a workflow: **Trigger: Inbound Webhook**. Copy its URL into `GHL_WEBHOOK_URL`, buy a test subscription
once so GHL sees a sample payload, then map fields.

Every POST is JSON with:

```
event                  purchase_verified | onboarding_completed | payment_failed | renewal_paid |
                       subscription_status_changed | subscription_cancel_scheduled | subscription_canceled | refund_issued
email, first_name, last_name, phone, company_name
plan                   base | peak            plan_label   Base System | The Peak System
stripe_customer_id, stripe_subscription_id, subscription_status, onboarding_status
pipeline_stage         New Purchase (purchase) / Setup in Progress (onboarding completed)
tags                   ["NPS Customer", "<plan> Subscription", "Onboarding Required" | "Onboarding Complete"]
source                 utm_source or ref of the first visit
+ per event: onboarding_url (purchase), amount, currency, previous_status, attempt_count, ends_at, amount_refunded
```

Suggested workflow branches (If/Else on `event`):

- **purchase_verified:** Create/Update Contact (email) → custom fields: Stripe customer ID, Stripe subscription
  ID, subscription status, plan → Add tags from `tags` → Create/Update Opportunity in pipeline
  **NPS Onboarding**, stage **New Purchase** → optional reminder email after 2 days using `onboarding_url` if the
  tag is still "Onboarding Required". (The welcome email is already sent by the site; don't send a second one.)
- **onboarding_completed:** remove tag "Onboarding Required", add "Onboarding Complete", move opportunity to
  **Setup in Progress**, create a task for the build.
- **payment_failed / subscription_status_changed / subscription_canceled / refund_issued:** update the status
  field and notify the team. Nothing on the site is switched off automatically.

Pipeline: **New Purchase → Awaiting Information → Setup in Progress → Customer Review → Live**. Only the first
and third are moved automatically; Customer Review and Live are moved by a person.

Purchases do **not** opt anyone into SMS or marketing. Keep promotional campaigns behind your normal consent steps.

## 5. Sales links (after a demo or a call)

- `https://northernpeaksystems.ca/start/peak?ref=demo` (or `/start/base`): straight to Checkout for that plan.
- Add `&email=owner@business.ca` to pre-fill their email, and `utm_source` / `utm_campaign` for cold email.
- `ref` and `utm_*` are saved on the subscription, in Supabase and in GHL (`source`), so direct purchases can be
  told apart from demo-first ones.

## 6. Testing

- Offline: `node --test scripts/test-checkout.mjs` (15 scenarios: both plans, duplicate and replayed webhooks,
  failed payments, abandoned onboarding, cancellations, refunds).
- Local, end to end with Stripe test mode: `node scripts/dev-server.mjs`, then in another terminal
  `stripe listen --api-key sk_test_... --forward-to localhost:8790/api/stripe-webhook` (put the printed
  `whsec_...` in `.env.local` as `STRIPE_WEBHOOK_SECRET`), open http://localhost:8790/pricing.html, click
  Get Started and pay with `4242 4242 4242 4242`, any future date, any CVC. Decline test: `4000 0000 0000 0002`.

## 7. Go-live checklist

1. Test mode passes scenarios A to H on a deployed test site (Stripe test keys in Netlify).
2. Run `node scripts/stripe-setup.mjs --live` with the live key (creates live prices/portal), then `--webhook`
   for the live endpoint. Put the live values in Netlify (production context only).
3. One real purchase with a real card, then refund it from the Stripe dashboard; check the welcome email,
   team notice, Supabase row and GHL contact.
4. Watch the Netlify function logs and the "Action needed: NPS automation failed" emails for the first week.

## Operations

- **Cancellations:** customers give 30 days' written notice (email). In Stripe, set the subscription to cancel
  at the right date. The portal's cancel button is deliberately off.
- **Failed automations:** the team gets one "Action needed" email per failing Stripe event; Stripe retries for
  up to 3 days and each retry only redoes the step that failed. `nps_stripe_events` shows status and error.
- **Nothing is deleted** on cancellation or failed payment. Offboarding (site removal) is a manual decision.
- **Lost setup link:** the customer can request a new one on `/welcome.html`; links last 30 days.
