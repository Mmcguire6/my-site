/**
 * Northern Peak Systems — Stripe webhook (Netlify Function)
 *
 * Endpoint: POST /api/stripe-webhook  (add it in Stripe → Developers → Webhooks)
 * Events: checkout.session.completed, checkout.session.async_payment_succeeded,
 *         checkout.session.async_payment_failed, customer.subscription.created,
 *         customer.subscription.updated, customer.subscription.deleted, invoice.paid,
 *         invoice.payment_failed, charge.refunded
 *
 * - Rejects anything without a valid Stripe signature.
 * - Each event ID is processed once (nps_stripe_events); finished steps are skipped on retry.
 * - Statuses are re-read from the Stripe API, so out-of-order delivery can't regress them.
 * - Never deletes customer data or switches services off: cancellations and failed payments
 *   are recorded and sent to the team and GHL for a person to act on.
 * - On failure it answers 500 so Stripe retries, and alerts the team once.
 *
 * Env vars: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, SUPABASE_URL, SUPABASE_SERVICE_KEY,
 *           RESEND_API_KEY, ONBOARDING_TOKEN_SECRET, GHL_WEBHOOK_URL (optional), TO_EMAIL (optional)
 */
const stripe = require("../lib/stripe");
const events = require("../lib/events");
const customers = require("../lib/customers");
const mail = require("../lib/mail");
const ghl = require("../lib/ghl");
const db = require("../lib/db");
const { json, rawBody, log } = require("../lib/util");

const HANDLED = new Set([
  "checkout.session.completed",
  "checkout.session.async_payment_succeeded",
  "checkout.session.async_payment_failed",
  "customer.subscription.created",
  "customer.subscription.updated",
  "customer.subscription.deleted",
  "invoice.paid",
  "invoice.payment_failed",
  "charge.refunded",
]);
const PROBLEM_STATUSES = ["past_due", "unpaid", "canceled", "incomplete_expired", "paused"];

const invoiceSub = (inv) =>
  inv.subscription || (inv.parent && inv.parent.subscription_details && inv.parent.subscription_details.subscription) || null;

const teamNotice = (title, row, detail) =>
  mail.send({ to: mail.TEAM(), ...mail.teamLifecycle({ title, customer: row && customers.view(row), detail }) });

async function handle(evt, steps) {
  const o = evt.data.object;
  switch (evt.type) {
    case "checkout.session.completed":
    case "checkout.session.async_payment_succeeded": {
      if (o.mode !== "subscription") return;
      const r = await customers.recordCheckout(o.id);
      if (!r.paid) {
        log("info", "checkout_not_paid_yet", { session: o.id, reason: r.reason || o.payment_status });
        return; // e.g. a bank debit still clearing: async_payment_succeeded will follow
      }
      await customers.afterPurchase(r.row);
      return;
    }

    case "checkout.session.async_payment_failed": {
      if (o.mode !== "subscription" || !o.subscription) return;
      const { row } = await customers.syncSubscription(o.subscription);
      if (!row) return;
      await steps.run("team", () => teamNotice("Initial payment failed", row, "The payment for this checkout did not go through, so no onboarding was started."));
      return;
    }

    case "customer.subscription.created":
    case "customer.subscription.updated": {
      const { row, before } = await customers.syncSubscription(o.id);
      if (!row || evt.type === "customer.subscription.created" || !before) return;
      const prev = before.subscription_status;
      const now = row.subscription_status;
      if (prev && now !== prev && PROBLEM_STATUSES.includes(now) && prev !== "incomplete") {
        await steps.run("ghl", () => ghl.send("subscription_status_changed", customers.ghlView(row), { previous_status: prev }));
        await steps.run("team", () => teamNotice(`Subscription is ${now.replace(/_/g, " ")}`, row, `Status changed from ${prev} to ${now}.`));
      }
      if (row.cancel_at_period_end && !before.cancel_at_period_end) {
        const ends = row.current_period_end ? new Date(row.current_period_end).toDateString() : "the end of the period";
        await steps.run("ghl_cancel", () => ghl.send("subscription_cancel_scheduled", customers.ghlView(row), { ends_at: row.current_period_end }));
        await steps.run("team_cancel", () => teamNotice("Cancellation scheduled", row, `The subscription is set to end on ${ends}. Nothing has been switched off.`));
      }
      return;
    }

    case "customer.subscription.deleted": {
      const { row } = await customers.syncSubscription(o.id);
      if (!row) return;
      await steps.run("ghl", () => ghl.send("subscription_canceled", customers.ghlView(row)));
      await steps.run("team", () => teamNotice("Subscription cancelled", row, "Stripe has ended this subscription. Customer data is kept and the site has not been touched; follow the offboarding process."));
      return;
    }

    case "invoice.paid": {
      const subId = invoiceSub(o);
      if (!subId) return;
      const { row } = await customers.syncSubscription(subId);
      if (!row) return;
      const paidAt = o.status_transitions && o.status_transitions.paid_at;
      await customers.updateRow(subId, { last_payment_at: new Date(paidAt ? paidAt * 1000 : Date.now()).toISOString() });
      if (o.billing_reason === "subscription_cycle") {
        await steps.run("ghl", () => ghl.send("renewal_paid", customers.ghlView(row), { amount: o.amount_paid / 100, currency: String(o.currency || "cad").toUpperCase() }));
      }
      return;
    }

    case "invoice.payment_failed": {
      const subId = invoiceSub(o);
      if (!subId || o.billing_reason === "subscription_create") return; // a first payment fails inside Checkout; nothing was activated
      const { row } = await customers.syncSubscription(subId);
      if (!row) return;
      const next = o.next_payment_attempt ? new Date(o.next_payment_attempt * 1000).toDateString() : "none scheduled";
      await steps.run("ghl", () => ghl.send("payment_failed", customers.ghlView(row), { attempt_count: o.attempt_count || 1, next_payment_attempt: o.next_payment_attempt || null }));
      await steps.run("team", () => teamNotice("Recurring payment failed", row, `Attempt ${o.attempt_count || 1}. Next retry: ${next}.`));
      return;
    }

    case "charge.refunded": {
      if (!o.customer) return;
      const rows = await db.select(customers.T, `stripe_customer_id=eq.${db.enc(o.customer)}&order=created_at.desc&limit=1`);
      const row = rows[0];
      if (!row) return;
      const amount = `${((o.amount_refunded || 0) / 100).toFixed(2)} ${String(o.currency || "cad").toUpperCase()}`;
      await steps.run("ghl", () => ghl.send("refund_issued", customers.ghlView(row), { amount_refunded: (o.amount_refunded || 0) / 100 }));
      await steps.run("team", () => teamNotice("Refund issued", row, `Refunded ${amount}.`));
      return;
    }
  }
}

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") return json(405, { error: "method_not_allowed" });
  const raw = rawBody(event);
  const sig = event.headers["stripe-signature"] || event.headers["Stripe-Signature"];
  let evt;
  try {
    evt = stripe.verifyWebhook(raw, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (e) {
    log("error", "webhook_rejected", { reason: e.message });
    return json(400, { error: "invalid_signature" });
  }
  if (!HANDLED.has(evt.type)) return json(200, { ignored: evt.type });

  let claim;
  try {
    claim = await events.claim(evt);
  } catch (e) {
    log("error", "webhook_claim_failed", { id: evt.id, message: e.message });
    return json(500, { error: "storage_unavailable" }); // Stripe retries
  }
  if (claim.skip) return json(200, { duplicate: true, status: claim.status });

  try {
    await handle(evt, claim.steps);
    await events.finish(evt.id);
    log("info", "webhook_processed", { id: evt.id, type: evt.type, attempt: claim.attempts });
    return json(200, { ok: true });
  } catch (e) {
    log("error", "webhook_failed", { id: evt.id, type: evt.type, attempt: claim.attempts, message: e.message });
    await events.fail(evt.id, e.message).catch(() => {});
    try {
      if (await events.firstAlert(evt.id)) await mail.send({ to: mail.TEAM(), ...mail.teamAlert({ where: evt.type, error: e.message, ref: evt.id }) });
    } catch (alertErr) {
      log("error", "alert_failed", { id: evt.id, message: alertErr.message });
    }
    return json(500, { error: "processing_failed" });
  }
};
