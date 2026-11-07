/**
 * Stripe webhook bookkeeping (nps_stripe_events): each event ID is processed once.
 * A duplicate delivery of a finished event is acknowledged and skipped; a failed or stalled
 * attempt is picked up again by Stripe's retry. Inside an event, finished steps are recorded
 * so a retry only redoes the steps that failed.
 */
const db = require("./db");

const T = "nps_stripe_events";
const STALE_MS = 5 * 60 * 1000;
const byId = (id) => `id=eq.${db.enc(id)}`;

/** @returns {{skip:boolean, status?:string, attempts?:number, steps?:object}} */
async function claim(evt) {
  const now = new Date().toISOString();
  const inserted = await db.insert(T, { id: evt.id, type: evt.type, livemode: Boolean(evt.livemode), status: "processing", updated_at: now }, { ignoreDuplicates: true });
  if (inserted.length) return { skip: false, attempts: 1, steps: stepper(evt.id, []) };

  const [row] = await db.select(T, `${byId(evt.id)}&limit=1`);
  if (!row) return { skip: false, attempts: 1, steps: stepper(evt.id, []) };
  if (row.status === "done") return { skip: true, status: "done" };
  const stale = Date.now() - new Date(row.updated_at).getTime() > STALE_MS;
  if (row.status === "processing" && !stale) return { skip: true, status: "processing" };

  // failed, or a stalled attempt: take it over, but only if nobody else just did
  const taken = await db.update(T, `${byId(evt.id)}&status=eq.${row.status}&updated_at=eq.${db.enc(row.updated_at)}`, {
    status: "processing",
    attempts: (row.attempts || 1) + 1,
    updated_at: now,
  });
  if (!taken.length) return { skip: true, status: "raced" };
  return { skip: false, attempts: taken[0].attempts, steps: stepper(evt.id, row.steps_done || []) };
}

function stepper(id, done) {
  const finished = new Set(done);
  return {
    /** Run fn once per event; a retry skips steps that already succeeded. */
    async run(name, fn) {
      if (finished.has(name)) return "already_done";
      await fn();
      finished.add(name);
      await db.update(T, byId(id), { steps_done: [...finished], updated_at: new Date().toISOString() });
      return "done";
    },
  };
}

const finish = (id) => db.update(T, byId(id), { status: "done", error: null, processed_at: new Date().toISOString(), updated_at: new Date().toISOString() });

const fail = (id, message) => db.update(T, byId(id), { status: "failed", error: String(message).slice(0, 1000), updated_at: new Date().toISOString() });

/** True the first time only, so a failing event alerts the team once, not on every retry. */
async function firstAlert(id) {
  const r = await db.update(T, `${byId(id)}&alerted=is.false`, { alerted: true });
  return r.length > 0;
}

module.exports = { claim, finish, fail, firstAlert };
