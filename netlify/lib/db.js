/**
 * Supabase (PostgREST) access for the checkout + onboarding records. Server only:
 * uses the service key, and the tables have row-level security on with no public
 * policies, so nothing is readable from the browser. Schema: docs/supabase-checkout.sql
 *
 *   SUPABASE_URL          https://<ref>.supabase.co
 *   SUPABASE_SERVICE_KEY  secret / service_role key
 */

function cfg() {
  // accept the project URL with or without a trailing /rest/v1
  const url = (process.env.SUPABASE_URL || process.env.SUPABASE_API_URL || "").replace(/\/+$/, "").replace(/\/rest\/v1$/, "");
  const key = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_SECRET_KEY || "";
  if (!url || !key) {
    const e = new Error("database_not_configured");
    e.code = "database_not_configured";
    throw e;
  }
  return { url, key };
}

function configured() {
  try {
    cfg();
    return true;
  } catch {
    return false;
  }
}

async function q(method, path, body, prefer) {
  const { url, key } = cfg();
  const headers = { apikey: key, "Content-Type": "application/json", Accept: "application/json" };
  if (/^eyJ/.test(key)) headers.Authorization = `Bearer ${key}`; // legacy JWT-style service_role key
  if (prefer) headers.Prefer = prefer;
  const res = await fetch(`${url}/rest/v1${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const e = new Error(`db_${res.status}: ${(data && (data.message || data.hint)) || text}`.slice(0, 300));
    e.status = res.status;
    e.code = (data && data.code) || "db_error";
    throw e;
  }
  return data;
}

const enc = encodeURIComponent;

module.exports = {
  configured,
  enc,
  select: (table, query) => q("GET", `/${table}?${query}`),
  /** Insert; with ignoreDuplicates a conflicting row is skipped and [] comes back. */
  insert: (table, row, { ignoreDuplicates = false } = {}) =>
    q("POST", `/${table}`, row, [ignoreDuplicates ? "resolution=ignore-duplicates" : null, "return=representation"].filter(Boolean).join(",")),
  /** Insert or update on a unique column; only the columns in `row` are changed on conflict. */
  upsert: (table, row, onConflict) => q("POST", `/${table}?on_conflict=${onConflict}`, row, "resolution=merge-duplicates,return=representation"),
  update: (table, query, patch) => q("PATCH", `/${table}?${query}`, patch, "return=representation"),
};
