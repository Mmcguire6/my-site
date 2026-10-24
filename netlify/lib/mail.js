/**
 * Transactional email through Resend (same account and sending domain as the contact form).
 *
 *   RESEND_API_KEY  required
 *   FROM_EMAIL      optional, default "Northern Peak Systems <noreply@northernpeaksystems.ca>"
 *   TO_EMAIL        optional team inbox for internal notices, default matt@northernpeaksystems.ca
 */
const { esc } = require("./util");

const FROM = () => process.env.FROM_EMAIL || "Northern Peak Systems <noreply@northernpeaksystems.ca>";
const TEAM = () => process.env.TO_EMAIL || "matt@northernpeaksystems.ca";
const PHONE = "(587) 200-5649";

async function send({ to, subject, html, text, replyTo }) {
  if (!process.env.RESEND_API_KEY) {
    const e = new Error("email_not_configured");
    e.code = "email_not_configured";
    throw e;
  }
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: FROM(), to: Array.isArray(to) ? to : [to], reply_to: replyTo || TEAM(), subject, html, text }),
  });
  if (!res.ok) throw new Error(`email_send_failed_${res.status}: ${(await res.text()).slice(0, 200)}`);
  return res.json().catch(() => ({}));
}

/* ---------- layout ---------- */
const wrap = (inner) =>
  `<div style="background:#f7f5f0;padding:28px 12px;font-family:-apple-system,'Segoe UI',Inter,Arial,sans-serif;color:#191713;">` +
  `<div style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #e8e2d4;border-radius:14px;padding:32px 30px;">` +
  `<div style="font-family:Georgia,'Times New Roman',serif;font-size:11px;letter-spacing:0.14em;text-transform:uppercase;color:#aa733b;font-weight:700;margin:0 0 6px">Northern Peak Systems</div>` +
  inner +
  `</div><p style="max-width:560px;margin:14px auto 0;font-size:12px;color:#8a8478;text-align:center;">Northern Peak Systems &middot; Edmonton, Alberta &middot; northernpeaksystems.ca</p></div>`;
const h = (t) => `<h2 style="font-family:Georgia,'Times New Roman',serif;margin:0 0 14px;font-size:22px;font-weight:600;color:#191713">${t}</h2>`;
const p = (t) => `<p style="margin:0 0 14px;font-size:15px;line-height:1.6;color:#3d382f">${t}</p>`;
const button = (href, label) =>
  `<p style="margin:22px 0"><a href="${esc(href)}" style="display:inline-block;background:#d2a24c;color:#181207;text-decoration:none;font-weight:700;font-size:14px;letter-spacing:0.04em;padding:14px 26px;border-radius:9px">${label}</a></p>`;
const rows = (pairs) =>
  `<table style="border-collapse:collapse;font-size:14px;margin:0 0 12px">` +
  pairs
    .filter(([, v]) => v !== undefined && v !== null && v !== "")
    .map(([k, v]) => `<tr><td style="padding:4px 14px 4px 0;color:#8a8478;vertical-align:top;white-space:nowrap">${esc(k)}</td><td style="padding:4px 0;color:#191713">${esc(v)}</td></tr>`)
    .join("") +
  `</table>`;
const firstName = (name) => (String(name || "").trim().split(/\s+/)[0] || "there");

/* ---------- customer emails ---------- */
function welcome({ name, planLabel, priceLabel, link }) {
  const subject = "You're in. Let's set up your system.";
  const html = wrap(
    h("Welcome to Northern Peak Systems") +
      p(`Hi ${esc(firstName(name))},`) +
      p(`Thanks for subscribing to <b>${esc(planLabel)}</b>. Your subscription is confirmed, and we handle the technical setup from here. We just need a few details about your business to get started.`) +
      button(link, "Complete your setup information") +
      p(`<b>What happens next</b><br>1. Tell us about your business (a few minutes).<br>2. We build and configure your system.<br>3. We review everything with you and launch.`) +
      p(`Your plan: ${esc(planLabel)}, ${esc(priceLabel)} per month.`) +
      p(`This link is private to you and stays active for 30 days. If it expires, you can request a new one from the setup page.`) +
      p(`Questions? Reply to this email or call ${PHONE}.`)
  );
  const text = `Welcome to Northern Peak Systems\n\nHi ${firstName(name)},\n\nThanks for subscribing to ${planLabel}. Your subscription is confirmed, and we handle the technical setup from here. We just need a few details about your business.\n\nComplete your setup information: ${link}\n\nWhat happens next:\n1. Tell us about your business (a few minutes).\n2. We build and configure your system.\n3. We review everything with you and launch.\n\nYour plan: ${planLabel}, ${priceLabel} per month.\n\nThis link is private to you and stays active for 30 days.\n\nQuestions? Reply to this email or call ${PHONE}.`;
  return { subject, html, text };
}

function resumeLink({ name, link }) {
  const subject = "Your Northern Peak Systems setup link";
  const html = wrap(
    h("Pick up where you left off") +
      p(`Hi ${esc(firstName(name))},`) +
      p("Here's a fresh link to your setup form. Anything you already filled in has been saved.") +
      button(link, "Continue your setup") +
      p("This link stays active for 30 days. If you didn't ask for it, you can ignore this email.")
  );
  return { subject, html, text: `Hi ${firstName(name)},\n\nHere's a fresh link to your setup form: ${link}\n\nIt stays active for 30 days. If you didn't ask for it, ignore this email.` };
}

/* ---------- internal notices ---------- */
function teamPurchase(c) {
  const subject = `New purchase: ${c.planLabel} - ${c.name || c.email}`;
  const pairs = [["Customer", c.name], ["Email", c.email], ["Business", c.businessName], ["Package", c.planLabel], ["Subscription status", c.status], ["Onboarding", c.onboarding], ["Source", c.source], ["Stripe customer", c.customerId], ["Stripe subscription", c.subscriptionId]];
  return { subject, html: wrap(h("New customer purchase") + rows(pairs)), text: pairs.filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join("\n") };
}

function teamOnboarding(c, answers) {
  const subject = `Onboarding complete: ${answers.business_name || c.email} (${c.planLabel})`;
  const pairs = Object.entries(answers).map(([k, v]) => [k.replace(/_/g, " "), v]);
  return {
    subject,
    html: wrap(h("Setup information received") + rows([["Package", c.planLabel], ["Stripe subscription", c.subscriptionId]]) + rows(pairs)),
    text: `Package: ${c.planLabel}\nSubscription: ${c.subscriptionId}\n\n` + pairs.map(([k, v]) => `${k}: ${v}`).join("\n"),
  };
}

function teamLifecycle({ title, customer, detail }) {
  const pairs = [["Customer", customer && (customer.name || customer.email)], ["Email", customer && customer.email], ["Package", customer && customer.planLabel], ["Detail", detail], ["Stripe subscription", customer && customer.subscriptionId]];
  return { subject: `Billing update: ${title}`, html: wrap(h(esc(title)) + rows(pairs)), text: pairs.filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join("\n") };
}

function teamAlert({ where, error, ref }) {
  return {
    subject: `Action needed: NPS automation failed (${where})`,
    html: wrap(h("An automation step failed") + p("Stripe will retry the event automatically, but please check it.") + rows([["Where", where], ["Reference", ref], ["Error", error]])),
    text: `An automation step failed. Stripe will retry automatically.\nWhere: ${where}\nReference: ${ref}\nError: ${error}`,
  };
}

module.exports = { send, TEAM, welcome, resumeLink, teamPurchase, teamOnboarding, teamLifecycle, teamAlert };
