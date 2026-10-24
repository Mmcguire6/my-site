/**
 * The two subscriptions, as sold on the site. Prices are NEVER taken from the browser:
 * checkout looks up the Stripe price ID from these env vars and checks it against
 * the amount/currency/interval below before creating a session.
 *
 *   STRIPE_PRICE_BASE  price_... for the Base System ($97 CAD / month)
 *   STRIPE_PRICE_PEAK  price_... for The Peak System ($297 CAD / month)
 *
 * scripts/stripe-setup.mjs creates both (looked up by lookup_key, so it never duplicates).
 */

const PLANS = {
  base: {
    key: "base",
    label: "Base System",
    amount: 9700,
    currency: "cad",
    interval: "month",
    priceEnv: "STRIPE_PRICE_BASE",
    lookupKey: "nps_base_monthly_cad",
    tag: "Base System Subscription",
  },
  peak: {
    key: "peak",
    label: "The Peak System",
    amount: 29700,
    currency: "cad",
    interval: "month",
    priceEnv: "STRIPE_PRICE_PEAK",
    lookupKey: "nps_peak_monthly_cad",
    tag: "Peak System Subscription",
  },
};

function getPlan(key) {
  return Object.prototype.hasOwnProperty.call(PLANS, key) ? PLANS[key] : null;
}

function priceIdFor(plan) {
  return process.env[plan.priceEnv] || "";
}

/** Which plan a Stripe price belongs to (by configured price ID, then by lookup_key). */
function planForPrice(price) {
  if (!price) return null;
  const id = typeof price === "string" ? price : price.id;
  for (const p of Object.values(PLANS)) {
    if (priceIdFor(p) && priceIdFor(p) === id) return p;
    if (typeof price === "object" && price.lookup_key === p.lookupKey) return p;
  }
  return null;
}

const money = (cents, currency = "cad") => `$${(cents / 100).toFixed(0)} ${currency.toUpperCase()}`;

module.exports = { PLANS, getPlan, priceIdFor, planForPrice, money };
