#!/usr/bin/env node
/**
 * Local preview of the site WITH its Netlify Functions (no Netlify CLI needed).
 *   node scripts/dev-server.mjs            -> http://localhost:8790
 * Loads secrets from .env.local and routes like netlify.toml:
 *   /api/checkout, /start/*  -> checkout     /api/stripe-webhook -> stripe-webhook
 *   /api/client              -> client       /api/onboarding     -> onboarding (alias)
 *   /api/contact             -> contact
 * For webhooks in Stripe test mode, forward with the Stripe CLI:
 *   stripe listen --api-key <sk_test_...> --forward-to localhost:8790/api/stripe-webhook
 * and put the printed whsec_... in .env.local as STRIPE_WEBHOOK_SECRET.
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
const PORT = Number(process.env.PORT || 8790);

const envFile = path.join(root, ".env.local");
if (fs.existsSync(envFile)) {
  for (const line of fs.readFileSync(envFile, "utf8").replace(/^﻿/, "").split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/);
    if (m && process.env[m[1]] === undefined) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
}
// local testing always uses the TEST key (live keys are never loaded here)
if (process.env.STRIPE_TEST_SECRET_KEY) process.env.STRIPE_SECRET_KEY = process.env.STRIPE_TEST_SECRET_KEY;
if (/_live_/.test(process.env.STRIPE_SECRET_KEY || "")) { console.error("Refusing to run with a live Stripe key."); process.exit(1); }
process.env.SITE_URL = `http://localhost:${PORT}`;

const ROUTES = [
  [/^\/api\/checkout\/?$/, "checkout"],
  [/^\/start\/[^/]+\/?$/, "checkout"],
  [/^\/api\/stripe-webhook\/?$/, "stripe-webhook"],
  [/^\/api\/client\/?$/, "client"],
  [/^\/api\/onboarding\/?$/, "onboarding"],
  [/^\/api\/contact\/?$/, "contact"],
];
const BLOCKED = /^\/(netlify|scripts|docs)\//;
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".ico": "image/x-icon", ".woff2": "font/woff2", ".xml": "application/xml", ".txt": "text/plain" };

http
  .createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const route = ROUTES.find(([re]) => re.test(url.pathname));
    if (route) {
      const chunks = [];
      for await (const c of req) chunks.push(c);
      const event = {
        httpMethod: req.method,
        path: url.pathname,
        rawUrl: url.href,
        headers: Object.fromEntries(Object.entries(req.headers).map(([k, v]) => [k.toLowerCase(), Array.isArray(v) ? v.join(",") : v])),
        queryStringParameters: Object.fromEntries(url.searchParams),
        body: Buffer.concat(chunks).toString("utf8"),
        isBase64Encoded: false,
      };
      try {
        const fn = require(path.join(root, "netlify/functions", `${route[1]}.js`));
        const r = await fn.handler(event);
        res.writeHead(r.statusCode || 200, r.headers || {});
        res.end(r.body || "");
      } catch (e) {
        console.error(e);
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "dev_server_error", message: e.message }));
      }
      return;
    }
    if (BLOCKED.test(url.pathname)) {
      res.writeHead(404);
      return res.end("Not found");
    }
    let file = path.join(root, decodeURIComponent(url.pathname));
    if (!file.startsWith(root)) {
      res.writeHead(403);
      return res.end();
    }
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
    else if (!path.extname(file) && fs.existsSync(`${file}.html`)) file = `${file}.html`; // clean URLs, like Netlify
    fs.readFile(file, (err, data) => {
      if (err) {
        res.writeHead(404, { "Content-Type": "text/html" });
        return res.end(fs.existsSync(path.join(root, "404.html")) ? fs.readFileSync(path.join(root, "404.html")) : "Not found");
      }
      res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
      res.end(data);
    });
  })
  .listen(PORT, () => console.log(`NPS dev server: http://localhost:${PORT}  (Stripe key: ${process.env.STRIPE_SECRET_KEY ? (/_live_/.test(process.env.STRIPE_SECRET_KEY) ? "LIVE" : "test") : "not set"})`));
