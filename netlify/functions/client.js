/**
 * Northern Peak Systems — Client Hub API (Netlify Function)
 *
 * Endpoint: POST /api/client  {action, ...}   (/api/onboarding is kept as an alias)
 *   verify       {session_id}   after Stripe Checkout: confirms the payment with the Stripe API and signs the
 *                               customer in (only within 48 hours of checkout; later they use an emailed link)
 *   load         {token}        everything the Hub shows: plan, progress stage, setup answers, billing, files
 *   save         {token, data}  autosave setup answers (partial allowed)
 *   submit       {token, data}  validate and submit setup; moves the project to "build"
 *   signin       {email}        email a sign-in link to the address on file (same reply either way)
 *   upload-url   {token, filename, size, type, kind}   one-time signed URL to upload a logo / photo / file
 *   files        {token}        the customer's uploaded files (short-lived view links)
 *   delete-file  {token, key}
 *   portal       {token}        Stripe Customer Portal session (update card, invoices)
 *
 * Tokens are HMAC-signed and expire (lib/token.js); every action re-checks them and only ever touches the
 * token's own subscription. No passwords are collected.
 *
 * Env vars: STRIPE_SECRET_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, ONBOARDING_TOKEN_SECRET, RESEND_API_KEY,
 *           STRIPE_PORTAL_CONFIGURATION (optional), GHL_WEBHOOK_URL (optional)
 */
const stripe = require("../lib/stripe");
const customers = require("../lib/customers");
const plans = require("../lib/plans");
const token = require("../lib/token");
const mail = require("../lib/mail");
const storage = require("../lib/storage");
const fields = require("../lib/fields");
const { SITE_URL, corsHeaders, json, parseJson, EMAIL_RE, log } = require("../lib/util");

const SESSION_MAX_AGE_S = 48 * 3600;
const RESEND_COOLDOWN_MS = 2 * 60 * 1000;
const APP_URL = "https://app.northernpeaksystems.ca/";
const portalEnabled = () => Boolean(process.env.STRIPE_PORTAL_CONFIGURATION);

/* ---------- what the Hub shows ---------- */
function publicView(row) {
  const plan = plans.getPlan(row.plan) || {};
  return {
    plan: row.plan,
    plan_label: plan.label,
    price_label: plan.amount ? plans.money(plan.amount) : "",
    email: row.email,
    name: row.name,
    business_name: (row.onboarding_data || {}).business_name || "",
    subscription_status: row.subscription_status,
    onboarding_status: row.onboarding_status,
    onboarding_completed_at: row.onboarding_completed_at,
    // rows that finished setup before stages existed are already in Build
    project_stage: !row.project_stage || row.project_stage === "setup" ? (row.onboarding_status === "complete" ? "build" : "setup") : row.project_stage,
    team_note: row.team_note || "",
    site_url: row.site_url || "",
    app_url: row.plan === "peak" ? APP_URL : "",
    subscribed_at: row.created_at,
    data: row.onboarding_data || {},
    portal: portalEnabled(),
  };
}

/** Billing summary straight from Stripe (the source of truth). Never blocks the Hub if Stripe is slow. */
async function billing(row) {
  try {
    const [sub, invoices] = await Promise.all([
      stripe.get(`/subscriptions/${encodeURIComponent(row.stripe_subscription_id)}`, { expand: ["default_payment_method"] }),
      stripe.get("/invoices", { customer: row.stripe_customer_id, limit: 12 }),
    ]);
    let pm = sub.default_payment_method;
    if (!pm || typeof pm === "string") {
      const cus = await stripe.get(`/customers/${encodeURIComponent(row.stripe_customer_id)}`, { expand: ["invoice_settings.default_payment_method"] });
      pm = cus.invoice_settings && cus.invoice_settings.default_payment_method;
    }
    const item = sub.items && sub.items.data && sub.items.data[0];
    const periodEnd = sub.current_period_end || (item && item.current_period_end);
    return {
      status: sub.status,
      next_payment_at: periodEnd && !sub.cancel_at && !sub.cancel_at_period_end ? new Date(periodEnd * 1000).toISOString() : null,
      ends_at: sub.cancel_at ? new Date(sub.cancel_at * 1000).toISOString() : sub.cancel_at_period_end && periodEnd ? new Date(periodEnd * 1000).toISOString() : null,
      amount: item && item.price ? item.price.unit_amount / 100 : null,
      currency: String((item && item.price && item.price.currency) || "cad").toUpperCase(),
      card: pm && pm.card ? { brand: pm.card.brand, last4: pm.card.last4, exp_month: pm.card.exp_month, exp_year: pm.card.exp_year } : null,
      invoices: (invoices.data || []).filter((i) => i.status !== "draft").map((i) => ({
        number: i.number, date: new Date(i.created * 1000).toISOString(), total: i.total / 100, currency: String(i.currency).toUpperCase(),
        status: i.status, url: i.hosted_invoice_url, pdf: i.invoice_pdf,
      })),
    };
  } catch (e) {
    log("error", "billing_summary_failed", { message: e.message });
    return null;
  }
}

async function filesFor(subId) {
  try {
    const files = await storage.list(subId);
    const urls = await storage.viewUrls(files.map((f) => f.path));
    return files.map((f) => ({ key: f.key, kind: f.kind, name: f.name, size: f.size, type: f.type, uploaded_at: f.uploaded_at, url: urls[f.path] || null }));
  } catch (e) {
    log("error", "files_list_failed", { message: e.message });
    return [];
  }
}

async function hub(row) {
  const [bill, files] = await Promise.all([billing(row), filesFor(row.stripe_subscription_id)]);
  return { ...publicView(row), billing: bill, files };
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
      if (s.status === "complete" && s.payment_status === "unpaid") return json(202, { status: "pending" });
      return json(402, { status: "not_paid" });
    }
    if (Math.floor(Date.now() / 1000) - s.created > SESSION_MAX_AGE_S) return json(410, { status: "session_expired" });
    await customers.afterPurchase(r.row).catch((e) => log("error", "after_purchase_from_verify", { message: e.message }));
    const row = (await customers.getRow(r.row.stripe_subscription_id)) || r.row;
    return json(200, { status: "ok", token: token.issue(row.stripe_subscription_id), session: s.id, amount: (s.amount_total || 0) / 100, currency: String(s.currency || "cad").toUpperCase(), customer: await hub(row) });
  },

  async load(body) {
    const { row, sub, error } = await rowFromToken(body);
    if (error) return error;
    return json(200, { status: "ok", token: token.issue(sub), customer: await hub(row) });
  },

  async save(body) {
    const { row, sub, error } = await rowFromToken(body);
    if (error) return error;
    if (row.onboarding_status === "complete") return json(409, { error: "already_complete" });
    const data = { ...(row.onboarding_data || {}), ...fields.clean(body.data, row.plan) };
    const now = new Date().toISOString();
    await customers.updateRow(sub, { onboarding_data: data, onboarding_status: "in_progress", onboarding_started_at: row.onboarding_started_at || now });
    return json(200, { ok: true, saved_at: now });
  },

  async submit(body) {
    const { row, sub, error } = await rowFromToken(body);
    if (error) return error;
    if (row.onboarding_status === "complete") return json(200, { ok: true, already: true });
    const data = fields.clean(body.data, row.plan);
    const errors = fields.validate(data, row.plan);
    if (Object.keys(errors).length) return json(422, { error: "validation", fields: errors });
    const now = new Date().toISOString();
    const saved = await customers.updateRow(sub, {
      onboarding_data: data,
      onboarding_status: "complete",
      onboarding_completed_at: now,
      onboarding_started_at: row.onboarding_started_at || now,
      project_stage: !row.project_stage || row.project_stage === "setup" ? "build" : row.project_stage,
    });
    try {
      const files = await storage.list(sub).catch(() => []);
      const urls = await storage.viewUrls(files.map((f) => f.path), 7 * 86400).catch(() => ({}));
      await customers.afterOnboarding(saved, files.map((f) => ({ name: f.name, kind: f.kind, url: urls[f.path] })));
    } catch (e) {
      log("error", "after_onboarding_failed", { sub, message: e.message });
      await mail.send({ to: mail.TEAM(), ...mail.teamAlert({ where: "setup submitted", error: e.message, ref: sub }) }).catch(() => {});
    }
    return json(200, { ok: true, customer: await hub(saved) });
  },

  async signin(body) {
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

  async "upload-url"(body) {
    const { sub, error } = await rowFromToken(body);
    if (error) return error;
    const existing = await storage.list(sub).catch(() => []);
    try {
      const r = await storage.signUpload(sub, { filename: body.filename, size: Number(body.size), type: body.type, kind: body.kind }, existing.length);
      return json(200, r);
    } catch (e) {
      if (["bad_kind", "too_large", "bad_type", "too_many"].includes(e.code)) return json(400, { error: e.code });
      throw e;
    }
  },

  async files(body) {
    const { sub, error } = await rowFromToken(body);
    if (error) return error;
    return json(200, { files: await filesFor(sub) });
  },

  async "delete-file"(body) {
    const { sub, error } = await rowFromToken(body);
    if (error) return error;
    try {
      await storage.remove(sub, String(body.key || ""));
    } catch (e) {
      if (e.code === "bad_key") return json(400, { error: "bad_key" });
      throw e;
    }
    return json(200, { files: await filesFor(sub) });
  },

  async portal(body) {
    if (!portalEnabled()) return json(404, { error: "portal_disabled" });
    const { row, error } = await rowFromToken(body);
    if (error) return error;
    const session = await stripe.post("/billing_portal/sessions", {
      customer: row.stripe_customer_id,
      return_url: `${SITE_URL()}/client.html`,
      configuration: process.env.STRIPE_PORTAL_CONFIGURATION,
    });
    return json(200, { url: session.url });
  },
};
actions.resend = actions.signin; // older pages / links

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
    log("error", "client_hub_failed", { action: body.action, code: e.code, message: e.message });
    const unavailable = ["stripe_not_configured", "database_not_configured", "onboarding_secret_missing", "email_not_configured", "storage_not_configured"].includes(e.code);
    return json(unavailable ? 503 : 500, { error: unavailable ? "not_configured" : "server_error" }, cors);
  }
};
