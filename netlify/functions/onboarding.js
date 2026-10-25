/**
 * Northern Peak Systems — post-purchase onboarding (Netlify Function)
 *
 * Endpoint: POST /api/onboarding  {action, ...}
 *   verify  {session_id}   after Stripe redirects to /welcome.html. Confirms the payment with
 *                          the Stripe API (the redirect alone proves nothing) and returns a
 *                          signed onboarding token. Only works for 48 hours after checkout;
 *                          after that the customer uses the emailed link.
 *   load    {token}        resume from the emailed link (token in the URL fragment)
 *   save    {token, data}  autosave a draft (partial answers allowed)
 *   submit  {token, data}  validate everything and mark onboarding complete
 *   resend  {email}        email a fresh link to the address on file (same reply either way)
 *   portal  {token}        open the Stripe Customer Portal (if enabled)
 *
 * No passwords are ever collected. Answers are whitelisted and length-limited server-side.
 *
 * Env vars: STRIPE_SECRET_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, ONBOARDING_TOKEN_SECRET,
 *           RESEND_API_KEY, STRIPE_PORTAL_CONFIGURATION (optional, enables "Manage billing"),
 *           GHL_WEBHOOK_URL (optional)
 */
const stripe = require("../lib/stripe");
const customers = require("../lib/customers");
const plans = require("../lib/plans");
const token = require("../lib/token");
const mail = require("../lib/mail");
const { SITE_URL, corsHeaders, json, parseJson, EMAIL_RE, log } = require("../lib/util");

const SESSION_MAX_AGE_S = 48 * 3600;
const RESEND_COOLDOWN_MS = 2 * 60 * 1000;

/* ---------- the form, server-side ---------- */
const yes = (d, k) => d[k] === "yes";
const FIELDS = [
  { k: "business_name", req: true },
  { k: "contact_name", req: true },
  { k: "email", req: true, type: "email" },
  { k: "phone", req: true, type: "phone" },
  { k: "trade", req: true },
  { k: "city", req: true },
  { k: "region", req: true },
  { k: "country", req: true, options: ["Canada", "United States", "Other"] },
  { k: "service_area", req: true, max: 500 },
  { k: "has_website", req: true, options: ["yes", "no"] },
  { k: "website_url", reqIf: (d) => yes(d, "has_website"), type: "url" },
  { k: "owns_domain", req: true, options: ["yes", "no", "not_sure"] },
  { k: "desired_domain", max: 200 },
  { k: "description", req: true, max: 2000 },
  { k: "services", req: true, max: 2000 },
  { k: "uses_crm", req: true, peak: true, options: ["yes", "no"] },
  { k: "crm_name", peak: true, reqIf: (d) => yes(d, "uses_crm") },
  { k: "has_gbp", req: true, peak: true, options: ["yes", "no", "not_sure"] },
  { k: "calls_number", req: true, peak: true, type: "phone" },
  { k: "missed_call", req: true, peak: true, options: ["yes", "no", "not_sure"] },
  { k: "scheduling_software", peak: true, max: 500 },
  { k: "notes", max: 3000 },
];

function clean(data, planKey) {
  const out = {};
  for (const f of FIELDS) {
    if (f.peak && planKey !== "peak") continue;
    const v = data && data[f.k];
    if (v === undefined || v === null) continue;
    out[f.k] = String(v).replace(/\u0000/g, "").trim().slice(0, f.max || 200);
  }
  return out;
}

function validate(d, planKey) {
  const errors = {};
  for (const f of FIELDS) {
    if (f.peak && planKey !== "peak") continue;
    const v = d[f.k] || "";
    const required = f.req || (f.reqIf && f.reqIf(d));
    if (!v) {
      if (required) errors[f.k] = "required";
      continue;
    }
    if (f.options && !f.options.includes(v)) errors[f.k] = "invalid_option";
    else if (f.type === "email" && !EMAIL_RE.test(v)) errors[f.k] = "invalid_email";
    else if (f.type === "phone" && !/^[0-9+().\-\s]{7,25}$/.test(v)) errors[f.k] = "invalid_phone";
    else if (f.type === "url" && !/^(https?:\/\/)?[^\s/]+\.[^\s]{2,}$/i.test(v)) errors[f.k] = "invalid_url";
  }
  return errors;
}

/* ---------- helpers ---------- */
const portalEnabled = () => Boolean(process.env.STRIPE_PORTAL_CONFIGURATION);

function publicView(row) {
  const plan = plans.getPlan(row.plan) || {};
  return {
    plan: row.plan,
    plan_label: plan.label,
    price_label: plan.amount ? plans.money(plan.amount) : "",
    email: row.email,
    name: row.name,
    subscription_status: row.subscription_status,
    onboarding_status: row.onboarding_status,
    data: row.onboarding_data || {},
    portal: portalEnabled(),
  };
}

async function rowFromToken(body) {
  const sub = token.verify(body.token);
  if (!sub) return { error: json(401, { error: "invalid_token" }) };
  const row = await customers.getRow(sub);
  if (!row) return { error: json(404, { error: "not_found" }) };
  return { row, sub };
}

/* ---------- actions ---------- */
const actions = {
  async verify(body) {
    const id = String(body.session_id || "");
    if (!/^cs_(test|live)_[A-Za-z0-9]{10,}$/.test(id)) return json(400, { error: "invalid_session" });
    const r = await customers.recordCheckout(id);
    const s = r.session || {};
    if (!r.paid) {
      if (s.status === "complete" && s.payment_status === "unpaid") return json(202, { status: "pending" }); // bank payment still clearing
      return json(402, { status: "not_paid" });
    }
    if (Math.floor(Date.now() / 1000) - s.created > SESSION_MAX_AGE_S) return json(410, { status: "session_expired" });
    // The webhook normally sends these; running them here too (idempotent) covers a delayed webhook.
    await customers.afterPurchase(r.row).catch((e) => log("error", "after_purchase_from_verify", { message: e.message }));
    const row = (await customers.getRow(r.row.stripe_subscription_id)) || r.row;
    return json(200, { status: "ok", token: token.issue(row.stripe_subscription_id), session: s.id, amount: (s.amount_total || 0) / 100, currency: String(s.currency || "cad").toUpperCase(), customer: publicView(row) });
  },

  async load(body) {
    const { row, sub, error } = await rowFromToken(body);
    if (error) return error;
    return json(200, { status: "ok", token: token.issue(sub), customer: publicView(row) });
  },

  async save(body) {
    const { row, sub, error } = await rowFromToken(body);
    if (error) return error;
    if (row.onboarding_status === "complete") return json(409, { error: "already_complete" });
    const data = { ...(row.onboarding_data || {}), ...clean(body.data, row.plan) };
    const now = new Date().toISOString();
    await customers.updateRow(sub, { onboarding_data: data, onboarding_status: "in_progress", onboarding_started_at: row.onboarding_started_at || now });
    return json(200, { ok: true, saved_at: now });
  },

  async submit(body) {
    const { row, sub, error } = await rowFromToken(body);
    if (error) return error;
    if (row.onboarding_status === "complete") return json(200, { ok: true, already: true });
    const data = clean(body.data, row.plan);
    const errors = validate(data, row.plan);
    if (Object.keys(errors).length) return json(422, { error: "validation", fields: errors });
    const now = new Date().toISOString();
    const saved = await customers.updateRow(sub, {
      onboarding_data: data,
      onboarding_status: "complete",
      onboarding_completed_at: now,
      onboarding_started_at: row.onboarding_started_at || now,
    });
    try {
      await customers.afterOnboarding(saved);
    } catch (e) {
      // the answers are saved; tell the team the follow-up didn't go out, don't fail the customer
      log("error", "after_onboarding_failed", { sub, message: e.message });
      await mail.send({ to: mail.TEAM(), ...mail.teamAlert({ where: "onboarding submitted", error: e.message, ref: sub }) }).catch(() => {});
    }
    return json(200, { ok: true });
  },

  async resend(body) {
    const email = String(body.email || "").trim().toLowerCase();
    const reply = json(200, { ok: true }); // same answer whether or not we found anyone
    if (!EMAIL_RE.test(email)) return reply;
    const rows = await customers.findByEmail(email);
    for (const row of rows) {
      if (!customers.ACTIVE.includes(row.subscription_status) && row.subscription_status !== "past_due") continue;
      if (row.link_sent_at && Date.now() - new Date(row.link_sent_at).getTime() < RESEND_COOLDOWN_MS) continue;
      await customers.updateRow(row.stripe_subscription_id, { link_sent_at: new Date().toISOString() });
      await mail.send({ to: row.email, ...mail.resumeLink({ name: row.name, planLabel: (plans.getPlan(row.plan) || {}).label, link: customers.onboardingLink(row.stripe_subscription_id) }) });
      break;
    }
    return reply;
  },

  async portal(body) {
    if (!portalEnabled()) return json(404, { error: "portal_disabled" });
    const { row, error } = await rowFromToken(body);
    if (error) return error;
    const session = await stripe.post("/billing_portal/sessions", {
      customer: row.stripe_customer_id,
      return_url: `${SITE_URL()}/welcome.html`,
      configuration: process.env.STRIPE_PORTAL_CONFIGURATION,
    });
    return json(200, { url: session.url });
  },
};

exports.handler = async (event) => {
  const cors = corsHeaders(event);
  if (event.httpMethod === "OPTIONS") return { statusCode: 204, headers: cors, body: "" };
  if (event.httpMethod !== "POST") return json(405, { error: "method_not_allowed" }, cors);
  const body = parseJson(event);
  if (!body || !Object.prototype.hasOwnProperty.call(actions, body.action)) return json(400, { error: "bad_request" }, cors);
  try {
    const r = await actions[body.action](body);
    r.headers = { ...cors, ...r.headers };
    return r;
  } catch (e) {
    log("error", "onboarding_failed", { action: body.action, code: e.code, message: e.message });
    const unavailable = ["stripe_not_configured", "database_not_configured", "onboarding_secret_missing", "email_not_configured"].includes(e.code);
    return json(unavailable ? 503 : 500, { error: unavailable ? "not_configured" : "server_error" }, cors);
  }
};

module.exports.FIELDS = FIELDS; // for tests
module.exports.validate = validate;
module.exports.clean = clean;
