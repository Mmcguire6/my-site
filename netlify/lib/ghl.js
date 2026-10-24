/**
 * GoHighLevel sync: each billing / onboarding event is POSTed as JSON to a GHL
 * workflow with an "Inbound Webhook" trigger. The workflow (built in GHL) does the
 * CRM work: create/update the contact, tags, the onboarding opportunity, emails.
 * Stripe stays the source of truth for billing; GHL gets a copy for operations.
 *
 *   GHL_WEBHOOK_URL  the Inbound Webhook URL from the GHL workflow trigger.
 *                    If unset, events are skipped (logged), not failed.
 */
const { log } = require("./util");

const TAGS = {
  customer: "NPS Customer",
  onboardingRequired: "Onboarding Required",
  onboardingComplete: "Onboarding Complete",
};

/** Suggested pipeline stage for each event (the GHL workflow decides what to do with it). */
const STAGE = {
  purchase_verified: "New Purchase",
  onboarding_started: "Awaiting Information",
  onboarding_completed: "Setup in Progress",
};

function contactFields(c) {
  const parts = String(c.name || "").trim().split(/\s+/);
  return {
    email: c.email || "",
    first_name: parts[0] || "",
    last_name: parts.slice(1).join(" "),
    phone: c.phone || "",
    company_name: c.business_name || "",
  };
}

/**
 * @param {string} event  purchase_verified | onboarding_started | onboarding_completed | payment_failed |
 *                        renewal_paid | subscription_status_changed | subscription_canceled | refund_issued
 * @param {object} c      customer row (nps_customers) plus optional extras
 */
async function send(event, c, extra = {}) {
  const url = process.env.GHL_WEBHOOK_URL;
  if (!url) {
    log("info", "ghl_skipped_not_configured", { event });
    return { skipped: true };
  }
  const tags = [TAGS.customer];
  if (c.plan_tag) tags.push(c.plan_tag);
  if (c.onboarding_status === "complete") tags.push(TAGS.onboardingComplete);
  else tags.push(TAGS.onboardingRequired);
  const body = {
    event,
    sent_at: new Date().toISOString(),
    ...contactFields(c),
    plan: c.plan || "",
    plan_label: c.plan_label || "",
    stripe_customer_id: c.stripe_customer_id || "",
    stripe_subscription_id: c.stripe_subscription_id || "",
    subscription_status: c.subscription_status || "",
    onboarding_status: c.onboarding_status || "",
    pipeline_stage: STAGE[event] || "",
    tags,
    source: (c.attribution && (c.attribution.utm_source || c.attribution.ref)) || "",
    ...extra,
  };
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`ghl_webhook_${res.status}`);
  return { ok: true };
}

module.exports = { send, TAGS, STAGE };
