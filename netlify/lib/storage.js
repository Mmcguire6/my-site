/**
 * Client files (logos, photos, brand files) in a PRIVATE Supabase Storage bucket.
 * The browser never gets the service key: the server hands out a one-time signed upload URL
 * for a path inside the customer's own folder, and short-lived signed URLs to view files.
 * Bucket: client-files (private, 25 MB per file, images / PDF / design files / zip).
 * Folder per customer: <stripe_subscription_id>/<kind>__<timestamp>__<safe-name>
 */
const BUCKET = "client-files";
const MAX_BYTES = 25 * 1024 * 1024;
const MAX_FILES = 60;
const KINDS = ["logo", "photo", "other"];
const TYPES = /^(image\/[a-z0-9.+-]+|application\/(pdf|postscript|illustrator|zip|x-zip-compressed))$/i;

function cfg() {
  const url = (process.env.SUPABASE_URL || process.env.SUPABASE_API_URL || "").replace(/\/+$/, "").replace(/\/rest\/v1$/, "");
  const key = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_SECRET_KEY || "";
  if (!url || !key) {
    const e = new Error("storage_not_configured");
    e.code = "storage_not_configured";
    throw e;
  }
  return { url: `${url}/storage/v1`, key };
}

async function call(method, path, body) {
  const { url, key } = cfg();
  const headers = { apikey: key };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (/^eyJ/.test(key)) headers.Authorization = `Bearer ${key}`;
  const res = await fetch(url + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) throw new Error(`storage_${res.status}: ${(data && (data.message || data.error)) || text}`.slice(0, 200));
  return data;
}

const safeName = (name) =>
  String(name || "file").toLowerCase().replace(/[^a-z0-9.\-]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "").slice(-80) || "file";

/** Parse "<kind>__<ts>__<name>" back into parts for display. */
function describe(subId, obj) {
  const [kind, ts, ...rest] = obj.name.split("__");
  return {
    key: obj.name,
    kind: KINDS.includes(kind) ? kind : "other",
    name: rest.join("__") || obj.name,
    size: (obj.metadata && obj.metadata.size) || 0,
    type: (obj.metadata && obj.metadata.mimetype) || "",
    uploaded_at: obj.created_at || (ts ? new Date(Number(ts)).toISOString() : null),
    path: `${subId}/${obj.name}`,
  };
}

async function list(subId) {
  const rows = await call("POST", `/object/list/${BUCKET}`, { prefix: `${subId}/`, limit: 200, offset: 0, sortBy: { column: "created_at", order: "desc" } });
  return (rows || []).filter((o) => o.id && o.name !== ".emptyFolderPlaceholder").map((o) => describe(subId, o));
}

/** Signed view URLs (absolute) for a set of paths. */
async function viewUrls(paths, expiresIn = 3600) {
  if (!paths.length) return {};
  const { url } = cfg();
  const rows = await call("POST", `/object/sign/${BUCKET}`, { expiresIn, paths });
  const out = {};
  for (const r of rows || []) if (r.signedURL) out[r.path] = url + r.signedURL;
  return out;
}

/**
 * Validate and return a one-time upload URL inside the customer's folder.
 * @returns {{upload_url:string, key:string}}
 */
async function signUpload(subId, { filename, size, type, kind }, existingCount = 0) {
  if (!KINDS.includes(kind)) throw Object.assign(new Error("bad_kind"), { code: "bad_kind" });
  if (!Number.isFinite(size) || size <= 0 || size > MAX_BYTES) throw Object.assign(new Error("too_large"), { code: "too_large" });
  if (!TYPES.test(String(type || ""))) throw Object.assign(new Error("bad_type"), { code: "bad_type" });
  if (existingCount >= MAX_FILES) throw Object.assign(new Error("too_many"), { code: "too_many" });
  const key = `${kind}__${Date.now()}__${safeName(filename)}`;
  const { url } = cfg();
  const r = await call("POST", `/object/upload/sign/${BUCKET}/${subId}/${encodeURIComponent(key)}`);
  return { upload_url: url + r.url, key };
}

async function remove(subId, key) {
  if (!key || key.includes("/") || key.includes("..")) throw Object.assign(new Error("bad_key"), { code: "bad_key" });
  await call("DELETE", `/object/${BUCKET}`, { prefixes: [`${subId}/${key}`] });
}

module.exports = { BUCKET, MAX_BYTES, MAX_FILES, KINDS, list, viewUrls, signUpload, remove, safeName };
