/**
 * Northern Peak Systems — onboarding reminders (Netlify Scheduled Function)
 *
 * Runs once a day (schedule in netlify.toml). Anyone who paid but hasn't finished the setup form
 * gets a friendly reminder with their private link after 2 days, and a second one after 5 days.
 * Each reminder is sent once (timestamp columns claimed atomically); nothing goes out once the
 * form is submitted or the subscription stops being active.
 *
 * Env vars: SUPABASE_URL, SUPABASE_SERVICE_KEY, RESEND_API_KEY, ONBOARDING_TOKEN_SECRET
 */
const db = require("../lib/db");
const customers = require("../lib/customers");
const plans = require("../lib/plans");
const mail = require("../lib/mail");
const { json, log } = require("../lib/util");

const DAY = 86400000;
const FIRST_AFTER = 2 * DAY;
const SECOND_AFTER = 5 * DAY;

async function run(now = Date.now()) {
  const due = await db.select(
    customers.T,
    "onboarding_status=neq.complete&subscription_status=in.(active,trialing)&email=not.is.null&order=created_at.asc&limit=200"
  );
  const sent = [];
  const failures = [];
  for (const row of due) {
    const age = now - new Date(row.created_at).getTime();
    let n = 0;
    if (!row.reminder_1_sent_at && age >= FIRST_AFTER) n = 1;
    else if (row.reminder_1_sent_at && !row.reminder_2_sent_at && age >= SECOND_AFTER && now - new Date(row.reminder_1_sent_at).getTime() >= 2 * DAY) n = 2;
    if (!n) continue;
    const plan = plans.getPlan(row.plan) || { label: row.plan };
    try {
      const r = await customers.sendOnce(row, `reminder_${n}_sent_at`, () =>
        mail.send({ to: row.email, ...mail.reminder({ name: row.name, planLabel: plan.label, link: customers.onboardingLink(row.stripe_subscription_id), n }) }));
      if (r === "done") sent.push(`${row.stripe_subscription_id}:${n}`);
    } catch (e) {
      failures.push(`${row.stripe_subscription_id}: ${e.message}`);
    }
  }
  if (failures.length) {
    log("error", "reminders_failed", { failures });
    await mail.send({ to: mail.TEAM(), ...mail.teamAlert({ where: "onboarding reminders", error: failures.join("; ").slice(0, 900), ref: new Date(now).toISOString() }) }).catch(() => {});
  }
  log("info", "reminders_run", { checked: due.length, sent: sent.length });
  return { checked: due.length, sent, failures: failures.length };
}

exports.handler = async () => {
  try {
    return json(200, await run());
  } catch (e) {
    log("error", "reminders_crashed", { message: e.message });
    return json(500, { error: "reminders_failed" });
  }
};

module.exports.run = run; // for tests
