/**
 * Small helpers shared by the checkout / onboarding / webhook functions.
 * (Lives outside netlify/functions so Netlify doesn't deploy it as an endpoint;
 * functions require it and the bundler includes it.)
 */

const SITE_URL = () => (process.env.SITE_URL || process.env.URL || "https://northernpeaksystems.ca").replace(/\/$/, "");

const ALLOWED_ORIGINS = [
  "https://northernpeaksystems.ca",
  "https://www.northernpeaksystems.ca",
  "http://localhost:8790",
  "http://127.0.0.1:8790",
];

function corsHeaders(event) {
  const origin = (event.headers && (event.headers.origin || event.headers.Origin)) || "";
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

function json(statusCode, obj, headers = {}) {
  return {
    statusCode,
    headers: { ...headers, "Content-Type": "application/json", "Cache-Control": "no-store" },
    body: JSON.stringify(obj),
  };
}

function redirect(location, headers = {}) {
  return { statusCode: 303, headers: { ...headers, Location: location, "Cache-Control": "no-store" }, body: "" };
}

function rawBody(event) {
  if (!event.body) return "";
  return event.isBase64Encoded ? Buffer.from(event.body, "base64").toString("utf8") : event.body;
}

function parseJson(event) {
  try {
    return JSON.parse(rawBody(event) || "{}");
  } catch {
    return null;
  }
}

const esc = (s) =>
  String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

/** One-line structured log (shows in Netlify function logs). Never pass card data or secrets. */
function log(level, msg, extra = {}) {
  console[level === "error" ? "error" : "log"](JSON.stringify({ level, msg, ...extra }));
}

module.exports = { SITE_URL, corsHeaders, json, redirect, rawBody, parseJson, esc, EMAIL_RE, log };
