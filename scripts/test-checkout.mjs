#!/usr/bin/env node
/**
 * Offline tests for self-serve checkout, the Stripe webhook and onboarding.
 *   node --test scripts/test-checkout.mjs
 * Stripe, Supabase (PostgREST), Resend and GoHighLevel are replaced by in-memory fakes,
 * so this runs without any credentials and never touches a real account.
 */
import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);

/* ---------------- environment ---------------- */
const WHSEC = "whsec_test_secret_for_unit_tests";
Object.assign(process.env, {
  STRIPE_SECRET_KEY: "sk_test_unit",
  STRIPE_WEBHOOK_SECRET: WHSEC,
  STRIPE_PRICE_BASE: "price_base",
  STRIPE_PRICE_PEAK: "price_peak",
  SUPABASE_URL: "https://db.test",
  SUPABASE_SERVICE_KEY: "sb_secret_unit",
  RESEND_API_KEY: "re_unit",
  ONBOARDING_TOKEN_SECRET: "x".repeat(48),
  GHL_WEBHOOK_URL: "https://ghl.test/hook",
  SITE_URL: "https://site.test",
  TO_EMAIL: "team@test",
});
delete process.env.STRIPE_PORTAL_CONFIGURATION;

/* ---------------- fakes ---------------- */
const now = () => Math.floor(Date.now() / 1000);
let db, stripeState, emails, ghlCalls, ghlFailures, emailFailures, files;

const UNIQUE = { nps_customers: ["stripe_subscription_id", "stripe_checkout_session_id"], nps_stripe_events: ["id"] };
const DEFAULTS = {
  nps_customers: () => ({ onboarding_status: "awaiting_information", onboarding_data: {}, attribution: {}, cancel_at_period_end: false, created_at: new Date().toISOString() }),
  nps_stripe_events: () => ({ status: "processing", attempts: 1, steps_done: [], alerted: false, received_at: new Date().toISOString() }),
};
function matches(row, params) {
  for (const [k, v] of params) {
    if (["limit", "order", "on_conflict", "select"].includes(k)) continue;
    const [op, ...rest] = v.split(".");
    const val = rest.join(".");
    if (op === "eq" && String(row[k]) !== val) return false;
    if (op === "neq" && String(row[k]) === val) return false;
    if (op === "in" && !val.replace(/^\(|\)$/g, "").split(",").includes(String(row[k]))) return false;
    if (op === "not" && val === "is.null" && row[k] == null) return false;
    if (op === "is" && val === "null" && row[k] != null) return false;
    if (op === "is" && val === "false" && row[k] !== false) return false;
  }
  return true;
}
function postgrest(method, url, body, prefer = "") {
  const u = new URL(url);
  const table = u.pathname.replace("/rest/v1/", "");
  const rows = (db[table] = db[table] || []);
  const params = [...u.searchParams.entries()];
  if (method === "GET") {
    let out = rows.filter((r) => matches(r, params));
    const order = u.searchParams.get("order");
    if (order) {
      const [col, dir] = order.split(".");
      out = [...out].sort((a, b) => (a[col] > b[col] ? 1 : -1) * (dir === "desc" ? -1 : 1));
    }
    const limit = Number(u.searchParams.get("limit") || 1e9);
    return [200, out.slice(0, limit)];
  }
  if (method === "POST") {
    const conflictCol = u.searchParams.get("on_conflict");
    const existing = rows.find((r) => (conflictCol ? [conflictCol] : UNIQUE[table]).some((c) => body[c] != null && r[c] === body[c]));
    if (existing) {
      if (prefer.includes("ignore-duplicates")) return [201, []];
      if (prefer.includes("merge-duplicates")) {
        Object.assign(existing, body, { updated_at: new Date().toISOString() });
        return [201, [existing]];
      }
      return [409, { code: "23505", message: "duplicate key" }];
    }
    const row = { ...DEFAULTS[table](), updated_at: new Date().toISOString(), ...body };
    rows.push(row);
    return [201, [row]];
  }
  if (method === "PATCH") {
    const hit = rows.filter((r) => matches(r, params));
    hit.forEach((r) => Object.assign(r, body, table === "nps_customers" ? { updated_at: new Date().toISOString() } : {}));
    return [200, hit];
  }
  return [405, {}];
}
const form = (body) => Object.fromEntries(new URLSearchParams(body || ""));
function stripeApi(method, url, body) {
  const u = new URL(url);
  const p = u.pathname.replace("/v1", "");
  let m;
  if (method === "GET" && (m = p.match(/^\/prices\/(.+)$/))) return stripeState.prices[m[1]] ? [200, stripeState.prices[m[1]]] : [404, { error: { message: "No such price" } }];
  if (method === "POST" && p === "/checkout/sessions") {
    const params = form(body);
    const id = `cs_test_${Math.random().toString(36).slice(2, 14)}abc`;
    stripeState.created.push({ id, params });
    return [200, { id, url: `https://checkout.stripe.com/c/pay/${id}` }];
  }
  if (method === "GET" && (m = p.match(/^\/checkout\/sessions\/(.+)$/))) {
    const s = stripeState.sessions[decodeURIComponent(m[1])];
    if (!s) return [404, { error: { message: "No such session" } }];
    return [200, { ...s, subscription: s.subscription ? stripeState.subscriptions[s.subscription] || s.subscription : null }];
  }
  if (method === "GET" && (m = p.match(/^\/subscriptions\/(.+)$/))) {
    const s = stripeState.subscriptions[decodeURIComponent(m[1])];
    return s ? [200, s] : [404, { error: { message: "No such subscription" } }];
  }
  if (method === "POST" && p === "/billing_portal/sessions") return [200, { url: "https://billing.stripe.com/p/session/test", params: form(body) }];
  if (method === "GET" && p === "/invoices") return [200, { data: [{ number: "NPS-0001", created: now(), total: 29700, currency: "cad", status: "paid", hosted_invoice_url: "https://invoice.stripe.com/i/1", invoice_pdf: "https://pay.stripe.com/invoice/1/pdf" }] }];
  if (method === "GET" && (m = p.match(/^\/customers\/(.+)$/))) return [200, { id: m[1], invoice_settings: { default_payment_method: { card: { brand: "visa", last4: "4242", exp_month: 12, exp_year: 2034 } } } }];
  return [404, { error: { message: `unmocked ${method} ${p}` } }];
}
function storageApi(method, url, body) {
  const p = new URL(url).pathname.replace("/storage/v1", "");
  let m;
  if (method === "POST" && (m = p.match(/^\/object\/upload\/sign\/client-files\/(.+)$/))) return [200, { url: `/object/upload/sign/client-files/${m[1]}?token=up_${files.length}` }];
  if (method === "POST" && p === "/object/list/client-files") {
    const prefix = body.prefix;
    return [200, files.filter((f) => f.startsWith(prefix)).map((f) => ({ id: f, name: f.slice(prefix.length), created_at: new Date().toISOString(), metadata: { size: 1234, mimetype: "image/png" } }))];
  }
  if (method === "POST" && p === "/object/sign/client-files") return [200, body.paths.map((x) => ({ path: x, signedURL: `/object/sign/client-files/${x}?token=view` }))];
  if (method === "DELETE" && p === "/object/client-files") { files = files.filter((f) => !body.prefixes.includes(f)); return [200, []]; }
  return [404, { message: "unmocked storage" }];
}
globalThis.fetch = async (url, opts = {}) => {
  const method = opts.method || "GET";
  const respond = ([status, obj]) => ({ ok: status < 400, status, json: async () => obj, text: async () => JSON.stringify(obj) });
  if (url.startsWith("https://db.test/storage/v1/")) return respond(storageApi(method, url, opts.body ? JSON.parse(opts.body) : undefined));
  if (url.startsWith("https://db.test/rest/v1/")) return respond(postgrest(method, url, opts.body ? JSON.parse(opts.body) : undefined, (opts.headers || {}).Prefer));
  if (url.startsWith("https://api.stripe.com/v1/")) return respond(stripeApi(method, url, opts.body));
  if (url === "https://api.resend.com/emails") {
    if (emailFailures > 0) {
      emailFailures--;
      return respond([500, { message: "resend down" }]);
    }
    const b = JSON.parse(opts.body);
    emails.push({ to: b.to[0], subject: b.subject, html: b.html });
    return respond([200, { id: `em_${emails.length}` }]);
  }
  if (url === "https://ghl.test/hook") {
    if (ghlFailures > 0) {
      ghlFailures--;
      return respond([500, {}]);
    }
    ghlCalls.push(JSON.parse(opts.body));
    return respond([200, {}]);
  }
  throw new Error(`unexpected fetch ${url}`);
};

const fn = (name) => require(path.join(root, "netlify/functions", `${name}.js`)).handler;
const checkout = fn("checkout");
const webhook = fn("stripe-webhook");
const onboarding = fn("onboarding");
const reminders = require(path.join(root, "netlify/functions/onboarding-reminders.js")).run;
const stripeLib = require(path.join(root, "netlify/lib/stripe.js"));
const tokenLib = require(path.join(root, "netlify/lib/token.js"));

const get = (q, extra = {}) => checkout({ httpMethod: "GET", path: "/api/checkout", headers: {}, queryStringParameters: q, ...extra });
let evtSeq = 0;
function send(type, object, { id, secret = WHSEC, t } = {}) {
  const raw = JSON.stringify({ id: id || `evt_${++evtSeq}`, type, livemode: false, data: { object } });
  return webhook({ httpMethod: "POST", headers: { "stripe-signature": stripeLib.signForTest(raw, secret, t) }, body: raw, isBase64Encoded: false });
}
const ob = async (body) => {
  const r = await onboarding({ httpMethod: "POST", headers: {}, body: JSON.stringify(body) });
  return { status: r.statusCode, body: JSON.parse(r.body) };
};
function purchase(plan, { sub = `sub_${plan}`, cs = `cs_test_${plan}0000000000`, paid = true, status = "active", email = "owner@example.com", created = now() } = {}) {
  stripeState.subscriptions[sub] = { id: sub, customer: `cus_${plan}`, status, cancel_at_period_end: false, current_period_end: now() + 30 * 86400, items: { data: [{ price: { id: `price_${plan}` } }] } };
  stripeState.sessions[cs] = { id: cs, mode: "subscription", status: "complete", payment_status: paid ? "paid" : "unpaid", subscription: sub, customer: `cus_${plan}`, created, amount_total: plan === "peak" ? 29700 : 9700, currency: "cad", customer_details: { email: email.toUpperCase(), name: "Pat Owner" }, metadata: { plan, attr_utm_source: "coldemail" } };
  return { sub, cs };
}
const customerRow = (sub) => db.nps_customers.find((r) => r.stripe_subscription_id === sub);
const tokenFromWelcome = () => {
  const m = emails.find((e) => e.subject.startsWith("You're in")).html.match(/#t=([A-Za-z0-9_\-.]+)/);
  return m[1];
};
const BASE_ANSWERS = { business_name: "Pat's Plumbing", contact_name: "Pat Owner", email: "owner@example.com", phone: "780-555-0101", trade: "Plumbing", city: "Edmonton", region: "AB", country: "Canada", service_area: "Edmonton and St. Albert", has_website: "no", owns_domain: "no", desired_domain: "patsplumbing.ca", description: "Residential plumbing.", services: "Repairs, water heaters" };
const PEAK_ANSWERS = { ...BASE_ANSWERS, uses_crm: "no", has_gbp: "yes", calls_number: "780-555-0101", missed_call: "yes" };

beforeEach(() => {
  db = { nps_customers: [], nps_stripe_events: [] };
  emails = [];
  ghlCalls = [];
  ghlFailures = 0;
  emailFailures = 0;
  files = [];
  stripeState = {
    created: [],
    sessions: {},
    subscriptions: {},
    prices: {
      price_base: { id: "price_base", active: true, type: "recurring", unit_amount: 9700, currency: "cad", recurring: { interval: "month" } },
      price_peak: { id: "price_peak", active: true, type: "recurring", unit_amount: 29700, currency: "cad", recurring: { interval: "month" } },
    },
  };
});

/* ---------------- checkout ---------------- */
test("Get Started (peak) redirects to Stripe with the server-side price and attribution", async () => {
  const r = await get({ plan: "peak", utm_source: "coldcall", price: "price_evil", amount: "1" });
  assert.equal(r.statusCode, 303);
  assert.match(r.headers.Location, /^https:\/\/checkout\.stripe\.com\//);
  const p = stripeState.created[0].params;
  assert.equal(p["line_items[0][price]"], "price_peak");
  assert.equal(p.mode, "subscription");
  assert.equal(p["metadata[plan]"], "peak");
  assert.equal(p["metadata[attr_utm_source]"], "coldcall");
  assert.equal(p["payment_method_types[0]"], "card");
  assert.equal(p["payment_method_types[1]"], "link");
  assert.equal(p["payment_method_types[2]"], undefined, "no buy-now-pay-later methods");
  assert.equal(p.success_url, "https://site.test/client.html?session_id={CHECKOUT_SESSION_ID}");
  assert.ok(!JSON.stringify(p).includes("price_evil"));
});

test("Base plan uses the base price; package links /start/base work", async () => {
  await get({ plan: "base" });
  await checkout({ httpMethod: "GET", path: "/start/base", headers: {}, queryStringParameters: { ref: "demo" } });
  assert.equal(stripeState.created[0].params["line_items[0][price]"], "price_base");
  assert.equal(stripeState.created[1].params["line_items[0][price]"], "price_base");
  assert.equal(stripeState.created[1].params["metadata[attr_ref]"], "demo");
});

test("Unknown plan and misconfigured price never reach Stripe Checkout", async () => {
  const bad = await get({ plan: "enterprise" });
  assert.match(bad.headers.Location, /pricing\.html\?checkout=invalid/);
  // someone pastes the wrong price ID into Netlify (Stripe price amounts can't change, so a mismatch is always a different ID)
  stripeState.prices.price_wrong = { id: "price_wrong", active: true, type: "recurring", unit_amount: 2900, currency: "usd", recurring: { interval: "month" } };
  process.env.STRIPE_PRICE_PEAK = "price_wrong";
  const mism = await checkout({ httpMethod: "POST", headers: {}, body: JSON.stringify({ plan: "peak" }) });
  process.env.STRIPE_PRICE_PEAK = "price_peak";
  assert.equal(mism.statusCode, 503);
  assert.equal(stripeState.created.length, 0);
  delete process.env.STRIPE_SECRET_KEY; // keys not set yet: graceful, no crash
  const off = await get({ plan: "base" });
  process.env.STRIPE_SECRET_KEY = "sk_test_unit";
  assert.match(off.headers.Location, /pricing\.html\?checkout=unavailable/);
});

/* ---------------- webhook security ---------------- */
test("Webhook rejects bad and replayed signatures", async () => {
  purchase("base");
  assert.equal((await send("checkout.session.completed", { id: "cs_test_base0000000000", mode: "subscription" }, { secret: "whsec_wrong" })).statusCode, 400);
  assert.equal((await send("checkout.session.completed", { id: "cs_test_base0000000000", mode: "subscription" }, { t: now() - 3600 })).statusCode, 400);
  assert.equal(emails.length, 0);
});

/* ---------------- scenario A / B ---------------- */
test("Scenario A: Base purchase -> customer record, one welcome, team notice, GHL, onboarding", async () => {
  const { sub, cs } = purchase("base");
  const r = await send("checkout.session.completed", { id: cs, mode: "subscription", payment_status: "paid", subscription: sub });
  assert.equal(r.statusCode, 200);
  const row = customerRow(sub);
  assert.equal(row.plan, "base");
  assert.equal(row.email, "owner@example.com");
  assert.equal(row.subscription_status, "active");
  assert.deepEqual(row.attribution, { utm_source: "coldemail" });
  assert.equal(emails.filter((e) => e.to === "owner@example.com").length, 1);
  assert.equal(emails.filter((e) => e.to === "team@test").length, 1);
  assert.equal(ghlCalls.length, 1);
  assert.equal(ghlCalls[0].event, "purchase_verified");
  assert.deepEqual(ghlCalls[0].tags, ["NPS Customer", "Base System Subscription", "Onboarding Required"]);
  assert.equal(ghlCalls[0].stripe_subscription_id, sub);

  const t = tokenFromWelcome();
  const loaded = await ob({ action: "load", token: t });
  assert.equal(loaded.status, 200);
  assert.equal(loaded.body.customer.plan, "base");
  const missing = await ob({ action: "submit", token: t, data: { ...BASE_ANSWERS, business_name: "" } });
  assert.equal(missing.status, 422);
  assert.equal(missing.body.fields.business_name, "required");
  const done = await ob({ action: "submit", token: t, data: { ...BASE_ANSWERS, password: "hunter2" } });
  assert.equal(done.status, 200);
  assert.equal(customerRow(sub).onboarding_status, "complete");
  assert.ok(!("password" in customerRow(sub).onboarding_data), "unknown fields are dropped");
  assert.ok(emails.some((e) => e.subject.startsWith("Setup complete:")));
  assert.equal(ghlCalls.at(-1).event, "onboarding_completed");
  assert.ok(ghlCalls.at(-1).tags.includes("Onboarding Complete"));
});

test("Scenario B: Peak purchase requires the Peak system questions", async () => {
  const { sub, cs } = purchase("peak");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const t = tokenFromWelcome();
  const r1 = await ob({ action: "submit", token: t, data: BASE_ANSWERS });
  assert.equal(r1.status, 422);
  assert.equal(r1.body.fields.calls_number, "required");
  const r2 = await ob({ action: "submit", token: t, data: { ...PEAK_ANSWERS, uses_crm: "yes" } });
  assert.equal(r2.body.fields.crm_name, "required");
  const r3 = await ob({ action: "submit", token: t, data: PEAK_ANSWERS });
  assert.equal(r3.status, 200);
  assert.equal(customerRow(sub).plan, "peak");
  assert.ok(ghlCalls[0].tags.includes("Peak System Subscription"));
});

test("Success page verifies with Stripe; racing the webhook still sends one welcome", async () => {
  const { sub, cs } = purchase("peak");
  const v = await ob({ action: "verify", session_id: cs }); // success page first
  assert.equal(v.status, 200);
  assert.ok(tokenLib.verify(v.body.token));
  assert.equal(v.body.customer.plan_label, "The Peak System");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  await ob({ action: "verify", session_id: cs });
  assert.equal(emails.filter((e) => e.subject.startsWith("You're in")).length, 1);
  assert.equal(ghlCalls.filter((c) => c.event === "purchase_verified").length, 1);
  assert.equal((await ob({ action: "verify", session_id: "../../etc" })).status, 400);
});

test("Old checkout links can't be replayed into the onboarding form", async () => {
  const { cs } = purchase("base", { created: now() - 3 * 86400 });
  assert.equal((await ob({ action: "verify", session_id: cs })).status, 410);
});

/* ---------------- scenario D ---------------- */
test("Scenario D: abandoned onboarding resumes securely", async () => {
  const { sub, cs } = purchase("peak");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const t = tokenFromWelcome();
  assert.equal((await ob({ action: "save", token: t, data: { business_name: "Pat's Plumbing", city: "Edmonton" } })).status, 200);
  assert.equal(customerRow(sub).onboarding_status, "in_progress");
  const back = await ob({ action: "load", token: t });
  assert.equal(back.body.customer.data.business_name, "Pat's Plumbing");
  // lost the email: ask for a new link (same reply for unknown addresses)
  assert.equal((await ob({ action: "resend", email: "OWNER@example.com" })).status, 200);
  assert.equal((await ob({ action: "resend", email: "owner@example.com" })).status, 200); // cooldown: no second email
  assert.equal((await ob({ action: "resend", email: "stranger@example.com" })).status, 200);
  assert.equal(emails.filter((e) => e.subject === "Your Client Hub sign-in link").length, 1);
  // tampered / expired tokens get nothing
  const forged = t.slice(0, -2) + (t.endsWith("A") ? "BB" : "AA");
  assert.equal((await ob({ action: "load", token: forged })).status, 401);
  const expired = tokenLib.issue(sub, 30, Date.now() - 31 * 86400 * 1000);
  assert.equal((await ob({ action: "load", token: expired })).status, 401);
  assert.equal((await ob({ action: "load", token: tokenLib.issue("sub_someone_else") })).status, 404);
});

/* ---------------- scenario E ---------------- */
test("Scenario E: unpaid / failed payments never start onboarding", async () => {
  const { sub, cs } = purchase("base", { paid: false, status: "incomplete" });
  assert.equal((await send("checkout.session.completed", { id: cs, mode: "subscription" })).statusCode, 200);
  assert.equal(emails.length, 0);
  assert.equal(ghlCalls.length, 0);
  assert.equal((await ob({ action: "verify", session_id: cs })).status, 202); // still clearing
  stripeState.sessions[cs].status = "open";
  assert.equal((await ob({ action: "verify", session_id: cs })).status, 402);
  await send("invoice.payment_failed", { subscription: sub, billing_reason: "subscription_create" });
  assert.equal(emails.length, 0);
  assert.notEqual(customerRow(sub).onboarding_status, "complete");
});

/* ---------------- scenario F ---------------- */
test("Scenario F: duplicate deliveries create one record, one email, one CRM event", async () => {
  const { cs, sub } = purchase("peak");
  const obj = { id: cs, mode: "subscription" };
  for (let i = 0; i < 3; i++) assert.equal((await send("checkout.session.completed", obj, { id: "evt_dupe" })).statusCode, 200);
  await send("checkout.session.async_payment_succeeded", obj); // a different event for the same purchase
  assert.equal(db.nps_customers.length, 1);
  assert.equal(emails.filter((e) => e.subject.startsWith("You're in")).length, 1);
  assert.equal(ghlCalls.filter((c) => c.event === "purchase_verified").length, 1);
  assert.equal(db.nps_stripe_events.find((e) => e.id === "evt_dupe").status, "done");
  assert.ok(customerRow(sub));
});

test("A failing CRM call is retried without re-sending the welcome, and alerts once", async () => {
  const { cs } = purchase("base");
  ghlFailures = 2;
  const obj = { id: cs, mode: "subscription" };
  assert.equal((await send("checkout.session.completed", obj, { id: "evt_retry" })).statusCode, 500);
  assert.equal((await send("checkout.session.completed", obj, { id: "evt_retry" })).statusCode, 500);
  assert.equal(db.nps_stripe_events[0].status, "failed");
  assert.equal((await send("checkout.session.completed", obj, { id: "evt_retry" })).statusCode, 200);
  assert.equal(emails.filter((e) => e.subject.startsWith("You're in")).length, 1);
  assert.equal(emails.filter((e) => e.subject.startsWith("Action needed")).length, 1);
  assert.equal(ghlCalls.length, 1);
});

/* ---------------- lifecycle ---------------- */
test("Lifecycle: past_due, cancellation, renewal and refund are recorded, data kept", async () => {
  const { sub, cs } = purchase("peak");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  await ob({ action: "submit", token: tokenFromWelcome(), data: PEAK_ANSWERS });
  ghlCalls = [];
  const team = () => emails.filter((e) => e.subject.startsWith("Billing update")).length;

  stripeState.subscriptions[sub].status = "past_due";
  await send("customer.subscription.updated", { id: sub }, { id: "evt_pd" });
  await send("customer.subscription.updated", { id: sub }, { id: "evt_pd" });
  assert.equal(customerRow(sub).subscription_status, "past_due");
  assert.equal(ghlCalls.filter((c) => c.event === "subscription_status_changed").length, 1);
  assert.equal(team(), 1);

  stripeState.subscriptions[sub].status = "active";
  await send("invoice.paid", { subscription: sub, billing_reason: "subscription_cycle", amount_paid: 29700, currency: "cad", status_transitions: { paid_at: now() } });
  assert.ok(customerRow(sub).last_payment_at);
  assert.ok(ghlCalls.some((c) => c.event === "renewal_paid" && c.amount === 297));

  await send("invoice.payment_failed", { subscription: sub, billing_reason: "subscription_cycle", attempt_count: 1 });
  assert.ok(ghlCalls.some((c) => c.event === "payment_failed"));

  await send("charge.refunded", { customer: "cus_peak", amount_refunded: 29700, currency: "cad" });
  assert.ok(ghlCalls.some((c) => c.event === "refund_issued"));

  stripeState.subscriptions[sub].status = "canceled";
  await send("customer.subscription.deleted", { id: sub });
  const row = customerRow(sub);
  assert.equal(row.subscription_status, "canceled");
  assert.equal(row.onboarding_data.business_name, "Pat's Plumbing", "nothing is deleted on cancel");
  assert.ok(ghlCalls.some((c) => c.event === "subscription_canceled"));
});

test("Subscriptions for other products on the same Stripe account are ignored", async () => {
  stripeState.subscriptions.sub_other = { id: "sub_other", customer: "cus_x", status: "active", items: { data: [{ price: { id: "price_unrelated" } }] } };
  await send("customer.subscription.created", { id: "sub_other" });
  assert.equal(db.nps_customers.length, 0);
});

test("A declined first payment leaves no customer record in the onboarding queue", async () => {
  const { sub } = purchase("peak", { paid: false, status: "incomplete" });
  await send("customer.subscription.created", { id: sub });
  stripeState.subscriptions[sub].status = "incomplete_expired";
  await send("customer.subscription.updated", { id: sub });
  assert.equal(db.nps_customers.length, 0);
  assert.equal(emails.length, 0);
});

test("Billing portal only opens when enabled, for the token's own customer", async () => {
  const { cs } = purchase("base");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const t = tokenFromWelcome();
  assert.equal((await ob({ action: "portal", token: t })).status, 404);
  process.env.STRIPE_PORTAL_CONFIGURATION = "bpc_test";
  const r = await ob({ action: "portal", token: t });
  assert.equal(r.status, 200);
  assert.match(r.body.url, /^https:\/\/billing\.stripe\.com\//);
  delete process.env.STRIPE_PORTAL_CONFIGURATION;
});

/* ---------------- customer emails ---------------- */
const subjects = (to) => emails.filter((e) => !to || e.to === to).map((e) => e.subject);

test("Submitting setup info emails the customer a confirmation, once", async () => {
  const { cs } = purchase("peak");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const t = tokenFromWelcome();
  await ob({ action: "submit", token: t, data: PEAK_ANSWERS });
  await ob({ action: "submit", token: t, data: PEAK_ANSWERS });
  const conf = emails.filter((e) => e.subject === "We've got your setup information");
  assert.equal(conf.length, 1);
  assert.equal(conf[0].to, "owner@example.com");
  assert.ok(conf[0].html.includes("Pat&#39;s Plumbing") || conf[0].html.includes("Pat's Plumbing"));
});

test("A failed renewal emails the customer a pay-with-another-card link, once", async () => {
  const { sub, cs } = purchase("base");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const inv = { subscription: sub, billing_reason: "subscription_cycle", attempt_count: 1, amount_due: 9700, currency: "cad", hosted_invoice_url: "https://invoice.stripe.com/i/test_123", next_payment_attempt: now() + 3 * 86400 };
  await send("invoice.payment_failed", inv, { id: "evt_fail1" });
  await send("invoice.payment_failed", inv, { id: "evt_fail1" });
  const mails = emails.filter((e) => e.to === "owner@example.com" && e.subject.includes("didn't go through"));
  assert.equal(mails.length, 1);
  assert.ok(mails[0].html.includes("https://invoice.stripe.com/i/test_123"));
  assert.ok(mails[0].html.includes("$97.00 CAD"));
});

test("Cancellation: scheduled end confirmed once; no second email when it ends", async () => {
  const { sub, cs } = purchase("peak");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const endsAt = now() + 30 * 86400;
  stripeState.subscriptions[sub].cancel_at = endsAt;
  await send("customer.subscription.updated", { id: sub }, { id: "evt_sched" });
  await send("customer.subscription.updated", { id: sub }, { id: "evt_sched2" });
  assert.equal(subjects("owner@example.com").filter((s) => s === "Your cancellation is confirmed").length, 1);
  stripeState.subscriptions[sub].status = "canceled";
  await send("customer.subscription.deleted", { id: sub });
  assert.equal(subjects("owner@example.com").filter((s) => s.startsWith("Your Northern Peak Systems subscription has ended")).length, 0);
  assert.ok(customerRow(sub).cancel_at);
});

test("Cancellation: withdrawn then rescheduled confirms again; an immediate cancel says it has ended", async () => {
  const { sub, cs } = purchase("peak");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  stripeState.subscriptions[sub].cancel_at = now() + 30 * 86400;
  await send("customer.subscription.updated", { id: sub });
  stripeState.subscriptions[sub].cancel_at = null;
  await send("customer.subscription.updated", { id: sub });
  assert.equal(customerRow(sub).cancel_confirm_sent_at, null);
  stripeState.subscriptions[sub].cancel_at = now() + 40 * 86400;
  await send("customer.subscription.updated", { id: sub });
  assert.equal(subjects("owner@example.com").filter((s) => s === "Your cancellation is confirmed").length, 2);

  const b = purchase("base", { sub: "sub_b2", cs: "cs_test_b20000000000" });
  await send("checkout.session.completed", { id: b.cs, mode: "subscription" });
  stripeState.subscriptions.sub_b2.status = "canceled";
  await send("customer.subscription.deleted", { id: "sub_b2" });
  assert.equal(subjects("owner@example.com").filter((s) => s === "Your Northern Peak Systems subscription has ended").length, 1);
});

test("Onboarding reminders go out on day 2 and day 5, once each, and stop when done", async () => {
  const { sub, cs } = purchase("peak");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const done = purchase("base", { sub: "sub_done", cs: "cs_test_done00000000" });
  await send("checkout.session.completed", { id: done.cs, mode: "subscription" });
  const DAY = 86400000;
  const t0 = Date.now();
  for (const r of db.nps_customers) r.created_at = new Date(t0).toISOString();
  customerRow("sub_done").onboarding_status = "complete";
  const rem = () => subjects("owner@example.com").filter((s) => /start your build|Still need your setup details/.test(s));

  await reminders(t0 + 1 * DAY);
  assert.equal(rem().length, 0, "nothing on day 1");
  await reminders(t0 + 2.1 * DAY);
  await reminders(t0 + 2.2 * DAY);
  assert.deepEqual(rem(), ["A few details and we can start your build"]);
  customerRow(sub).reminder_1_sent_at = new Date(t0 + 2.1 * DAY).toISOString();
  await reminders(t0 + 5.2 * DAY);
  await reminders(t0 + 6 * DAY);
  assert.equal(rem().length, 2);
  assert.ok(rem()[1].startsWith("Still need your setup details"));
  assert.ok(emails.filter((e) => /start your build/.test(e.subject))[0].html.includes("/client.html#t="));
  await reminders(t0 + 30 * DAY);
  assert.equal(rem().length, 2, "never more than two");
});

/* ---------------- Client Hub ---------------- */
const hubCall = async (body) => {
  const r = await require(path.join(root, "netlify/functions/client.js")).handler({ httpMethod: "POST", headers: {}, body: JSON.stringify(body) });
  return { status: r.statusCode, body: JSON.parse(r.body) };
};

test("Client Hub load: plan, stage, billing (next payment, card, invoices) and files", async () => {
  const { cs } = purchase("peak");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const t = tokenFromWelcome();
  assert.ok(emails.find((e) => e.subject.startsWith("You're in")).html.includes("/client.html#t="), "emails link to the Client Hub");
  const r = await hubCall({ action: "load", token: t });
  assert.equal(r.status, 200);
  const c = r.body.customer;
  assert.equal(c.project_stage, "setup");
  assert.equal(c.app_url, "https://app.northernpeaksystems.ca/");
  assert.equal(c.billing.card.last4, "4242");
  assert.equal(c.billing.invoices[0].number, "NPS-0001");
  assert.ok(c.billing.next_payment_at);
  assert.deepEqual(c.files, []);
});

test("Uploads: signed URL only in the customer's own folder, validated, listable, deletable", async () => {
  const { sub, cs } = purchase("base");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const t = tokenFromWelcome();
  const up = await hubCall({ action: "upload-url", token: t, filename: "Our Logo.PNG", size: 5000, type: "image/png", kind: "logo" });
  assert.equal(up.status, 200);
  assert.ok(up.body.upload_url.includes(`/client-files/${sub}/logo__`));
  assert.ok(up.body.key.endsWith("__our-logo.png"));
  files.push(`${sub}/${up.body.key}`); // what the browser upload would create
  for (const bad of [{ type: "application/x-msdownload", kind: "logo", size: 10 }, { type: "image/png", kind: "logo", size: 30 * 1024 * 1024 }, { type: "image/png", kind: "secret", size: 10 }]) {
    assert.equal((await hubCall({ action: "upload-url", token: t, filename: "x", ...bad })).status, 400);
  }
  const list = await hubCall({ action: "files", token: t });
  assert.equal(list.body.files.length, 1);
  assert.equal(list.body.files[0].kind, "logo");
  assert.ok(list.body.files[0].url.includes("token=view"));
  assert.equal((await hubCall({ action: "delete-file", token: t, key: "../other_sub/x.png" })).status, 400);
  const del = await hubCall({ action: "delete-file", token: t, key: up.body.key });
  assert.equal(del.body.files.length, 0);
  assert.equal((await hubCall({ action: "upload-url", token: "forged", filename: "x.png", size: 10, type: "image/png", kind: "logo" })).status, 401);
});

test("Submitting setup moves the project to Build and sends the team the files", async () => {
  const { sub, cs } = purchase("peak");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  files.push(`${sub}/photo__1__truck.jpg`);
  const r = await hubCall({ action: "submit", token: tokenFromWelcome(), data: { ...PEAK_ANSWERS, team_size: "2-5", main_goal: "More Google reviews" } });
  assert.equal(r.status, 200);
  assert.equal(customerRow(sub).project_stage, "build");
  assert.equal(r.body.customer.project_stage, "build");
  const team = emails.find((e) => e.subject.startsWith("Setup complete:"));
  assert.ok(team.html.includes("truck.jpg"));
  assert.ok(team.html.includes("More Google reviews"));
  assert.ok(emails.find((e) => e.subject === "We've got your setup information").html.includes("/client.html#t="));
});

test("Expanded setup: optional fields validated only when filled, unknown fields dropped", async () => {
  const { cs } = purchase("base");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  const t = tokenFromWelcome();
  const bad = await hubCall({ action: "submit", token: t, data: { ...BASE_ANSWERS, team_size: "a hundred", brand_style: "Rainbow" } });
  assert.equal(bad.status, 422);
  assert.equal(bad.body.fields.team_size, "invalid_option");
  const ok = await hubCall({ action: "submit", token: t, data: { ...BASE_ANSWERS, hours: "Mon-Fri 8-5", gbp_email: "not-for-base" } });
  assert.equal(ok.status, 200);
});

test("A customer who finished setup before stages existed shows as Build", async () => {
  const { sub, cs } = purchase("base");
  await send("checkout.session.completed", { id: cs, mode: "subscription" });
  Object.assign(customerRow(sub), { onboarding_status: "complete", project_stage: "setup" });
  const r = await hubCall({ action: "load", token: tokenFromWelcome() });
  assert.equal(r.body.customer.project_stage, "build");
});
