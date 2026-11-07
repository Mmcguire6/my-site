#!/usr/bin/env node
/**
 * One-time Stripe setup for self-serve checkout (safe to re-run: never duplicates).
 *
 *   node scripts/stripe-setup.mjs            # uses STRIPE_SECRET_KEY from env or .env.local
 *   node scripts/stripe-setup.mjs --live     # required before it will touch a LIVE account
 *   node scripts/stripe-setup.mjs --webhook https://northernpeaksystems.ca/api/stripe-webhook
 *
 * Creates (only if missing, found by lookup_key / metadata):
 *   - Product "Base System"      + price $97.00 CAD / month   (lookup_key nps_base_monthly_cad)
 *   - Product "The Peak System"  + price $297.00 CAD / month  (lookup_key nps_peak_monthly_cad)
 *   - Customer Portal configuration: update payment method, billing details, invoice history.
 *     Cancellation in the portal is OFF (cancellations need 30 days' written notice per the terms).
 *   - With --webhook <url>: the webhook endpoint; its signing secret is written to .env.local, not printed.
 * Prints the env vars to put in Netlify.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const envFile = path.join(root, ".env.local");
if (!process.env.STRIPE_SECRET_KEY && fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, "utf8").replace(/^﻿/, "").split(/\r?\n/)) {
    const m = line.match(/^\s*STRIPE_SECRET_KEY\s*=\s*(.+?)\s*$/);
    if (m) process.env.STRIPE_SECRET_KEY = m[1].replace(/^["']|["']$/g, "");
  }
}
const KEY = process.env.STRIPE_SECRET_KEY || "";
const args = process.argv.slice(2);
const LIVE = /^(sk|rk)_live_/.test(KEY);
if (!KEY) {
  console.error("STRIPE_SECRET_KEY is not set (env or .env.local).");
  process.exit(1);
}
if (LIVE && !args.includes("--live")) {
  console.error("This is a LIVE key. Re-run with --live once test mode has been verified.");
  process.exit(1);
}

const encode = (params, prefix = "", out = []) => {
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined) continue;
    const key = prefix ? `${prefix}[${k}]` : k;
    if (Array.isArray(v)) v.forEach((item, i) => (typeof item === "object" ? encode(item, `${key}[${i}]`, out) : out.push(`${encodeURIComponent(`${key}[${i}]`)}=${encodeURIComponent(item)}`)));
    else if (v && typeof v === "object") encode(v, key, out);
    else out.push(`${encodeURIComponent(key)}=${encodeURIComponent(v)}`);
  }
  return out.join("&");
};
async function stripe(method, p, params) {
  const qs = method === "GET" && params ? `?${encode(params)}` : "";
  const res = await fetch(`https://api.stripe.com/v1${p}${qs}`, {
    method,
    headers: { Authorization: `Bearer ${KEY}`, "Stripe-Version": "2024-06-20", "Content-Type": "application/x-www-form-urlencoded" },
    body: method === "GET" ? undefined : encode(params || {}),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(`${method} ${p}: ${data.error && data.error.message}`);
  return data;
}

const PLANS = [
  { key: "base", env: "STRIPE_PRICE_BASE", name: "Base System", amount: 9700, lookup: "nps_base_monthly_cad", desc: "Custom website, hosting, security, unlimited edits, local SEO foundations and direct support." },
  { key: "peak", env: "STRIPE_PRICE_PEAK", name: "The Peak System", amount: 29700, lookup: "nps_peak_monthly_cad", desc: "Everything in the Base System plus missed call text-back, estimate follow-up, lead management and booking, reputation management and customer retention." },
];

const acct = await stripe("GET", "/account");
console.log(`Stripe account: ${acct.settings?.dashboard?.display_name || acct.business_profile?.name || acct.id} (${LIVE ? "LIVE" : "test"} mode)\n`);

const env = {};
for (const plan of PLANS) {
  const found = await stripe("GET", "/prices", { lookup_keys: [plan.lookup], active: "true", limit: 1 });
  let price = found.data[0];
  if (price) {
    const ok = price.unit_amount === plan.amount && price.currency === "cad" && price.recurring?.interval === "month";
    console.log(`${plan.name}: found ${price.id}${ok ? "" : "  !! amount/currency/interval do not match, fix in Stripe"}`);
  } else {
    const product = await stripe("POST", "/products", { name: plan.name, description: plan.desc, metadata: { nps_plan: plan.key } });
    price = await stripe("POST", "/prices", { product: product.id, unit_amount: plan.amount, currency: "cad", recurring: { interval: "month" }, lookup_key: plan.lookup, nickname: `${plan.name} monthly (CAD)`, metadata: { nps_plan: plan.key } });
    console.log(`${plan.name}: created ${price.id}`);
  }
  env[plan.env] = price.id;
}

const portals = await stripe("GET", "/billing_portal/configurations", { limit: 100 });
let portal = portals.data.find((c) => c.metadata?.nps === "self_serve_v1" && c.active);
if (!portal) {
  portal = await stripe("POST", "/billing_portal/configurations", {
    business_profile: { headline: "Northern Peak Systems: manage your billing", terms_of_service_url: "https://northernpeaksystems.ca/terms", privacy_policy_url: "https://northernpeaksystems.ca/privacy" },
    features: {
      payment_method_update: { enabled: true },
      invoice_history: { enabled: true },
      customer_update: { enabled: true, allowed_updates: ["email", "address", "phone", "name"] },
      subscription_cancel: { enabled: false },
    },
    default_return_url: "https://northernpeaksystems.ca/client.html",
    metadata: { nps: "self_serve_v1" },
  });
  console.log(`Customer portal: created ${portal.id}`);
} else console.log(`Customer portal: found ${portal.id}`);
env.STRIPE_PORTAL_CONFIGURATION = portal.id;

const wi = args.indexOf("--webhook");
if (wi >= 0 && args[wi + 1]) {
  const url = args[wi + 1];
  const existing = (await stripe("GET", "/webhook_endpoints", { limit: 100 })).data.find((w) => w.url === url);
  if (existing) console.log(`Webhook: ${url} already exists (${existing.id}); its secret is in the Stripe dashboard.`);
  else {
    const wh = await stripe("POST", "/webhook_endpoints", {
      url,
      api_version: "2024-06-20",
      enabled_events: ["checkout.session.completed", "checkout.session.async_payment_succeeded", "checkout.session.async_payment_failed", "customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted", "invoice.paid", "invoice.payment_failed", "charge.refunded"],
      description: "NPS self-serve checkout",
    });
    console.log(`Webhook: created ${wh.id}`);
    // the signing secret is shown only once: keep it out of the terminal, save it next to the other secrets
    fs.appendFileSync(envFile, `
STRIPE_WEBHOOK_SECRET${LIVE ? "_LIVE" : ""}=${wh.secret}
`);
    console.log(`Webhook signing secret saved to .env.local as STRIPE_WEBHOOK_SECRET${LIVE ? "_LIVE" : ""} (copy it into Netlify).`);
  }
}

console.log("\nSet these in Netlify (Site configuration -> Environment variables):");
for (const [k, v] of Object.entries(env)) console.log(`  ${k}=${v}`);
