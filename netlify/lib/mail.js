/**
 * Transactional email through Resend (same account and sending domain as the contact form).
 * One branded layout for everything: dark header with the NPS logo, gold rule and buttons,
 * table-based HTML so it holds up in Gmail, Outlook and Apple Mail, plus a plain-text version.
 * Payment receipts are NOT sent from here: Stripe sends those (Settings > Customer emails).
 *
 *   RESEND_API_KEY  required
 *   FROM_EMAIL      optional, default "Northern Peak Systems <noreply@northernpeaksystems.ca>"
 *   TO_EMAIL        optional team inbox for internal notices, default matt@northernpeaksystems.ca
 *   EMAIL_ASSET_URL optional base URL for the logo (defaults to the live site)
 */
const { esc } = require("./util");

const FROM = () => process.env.FROM_EMAIL || "Northern Peak Systems <noreply@northernpeaksystems.ca>";
const TEAM = () => process.env.TO_EMAIL || "matt@northernpeaksystems.ca";
const PHONE = "(587) 200-5649";
const PHONE_HREF = "tel:+15872005649";
const ASSETS = () => (process.env.EMAIL_ASSET_URL || "https://northernpeaksystems.ca").replace(/\/$/, "");

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

/* ================= layout ================= */
const C = { gold: "#d2a24c", goldDeep: "#9a6f2c", ink: "#16140f", body: "#3d382f", muted: "#857e71", cream: "#f4f1ea", panel: "#faf7f0", line: "#e8e2d4", dark: "#0f0f12" };
const FONT = "'Plus Jakarta Sans','Segoe UI',Helvetica,Arial,sans-serif";

function layout({ preheader, eyebrow, title, body, note }) {
  const pad = "&#8203;&nbsp;".repeat(60); // keeps inbox previews to the preheader
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light"><title>${esc(title)}</title></head>
<body style="margin:0;padding:0;background:${C.cream};-webkit-text-size-adjust:100%;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;mso-hide:all;">${esc(preheader)}${pad}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:${C.cream};">
<tr><td align="center" style="padding:28px 12px 32px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;">
<tr><td style="background:${C.dark};border-radius:14px 14px 0 0;padding:24px 34px 22px;border-bottom:3px solid ${C.gold};">
<img src="${ASSETS()}/img/email/nps-logo-white.png" width="190" height="41" alt="Northern Peak Systems" style="display:block;border:0;outline:none;width:190px;height:auto;">
</td></tr>
<tr><td style="background:#ffffff;border:1px solid ${C.line};border-top:0;border-radius:0 0 14px 14px;padding:36px 34px 30px;font-family:${FONT};color:${C.body};">
${eyebrow ? `<p style="margin:0 0 10px;font-family:${FONT};font-size:12px;line-height:1.4;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:${C.goldDeep};">${eyebrow}</p>` : ""}
<h1 style="margin:0 0 18px;font-family:${FONT};font-size:26px;line-height:1.22;font-weight:800;letter-spacing:-0.01em;color:${C.ink};">${title}</h1>
${body}
</td></tr>
<tr><td style="padding:22px 24px 0;font-family:${FONT};font-size:12px;line-height:1.7;color:${C.muted};text-align:center;">
${note ? `${note}<br>` : ""}Northern Peak Systems &middot; Edmonton, Alberta &middot; <a href="https://northernpeaksystems.ca" style="color:${C.muted};text-decoration:underline;">northernpeaksystems.ca</a>
</td></tr>
</table>
</td></tr>
</table>
</body></html>`;
}

const p = (html) => `<p style="margin:0 0 16px;font-family:${FONT};font-size:16px;line-height:1.6;color:${C.body};">${html}</p>`;
const small = (html) => `<p style="margin:18px 0 0;font-family:${FONT};font-size:13.5px;line-height:1.6;color:${C.muted};">${html}</p>`;
const button = (href, label) =>
  `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:26px 0 28px;"><tr><td bgcolor="${C.gold}" style="border-radius:10px;background:${C.gold};">` +
  `<a href="${esc(href)}" style="display:inline-block;padding:15px 30px;font-family:${FONT};font-size:15px;line-height:1.2;font-weight:700;color:#181207;text-decoration:none;border-radius:10px;">${label} &rarr;</a></td></tr></table>`;
const heading = (t) => `<p style="margin:26px 0 12px;font-family:${FONT};font-size:15px;line-height:1.4;font-weight:800;color:${C.ink};">${t}</p>`;
const steps = (items) =>
  `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 6px;">` +
  items
    .map(([t, d], i) =>
      `<tr><td width="40" valign="top" style="padding:0 0 14px;"><div style="width:28px;height:28px;border-radius:14px;background:${C.gold};font-family:${FONT};font-size:13px;line-height:28px;font-weight:800;color:#181207;text-align:center;">${i + 1}</div></td>` +
      `<td valign="top" style="padding:3px 0 14px;font-family:${FONT};font-size:15px;line-height:1.5;color:${C.body};"><b style="color:${C.ink};">${t}</b>${d ? `<br><span style="color:${C.muted};font-size:14px;">${d}</span>` : ""}</td></tr>`)
    .join("") +
  `</table>`;
const box = (rows, title) =>
  `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 6px;background:${C.panel};border:1px solid ${C.line};border-radius:12px;"><tr><td style="padding:16px 20px;">` +
  (title ? `<p style="margin:0 0 10px;font-family:${FONT};font-size:12px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:${C.goldDeep};">${title}</p>` : "") +
  `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">` +
  rows
    .filter(([, v]) => v !== undefined && v !== null && v !== "")
    .map(([k, v]) => `<tr><td valign="top" style="padding:5px 14px 5px 0;font-family:${FONT};font-size:13.5px;color:${C.muted};white-space:nowrap;">${esc(k)}</td><td valign="top" style="padding:5px 0;font-family:${FONT};font-size:14px;color:${C.ink};">${esc(v)}</td></tr>`)
    .join("") +
  `</table></td></tr></table>`;

const firstName = (name) => (String(name || "").trim().split(/\s+/)[0] || "there");
const help = () => small(`Questions? Reply to this email or call <a href="${PHONE_HREF}" style="color:${C.goldDeep};white-space:nowrap;">${PHONE}</a>.`);
const why = (plan) => `You&rsquo;re receiving this because you subscribed to ${esc(plan)}.`;
const fmtDate = (d) => (d ? new Date(d).toLocaleDateString("en-CA", { year: "numeric", month: "long", day: "numeric", timeZone: "America/Edmonton" }) : "");
const text = (...lines) => lines.filter((l) => l !== null && l !== undefined).join("\n");

/* ================= customer emails ================= */
function welcome({ name, planLabel, priceLabel, link }) {
  return {
    subject: "You're in. Let's set up your system.",
    html: layout({
      preheader: `Your subscription to ${planLabel} is confirmed. Here's what happens next.`,
      eyebrow: "Subscription confirmed",
      title: `Welcome to Northern Peak Systems, ${esc(firstName(name))}.`,
      body:
        p(`Thanks for subscribing to <b style="color:${C.ink};">${esc(planLabel)}</b>. You&rsquo;re officially on your way to a more organized, automated business. We handle the technical setup; we just need a few details about your business to get started.`) +
        button(link, "Complete your setup information") +
        heading("What happens next") +
        steps([
          ["Tell us about your business", "A short form about your business, website and current tools. It saves as you go."],
          ["We build and configure your system", "Our team prepares your website and automations."],
          ["Review and launch", "We go over everything with you and get ready to launch."],
        ]) +
        box([["Plan", planLabel], ["Price", `${priceLabel} per month`], ["Receipt", "Sent separately by Stripe, our payment processor"]], "Your subscription") +
        small("Your setup link is private to you and stays active for 30 days. If it expires, you can request a new one from the setup page.") +
        help(),
      note: why(planLabel),
    }),
    text: text(`Welcome to Northern Peak Systems, ${firstName(name)}.`, "", `Thanks for subscribing to ${planLabel}. We handle the technical setup; we just need a few details about your business.`, "", `Complete your setup information: ${link}`, "", "What happens next:", "1. Tell us about your business (a short form that saves as you go).", "2. We build and configure your system.", "3. Review and launch.", "", `Plan: ${planLabel}, ${priceLabel} per month. Your receipt comes separately from Stripe.`, "", "Your setup link is private and stays active for 30 days.", `Questions? Reply to this email or call ${PHONE}.`),
  };
}

function resumeLink({ name, planLabel, link }) {
  return {
    subject: "Your Northern Peak Systems setup link",
    html: layout({
      preheader: "Here's a fresh link to finish your setup. Your answers are saved.",
      eyebrow: "Your setup link",
      title: "Pick up where you left off",
      body: p(`Hi ${esc(firstName(name))}, here&rsquo;s a fresh link to your setup form. Anything you already filled in has been saved.`) + button(link, "Continue your setup") + small("This link stays active for 30 days. If you didn&rsquo;t ask for it, you can ignore this email.") + help(),
      note: planLabel ? why(planLabel) : "",
    }),
    text: text(`Hi ${firstName(name)},`, "", "Here's a fresh link to your setup form (your answers are saved):", link, "", "It stays active for 30 days. If you didn't ask for it, ignore this email."),
  };
}

function setupReceived({ name, planLabel, answers }) {
  const a = answers || {};
  const website = a.has_website === "yes" ? a.website_url : a.desired_domain ? `New site (wants ${a.desired_domain})` : "New site";
  return {
    subject: "We've got your setup information",
    html: layout({
      preheader: `Thanks, ${firstName(name)}. Here's what happens next.`,
      eyebrow: "Setup information received",
      title: "You&rsquo;re all set. We&rsquo;ll take it from here.",
      body:
        p(`Thanks, ${esc(firstName(name))}. We&rsquo;ve received your setup information${a.business_name ? ` for <b style="color:${C.ink};">${esc(a.business_name)}</b>` : ""}, and our team is getting started on your system.`) +
        heading("What happens next") +
        steps([
          ["We build and configure your system", "Your website and automations, set up around how you work."],
          ["We reach out if we need anything", "If we need access to your domain, Google profile or phone provider, we&rsquo;ll arrange it with you securely. We&rsquo;ll never ask for a password by email."],
          ["Review and launch", "We walk you through everything before it goes live. Most businesses are live within 7&ndash;10 days."],
        ]) +
        box([["Business", a.business_name], ["Trade", a.trade], ["Service area", a.service_area], ["Website", website], ["Phone", a.phone]], "What you sent us") +
        small("Need to add or change something? Just reply to this email.") +
        help(),
      note: why(planLabel),
    }),
    text: text(`Thanks, ${firstName(name)}. We've received your setup information${a.business_name ? ` for ${a.business_name}` : ""}.`, "", "What happens next:", "1. We build and configure your system.", "2. We reach out if we need anything (never for passwords by email).", "3. Review and launch. Most businesses are live within 7-10 days.", "", "Need to add or change something? Just reply to this email.", `Questions? Call ${PHONE}.`),
  };
}

function reminder({ name, planLabel, link, n }) {
  const first = n === 1;
  return {
    subject: first ? "A few details and we can start your build" : `Still need your setup details, ${firstName(name)}`,
    html: layout({
      preheader: first ? "Your subscription is active. We just need your setup information to start." : "We can't start building until we have your setup information.",
      eyebrow: "Finish your setup",
      title: first ? "We&rsquo;re ready when you are" : "Your build is waiting on a few details",
      body:
        p(first
          ? `Hi ${esc(firstName(name))}, your subscription to ${esc(planLabel)} is active and our team is ready to start. We just need your setup information. It only takes a few minutes, and it saves as you go.`
          : `Hi ${esc(firstName(name))}, we still haven&rsquo;t received your setup information, so we can&rsquo;t start building your system yet. Anything you&rsquo;ve already filled in is saved.`) +
        button(link, first ? "Finish your setup" : "Finish your setup now") +
        (first ? "" : p("Rather go through it on a quick call? Reply to this email and we&rsquo;ll set one up.")) +
        help(),
      note: why(planLabel),
    }),
    text: text(`Hi ${firstName(name)},`, "", first ? `Your subscription to ${planLabel} is active and we're ready to start. We just need your setup information (a few minutes, saves as you go).` : `We still haven't received your setup information, so we can't start building your system yet.`, "", `Finish your setup: ${link}`, first ? null : "\nRather do it on a call? Reply and we'll set one up.", "", `Questions? Call ${PHONE}.`),
  };
}

function paymentFailed({ name, planLabel, amountLabel, payUrl, nextAttempt }) {
  return {
    subject: "Your Northern Peak Systems payment didn't go through",
    html: layout({
      preheader: "We couldn't process your payment. It takes a minute to fix.",
      eyebrow: "Payment issue",
      title: "Your payment didn&rsquo;t go through",
      body:
        p(`Hi ${esc(firstName(name))}, we tried to charge your card for your subscription to ${esc(planLabel)}${amountLabel ? ` (${esc(amountLabel)})` : ""}, but the payment didn&rsquo;t go through. This usually means a card expired or the bank declined the charge.`) +
        (payUrl ? button(payUrl, "Pay with a different card") : "") +
        p(nextAttempt ? `We&rsquo;ll also try your card again automatically on ${esc(fmtDate(nextAttempt))}. Nothing has been switched off.` : "Nothing has been switched off.") +
        small("The payment page is hosted securely by Stripe, our payment processor. We never see your card details.") +
        help(),
      note: why(planLabel),
    }),
    text: text(`Hi ${firstName(name)},`, "", `We tried to charge your card for your subscription to ${planLabel}${amountLabel ? ` (${amountLabel})` : ""}, but the payment didn't go through.`, payUrl ? `\nPay with a different card: ${payUrl}` : null, nextAttempt ? `\nWe'll also try again automatically on ${fmtDate(nextAttempt)}. Nothing has been switched off.` : "\nNothing has been switched off.", "", `Questions? Reply or call ${PHONE}.`),
  };
}

function cancellation({ name, planLabel, endsAt, ended }) {
  const date = fmtDate(endsAt);
  return {
    subject: ended ? "Your Northern Peak Systems subscription has ended" : "Your cancellation is confirmed",
    html: layout({
      preheader: ended ? `Your subscription to ${planLabel} has ended.` : `Your subscription to ${planLabel} ends on ${date}.`,
      eyebrow: ended ? "Subscription ended" : "Cancellation confirmed",
      title: ended ? "Your subscription has ended" : `Your subscription ends on ${esc(date)}`,
      body:
        p(ended
          ? `Hi ${esc(firstName(name))}, your subscription to ${esc(planLabel)} has ended${date ? ` as of ${esc(date)}` : ""}. You won&rsquo;t be charged again.`
          : `Hi ${esc(firstName(name))}, we&rsquo;ve confirmed your cancellation. Your subscription to ${esc(planLabel)} ends on <b style="color:${C.ink};">${esc(date)}</b>, and you won&rsquo;t be charged after that. Until then, everything keeps working as usual.`) +
        box([["Your domain", "Stays yours, registered in your business's name"], ["Your content", "Logo, photos and copy you gave us are yours to take with you"], ["The website itself", "Comes down when the subscription ends (see our terms)"]], "What you keep") +
        p("Want to keep the site? Ask us about a one-time buyout.") +
        (ended ? "" : p(`Changed your mind? Reply before ${esc(date)} and we&rsquo;ll keep everything running.`)) +
        small(`Thanks for working with us. Our <a href="https://northernpeaksystems.ca/terms" style="color:${C.goldDeep};">terms</a> have the full details.`) +
        help(),
      note: why(planLabel),
    }),
    text: text(`Hi ${firstName(name)},`, "", ended ? `Your subscription to ${planLabel} has ended${date ? ` as of ${date}` : ""}. You won't be charged again.` : `Your cancellation is confirmed. Your subscription to ${planLabel} ends on ${date}; you won't be charged after that.`, "", "What you keep: your domain and the content you gave us. The website itself comes down when the subscription ends (see our terms). Ask us about a one-time buyout if you want to keep it.", ended ? null : `\nChanged your mind? Reply before ${date}.`, "", `Questions? Call ${PHONE}.`),
  };
}

/* ================= team notices ================= */
const stripeLink = (live, subId) => (subId ? `https://dashboard.stripe.com/${live ? "" : "test/"}subscriptions/${subId}` : "");
const teamRows = (c) => [["Customer", c.name], ["Email", c.email], ["Business", c.businessName], ["Package", c.planLabel], ["Subscription", c.status], ["Onboarding", c.onboarding ? c.onboarding.replace(/_/g, " ") : ""], ["Source", c.source]];
const teamText = (rows) => rows.filter(([, v]) => v).map(([k, v]) => `${k}: ${v}`).join("\n");

function teamPurchase(c) {
  const rows = teamRows(c);
  const link = stripeLink(c.live, c.subscriptionId);
  return {
    subject: `New purchase: ${c.planLabel} - ${c.name || c.email}`,
    html: layout({ preheader: `${c.name || c.email} just subscribed to ${c.planLabel}.`, eyebrow: "Team notice", title: "New customer purchase", body: p(`${esc(c.name || c.email)} just subscribed to <b style="color:${C.ink};">${esc(c.planLabel)}</b>. Their welcome email and setup link have been sent.`) + box(rows) + (link ? button(link, "View in Stripe") : "") }),
    text: teamText(rows) + (link ? `\n\nStripe: ${link}` : ""),
  };
}

function teamOnboarding(c, answers) {
  const rows = Object.entries(answers).map(([k, v]) => [k.replace(/_/g, " "), v]);
  const link = stripeLink(c.live, c.subscriptionId);
  return {
    subject: `Onboarding complete: ${answers.business_name || c.email} (${c.planLabel})`,
    html: layout({ preheader: `${answers.business_name || c.email} sent their setup information.`, eyebrow: "Team notice", title: "Setup information received", body: p(`<b style="color:${C.ink};">${esc(answers.business_name || c.email)}</b> (${esc(c.planLabel)}) has sent their setup information. Reply to this email to reach them.`) + box(rows, "Their answers") + (link ? button(link, "View in Stripe") : "") }),
    text: `Package: ${c.planLabel}\n\n` + teamText(rows) + (link ? `\n\nStripe: ${link}` : ""),
  };
}

function teamLifecycle({ title, customer, detail }) {
  const c = customer || {};
  const rows = [["Customer", c.name || c.email], ["Email", c.email], ["Package", c.planLabel], ["Detail", detail]];
  const link = stripeLink(c.live, c.subscriptionId);
  return {
    subject: `Billing update: ${title}`,
    html: layout({ preheader: `${title}: ${c.name || c.email || ""}`, eyebrow: "Billing update", title: esc(title), body: box(rows) + (link ? button(link, "View in Stripe") : "") }),
    text: teamText(rows) + (link ? `\n\nStripe: ${link}` : ""),
  };
}

function teamAlert({ where, error, ref }) {
  return {
    subject: `Action needed: NPS automation failed (${where})`,
    html: layout({ preheader: `An automation step failed at ${where}. Stripe will retry.`, eyebrow: "Action needed", title: "An automation step failed", body: p("Stripe will retry the event automatically, and only the failed step runs again. Please check it if this keeps happening.") + box([["Where", where], ["Reference", ref], ["Error", error]]) }),
    text: `An automation step failed. Stripe will retry automatically.\nWhere: ${where}\nReference: ${ref}\nError: ${error}`,
  };
}

module.exports = { send, TEAM, welcome, resumeLink, setupReceived, reminder, paymentFailed, cancellation, teamPurchase, teamOnboarding, teamLifecycle, teamAlert, fmtDate };
