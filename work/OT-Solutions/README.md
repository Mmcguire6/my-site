# OT Solutions — site handover

Production website for **otsolutions.ca**. Multi-page static site, deploys to Netlify.

---

## 1. Page structure

| URL | File | Purpose |
|---|---|---|
| `/` | `index.html` | Home — hero, logos, global reach strip, services accordion (UKG #1), why us, featured testimonial, CTA |
| `/services` | `services.html` | All four services as full detail rows |
| `/kronos-expertise` | `kronos-expertise.html` | Dedicated UKG Consulting page (URL preserved from legacy site for SEO) |
| `/about-us` | `about-us.html` | Why Us + Track Record + Global Reach (full section) |
| `/references` | `references.html` | All testimonials + Trusted-by logos |
| `/contact` | `contact.html` | Contact form + meta block |
| `/privacy.html` | `privacy.html` | Privacy policy (PIPEDA + Alberta PIPA template) |
| `/404` | `404.html` | Custom not-found page |

All five legacy WebsiteBuilder URLs (`/about-us`, `/services`, `/contact`, `/references`, `/kronos-expertise`) are kept as real pages. **No 301 redirects are required** at launch — the URLs Google has already indexed continue to resolve to real content.

---

## 2. Files in this folder

**Production deliverables (deployed to Netlify):**

| File | Purpose |
|---|---|
| `index.html`, `services.html`, `kronos-expertise.html`, `about-us.html`, `references.html`, `contact.html` | The six site pages |
| `privacy.html`, `404.html` | Privacy policy + custom 404 |
| `styles.css` | All visual styling — used by every page |
| `script.js` | Nav scroll behavior, scroll-reveal, services accordion, contact-form submission |
| `assets/` | Optimized photography and logo files |
| `uploads/` | Hero source images (1280 / 1920 / 3840 in WEBP + JPG for `srcset`) |
| `_redirects` | Placeholder — no redirects currently needed |
| `netlify.toml` | Netlify build / cache / security-header configuration |
| `robots.txt`, `sitemap.xml` | Search-engine directives |

**Dev / source (NOT deployed, safe to ignore):**

- `dev.html` — React + Babel dev preview (used during design iteration)
- `app.jsx`, `tweaks-panel.jsx`, `sections/*.jsx` — JSX source for the dev preview

---

## 3. Before going live — two things to confirm

### 3.1 Two-contact routing (already wired)
The site routes phone calls / emails by role rather than to a single number:

- **Top of funnel** (top bar, hero CTA, all section CTAs, footer phone, JSON-LD) → **Ariel Dinel — Account Executive — (780) 243-5796 — AO.OTSolutions@shaw.ca**. Cold inquiries from the website land with the person whose job is to handle them.
- **Contact page only** → both contacts shown side-by-side with role labels:
  - **Ariel Dinel** — Account Executive — (780) 243-5796 — AO.OTSolutions@shaw.ca *(new inquiries)*
  - **Tom Olthoff** — Director — (780) 974-0124 — OTSolutions@shaw.ca *(engineering & existing clients)*

If Tom or Ariel ever want this routing changed, search across `*.html` for the relevant phone/email and swap.

### 3.2 GA4 measurement ID
- Every page has the GA4 snippet wired in but with placeholder ID `G-XXXXXXXXXX`.
- After the client (or you on their behalf) creates a GA4 property at <https://analytics.google.com/>, get the measurement ID (format `G-XXXXXXXXXX`).
- Search-and-replace `G-XXXXXXXXXX` across **all `.html` files** with the real ID. Each page has two occurrences (the `src=` and the `gtag('config', ...)` call).
- Microsoft Clarity is already wired in (project ID `wh3e6pv2u4`).

### 3.3 Trusted-by logo expansion
- The "Trusted by" grid currently shows 5 client cards on the home page (and the references page).
- Tom is sending a longer list. To add more entries: in `index.html` and `references.html`, find the `.logos-list` block and append additional `<div class="logo-card">…</div>` entries. The grid auto-scales (5 cols on desktop, 2 on mobile).

---

## 4. Deploy to Netlify (under the client's account)

### Option A — Drag-and-drop deploy (recommended for first launch)

1. Have the client create a free account at <https://app.netlify.com/signup> using their business email.
2. Have them invite you as a collaborator: **Team settings → Members → Invite**.
3. Log in to their Netlify team. **Sites → Add new site → Deploy manually**.
4. Drag this entire `OT-Solutions` folder into the upload area.
5. Netlify provisions a temporary URL like `random-name-12345.netlify.app`. Verify all pages load correctly.
6. Rename the site: **Site configuration → General → Change site name** → e.g. `otsolutions`.

### Option B — Git-connected deploy (for future edits via push)

1. Create a private GitHub repo under the client's account.
2. Push these files to the repo.
3. In Netlify: **Add new site → Import from Git → GitHub** → select the repo.
4. Build settings: leave **Build command** blank, set **Publish directory** to `.` (or whatever root contains `index.html`).
5. Deploy.

---

## 5. Custom domain & DNS

Once the site is verified working on the `*.netlify.app` URL:

1. In Netlify: **Site configuration → Domain management → Add custom domain** → enter `otsolutions.ca`.
2. Netlify gives nameservers (typically four `dns1.p0X.nsone.net`-style addresses).
3. The client logs in to their domain registrar (where otsolutions.ca is registered).
4. Update the nameservers to the four Netlify ones. **DNS propagation can take up to 48 hours** but is usually live within an hour.
5. Netlify auto-provisions SSL via Let's Encrypt — confirm green padlock once DNS is live.
6. Set primary domain in Domain management (recommend non-www: `otsolutions.ca`).

---

## 6. Form submissions

The contact form on `/contact` uses **Netlify Forms** (free tier: 100 submissions/month).

- Submissions appear in: **Site → Forms → contact**.
- To get email notifications: **Site → Forms → Settings & usage → Form notifications → Add notification → Email**.
- The honeypot field (`bot-field`) catches simple spam bots automatically.

---

## 7. Editing content (no build step required)

The site is plain HTML/CSS/JS — no framework, no build pipeline.

- **Text changes** → edit the relevant `.html` file directly.
- **Style changes** → edit `styles.css` (one stylesheet for all pages).
- **Behavior changes** → edit `script.js` (one script for all pages).
- **Header / footer changes** → these are duplicated across every `.html` file. To change the nav menu or footer, you have to update every page (six instances each). This is the trade-off of a build-step-free site.
- **New service item** → in `index.html` and `services.html`, copy an existing service row block and modify.
- **New testimonial** → in `index.html` and `references.html`, copy an existing `<figure class="t-card">` block.
- **New region in global reach** → in `index.html` (`.global-strip-list`) and `about-us.html` (`.global-grid`), append a new `<li>` with the same structure.

After editing: re-deploy by dragging the folder back into Netlify (Option A) or by pushing to Git (Option B). Updates go live within ~30 seconds.

---

## 8. Privacy policy notice

`privacy.html` is a **PIPEDA / Alberta PIPA template**, not a legally vetted document. It accurately describes what this website actually does (collects contact-form data, runs Google Analytics + Microsoft Clarity, transmits over HTTPS). For most B2B consulting use cases it's sufficient as-is, but if the client wants legal sign-off they should run it past a lawyer before launch.

---

## 9. Post-launch verification checklist

- [ ] All 6 main pages load at the right URLs (`/`, `/services`, `/kronos-expertise`, `/about-us`, `/references`, `/contact`)
- [ ] Green SSL padlock on every page
- [ ] Nav links work between pages, current page is marked
- [ ] All footer links work
- [ ] Mobile viewport tested (iPhone + Android sizing) on every page
- [ ] Hero image loads the right `srcset` size on each viewport
- [ ] Services accordion expands/collapses correctly on home + services pages
- [ ] Contact form submits successfully → check Netlify Forms inbox
- [ ] Form email notification fires to client's email
- [ ] Microsoft Clarity recording is active
- [ ] GA4 real-time report shows hits (after replacing `G-XXXXXXXXXX`)
- [ ] Sitemap reachable at `/sitemap.xml`
- [ ] `robots.txt` reachable at `/robots.txt`
- [ ] 404 page renders for an invalid URL like `/asdf`
- [ ] Privacy policy link in footer works
- [ ] Sitemap submitted in Google Search Console

---

## 10. Contact

For questions or changes after handover, contact the developer at the email on the original engagement.
