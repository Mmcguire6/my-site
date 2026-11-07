/**
 * Minimal Stripe REST client (no SDK, same fetch approach as the contact function)
 * plus webhook signature verification.
 *
 *   STRIPE_SECRET_KEY       sk_test_... / sk_live_...  (server only, never in page code)
 *   STRIPE_WEBHOOK_SECRET   whsec_... for the /api/stripe-webhook endpoint
 */
const crypto = require("crypto");

const API = "https://api.stripe.com/v1";
const API_VERSION = "2024-06-20"; // pinned so responses keep the fields this code reads

/** Flatten nested params into Stripe's form encoding: a[b][0][c]=v */
function encode(params, prefix = "", out = []) {
  for (const [k, v] of Object.entries(params || {})) {
    if (v === undefined || v === null) continue;
    const key = prefix ? `${prefix}[${k}]` : k;
    if (Array.isArray(v)) {
      v.forEach((item, i) => {
        if (item !== null && typeof item === "object") encode(item, `${key}[${i}]`, out);
        else out.push(`${encodeURIComponent(`${key}[${i}]`)}=${encodeURIComponent(item)}`);
      });
    } else if (typeof v === "object") {
      encode(v, key, out);
    } else {
      out.push(`${encodeURIComponent(key)}=${encodeURIComponent(v)}`);
    }
  }
  return out.join("&");
}

function configured() {
  return Boolean(process.env.STRIPE_SECRET_KEY);
}

function isLiveKey() {
  return /^(sk|rk)_live_/.test(process.env.STRIPE_SECRET_KEY || "");
}

async function request(method, path, params, { idempotencyKey } = {}) {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    const e = new Error("stripe_not_configured");
    e.code = "stripe_not_configured";
    throw e;
  }
  const qs = method === "GET" && params ? `?${encode(params)}` : "";
  const headers = { Authorization: `Bearer ${key}`, "Stripe-Version": API_VERSION };
  if (method !== "GET") headers["Content-Type"] = "application/x-www-form-urlencoded";
  if (idempotencyKey) headers["Idempotency-Key"] = idempotencyKey;
  const res = await fetch(API + path + qs, { method, headers, body: method === "GET" ? undefined : encode(params) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const e = new Error((data.error && data.error.message) || `stripe_${res.status}`);
    e.status = res.status;
    e.code = (data.error && (data.error.code || data.error.type)) || "stripe_error";
    throw e;
  }
  return data;
}

const get = (path, params) => request("GET", path, params);
const post = (path, params, opts) => request("POST", path, params, opts);

/**
 * Verify a Stripe-Signature header against the raw request body.
 * Returns the parsed event, or throws. Tolerance guards against replayed payloads.
 */
function verifyWebhook(raw, header, secret, toleranceSec = 300, now = Math.floor(Date.now() / 1000)) {
  if (!secret) throw new Error("webhook_secret_missing");
  if (!header) throw new Error("signature_missing");
  let t = null;
  const v1 = [];
  for (const part of String(header).split(",")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    const k = part.slice(0, i).trim();
    const v = part.slice(i + 1).trim();
    if (k === "t") t = Number(v);
    else if (k === "v1") v1.push(v);
  }
  if (!t || !v1.length) throw new Error("signature_malformed");
  if (Math.abs(now - t) > toleranceSec) throw new Error("signature_expired");
  const expected = crypto.createHmac("sha256", secret).update(`${t}.${raw}`, "utf8").digest("hex");
  const exp = Buffer.from(expected, "hex");
  const ok = v1.some((sig) => {
    const got = Buffer.from(sig, "hex");
    return got.length === exp.length && crypto.timingSafeEqual(got, exp);
  });
  if (!ok) throw new Error("signature_invalid");
  return JSON.parse(raw);
}

/** Sign a payload the way Stripe does (used by the local tests only). */
function signForTest(raw, secret, t = Math.floor(Date.now() / 1000)) {
  const sig = crypto.createHmac("sha256", secret).update(`${t}.${raw}`, "utf8").digest("hex");
  return `t=${t},v1=${sig}`;
}

module.exports = { encode, configured, isLiveKey, request, get, post, verifyWebhook, signForTest, API_VERSION };
