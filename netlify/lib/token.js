/**
 * Signed, expiring onboarding links. A token names one Stripe subscription and is
 * HMAC-signed with ONBOARDING_TOKEN_SECRET, so it can't be guessed or edited
 * (unlike a plain ?id= parameter). Links go to the customer's verified email.
 *
 *   ONBOARDING_TOKEN_SECRET  long random string (32+ chars), e.g. `openssl rand -hex 32`
 */
const crypto = require("crypto");

const b64url = (buf) => Buffer.from(buf).toString("base64").replace(/=+$/, "").replace(/\+/g, "-").replace(/\//g, "_");
const fromB64url = (s) => Buffer.from(String(s).replace(/-/g, "+").replace(/_/g, "/"), "base64");

function secret() {
  const s = process.env.ONBOARDING_TOKEN_SECRET || "";
  if (s.length < 32) {
    const e = new Error("onboarding_secret_missing");
    e.code = "onboarding_secret_missing";
    throw e;
  }
  return s;
}

const mac = (body) => crypto.createHmac("sha256", secret()).update(body).digest();

function issue(subscriptionId, days = 30, now = Date.now()) {
  const body = b64url(JSON.stringify({ s: subscriptionId, p: "onb", exp: Math.floor(now / 1000) + days * 86400 }));
  return `${body}.${b64url(mac(body))}`;
}

/** Returns the subscription ID, or null if the token is missing, tampered with or expired. */
function verify(token, now = Date.now()) {
  if (typeof token !== "string" || token.length > 600) return null;
  const [body, sig] = token.split(".");
  if (!body || !sig) return null;
  const expected = mac(body);
  const got = fromB64url(sig);
  if (got.length !== expected.length || !crypto.timingSafeEqual(got, expected)) return null;
  let payload;
  try {
    payload = JSON.parse(fromB64url(body).toString("utf8"));
  } catch {
    return null;
  }
  if (payload.p !== "onb" || typeof payload.s !== "string" || !payload.exp || payload.exp * 1000 < now) return null;
  return payload.s;
}

module.exports = { issue, verify };
