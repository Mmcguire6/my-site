# -*- coding: utf-8 -*-
"""Generate SEO-optimized Alberta-city landing pages for northernpeaksystems.ca.

Each page targets the high-intent local keyword pattern "[city] web designer"
with a keyword-targeted title/H1/H2 hierarchy, ~1000 words of body, an FAQ
block (FAQPage schema), and internal links to nearby cities.

Scope: only Alberta cities the studio actually serves. (A previous version
included pages for every Canadian province; that was a doorway-page pattern
and was scoped down on 2026-05-06.)

Run from the my-site directory:  python gen_locations.py
Outputs:
  - locations/<slug>.html   (8 pages, CRLF line endings, as stored in git)
  - locations.html          (index page grouping cities by province, CRLF)
  - sitemap.xml             (every indexable main-site page, LF; see build_sitemap)

The header, mobile menu and footer are NOT authored here: the templates carry
empty placeholder tags that sync_nav.apply_nav() fills from index.html.
"""

from __future__ import annotations
import html as htmllib
import json
import re
import subprocess
import tomllib
from pathlib import Path
from datetime import date
from sync_nav import apply_nav  # header, mobile menu and footer come from index.html

ROOT = Path(__file__).parent
OUT = ROOT / "locations"
OUT.mkdir(exist_ok=True)
ORG_ID = "https://northernpeaksystems.ca/#org"  # defined once, in index.html's JSON-LD


def write_file(path: Path, text: str, eol: str) -> None:
    """Write `text` with one consistent line ending (git stores the HTML pages as CRLF)."""
    text = text.replace("\r\n", "\n")
    if eol != "\n":
        text = text.replace("\n", eol)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

# ---------------------------------------------------------------------------
# CITY DATA
#   province (full name), province abbreviation, list of city tuples
#   Each city tuple: (slug, display_name, intro_paragraph)
#
# Per-city `EXTRAS` dict adds:
#   areas  — comma-separated neighborhoods/regions for the "areas served" line
#   nearby — list of 3 nearby city slugs for internal-linking section
# ---------------------------------------------------------------------------

CITIES: list[tuple[str, str, list[tuple[str, str, str]]]] = [
    ("Alberta", "AB", [
        ("edmonton", "Edmonton",
         "Edmonton is home base &mdash; Northern Peak Systems is run from here. We build websites, and the follow-up system behind them, for Edmonton plumbers, electricians, HVAC companies, roofers, landscapers, and contractors: the owner-operators and small crews who can't afford to let a call go to voicemail. Your website is built free, and the same founder-led team that sets everything up is the one that answers when something needs to change."),
        ("calgary", "Calgary",
         "Calgary homeowners have plenty of contractors to choose from, so the businesses that answer fast and follow up on every quote stand out. We build websites with missed-call text-back and estimate follow-up for Calgary trades, from inner-city renovations to the newer communities on the city's edges. Every demo, build, edit, and launch call happens online or by phone &mdash; no in-person meeting required."),
        ("st-albert", "St. Albert",
         "St. Albert homeowners expect a small, owner-run crew to look as professional online as a big company &mdash; and to reply just as fast. We build the website and the follow-up behind it for St. Albert contractors, plumbers, electricians, and landscapers who are too small for a big-city agency but too busy to answer every call. That's the gap Northern Peak Systems is built for."),
        ("sherwood-park", "Sherwood Park",
         "Sherwood Park is Strathcona County's main community, and the trades working here serve everything from homes in town to county acreages and the industrial corridor. They all need the same thing: a credible website, a system that texts back every missed call, and local SEO &mdash; without an enterprise budget. Your website is built free, with plans from $97/month and no contracts."),
        ("leduc", "Leduc",
         "Leduc businesses serve a busy corridor south of Edmonton: Edmonton International Airport, the Nisku industrial area, and nearby Beaumont. Customers might find you on a phone in a parking lot or at a desk in an office, so we build fast, mobile-first websites with missed-call text-back and estimate follow-up wired in."),
        ("spruce-grove", "Spruce Grove",
         "For trades serving Spruce Grove, Stony Plain, and the acreages of Parkland County, the work is spread out and the phone rings while you're on a job. We build for home service businesses growing in that market &mdash; contractors adding a second crew, landscapers taking on staff &mdash; with a website and follow-up system that grows with you, from $97/month with no contract."),
        ("airdrie", "Airdrie",
         "Airdrie sits just north of Calgary on the QE2. If you're an owner-operator here &mdash; a solo trade or a small crew running the business from your phone &mdash; a custom website with missed-call text-back and estimate follow-up, without an enterprise budget, is exactly the gap Northern Peak Systems fills."),
        ("red-deer", "Red Deer",
         "Red Deer businesses serve a regional customer base stretching from Olds to Lacombe, and that reach deserves a system that works as hard as you do. We build websites with missed-call text-back and estimate follow-up for central Alberta trades, all remotely: the demo happens over the phone, the preview shows up in your browser, and your site goes live without anyone having to drive Highway 2."),
    ]),
]

# Per-city extras: areas served, nearby city slugs.
# `areas` is a one-line phrase that gets dropped into "across {areas}".
# `nearby` is a list of slugs (must exist elsewhere in CITIES).
EXTRAS: dict[str, dict] = {
    # St. Albert and Sherwood Park have their own pages, so Edmonton's line doesn't list them.
    "edmonton":      {"areas": "downtown, Whyte Avenue, the west end, Mill Woods, and the surrounding capital region", "nearby": ["st-albert", "sherwood-park", "leduc"]},
    "calgary":       {"areas": "downtown, the Beltline, Mission, Kensington, and residential communities like Mahogany, Tuscany, and Auburn Bay", "nearby": ["airdrie", "red-deer", "edmonton"]},
    "st-albert":     {"areas": "downtown St. Albert, Erin Ridge, Mission, and the Sturgeon County edge", "nearby": ["edmonton", "sherwood-park", "spruce-grove"]},
    "sherwood-park": {"areas": "Baseline Road, Sherwood Drive, Centre in the Park, and Strathcona County's industrial corridor", "nearby": ["edmonton", "st-albert", "leduc"]},
    "leduc":         {"areas": "downtown Leduc, Nisku, Beaumont, and the airport corridor", "nearby": ["edmonton", "sherwood-park", "spruce-grove"]},
    "spruce-grove":  {"areas": "Spruce Grove proper, Stony Plain, Parkland County, and the western Edmonton region", "nearby": ["edmonton", "st-albert", "leduc"]},
    "airdrie":       {"areas": "downtown, Bayside, the QE2 corridor, and the bedroom communities north of Calgary", "nearby": ["calgary", "red-deer", "edmonton"]},
    "red-deer":      {"areas": "downtown, Riverside, Oriole Park, and the QE2 corridor stretching to Penhold and Innisfail", "nearby": ["calgary", "edmonton", "airdrie"]},
}

# Look up display name for a slug — used for nearby-city links.
SLUG_TO_NAME: dict[str, tuple[str, str]] = {}
for prov, abbr, cities in CITIES:
    for slug, name, _intro in cities:
        SLUG_TO_NAME[slug] = (name, prov)


# ---------------------------------------------------------------------------
# CITY-PAGE TEMPLATE
# ---------------------------------------------------------------------------

CITY_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="../favicon.ico?v=2" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="../favicon-32.png?v=2">
<link rel="apple-touch-icon" href="../apple-touch-icon.png?v=2">

<title>{title}</title>
<meta name="description" content="{meta_desc}">

<meta property="og:type" content="website">
<link rel="canonical" href="https://northernpeaksystems.ca/locations/{slug}">
<meta property="og:url" content="https://northernpeaksystems.ca/locations/{slug}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{meta_desc}">
<meta property="og:site_name" content="Northern Peak Systems">
<meta name="twitter:card" content="summary_large_image">

<script type="application/ld+json">
{ld_json}
</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<style>
{styles}
</style>

<script async src="https://www.googletagmanager.com/gtag/js?id=G-CR8009ZP6T"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-CR8009ZP6T');</script>
<script type="text/javascript">(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","wh3e6pv2u4");</script>
<style id="nav-mega-css">
.nav-dd-menu.mega{{background:#fff;border-color:#e8e2d4;min-width:620px;padding:18px 20px 14px;box-shadow:0 30px 64px -24px rgba(0,0,0,0.5);}}
.mega-head{{font-size:13.5px;font-weight:600;color:#16140f;padding-bottom:12px;border-bottom:1px solid #ece5d6;margin-bottom:8px;}}
.mega-grid{{display:grid;grid-template-columns:1fr 1fr;gap:2px 16px;}}
.nav-dd-menu a.mega-item{{display:flex;gap:12px;align-items:flex-start;padding:10px;border-radius:10px;white-space:normal;transition:background .15s;}}
.nav-dd-menu a.mega-item:hover{{background:#f7f3ea;}}
.mega-item .mi{{width:38px;height:38px;border-radius:10px;background:#f7f3ea;border:1px solid #e8e2d4;display:flex;align-items:center;justify-content:center;color:#a97c33;flex-shrink:0;}}
.mega-item .mi svg{{width:18px;height:18px;stroke-width:1.7;}}
.mega-item b{{display:block;font-size:13.5px;font-weight:700;color:#16140f;line-height:1.3;}}
.mega-item span{{display:block;font-size:12px;color:#8a8478;line-height:1.45;margin-top:2px;}}
.nav-cta .btn-line{{background:transparent;color:#d2a24c;border:1px solid rgba(210,162,76,0.35);}}
.nav-cta .btn-line:hover{{border-color:#d2a24c;color:#e6be6e;transform:translateY(-2px);}}
</style>
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<!-- NAV / MOBILE MENU: placeholders, filled from index.html by sync_nav.apply_nav() -->
<header class="nav"></header>
<div class="mnav" id="mnav" inert></div>

<main id="main">

<!-- HERO -->
<section id="top" class="hhero">
    <div class="hhero-bg"><img src="../img/work-hero-bg.webp" alt="" fetchpriority="high" decoding="async" width="1536" height="1024"></div>
    <div class="hhero-scrim"></div>
    <div class="wrap">
        <span class="eyebrow">{name}, {province} &middot; Now accepting new projects</span>
        <h1>{name} web design that <em>books more jobs.</em></h1>
        <p class="hhero-sub">Websites, missed-call text-back, and estimate follow-up for {name} home service businesses &mdash; plumbers, electricians, HVAC, roofers, landscapers, and contractors. Your website is built free; plans from $97/month &middot; no setup fees &middot; no contracts.</p>
        <p class="hhero-lede">{intro}</p>
        <div class="hhero-actions">
            <a href="../book.html" class="btn btn-gold">Book a Demo <span class="arr">→</span></a>
            <a href="../how.html" class="btn btn-ghost">See how it works</a>
        </div>
    </div>
</section>

<!-- AREAS -->
<section class="section section-dark">
    <div class="wrap">
        <span class="eyebrow">Areas served</span>
        <h2 class="section-h">Serving home service businesses across <em>{name}.</em></h2>
        <p class="section-body">
            Northern Peak Systems works with home service businesses across {areas} &mdash; plumbers, electricians, HVAC companies, roofers, landscapers, and general contractors, from solo operators to growing crews. They need a website that looks as good as their work and a way to stop losing jobs to missed calls and forgotten estimates, without paying what downtown agencies charge.
        </p>
        <p class="section-body">
            The process is the same whether you're based in {name} or in a community an hour's drive away. It starts with a free 15-minute demo, we build a free custom preview of your website and system before you decide, and if you go ahead you're live in 7&ndash;10 days &mdash; hosted, connected, and supported by the same founder-led team that built it. No account managers, no offshore dev team, no hidden hand-offs.
        </p>
    </div>
</section>

<!-- SERVICES -->
<section class="section section-dark-2">
    <div class="wrap">
        <span class="eyebrow">Services in {name}</span>
        <h2 class="section-h">What's included for <em>{name} businesses.</em></h2>
        <p class="section-lede">Websites &amp; SEO is the Base System: $97/month, with your website built free. The Peak System, $297/month flat, adds everything else below. No setup fees, no contracts, no pay-per-edit tickets or surprise hosting bills.</p>
        <ul class="svc-list">
            <li>
                <h3><a href="../features/missed-call-text-back.html">Missed Call Recovery</a></h3>
                <p>When you can't pick up, the caller gets a text back in seconds, so a homeowner in {name} starts a conversation with you instead of calling the next company on the list.</p>
            </li>
            <li>
                <h3><a href="../features/lead-follow-up.html">Estimate Follow-Up</a></h3>
                <p>Quotes that go quiet get friendly, automatic check-ins until the customer replies, so fewer {name} estimates are left sitting in someone's inbox.</p>
            </li>
            <li>
                <h3><a href="../features/website.html">Websites &amp; SEO</a></h3>
                <p>A custom website designed for your business and built free, with hosting, security, unlimited edits, local SEO so {name} customers find you on Google, and direct support from the founder. Included in every plan.</p>
            </li>
            <li>
                <h3><a href="../features/crm-and-booking.html">Lead Management</a></h3>
                <p>Calls, texts, and website inquiries land in one inbox on your phone, with online booking that puts jobs straight on your calendar.</p>
            </li>
            <li>
                <h3><a href="../features/review-automation.html">Reputation Management</a></h3>
                <p>After each job, customers get a simple request to leave a Google review, so your rating keeps up with the work you actually do.</p>
            </li>
            <li>
                <h3><a href="../features/marketing-campaigns.html">Customer Retention</a></h3>
                <p>Reminders and reactivation campaigns bring past customers back for the next service call, tune-up, or seasonal job.</p>
            </li>
        </ul>
    </div>
</section>

<!-- WHY -->
<section class="section section-dark">
    <div class="wrap">
        <span class="eyebrow">Why custom</span>
        <h2 class="section-h">Why {name} businesses choose custom over <em>templates.</em></h2>
        <p class="section-body">
            A template is faster and cheaper up front. It's also why so many small-business websites in {name} look alike: the same stock photos, the same layouts, the same Wix or Squarespace defaults. When a homeowner is comparing three contractors, the one that looks established and makes it easy to call, text, or book has the edge.
        </p>
        <p class="section-body">
            A custom build pays back in three places: customers trust it more, it loads fast and structures content clearly (which is what search engines reward), and you're not locked into a platform's roadmap. It also lets us connect missed-call text-back, estimate follow-up, and booking directly to the site instead of bolting on plugins. And you always keep your domain and the content you provided.
        </p>
    </div>
</section>

<!-- PROCESS -->
<section class="section section-dark-2">
    <div class="wrap">
        <span class="eyebrow">Process</span>
        <h2 class="section-h">The {name} build <em>process.</em></h2>
        <ol class="process-list">
            <li>
                <span class="process-n">01</span>
                <h3>Book a Demo</h3>
                <p>A free 15-minute demo. We learn about your {name} business &mdash; what you do, who you serve, and where jobs are slipping through &mdash; and tell you straight which plan fits. Then we build a free custom preview of your website and system before you decide. No pressure, no obligation.</p>
            </li>
            <li>
                <span class="process-n">02</span>
                <h3>We build everything</h3>
                <p>Your custom website is designed and built at no charge, with the local SEO foundation wired in. Choose The Peak System and missed call recovery, estimate follow-up, lead management, reputation management, and customer retention are connected around it. Live in 7&ndash;10 days.</p>
            </li>
            <li>
                <span class="process-n">03</span>
                <h3>Launch &amp; grow</h3>
                <p>The site goes live on your domain, hosted with SSL and backups, and leads start landing on your phone. We walk you through everything on a short launch call.</p>
            </li>
            <li>
                <span class="process-n">04</span>
                <h3>Improve &amp; support</h3>
                <p>You message us when something needs to change: a new hire, a new service, a new photo, new copy. Unlimited edits are included in the monthly fee. Every month we monitor, analyze, and optimize so the system keeps working as your business grows.</p>
            </li>
        </ol>
    </div>
</section>

<!-- PRICING -->
<section class="section section-dark">
    <div class="wrap">
        <span class="eyebrow">Pricing</span>
        <h2 class="section-h">{name} pricing, <em>simplified.</em></h2>
        <div class="pricing-row">
            <div class="pricing-card">
                <p class="pricing-card-name">Base System</p>
                <p class="pricing-card-price"><strong>$97</strong>/mo</p>
                <p class="pricing-card-sub">website built free</p>
                <p class="pricing-card-body">We design and build your custom website free. The monthly covers hosting, security, unlimited edits, local SEO, and direct founder-led support.</p>
            </div>
            <div class="pricing-card">
                <p class="pricing-card-name">The Peak System</p>
                <p class="pricing-card-price"><strong>$297</strong>/mo</p>
                <p class="pricing-card-sub">flat &middot; everything included</p>
                <p class="pricing-card-body">Everything in the Base System, plus Missed Call Recovery, Estimate Follow-Up, Lead Management &amp; booking, Reputation Management, and Customer Retention.</p>
            </div>
        </div>
        <p class="pricing-terms">No setup fees &middot; No contracts &middot; Live in 7&ndash;10 days</p>
        <p class="pricing-foot"><a href="../pricing.html" class="link-arrow">See full pricing details <span class="arr">→</span></a></p>
    </div>
</section>

<!-- FAQ -->
<section class="section section-dark-2">
    <div class="wrap">
        <span class="eyebrow">FAQ</span>
        <h2 class="section-h">{name} <em>questions.</em></h2>
        <dl class="faq-list">
{faq_items}
        </dl>
    </div>
</section>

<!-- NEARBY -->
<section class="section section-dark">
    <div class="wrap">
        <span class="eyebrow">Also serving</span>
        <h2 class="section-h">Web design near <em>{name}.</em></h2>
        <p class="section-body">
            We work with home service businesses across {province}, and across Canada and the US. If you're outside {name} proper, you get the same website, the same follow-up system, the same flat pricing, and the same remote process.
        </p>
        <ul class="nearby-list">
{nearby_links}
            <li class="nearby-all"><a href="../locations.html">See all locations <span class="arr">→</span></a></li>
        </ul>
    </div>
</section>

<!-- CTA -->
<section class="hcta">
    <div class="wrap">
        <span class="eyebrow">Start a project</span>
        <h2>Your {name} website, <em>built to match your work.</em></h2>
        <p>Book a free 15-minute demo, and we build a free custom preview of your website and system before you decide &mdash; no cost, no obligation.</p>
        <div class="hcta-actions">
            <a href="../book.html" class="btn btn-gold">Book a Demo <span class="arr">→</span></a>
            <a href="../pricing.html" class="btn btn-dark">See pricing</a>
        </div>
    </div>
</section>

</main>

<!-- FOOTER: placeholder, filled from index.html by sync_nav.apply_nav() -->
<footer class="foot"></footer>

<script>
var yr=document.getElementById('yr');if(yr)yr.textContent=new Date().getFullYear();
var burger=document.getElementById('burger'),mnav=document.getElementById('mnav'),mclose=document.getElementById('mclose');
function openM(){{mnav.classList.add('open');mnav.removeAttribute('inert');burger.setAttribute('aria-expanded','true');document.body.style.overflow='hidden';}}
function closeM(){{mnav.classList.remove('open');mnav.setAttribute('inert','');burger.setAttribute('aria-expanded','false');document.body.style.overflow='';}}
burger.addEventListener('click',openM);mclose.addEventListener('click',closeM);
mnav.querySelectorAll('a').forEach(function(a){{a.addEventListener('click',closeM);}});

var io=new IntersectionObserver(function(es){{es.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target);}}}});}},{{threshold:0.12}});
document.querySelectorAll('.reveal').forEach(function(el){{io.observe(el);}});
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# CITY STYLES
# ---------------------------------------------------------------------------

CITY_STYLES = """
@font-face{font-family:'Inter';font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/inter-400-normal.woff2) format('woff2');}
@font-face{font-family:'Inter';font-style:normal;font-weight:500;font-display:swap;src:url(/fonts/inter-500-normal.woff2) format('woff2');}
@font-face{font-family:'Inter';font-style:normal;font-weight:600;font-display:swap;src:url(/fonts/inter-600-normal.woff2) format('woff2');}
@font-face{font-family:'Inter';font-style:normal;font-weight:700;font-display:swap;src:url(/fonts/inter-700-normal.woff2) format('woff2');}
@font-face{font-family:'Inter';font-style:normal;font-weight:800;font-display:swap;src:url(/fonts/inter-800-normal.woff2) format('woff2');}

:root{
  --bg:#0a0a0c; --bg-2:#0f0f12; --bg-3:#131317; --bg-4:#17171c;
  --line:rgba(255,255,255,0.09); --line-2:rgba(255,255,255,0.14);
  --gold:#d2a24c; --gold-2:#e6be6e; --gold-soft:rgba(210,162,76,0.13);
  --white:#f5f2ec; --mist:#a9a49a; --mist-2:#7b766c; --ink:#0a0a0c;
  --cream:#f5f2ec; --ink-1:#16140f; --ink-2:#6f695d;
  --sans:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
  --display:'Plus Jakarta Sans','Inter',system-ui,sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased;overflow-x:hidden;}
body{font-family:var(--sans);color:var(--white);background:var(--bg);line-height:1.6;overflow-x:hidden;overflow-wrap:break-word;}
a{color:inherit;text-decoration:none;}
img{max-width:100%;display:block;}
button{font-family:inherit;cursor:pointer;}
ul,ol{list-style:none;}
.wrap{max-width:1320px;margin:0 auto;padding:0 clamp(20px,4vw,52px);}
.eyebrow{font-size:14px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:var(--gold);display:inline-flex;gap:8px;align-items:center;}
.gold{color:var(--gold);}
section{position:relative;}

.skip-link{position:absolute;top:-40px;left:8px;background:var(--gold);color:#fff;padding:8px 14px;font-size:13px;font-weight:600;border-radius:6px;z-index:200;transition:top .2s ease;}
.skip-link:focus{top:8px;}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:11px;font-size:13px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:12px 58px;border-radius:9px;transition:transform .2s,background .2s,box-shadow .2s,border-color .2s,color .2s;border:1px solid transparent;white-space:nowrap;}
.btn .arr{transition:transform .22s;}
.btn:hover .arr{transform:translateX(4px);}
.btn-gold{background:linear-gradient(180deg,#e0b360,#c2903c);color:#181207;box-shadow:0 16px 40px -16px rgba(210,162,76,0.55);}
.btn-gold:hover{background:linear-gradient(180deg,#eabf6c,#cd9a42);transform:translateY(-2px);}
.btn-ghost{background:#15171a;color:var(--white);border-color:var(--line-2);}
.btn-ghost:hover{border-color:var(--gold);color:var(--gold);transform:translateY(-2px);}
.btn-dark{background:#15140f;color:#fff;}
.btn-dark:hover{background:#000;transform:translateY(-2px);}

/* ===== NAV ===== */
.nav{position:sticky;top:0;z-index:50;background:rgba(10,10,12,0.85);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border-bottom:1px solid var(--line);}
.nav-inner{display:flex;align-items:center;justify-content:space-between;gap:24px;height:74px;}
.brand{flex-shrink:0;}
.brand-logo{height:48px;width:auto;display:block;}
.nav-links{display:flex;align-items:center;gap:30px;}
.nav-links > a{font-size:15.5px;color:#dcd7cc;transition:color .18s;}
.nav-links > a:hover,.nav-links > a.active{color:var(--white);}
.nav-dd{position:relative;}
.nav-dd::after{content:"";position:absolute;top:100%;left:-12px;right:-12px;height:16px;}
.nav-dd-toggle{background:none;border:none;padding:0;font-family:inherit;font-size:15.5px;color:#dcd7cc;display:inline-flex;align-items:center;gap:5px;cursor:pointer;transition:color .18s;}
.nav-dd-toggle svg{width:10px;height:10px;transition:transform .2s;}
.nav-dd:hover .nav-dd-toggle{color:var(--white);}
.nav-dd:hover .nav-dd-toggle svg{transform:rotate(180deg);}
.nav-dd-menu{position:absolute;top:calc(100% + 14px);left:50%;transform:translateX(-50%) translateY(8px);min-width:188px;background:var(--bg-3);border:1px solid var(--line-2);border-radius:12px;padding:8px;display:flex;flex-direction:column;gap:1px;box-shadow:0 26px 54px -22px rgba(0,0,0,0.85);opacity:0;visibility:hidden;transition:opacity .2s,transform .2s;z-index:70;}
.nav-dd:hover .nav-dd-menu{opacity:1;visibility:visible;transform:translateX(-50%) translateY(0);}
.nav-dd-menu a{display:block;padding:9px 14px;font-size:13.5px;color:var(--mist);border-radius:7px;white-space:nowrap;transition:background .15s,color .15s;}
.nav-dd-menu a:hover{background:var(--bg-4);color:var(--white);}
.nav-dd-menu a.active{color:var(--gold);background:var(--gold-soft);}
.nav-dd-menu.cols{display:grid;grid-template-columns:1fr 1fr;min-width:300px;}
.nav-dd-menu .dd-all{grid-column:1 / -1;color:var(--gold);border-top:1px solid var(--line);margin-top:5px;padding-top:11px;}
.nav-cta{display:flex;align-items:center;gap:14px;}
.nav-burger{display:none;width:42px;height:42px;border:1px solid var(--line-2);border-radius:9px;background:transparent;color:var(--white);align-items:center;justify-content:center;}
.nav-burger svg{width:20px;height:20px;}
@media(max-width:980px){.nav-links,.nav-cta .btn{display:none;}.nav-burger{display:inline-flex;}}
.mnav{position:fixed;inset:0;z-index:60;background:var(--bg);transform:translateY(-100%);transition:transform .4s cubic-bezier(.5,0,.1,1);display:flex;flex-direction:column;padding:24px clamp(22px,6vw,40px);overflow-y:auto;}
.mnav.open{transform:translateY(0);}
.mnav-top{display:flex;align-items:center;justify-content:space-between;height:50px;}
.mnav-top .brand-logo{height:38px;}
.mnav-close{width:42px;height:42px;border:1px solid var(--line-2);border-radius:9px;background:transparent;color:var(--white);display:flex;align-items:center;justify-content:center;}
.mnav-links{display:flex;flex-direction:column;gap:6px;margin-top:40px;}
.mnav-links a{font-family:var(--display);font-size:clamp(26px,5.5vw,34px);color:var(--white);padding:8px 0;border-bottom:1px solid var(--line);}
.mnav-links a .gold{font-style:normal;}
.mnav-foot{margin-top:auto;padding-top:24px;display:flex;flex-direction:column;gap:16px;}

/* ===== HERO ===== */
.hhero{position:relative;overflow:hidden;background:#000;border-bottom:1px solid var(--line);}
.hhero-bg{position:absolute;inset:0;z-index:0;}
.hhero-bg img{width:100%;height:100%;object-fit:cover;object-position:center;opacity:0.5;}
.hhero-scrim{position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(8,9,11,0.95) 0%,rgba(8,9,11,0.8) 45%,rgba(8,9,11,0.55) 100%),linear-gradient(to top,var(--bg) 1%,transparent 50%);}
.hhero .wrap{position:relative;z-index:2;padding-top:clamp(64px,9vw,128px);padding-bottom:clamp(56px,8vw,110px);}
.hhero h1{font-family:var(--display);font-weight:700;font-size:clamp(40px,6.0vw,84px);line-height:1.02;letter-spacing:-0.02em;max-width:16ch;margin-top:14px;}
.hhero h1 em{font-style:normal;color:var(--gold);}
.hhero-sub{font-size:clamp(16px,1.4vw,19px);color:var(--white);margin:24px 0 18px;max-width:58ch;font-weight:500;}
.hhero-lede{font-size:clamp(14.5px,1.2vw,16.5px);color:var(--mist);margin:0 0 34px;max-width:64ch;line-height:1.75;}
.hhero-actions{display:flex;flex-wrap:wrap;gap:14px;}

/* ===== SECTIONS ===== */
.section{padding:clamp(64px,8vw,110px) 0;border-bottom:1px solid var(--line);}
.section-dark{background:var(--bg);}
.section-dark-2{background:var(--bg-2);}
.section-h{font-family:var(--display);font-weight:700;font-size:clamp(30px,4vw,52px);line-height:1.05;letter-spacing:-0.02em;margin:14px 0 24px;max-width:24ch;}
.section-h em{font-style:normal;color:var(--gold);}
.section-lede{font-size:clamp(16px,1.3vw,18px);color:var(--mist);max-width:62ch;margin-bottom:48px;line-height:1.65;}
.section-body{font-size:clamp(15px,1.1vw,16.5px);line-height:1.75;color:var(--mist);max-width:70ch;margin-bottom:22px;}

/* SERVICES */
.svc-list{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(22px,2.4vw,34px);}
.svc-list li{background:var(--bg-3);border:1px solid var(--line);border-radius:16px;padding:clamp(24px,2.4vw,32px);transition:border-color .2s,transform .2s;}
.svc-list li:hover{border-color:rgba(210,162,76,0.4);transform:translateY(-4px);}
.svc-list h3{font-family:var(--display);font-size:21px;font-weight:700;color:var(--white);margin-bottom:10px;line-height:1.2;}
.svc-list p{font-size:14.5px;line-height:1.7;color:var(--mist);}
.svc-list h3 a{transition:color .18s;}
.svc-list h3 a:hover{color:var(--gold);}

/* PROCESS */
.process-list{display:grid;grid-template-columns:repeat(2,1fr);gap:clamp(24px,2.6vw,36px);}
.process-list li{border-top:2px solid var(--gold);padding-top:22px;}
.process-n{font-family:var(--display);font-size:14px;letter-spacing:0.16em;color:var(--gold);font-weight:700;display:block;margin-bottom:10px;}
.process-list h3{font-family:var(--display);font-size:24px;font-weight:700;color:var(--white);margin-bottom:10px;line-height:1.2;}
.process-list p{font-size:15px;line-height:1.7;color:var(--mist);}

/* PRICING */
.pricing-row{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:8px;}
.pricing-card{background:var(--bg-3);border:1px solid var(--line);border-radius:18px;padding:clamp(28px,3vw,40px);}
.pricing-card-name{font-size:12px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:var(--mist-2);margin-bottom:16px;}
.pricing-card-price{font-family:var(--display);font-size:clamp(34px,4.4vw,48px);font-weight:700;color:var(--white);line-height:1;}
.pricing-card-price strong{color:var(--gold);font-style:italic;font-weight:700;}
.pricing-card-sub{font-size:12px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--gold-2);margin:14px 0 22px;}
.pricing-card-body{font-size:15px;line-height:1.7;color:var(--mist);}
.pricing-terms{margin-top:26px;font-size:12px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:var(--gold-2);}
.pricing-foot{margin-top:36px;}
.link-arrow{font-size:13px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--gold);border-bottom:1px solid currentColor;padding-bottom:4px;display:inline-flex;align-items:center;gap:8px;transition:color .2s;}
.link-arrow:hover{color:var(--gold-2);}

/* FAQ */
.faq-list{display:flex;flex-direction:column;gap:22px;max-width:78ch;}
.faq-item{border-top:1px solid var(--line);padding-top:22px;}
.faq-item dt{font-family:var(--display);font-size:clamp(20px,1.8vw,26px);font-weight:700;color:var(--white);line-height:1.25;margin-bottom:12px;letter-spacing:-0.012em;}
.faq-item dd{font-size:15.5px;line-height:1.75;color:var(--mist);margin-left:0;}

/* NEARBY */
.nearby-list{display:grid;grid-template-columns:repeat(3,1fr);gap:4px 28px;margin-top:28px;max-width:1000px;}
.nearby-list a{display:flex;align-items:center;justify-content:space-between;padding:14px 0;font-family:var(--display);font-size:19px;color:var(--white);border-bottom:1px solid var(--line);transition:padding .22s ease,color .2s ease;}
.nearby-list a::after{content:"→";color:var(--mist-2);transition:transform .22s ease,color .2s ease;}
.nearby-list a:hover{color:var(--gold);padding-left:4px;}
.nearby-list a:hover::after{transform:translateX(4px);color:var(--gold);}
.nearby-list .nearby-all{grid-column:1 / -1;margin-top:22px;}
.nearby-list .nearby-all a{border-bottom:none;font-family:var(--sans);font-size:13px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--gold);padding-left:0;gap:12px;}
.nearby-list .nearby-all a::after{display:none;}
.nearby-list .nearby-all a:hover{color:var(--gold-2);}

/* CTA */
.hcta{background:var(--bg) url('../img/work-page-bottom-bg.webp') center/cover no-repeat;padding:clamp(64px,8vw,110px) 0;text-align:center;border-bottom:1px solid var(--line);}
.hcta .eyebrow{justify-content:center;}
.hcta h2{font-family:var(--display);font-weight:700;font-size:clamp(32px,5vw,58px);line-height:1.04;letter-spacing:-0.02em;max-width:20ch;margin:14px auto 0;}
.hcta h2 em{font-style:normal;color:var(--gold);}
.hcta p{font-size:clamp(15px,1.3vw,18px);color:var(--mist);margin:18px auto 32px;max-width:54ch;}
.hcta-actions{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;}

/* FOOTER */
.foot{background:#0a0b0c;border-top:1px solid var(--line);padding:clamp(56px,7vw,88px) 0 40px;}
.foot-grid{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:clamp(30px,4vw,56px);}
.foot-brand .brand-logo{height:56px;}
.foot-copy{font-size:13px;color:var(--mist-2);line-height:1.7;margin-top:18px;}
.foot-col h4{font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:var(--mist-2);margin-bottom:18px;font-weight:700;}
.foot-col a{display:block;font-size:14px;color:var(--mist);padding:6px 0;transition:color .18s;}
.foot-col a:hover{color:var(--gold);}
.foot-bottom{display:flex;flex-wrap:wrap;justify-content:space-between;gap:14px;align-items:center;margin-top:clamp(44px,5vw,64px);padding-top:26px;border-top:1px solid var(--line);font-size:12.5px;color:var(--mist-2);}
.foot-social{display:flex;gap:14px;align-items:center;}
.foot-social a{width:36px;height:36px;border:1px solid var(--line-2);border-radius:9px;display:flex;align-items:center;justify-content:center;color:var(--mist);transition:color .18s,border-color .18s;}
.foot-social a:hover{color:var(--gold);border-color:var(--gold);}
.foot-social svg{width:17px;height:17px;}

.reveal{opacity:0;transform:translateY(26px);transition:opacity .7s cubic-bezier(.2,.7,.2,1),transform .7s cubic-bezier(.2,.7,.2,1);}
.reveal.in{opacity:1;transform:none;}

@media(max-width:980px){
  .svc-list{grid-template-columns:1fr 1fr;}
  .pricing-row{grid-template-columns:1fr;}
  .foot-grid{grid-template-columns:1fr 1fr;}
}
@media(max-width:760px){
  .svc-list{grid-template-columns:1fr;}
  .process-list{grid-template-columns:1fr;}
  .nearby-list{grid-template-columns:1fr;}
}
@media(max-width:560px){
  .foot-grid{grid-template-columns:1fr;}
}
@media(prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none;}}
"""


# ---------------------------------------------------------------------------
# SCHEMA
# ---------------------------------------------------------------------------

PLANS = [
    # (name, monthly price, description) - mirrors the Base System / The Peak System cards
    ("Base System", "97",
     "Custom website designed and built free. $97/month covers hosting, security, unlimited edits, "
     "local SEO, and founder-led support. No setup fees, no contracts."),
    ("The Peak System", "297",
     "Everything in the Base System plus Missed Call Recovery, Estimate Follow-Up, Lead Management & booking, "
     "Reputation Management, and Customer Retention. $297/month flat, no setup fees, no contracts."),
]


def city_faqs(slug: str, name: str, province: str) -> list[tuple[str, str]]:
    """(question, answer HTML) pairs. The visible FAQ and the FAQPage schema both come from here."""
    if slug == "edmonton":
        where = ("No. Edmonton is home base, but we work with home service businesses across "
                 f"{province}, and across Canada and the US.")
    else:
        where = ("No. We're based in Edmonton and work with home service businesses across "
                 f"{province}, and across Canada and the US.")
    return [
        (f"Do you only work with businesses in {name}?",
         f"{where} Whether you're in {name} proper or a nearby community, the process is the same: "
         "a free 15-minute demo, a free custom preview of your website and system before you decide, "
         "and a build that's live in 7&ndash;10 days. Nothing about the work depends on being in the same room."),
        (f"How long does a build take in {name}?",
         f"Most {name} businesses are live in 7&ndash;10 days. We learn your business on a free 15-minute demo, "
         "build a free custom preview, and once you decide to go ahead, set up the system and walk you "
         "through everything on a launch call. No in-person meeting required at any step."),
        (f"What kinds of {name} businesses do you build for?",
         f"Home service businesses: {name} plumbers, electricians, HVAC companies, roofers, landscapers, "
         "general contractors, concrete and handyman services, and other trades. If your work starts with "
         "a phone call or a quote, the system is built for you."),
        (f"How much does it cost in {name}?",
         "Two flat plans, no setup fees, no contracts. The Base System is $97/month: we build your custom "
         "website free, and the monthly covers hosting, security, unlimited edits, local SEO, and direct "
         "founder-led support. The Peak System is $297/month flat and adds Missed Call Recovery, Estimate "
         "Follow-Up, Lead Management &amp; booking, Reputation Management, and Customer Retention. You always "
         "keep your domain and any content you provided."),
    ]


def _plain(fragment: str) -> str:
    """HTML fragment -> plain text for JSON-LD."""
    return htmllib.unescape(re.sub(r"<[^>]+>", "", fragment))


def build_ld_json(slug: str, name: str, province: str) -> str:
    url = f"https://northernpeaksystems.ca/locations/{slug}"
    desc = (f"Websites, local SEO, missed-call text-back, estimate follow-up, lead management, reputation "
            f"management, and customer retention for home service businesses in {name}, {province}. "
            f"Website built free; Base System $97/month, The Peak System $297/month flat. "
            f"No setup fees, no contracts.")
    offers = [
        {
            "@type": "Offer",
            "name": plan,
            "price": price,
            "priceCurrency": "CAD",
            "priceSpecification": {
                "@type": "UnitPriceSpecification",
                "price": price,
                "priceCurrency": "CAD",
                "unitText": "MONTH",
            },
            "description": text,
        }
        for plan, price, text in PLANS
    ]
    graph = [
        {
            "@type": "Service",
            "@id": f"{url}#service",
            "url": url,
            "name": f"Web Design & Local SEO for Home Service Businesses in {name}, {province}",
            "serviceType": "Web design, local SEO, and lead follow-up",
            # The organization is defined once (index.html); reference it, don't redefine it here.
            "provider": {"@id": ORG_ID},
            "areaServed": {
                "@type": "City",
                "name": name,
                "containedInPlace": {"@type": "AdministrativeArea", "name": province},
            },
            "description": desc,
            "offers": offers,
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": _plain(a)},
                }
                for q, a in city_faqs(slug, name, province)
            ],
        },
    ]
    payload = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# WRITERS
# ---------------------------------------------------------------------------

def faq_items_html(slug: str, name: str, province: str) -> str:
    out = []
    for q, a in city_faqs(slug, name, province):
        out.append(f'            <div class="faq-item">\n'
                   f'                <dt>{q}</dt>\n'
                   f'                <dd>{a}</dd>\n'
                   f'            </div>')
    return "\n".join(out)


def nearby_links_html(nearby_slugs: list[str]) -> str:
    out = []
    for s in nearby_slugs:
        if s in SLUG_TO_NAME:
            n, _p = SLUG_TO_NAME[s]
            out.append(f'            <li><a href="../locations/{s}.html">{n} web design</a></li>')
    return "\n".join(out)


def write_city_page(slug: str, name: str, province: str, intro: str) -> Path:
    extras = EXTRAS.get(slug, {"areas": "the surrounding region", "nearby": []})
    title = f"{name} Web Design &amp; SEO | Northern Peak Systems"
    meta_desc = (f"Web design and local SEO for {name} home service businesses, plus missed-call "
                 f"text-back and estimate follow-up. Website built free, from $97/month.")

    html = CITY_PAGE.format(
        slug=slug,
        title=title,
        meta_desc=meta_desc,
        name=name,
        province=province,
        intro=intro,
        areas=extras["areas"],
        styles=CITY_STYLES,
        ld_json=build_ld_json(slug, name, province),
        faq_items=faq_items_html(slug, name, province),
        nearby_links=nearby_links_html(extras["nearby"]),
    )
    path = OUT / f"{slug}.html"
    write_file(path, apply_nav(html, depth=1), "\r\n")
    return path


# ---------------------------------------------------------------------------
# LOCATIONS INDEX
# ---------------------------------------------------------------------------

LOCATIONS_INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="favicon.ico?v=2" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png?v=2">
<link rel="apple-touch-icon" href="apple-touch-icon.png?v=2">

<title>Alberta Web Design &amp; Local SEO | Northern Peak Systems</title>
<meta name="description" content="Web design, local SEO, and lead follow-up for home service businesses in Edmonton, Calgary, Red Deer and across Alberta. Website built free, from $97/month.">

<meta property="og:type" content="website">
<link rel="canonical" href="https://northernpeaksystems.ca/locations">
<meta property="og:url" content="https://northernpeaksystems.ca/locations">
<meta property="og:title" content="Alberta Web Design &amp; Local SEO | Northern Peak Systems">
<meta property="og:description" content="Based in Edmonton, we work with trades across Alberta, and across Canada and the US. Website built free, from $97/month, no setup fees, no contracts.">
<meta property="og:site_name" content="Northern Peak Systems">
<meta name="twitter:card" content="summary_large_image">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<style>
{styles_root}

.loc-grid{{ padding: clamp(64px,8vw,110px) 0; background:var(--bg); border-bottom:1px solid var(--line); }}
.prov-block{{ border-top:1px solid var(--line); padding:44px 0 36px; display:grid; grid-template-columns:0.9fr 2.1fr; gap:40px; scroll-margin-top:90px; }}
.prov-block:first-of-type{{ border-top:none; padding-top:0; }}
.prov-h{{ font-family:var(--display); font-weight:700; font-size:clamp(28px,3vw,40px); color:var(--white); letter-spacing:-0.016em; line-height:1.1; }}
.prov-h em{{ font-style:italic; color:var(--gold); }}
.prov-h-sub{{ font-size:11px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; color:var(--mist-2); margin-top:8px; }}
.prov-cities{{ display:grid; grid-template-columns:repeat(2,1fr); gap:4px 28px; }}
.prov-cities a{{ display:flex; align-items:center; justify-content:space-between; padding:14px 0; font-family:var(--display); font-size:19px; color:var(--white); border-bottom:1px solid var(--line); transition:color .2s ease, padding .2s ease; }}
.prov-cities a::after{{ content:"→"; color:var(--mist-2); transition:transform .22s ease, color .2s ease; }}
.prov-cities a:hover{{ color:var(--gold); padding-left:4px; }}
.prov-cities a:hover::after{{ transform:translateX(4px); color:var(--gold); }}
@media(max-width:880px){{ .prov-block{{ grid-template-columns:1fr; gap:18px; }} .prov-cities{{ grid-template-columns:1fr; }} }}
</style>

<script async src="https://www.googletagmanager.com/gtag/js?id=G-CR8009ZP6T"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-CR8009ZP6T');</script>
<script type="text/javascript">(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","wh3e6pv2u4");</script>
<style id="nav-mega-css">
.nav-dd-menu.mega{{background:#fff;border-color:#e8e2d4;min-width:620px;padding:18px 20px 14px;box-shadow:0 30px 64px -24px rgba(0,0,0,0.5);}}
.mega-head{{font-size:13.5px;font-weight:600;color:#16140f;padding-bottom:12px;border-bottom:1px solid #ece5d6;margin-bottom:8px;}}
.mega-grid{{display:grid;grid-template-columns:1fr 1fr;gap:2px 16px;}}
.nav-dd-menu a.mega-item{{display:flex;gap:12px;align-items:flex-start;padding:10px;border-radius:10px;white-space:normal;transition:background .15s;}}
.nav-dd-menu a.mega-item:hover{{background:#f7f3ea;}}
.mega-item .mi{{width:38px;height:38px;border-radius:10px;background:#f7f3ea;border:1px solid #e8e2d4;display:flex;align-items:center;justify-content:center;color:#a97c33;flex-shrink:0;}}
.mega-item .mi svg{{width:18px;height:18px;stroke-width:1.7;}}
.mega-item b{{display:block;font-size:13.5px;font-weight:700;color:#16140f;line-height:1.3;}}
.mega-item span{{display:block;font-size:12px;color:#8a8478;line-height:1.45;margin-top:2px;}}
.nav-cta .btn-line{{background:transparent;color:#d2a24c;border:1px solid rgba(210,162,76,0.35);}}
.nav-cta .btn-line:hover{{border-color:#d2a24c;color:#e6be6e;transform:translateY(-2px);}}
</style>
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<!-- NAV / MOBILE MENU: placeholders, filled from index.html by sync_nav.apply_nav() -->
<header class="nav"></header>
<div class="mnav" id="mnav" inert></div>

<main id="main">

<!-- HERO -->
<section class="hhero">
    <div class="hhero-bg"><img src="img/work-hero-bg.webp" alt="" fetchpriority="high" decoding="async" width="1536" height="1024"></div>
    <div class="hhero-scrim"></div>
    <div class="wrap">
        <span class="eyebrow">Locations</span>
        <h1>Serving home service businesses <em>across Alberta.</em></h1>
        <p class="hhero-sub">Based in Edmonton, we work with trades across Alberta &mdash; and across Canada and the US. Websites, missed-call text-back, and estimate follow-up for plumbers, electricians, HVAC companies, roofers, landscapers, and contractors in Edmonton, Calgary, St. Albert, Sherwood Park, Leduc, Spruce Grove, Airdrie, and Red Deer.</p>
        <p class="hhero-lede">Base System $97/month &middot; The Peak System $297/month flat &middot; No setup fees &middot; No contracts &middot; Live in 7&ndash;10 days.</p>
        <div class="hhero-actions">
            <a href="book.html" class="btn btn-gold">Book a Demo <span class="arr">→</span></a>
            <a href="pricing.html" class="btn btn-ghost">See pricing</a>
        </div>
    </div>
</section>

<section class="loc-grid">
    <div class="wrap">
{prov_blocks}
    </div>
</section>

<section class="section">
    <div class="wrap">
        <span class="eyebrow">Why local</span>
        <h2 class="section-h">A web partner that actually <em>knows Alberta.</em></h2>
        <p class="section-body">
            Alberta trades don't need a big-agency retainer or a slow, template-heavy website. They need a fast site that shows up when people in their own town search, and a system that answers the leads it brings in. That's what we build: hand-coded websites tuned for local search, paired with missed call recovery, estimate follow-up, lead management and booking, reputation management, and customer retention &mdash; all founder-led from right here in Edmonton.
        </p>
        <p class="section-body">
            You get the same connected system whether you're a roofer in Red Deer, an HVAC company in Calgary, or a landscaper in St. Albert &mdash; built to load fast, show up for &ldquo;your service + your city&rdquo; searches, and turn visitors into booked jobs. Flat pricing from $97/month, no setup fees, no contracts, and we build a free custom preview of your website and system before you decide.
        </p>
    </div>
</section>

<!-- CTA -->
<section class="hcta">
    <div class="wrap">
        <span class="eyebrow">Start a project</span>
        <h2>Don't see your city? <em>We work across Canada and the US.</em></h2>
        <p>Based in Edmonton, we work with home service businesses across Alberta, and across Canada and the US. Book a free 15-minute demo, and we build a free custom preview of your website and system before you decide.</p>
        <div class="hcta-actions">
            <a href="book.html" class="btn btn-gold">Book a Demo <span class="arr">→</span></a>
            <a href="pricing.html" class="btn btn-dark">See pricing</a>
        </div>
    </div>
</section>

</main>

<!-- FOOTER: placeholder, filled from index.html by sync_nav.apply_nav() -->
<footer class="foot"></footer>

<script>
var yr=document.getElementById('yr');if(yr)yr.textContent=new Date().getFullYear();
var burger=document.getElementById('burger'),mnav=document.getElementById('mnav'),mclose=document.getElementById('mclose');
function openM(){{mnav.classList.add('open');mnav.removeAttribute('inert');burger.setAttribute('aria-expanded','true');document.body.style.overflow='hidden';}}
function closeM(){{mnav.classList.remove('open');mnav.setAttribute('inert','');burger.setAttribute('aria-expanded','false');document.body.style.overflow='';}}
burger.addEventListener('click',openM);mclose.addEventListener('click',closeM);
mnav.querySelectorAll('a').forEach(function(a){{a.addEventListener('click',closeM);}});

var io=new IntersectionObserver(function(es){{es.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target);}}}});}},{{threshold:0.12}});
document.querySelectorAll('.reveal').forEach(function(el){{io.observe(el);}});
</script>
</body>
</html>
"""


def styles_for_root() -> str:
    return CITY_STYLES.replace("../img/", "img/")


def build_locations_index() -> Path:
    blocks = []
    for prov, abbr, cities in CITIES:
        rows = "\n".join(
            f'                <a href="locations/{slug}.html">{name}</a>'
            for slug, name, _intro in cities
        )
        blocks.append(f"""
        <div class="prov-block" id="{abbr.lower()}">
            <div>
                <h2 class="prov-h">{prov} <em>cities</em></h2>
                <p class="prov-h-sub">{len(cities)} {'city' if len(cities) == 1 else 'cities'}</p>
            </div>
            <div class="prov-cities">
{rows}
            </div>
        </div>""")
    html = LOCATIONS_INDEX.format(
        styles_root=styles_for_root(),
        prov_blocks="\n".join(blocks),
    )
    path = ROOT / "locations.html"
    write_file(path, apply_nav(html, depth=0, page="locations.html"), "\r\n")
    return path


# ---------------------------------------------------------------------------
# SITEMAP
# ---------------------------------------------------------------------------
# Every indexable main-site page, at the URL its own canonical tag uses (clean
# URLs, except blog posts, whose canonicals keep .html). Pages are discovered
# from disk, so a new blog post or page is picked up on the next run. A page is
# left out when it has no canonical (404), is robots-noindex (privacy, terms),
# is permanently redirected in netlify.toml, or is listed in SITEMAP_EXCLUDE.
# /work/* and /campground/* are never scanned (prospect previews, robots-disallowed).

SITE = "https://northernpeaksystems.ca"
ROOT_ORDER = ["index.html", "about.html", "how.html", "pricing.html", "faq.html",
              "locations.html", "contact.html", "book.html"]
FEATURE_ORDER = ["website", "missed-call-text-back", "review-automation", "lead-follow-up",
                 "marketing-campaigns", "crm-and-booking"]
PRIORITY = {
    "/": 1.0, "/about": 0.8, "/how": 0.75, "/pricing": 0.9, "/faq": 0.7,
    "/locations": 0.85, "/contact": 0.8, "/book": 0.8, "/blog/": 0.8,
    "/features/website": 0.75, "/features/missed-call-text-back": 0.75,
    "/features/review-automation": 0.75, "/features/lead-follow-up": 0.7,
    "/features/marketing-campaigns": 0.7, "/features/crm-and-booking": 0.7,
}
# /work is intentionally unlinked; /features/local-seo 301s to /features/website.
SITEMAP_EXCLUDE = {"/work", "/features/local-seo"}


def _git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    except OSError:
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def _lastmod(path: Path, today: str) -> str:
    """Last commit date of the file, or today if it has uncommitted changes (or was never committed)."""
    rel = path.relative_to(ROOT).as_posix()
    if _git("status", "--porcelain", "--", rel):
        return today
    return _git("log", "-1", "--format=%cs", "--", rel) or today


def _redirected_paths() -> set[str]:
    try:
        conf = tomllib.loads((ROOT / "netlify.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return set()
    return {r["from"].removesuffix(".html") for r in conf.get("redirects", [])
            if "from" in r and r.get("status") in (301, 302, 307, 308)}


def _canonical_path(path: Path) -> str | None:
    """Canonical URL path of an indexable page ('/', '/about', '/blog/x.html'), else None."""
    text = path.read_text(encoding="utf-8")
    head = text[:text.find("</head>")]
    robots = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']*)', head, re.I)
    if robots and "noindex" in robots.group(1).lower():
        return None
    canon = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', head, re.I)
    if not canon or not canon.group(1).startswith(SITE):
        return None
    return canon.group(1)[len(SITE):] or "/"


def _sitemap_files() -> list[Path]:
    feats, blog = ROOT / "features", ROOT / "blog"
    files = [ROOT / n for n in ROOT_ORDER]
    files += sorted(p for p in ROOT.glob("*.html") if p.name not in ROOT_ORDER)
    files += [feats / f"{s}.html" for s in FEATURE_ORDER]
    files += sorted(p for p in feats.glob("*.html") if p.stem not in FEATURE_ORDER)
    files += [OUT / f"{slug}.html" for _p, _a, cities in CITIES for slug, _n, _i in cities]
    files += [blog / "index.html"]
    files += sorted(p for p in blog.glob("*.html") if p.name != "index.html")
    seen, out = set(), []
    for p in files:
        if p.exists() and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def build_sitemap() -> Path:
    today = date.today().isoformat()
    skip = SITEMAP_EXCLUDE | _redirected_paths()
    urls = []
    for f in _sitemap_files():
        loc = _canonical_path(f)
        if loc is None or loc in skip:
            continue
        prio = PRIORITY.get(loc, 0.6 if loc.startswith("/locations/") else 0.7)
        urls.append(
            f"  <url>\n    <loc>{SITE}{loc}</loc>\n"
            f"    <lastmod>{_lastmod(f, today)}</lastmod>\n    <priority>{prio}</priority>\n  </url>"
        )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n"
    )
    path = ROOT / "sitemap.xml"
    write_file(path, sitemap, "\n")  # sitemap.xml is stored with LF in git
    return path


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    count = 0
    for prov, abbr, cities in CITIES:
        for slug, name, intro in cities:
            write_city_page(slug, name, prov, intro)
            count += 1
    print(f"wrote {count} city pages -> {OUT}")
    p = build_locations_index()
    print(f"wrote locations index -> {p}")
    p = build_sitemap()
    print(f"wrote sitemap -> {p}")


if __name__ == "__main__":
    main()
