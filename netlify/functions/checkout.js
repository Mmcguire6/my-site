/**
 * Northern Peak Systems — start a Stripe Checkout subscription (Netlify Function)
 *
 * Endpoints (netlify.toml):
 *   GET  /api/checkout?plan=base|peak   "Get Started" buttons: 303 redirect to Stripe Checkout
 *   GET  /start/base  |  /start/peak    package links to send after a demo or call
 *   POST /api/checkout {plan}           JSON {url}, for script callers
 * Optional on GET: utm_* / ref / gclid / fbclid (kept as attribution), email (pre-fills Checkout).
 *
 * The browser only names a plan. The price comes from server env vars and is checked against
 * the expected amount, currency and interval before a session is created.
 *
 * Env vars: STRIPE_SECRET_KEY, STRIPE_PRICE_BASE, STRIPE_PRICE_PEAK, SITE_URL (optional)
 */
const stripe = require("../lib/stripe");
const plans = require("../lib/plans");
const { SITE_URL, corsHeaders, json, redirect, parseJson, EMAIL_RE, log } = require("../lib/util");

const ATTR_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "ref", "gclid", "fbclid"];
const checkedPrices = new Set(); // per warm instance

async function checkedPriceId(plan) {
  const id = plans.priceIdFor(plan);
  if (!id) {
    const e = new Error(`${plan.priceEnv} is not set`);
    e.code = "price_not_configured";
    throw e;
  }
  if (!checkedPrices.has(id)) {
    const p = await stripe.get(`/prices/${encodeURIComponent(id)}`);
    const ok = p.active && p.type === "recurring" && p.unit_amount === plan.amount && p.currency === plan.currency && p.recurring && p.recurring.interval === plan.interval;
    if (!ok) {
      const e = new Error(`${plan.priceEnv} does not match ${plans.money(plan.amount)} per ${plan.interval}`);
      e.code = "price_mismatch";
      throw e;
    }
    checkedPrices.add(id);
  }
  return id;
}

function planFrom(event, input) {
  const fromInput = String(input.plan || "").toLowerCase();
  if (fromInput) return plans.getPlan(fromInput);
  const m = String(event.path || "").match(/\/start\/(base|peak)\/?$/i);
  return m ? plans.getPlan(m[1].toLowerCase()) : null;
}

exports.handler = async (event) => {
  const cors = corsHeaders(event);
  if (event.httpMethod === "OPTIONS") return { statusCode: 204, headers: cors, body: "" };
  if (event.httpMethod !== "GET" && event.httpMethod !== "POST") return json(405, { error: "method_not_allowed" }, cors);

  const wantsJson = event.httpMethod === "POST";
  const input = wantsJson ? parseJson(event) || {} : event.queryStringParameters || {};
  const fail = (code, status) =>
    wantsJson ? json(status, { error: code }, cors) : redirect(`${SITE_URL()}/pricing.html?checkout=${code === "invalid_plan" ? "invalid" : "unavailable"}#plans`);

  const plan = planFrom(event, input);
  if (!plan) return fail("invalid_plan", 400);

  try {
    const price = await checkedPriceId(plan);
    const metadata = { plan: plan.key, source: "website" };
    for (const k of ATTR_KEYS) if (input[k]) metadata[`attr_${k}`] = String(input[k]).slice(0, 200);

    const params = {
      mode: "subscription",
      line_items: [{ price, quantity: 1 }],
      // cards only (Apple Pay / Google Pay ride on "card"; "link" is Stripe's saved-card wallet). No buy-now-pay-later.
      payment_method_types: ["card", "link"],
      success_url: `${SITE_URL()}/welcome.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${SITE_URL()}/pricing.html?checkout=cancelled#plans`,
      metadata,
      subscription_data: { metadata, description: `${plan.label}, Northern Peak Systems` },
      billing_address_collection: "auto",
      custom_text: {
        submit: {
          message: "Your first month is charged today and renews monthly. Cancel any time with 30 days' written notice. After you subscribe, we handle the setup. Terms: northernpeaksystems.ca/terms",
        },
      },
    };
    const email = String(input.email || "").trim();
    if (email && EMAIL_RE.test(email) && email.length <= 254) params.customer_email = email;

    const session = await stripe.post("/checkout/sessions", params);
    log("info", "checkout_session_created", { plan: plan.key, session: session.id, live: stripe.isLiveKey() });
    return wantsJson ? json(200, { url: session.url }, cors) : redirect(session.url);
  } catch (e) {
    log("error", "checkout_failed", { plan: plan.key, code: e.code, message: e.message });
    return fail(e.code || "checkout_failed", 503);
  }
};
