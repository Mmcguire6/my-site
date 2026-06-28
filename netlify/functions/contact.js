/**
 * Northern Peak Systems — contact form (Netlify Function)
 * Receives the site's contact-form POST and relays it to
 * matt@northernpeaksystems.ca via Resend.
 *
 * Endpoint: /.netlify/functions/contact  (aliased to /api/contact in netlify.toml)
 *
 * Handles CORS preflight (OPTIONS) so it works even when the page is loaded on a
 * non-canonical domain (www / matthewmcguire.ca) and the request is cross-origin.
 *
 * Env vars (Netlify → Site settings → Environment variables):
 *   RESEND_API_KEY  — required (re_...)
 *   TO_EMAIL        — optional, defaults to matt@northernpeaksystems.ca
 *   FROM_EMAIL      — optional, must be on a Resend-verified domain
 */

const ALLOWED_ORIGINS = [
  "https://northernpeaksystems.ca",
  "https://www.northernpeaksystems.ca",
  "https://matthewmcguire.ca",
  "https://www.matthewmcguire.ca",
  "http://localhost:5500",
  "http://127.0.0.1:5500",
];

function corsHeaders(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

const esc = (s) =>
  String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

function resp(statusCode, obj, headers) {
  return {
    statusCode,
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify(obj),
  };
}

exports.handler = async (event) => {
  const origin = event.headers.origin || event.headers.Origin || "";
  const cors = corsHeaders(origin);

  if (event.httpMethod === "OPTIONS") return { statusCode: 204, headers: cors, body: "" };
  if (event.httpMethod !== "POST") return resp(405, { error: "method_not_allowed" }, cors);

  let data;
  try {
    data = JSON.parse(event.body || "{}");
  } catch {
    return resp(400, { error: "invalid_json" }, cors);
  }

  // Honeypot — bots fill this hidden field. Pretend success, send nothing.
  if (data["bot-field"]) return resp(200, { ok: true }, cors);

  const name = String(data.name || "").trim();
  const email = String(data.email || "").trim();
  const firm = String(data.firm || "").trim();
  const message = String(data.message || "").trim();
  const plan = String(data.plan || "").trim();

  if (!name || !email || !message) return resp(400, { error: "missing_fields" }, cors);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return resp(400, { error: "invalid_email" }, cors);

  if (!process.env.RESEND_API_KEY) return resp(500, { error: "missing_api_key" }, cors);

  const TO = process.env.TO_EMAIL || "matt@northernpeaksystems.ca";
  const FROM = process.env.FROM_EMAIL || "Northern Peak Systems <noreply@northernpeaksystems.ca>";

  const subject = `New enquiry — ${name}${firm ? " (" + firm + ")" : ""}`;

  const text = [
    `Name: ${name}`,
    `Email: ${email}`,
    firm ? `Business: ${firm}` : null,
    plan ? `\nSelected plan:\n${plan}` : null,
    ``,
    `Message:`,
    message,
  ]
    .filter((x) => x !== null)
    .join("\n");

  const html =
    `<div style="font-family:Georgia,'Times New Roman',serif;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:#aa733b;font-weight:700;margin:0 0 4px">Northern Peak Systems</div>` +
    `<h2 style="font-family:Georgia,'Times New Roman',serif;margin:0 0 16px;font-size:21px;font-weight:600;color:#191713">New Contact Enquiry</h2>` +
    `<p style="margin:0 0 12px"><b>Name:</b> ${esc(name)}<br>` +
    `<b>Email:</b> <a href="mailto:${esc(email)}">${esc(email)}</a>` +
    (firm ? `<br><b>Business:</b> ${esc(firm)}` : "") +
    `</p>` +
    (plan
      ? `<p style="margin:0 0 12px"><b>Selected plan</b><br>${esc(plan).replace(/\n/g, "<br>")}</p>`
      : "") +
    `<p style="margin:0"><b>Message</b><br>${esc(message).replace(/\n/g, "<br>")}</p>`;

  let r;
  try {
    r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: FROM,
        to: [TO],
        reply_to: email, // hitting reply emails the lead back
        subject,
        text,
        html,
      }),
    });
  } catch (e) {
    return resp(502, { error: "network_error", detail: String(e) }, cors);
  }

  if (!r.ok) {
    const detail = await r.text();
    return resp(502, { error: "send_failed", status: r.status, detail }, cors);
  }

  return resp(200, { ok: true }, cors);
};
