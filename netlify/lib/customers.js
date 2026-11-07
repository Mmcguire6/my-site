/**
 * Customer records (nps_customers) and the one-time steps that follow a verified purchase.
 *
 * Source of truth: every status written here is read back from the Stripe API, never from
 * the browser or the success-page redirect. Each one-time step (welcome email, team notice,
 * GHL purchase event) is guarded by a timestamp column claimed atomically, so webhook retries,
 * duplicate deliveries and the success page racing the webhook can't send anything twice.
 */
const stripe = require("./stripe");
const db = require("./db");
const plans = require("./plans");
const mail = require("./mail");
const ghl = require("./ghl");
const token = require("./token");
const { SITE_URL, log } = require("./util");

const T = "nps_customers";
const ACTIVE = ["active", "trialing"];

const bySub = (id) => `stripe_subscription_id=eq.${db.enc(id)}`;

async function getRow(subscriptionId) {
  const r = await db.select(T, `${bySub(subscriptionId)}&limit=1`);
  return r[0] || null;
}

async function findByEmail(email) {
  return db.select(T, `email=eq.${db.enc(String(email).trim().toLowerCase())}&order=created_at.desc&limit=5`);
}

/** Status fields from a Stripe subscription object (works with older and newer API shapes). */
function subFields(sub) {
  const item = sub.items && sub.items.data && sub.items.data[0];
  const plan = plans.planForPrice(item && item.price);
  const periodEnd = sub.current_period_end || (item && item.current_period_end) || null;
  const out = {
    stripe_subscription_id: sub.id,
    stripe_customer_id: typeof sub.customer === "string" ? sub.customer : sub.customer && sub.customer.id,
    subscription_status: sub.status,
    cancel_at_period_end: Boolean(sub.cancel_at_period_end),
    current_period_end: periodEnd ? new Date(periodEnd * 1000).toISOString() : null,
    cancel_at: sub.cancel_at ? new Date(sub.cancel_at * 1000).toISOString() : sub.cancel_at_period_end && periodEnd ? new Date(periodEnd * 1000).toISOString() : null,
  };
  if (plan) out.plan = plan.key;
  return out;
}

function attributionFrom(metadata = {}) {
  const out = {};
  for (const [k, v] of Object.entries(metadata || {})) if (k.startsWith("attr_")) out[k.slice(5)] = v;
  return out;
}

/**
 * Look a Checkout Session up in Stripe, confirm it really paid for one of our subscriptions,
 * and upsert the customer row. Safe to call any number of times.
 * @returns {{paid:boolean, row?:object, session?:object, reason?:string}}
 */
async function recordCheckout(sessionId) {
  const s = await stripe.get(`/checkout/sessions/${encodeURIComponent(sessionId)}`, { expand: ["subscription"] });
  if (s.mode !== "subscription" || !s.subscription) return { paid: false, reason: "not_subscription", session: s };
  const sub = typeof s.subscription === "string" ? await stripe.get(`/subscriptions/${encodeURIComponent(s.subscription)}`) : s.subscription;
  const fields = subFields(sub);
  if (!fields.plan) return { paid: false, reason: "unknown_price", session: s }; // not one of our two plans
  const details = s.customer_details || {};
  const row = {
    ...fields,
    stripe_checkout_session_id: s.id,
    email: (details.email || s.customer_email || "").toLowerCase() || null,
    name: details.name || null,
    phone: details.phone || null,
    attribution: attributionFrom(s.metadata),
  };
  const saved = await db.upsert(T, row, "stripe_subscription_id");
  const paid = s.status === "complete" && s.payment_status === "paid" && ACTIVE.includes(sub.status);
  return { paid, row: saved[0], session: s };
}

/** Re-read a subscription from Stripe and store its current status. */
async function syncSubscription(subscriptionId) {
  const sub = await stripe.get(`/subscriptions/${encodeURIComponent(subscriptionId)}`);
  const fields = subFields(sub);
  const before = await getRow(subscriptionId);
  // not ours (another product on this Stripe account), or a checkout whose first payment hasn't succeeded:
  // no record yet, so the onboarding queue only lists people who actually paid
  if (!before && (!fields.plan || ["incomplete", "incomplete_expired"].includes(sub.status))) return { row: null, before: null, sub };
  const saved = await db.upsert(T, fields, "stripe_subscription_id");
  return { row: saved[0], before, sub };
}

function onboardingLink(subscriptionId) {
  return `${SITE_URL()}/client.html#t=${token.issue(subscriptionId)}`;
}

/** Shape used by the internal emails. */
function view(row) {
  const plan = plans.getPlan(row.plan) || { label: row.plan };
  const ob = row.onboarding_data || {};
  return {
    name: row.name || ob.contact_name,
    email: row.email,
    businessName: ob.business_name,
    planLabel: plan.label,
    status: row.subscription_status,
    onboarding: row.onboarding_status,
    source: Object.entries(row.attribution || {}).map(([k, v]) => `${k}=${v}`).join(", "),
    customerId: row.stripe_customer_id,
    subscriptionId: row.stripe_subscription_id,
    live: stripe.isLiveKey(),
  };
}

/** Shape sent to GoHighLevel. */
function ghlView(row) {
  const plan = plans.getPlan(row.plan) || {};
  const ob = row.onboarding_data || {};
  return { ...row, plan_label: plan.label, plan_tag: plan.tag, business_name: ob.business_name, phone: ob.phone || row.phone, name: row.name || ob.contact_name };
}

/* ---------- once-only steps, guarded by a timestamp column ---------- */
async function claim(subscriptionId, col) {
  const r = await db.update(T, `${bySub(subscriptionId)}&${col}=is.null`, { [col]: new Date().toISOString() });
  return r.length > 0;
}
async function release(subscriptionId, col) {
  await db.update(T, bySub(subscriptionId), { [col]: null });
}
async function once(row, col, fn) {
  if (!(await claim(row.stripe_subscription_id, col))) return "already_done";
  try {
    await fn();
    return "done";
  } catch (e) {
    await release(row.stripe_subscription_id, col).catch(() => {});
    throw e;
  }
}

/** Run every step even if one fails, then report all failures together (so Stripe retries). */
async function runSteps(row, steps) {
  const failures = [];
  for (const [col, enabled, fn] of steps) {
    if (!enabled) continue;
    try {
      const r = await once(row, col, fn);
      log("info", "step", { col, result: r, sub: row.stripe_subscription_id });
    } catch (e) {
      failures.push(`${col}: ${e.message}`);
    }
  }
  if (failures.length) throw new Error(failures.join("; "));
}

/** After Stripe confirms payment: welcome email, team notice, GHL purchase event. */
async function afterPurchase(row) {
  const plan = plans.getPlan(row.plan);
  const link = onboardingLink(row.stripe_subscription_id);
  await runSteps(row, [
    ["welcome_sent_at", Boolean(row.email), () =>
      mail.send({ to: row.email, ...mail.welcome({ name: row.name, planLabel: plan.label, priceLabel: plans.money(plan.amount), link }) })],
    ["team_notified_at", true, () => mail.send({ to: mail.TEAM(), ...mail.teamPurchase(view(row)) })],
    ["ghl_purchase_sent_at", Boolean(process.env.GHL_WEBHOOK_URL), () =>
      ghl.send("purchase_verified", ghlView(row), { onboarding_url: link, amount: plan.amount / 100, currency: "CAD" })],
  ]);
}

/** After setup is submitted: customer confirmation, team notice with the answers and file links, GHL event. */
async function afterOnboarding(row, files = []) {
  const plan = plans.getPlan(row.plan) || { label: row.plan };
  const to = row.email || (row.onboarding_data && row.onboarding_data.email);
  await runSteps(row, [
    ["customer_confirm_sent_at", Boolean(to), () =>
      mail.send({ to, ...mail.setupReceived({ name: row.name || (row.onboarding_data || {}).contact_name, planLabel: plan.label, answers: row.onboarding_data || {}, link: onboardingLink(row.stripe_subscription_id), fileCount: files.length }) })],
    ["onboarding_notified_at", true, () => mail.send({ to: mail.TEAM(), replyTo: row.email || undefined, ...mail.teamOnboarding(view(row), row.onboarding_data || {}, files, row.plan) })],
    ["ghl_onboarding_sent_at", Boolean(process.env.GHL_WEBHOOK_URL), () => ghl.send("onboarding_completed", ghlView(row))],
  ]);
}

async function updateRow(subscriptionId, patch) {
  const r = await db.update(T, bySub(subscriptionId), patch);
  return r[0] || null;
}

/** Exported for the reminder job and cancellation emails: run fn once per customer, guarded by a timestamp column. */
const sendOnce = once;

module.exports = { sendOnce, release, T, ACTIVE, getRow, findByEmail, recordCheckout, syncSubscription, onboardingLink, afterPurchase, afterOnboarding, updateRow, view, ghlView, subFields };
