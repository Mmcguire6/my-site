# -*- coding: utf-8 -*-
"""Generate the blog: Markdown posts -> fast static HTML in the site's editorial
style, with BlogPosting + FAQPage schema and sitemap integration.

Write a post as blog_posts/<slug>.md with frontmatter, then run:
    python gen_blog.py
Outputs:
    blog/index.html        (blog listing)
    blog/<slug>.html        (one per post)
    sitemap.xml             (blog URLs injected)

Self-contained Markdown subset (headings, paragraphs, bold/italic, links,
inline code, ordered/unordered lists, blockquotes) — no external deps.
"""
from __future__ import annotations
import re, json, html
from pathlib import Path
from datetime import date

from gen_locations import CITY_STYLES, desktop_dropdown, mobile_loc_provinces_html

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "blog_posts"
OUT = ROOT / "blog"
OUT.mkdir(exist_ok=True)
SITE = "https://northernpeaksystems.ca"
AUTHOR = "Matthew McGuire"

# ---------------------------------------------------------------------------
# Markdown (small, sufficient subset)
# ---------------------------------------------------------------------------

def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text

def md_to_html(md: str) -> str:
    """Convert a Markdown body (no frontmatter) to HTML. Stops nothing —
    the FAQ section is left in and handled by the caller after extraction."""
    out, i = [], 0
    lines = md.split("\n")
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1; continue
        if line.startswith("### "):
            out.append(f"<h3>{_inline(line[4:].strip())}</h3>"); i += 1
        elif line.startswith("## "):
            out.append(f"<h2>{_inline(line[3:].strip())}</h2>"); i += 1
        elif re.match(r'^\s*[-*] ', line):
            items = []
            while i < len(lines) and re.match(r'^\s*[-*] ', lines[i]):
                items.append(f"<li>{_inline(re.sub(r'^\s*[-*] ', '', lines[i]).strip())}</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
        elif re.match(r'^\s*\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\s*\d+\. ', lines[i]):
                items.append(f"<li>{_inline(re.sub(r'^\s*\d+\. ', '', lines[i]).strip())}</li>"); i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
        elif line.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append(lines[i][2:].strip()); i += 1
            out.append(f"<blockquote><p>{_inline(' '.join(buf))}</p></blockquote>")
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#|>|\s*[-*] |\s*\d+\. )', lines[i]):
                buf.append(lines[i].strip()); i += 1
            out.append(f"<p>{_inline(' '.join(buf))}</p>")
    return "\n".join(out)

# ---------------------------------------------------------------------------
# Post parsing
# ---------------------------------------------------------------------------

def parse_post(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
    if not m:
        raise ValueError(f"{path.name}: missing frontmatter")
    meta = {}
    for ln in m.group(1).split("\n"):
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    body = m.group(2).strip()

    # Split off the FAQ section (## Frequently asked questions) for FAQPage schema
    faqs = []
    fm = re.search(r'\n##\s+Frequently asked questions\s*\n(.*)$', body, re.S | re.I)
    if fm:
        body_main = body[:fm.start()].strip()
        faq_md = fm.group(1)
        for qm in re.finditer(r'###\s+(.+?)\n(.*?)(?=\n###\s+|\Z)', faq_md, re.S):
            faqs.append((qm.group(1).strip(), qm.group(2).strip()))
    else:
        body_main = body

    meta["faqs"] = faqs
    meta["body_html"] = md_to_html(body_main)
    meta.setdefault("read_time", "6")
    return meta

# ---------------------------------------------------------------------------
# Shared chrome (nav + footer), ../ paths, "Blog" active
# ---------------------------------------------------------------------------

def nav_html() -> str:
    return f"""<header class="nav" id="site-nav">
    <div class="wrap nav-inner">
        <a href="../index.html" class="nav-mark" aria-label="Northern Peak Systems, home">
            <img src="../img/mm-nav-logo.webp" alt="Northern Peak Systems" class="nav-mark-img" width="988" height="180">
        </a>
        <nav class="nav-links" aria-label="Primary">
            <a href="../index.html">Home</a>
            <a href="../work.html">Work</a>
            <a href="../pricing.html">Pricing</a>
            <div class="nav-dd nav-dd--studio" aria-current="page">
                <button type="button" class="nav-dd-trigger" aria-haspopup="true" aria-expanded="false">Studio</button>
                <ul class="nav-dd-panel nav-dd-panel--rich" style="left:0;right:auto;">
                    <li><a href="../about.html"><span class="dd-t">About</span><span class="dd-d">The studio &amp; the founder</span></a></li>
                    <li><a href="../how.html"><span class="dd-t">How we work</span><span class="dd-d">Preview-first, no surprises</span></a></li>
                    <li><a href="../faq.html"><span class="dd-t">FAQ</span><span class="dd-d">Pricing, plans &amp; details</span></a></li>
                    <li><a href="../blog/" aria-current="page"><span class="dd-t">Blog</span><span class="dd-d">Guides &amp; insights</span></a></li>
                </ul>
            </div>
{desktop_dropdown()}
            <a href="../contact.html">Contact</a>
        </nav>
        <a href="../contact.html" class="nav-cta">Start a project →</a>
        <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="nav-mobile">
            <span class="nav-toggle-bars" aria-hidden="true"></span>
        </button>
    </div>
</header>

<aside class="nav-mobile" id="nav-mobile" aria-label="Mobile menu">
    <ul class="nav-mobile-links">
        <li><a href="../index.html">Home</a></li>
        <li><a href="../work.html">Work</a></li>
        <li><a href="../pricing.html">Pricing</a></li>
        <li class="nm-group"><details>
            <summary>Studio</summary>
            <ul class="nm-sub">
                <li><a href="../about.html">About</a></li>
                <li><a href="../how.html">How we work</a></li>
                <li><a href="../faq.html">FAQ</a></li>
                <li><a href="../blog/" aria-current="page">Blog</a></li>
            </ul>
        </details></li>
        <li><button type="button" class="nm-loc-trigger" aria-haspopup="true" aria-controls="nav-mobile-locations" aria-expanded="false">Locations <span class="nm-loc-chev" aria-hidden="true">→</span></button></li>
        <li><a href="../contact.html">Contact</a></li>
    </ul>
    <a href="../contact.html" class="nav-mobile-cta">Start a project →</a>
</aside>

<aside class="nav-mobile-locations" id="nav-mobile-locations" aria-label="Locations menu" aria-hidden="true" inert>
    <button type="button" class="nm-loc-back" aria-label="Back to main menu">
        <span class="nm-loc-back-arrow" aria-hidden="true">←</span>
        <span class="nm-loc-back-label">Back</span>
    </button>
    <div class="nm-loc-content">
        <p class="eyebrow">Locations</p>
        <h2 class="nm-loc-h">Web designer <em>across Alberta.</em></h2>
{mobile_loc_provinces_html("../locations/")}
        <a href="../locations.html" class="nm-loc-all-link">See all locations <span class="arrow">→</span></a>
    </div>
</aside>"""

FOOTER = """<footer class="footer">
    <div class="wrap">
        <div class="footer-grid">
            <div>
                <p class="footer-brand">Northern Peak Systems</p>
                <p class="footer-blurb">Small businesses deserve websites that feel like the work behind them. That's what the studio is for.</p>
                <p class="footer-credit"><span class="footer-credit-dot" aria-hidden="true"></span>Canadian owned &middot; Based in Edmonton, Alberta</p>
            </div>
            <div class="footer-col">
                <h2 class="footer-h5">Site</h2>
                <ul>
                    <li><a href="../about.html">About</a></li>
                    <li><a href="../work.html">Selected work</a></li>
                    <li><a href="index.html">Blog</a></li>
                    <li><a href="../pricing.html">Pricing</a></li>
                    <li><a href="../faq.html">FAQ</a></li>
                    <li><a href="../locations.html">All locations</a></li>
                    <li><a href="../contact.html">Contact</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h2 class="footer-h5">Reach</h2>
                <ul><li><a href="mailto:matt@northernpeaksystems.ca">matt@northernpeaksystems.ca</a></li></ul>
            </div>
            <div class="footer-col">
                <h2 class="footer-h5">Based</h2>
                <ul><li>Edmonton, Alberta</li><li>Working with businesses across Canada and the US</li></ul>
            </div>
        </div>
        <div class="footer-bottom">
            <span>© <span id="footer-year">2026</span> Northern Peak Systems. All rights reserved.</span>
            <span class="footer-bottom-links"><a href="../privacy.html">Privacy</a><span class="dot">·</span><a href="../terms.html">Terms</a></span>
            <span>Designed &amp; built by hand</span>
        </div>
    </div>
</footer>"""

NAV_SCRIPT = """<script>
    var nav=document.getElementById('site-nav');
    if(nav){var os=function(){nav.classList.toggle('scrolled',window.scrollY>12)};window.addEventListener('scroll',os,{passive:true});os();}
    var y=document.getElementById('footer-year'); if(y)y.textContent=new Date().getFullYear();
    var nt=document.querySelector('.nav-toggle'),nm=document.querySelector('.nav-mobile'),nl=document.querySelector('.nav-mobile-locations');
    function setLoc(o){document.body.classList.toggle('nav-loc-open',o);if(nl){nl.setAttribute('aria-hidden',o?'false':'true');nl.toggleAttribute('inert',!o);}var t=document.querySelector('.nm-loc-trigger');if(t)t.setAttribute('aria-expanded',o?'true':'false');}
    function setNav(o){document.body.classList.toggle('nav-open',o);if(!o)setLoc(false);if(nt){nt.setAttribute('aria-expanded',o?'true':'false');nt.setAttribute('aria-label',o?'Close menu':'Open menu');}}
    if(nt)nt.addEventListener('click',function(){setNav(!document.body.classList.contains('nav-open'));});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'){if(document.body.classList.contains('nav-loc-open'))setLoc(false);else if(document.body.classList.contains('nav-open'))setNav(false);}});
    if(nm)nm.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){setNav(false);});});
    document.querySelectorAll('.nm-loc-trigger').forEach(function(b){b.addEventListener('click',function(){setLoc(true);});});
    document.querySelectorAll('.nm-loc-back').forEach(function(b){b.addEventListener('click',function(){setLoc(false);});});
    if(nl)nl.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){setLoc(false);setNav(false);});});
</script>"""

# Blog-specific CSS appended to the shared site styles
BLOG_CSS = CITY_STYLES + """
/* BLOG */
.post-hero { padding: clamp(56px,7vw,104px) 0 clamp(28px,3vw,44px); background: var(--paper); border-bottom: 1px solid var(--rule); }
.post-hero .wrap { max-width: 820px; }
.post-cat { font-family: var(--mono); font-size: 11px; letter-spacing: .18em; text-transform: uppercase; color: var(--rust-deep); }
.post-h1 { font-family: var(--serif); font-weight: 800; font-size: clamp(32px,4.6vw,58px); line-height: 1.06; letter-spacing: -.022em; color: var(--ink); margin: 16px 0 18px; text-wrap: balance; }
.post-meta { font-family: var(--mono); font-size: 11.5px; letter-spacing: .04em; color: var(--ink-3); display: flex; gap: 14px; flex-wrap: wrap; }
.post-body { padding: clamp(40px,5vw,72px) 0 clamp(48px,6vw,88px); }
.post-body .wrap { max-width: 720px; }
.post-body p, .post-body li { font-size: clamp(16.5px,1.2vw,18.5px); line-height: 1.75; color: var(--ink-2); text-wrap: pretty; }
.post-body p { margin: 0 0 22px; }
.post-body > p:first-of-type { font-size: clamp(18px,1.4vw,21px); color: var(--ink); line-height: 1.65; }
.post-body h2 { font-family: var(--serif); font-weight: 700; font-size: clamp(24px,2.6vw,34px); line-height: 1.2; letter-spacing: -.018em; color: var(--ink); margin: 48px 0 16px; text-wrap: balance; }
.post-body h3 { font-family: var(--serif); font-weight: 600; font-size: clamp(19px,1.7vw,23px); color: var(--ink); margin: 32px 0 10px; }
.post-body ul, .post-body ol { margin: 0 0 22px; padding-left: 24px; }
.post-body li { margin-bottom: 9px; }
.post-body ul li { list-style: none; position: relative; }
.post-body ul li::before { content: ""; position: absolute; left: -18px; top: 12px; width: 6px; height: 6px; background: var(--rust); border-radius: 999px; }
.post-body ol { list-style: decimal; }
.post-body a { color: var(--rust-deep); border-bottom: 1px solid color-mix(in oklch, var(--rust) 40%, transparent); }
.post-body a:hover { background: color-mix(in oklch, var(--rust) 8%, transparent); }
.post-body strong { color: var(--ink); font-weight: 700; }
.post-body code { font-family: var(--mono); font-size: .88em; background: var(--paper-soft); padding: 1px 6px; border-radius: 4px; }
.post-body blockquote { margin: 28px 0; padding: 4px 0 4px 24px; border-left: 3px solid var(--rust); }
.post-body blockquote p { font-family: var(--serif); font-style: italic; font-size: clamp(19px,1.7vw,23px); color: var(--ink); }
.post-faq { background: var(--paper-soft); padding: clamp(48px,6vw,88px) 0; border-top: 1px solid var(--rule); }
.post-faq .wrap { max-width: 760px; }
.post-faq .eyebrow { margin-bottom: 16px; }
.post-faq h2 { font-family: var(--serif); font-weight: 700; font-size: clamp(26px,3vw,40px); color: var(--ink); margin-bottom: 32px; letter-spacing: -.018em; }
.faq-q { border-top: 1px solid var(--rule); padding-top: 22px; margin-top: 22px; }
.faq-q:first-of-type { border-top: none; padding-top: 0; margin-top: 0; }
.faq-q dt { font-family: var(--serif); font-weight: 600; font-size: clamp(18px,1.7vw,23px); color: var(--ink); margin-bottom: 10px; }
.faq-q dd { margin: 0; font-size: 16px; line-height: 1.7; color: var(--ink-2); }
.faq-q dd a { color: var(--rust-deep); border-bottom: 1px solid color-mix(in oklch, var(--rust) 40%, transparent); }
/* index */
.blog-hero { padding: clamp(72px,9vw,130px) 0 clamp(32px,4vw,56px); }
.blog-hero h1 { font-family: var(--serif); font-style: italic; font-weight: 700; font-size: clamp(40px,5.4vw,76px); letter-spacing: -.022em; color: var(--ink); margin: 16px 0 18px; }
.blog-hero h1 em { color: var(--rust-deep); }
.blog-hero .lede { max-width: 60ch; }
.post-list { padding: clamp(40px,5vw,80px) 0 clamp(60px,8vw,110px); }
.post-card { display: block; border-top: 1px solid var(--rule); padding: 32px 0; transition: padding 220ms cubic-bezier(.2,.7,.2,1); }
.post-card:hover { padding-left: 8px; }
.post-card-cat { font-family: var(--mono); font-size: 10.5px; letter-spacing: .18em; text-transform: uppercase; color: var(--rust-deep); }
.post-card h2 { font-family: var(--serif); font-weight: 700; font-size: clamp(24px,2.6vw,34px); line-height: 1.15; letter-spacing: -.018em; color: var(--ink); margin: 12px 0 12px; max-width: 26ch; transition: color 200ms ease; }
.post-card:hover h2 { color: var(--rust-deep); }
.post-card p { font-size: 16px; line-height: 1.6; color: var(--ink-2); max-width: 62ch; margin: 0 0 14px; }
.post-card-meta { font-family: var(--mono); font-size: 11px; letter-spacing: .04em; color: var(--ink-3); }
.post-cta { background: var(--ink); color: var(--paper); padding: clamp(48px,6vw,88px) 0; }
.post-cta .wrap { max-width: 760px; }
.post-cta .eyebrow { color: color-mix(in oklch, var(--paper) 70%, transparent); }
.post-cta .eyebrow::before { background: color-mix(in oklch, var(--rust) 90%, transparent); }
.post-cta h2 { font-family: var(--serif); font-weight: 700; font-size: clamp(28px,3.4vw,44px); color: var(--paper); margin: 16px 0 16px; max-width: 20ch; letter-spacing: -.018em; }
.post-cta p { color: color-mix(in oklch, var(--paper) 76%, transparent); font-size: 16px; line-height: 1.65; max-width: 54ch; margin-bottom: 28px; }
.post-cta .btn-primary { background: var(--paper); color: var(--ink); }
.post-cta .btn-primary:hover { background: var(--rust); color: var(--paper); }
"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/png" href="../favicon.png">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Northern Peak Systems">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500;1,600;1,700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-CR8009ZP6T"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-CR8009ZP6T');</script>
<script type="application/ld+json">
{ld_json}
</script>
<style>
{styles}
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<div class="masthead"><div class="wrap masthead-inner"><span class="masthead-edition">AI Automation &amp; Web Studio &middot; Edmonton</span><span class="masthead-meta">Vol. I &middot; MMXXVI</span></div></div>
"""

def _plain(text: str) -> str:
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = text.replace('**', '').replace('`', '')
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    return ' '.join(text.split())

def post_schema(p: dict, url: str) -> str:
    graph = [{
        "@type": "BlogPosting", "@id": url + "#post", "headline": p["title"],
        "description": p["description"], "url": url,
        "datePublished": p["date"], "dateModified": p.get("modified", p["date"]),
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "/about.html"},
        "publisher": {"@type": "Organization", "@id": "https://northernpeaksystems.ca/#org", "name": "Northern Peak Systems",
                       "logo": {"@type": "ImageObject", "url": SITE + "/favicon.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "articleSection": p.get("category", "Articles"),
        "keywords": p.get("keyword", ""),
    }]
    if p["faqs"]:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": _plain(q),
             "acceptedAnswer": {"@type": "Answer", "text": _plain(a)}}
            for q, a in p["faqs"]]})
    graph.append({"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
        {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)

def pretty_date(iso: str) -> str:
    y, m, d = iso.split("-")
    months = ["", "January","February","March","April","May","June","July","August","September","October","November","December"]
    return f"{months[int(m)]} {int(d)}, {y}"

def write_post(p: dict) -> Path:
    url = f"{SITE}/blog/{p['slug']}.html"
    faq_html = ""
    if p["faqs"]:
        items = "\n".join(
            f'<div class="faq-q"><dt>{html.escape(q)}</dt><dd>{md_to_html(a).replace("<p>","").replace("</p>","")}</dd></div>'
            for q, a in p["faqs"])
        faq_html = f"""<section class="post-faq"><div class="wrap"><p class="eyebrow">FAQ</p><h2>Frequently asked questions</h2><dl>{items}</dl></div></section>"""

    head = HEAD.format(title=html.escape(p["title"]) + " | Northern Peak Systems",
                       desc=html.escape(p["description"]), canonical=url, og_type="article",
                       ld_json=post_schema(p, url), styles=BLOG_CSS)
    body = f"""{nav_html()}
<main id="main">
<article>
<header class="post-hero"><div class="wrap">
    <p class="post-cat">{html.escape(p.get('category','Article'))}</p>
    <h1 class="post-h1">{html.escape(p['title'])}</h1>
    <p class="post-meta"><span>{pretty_date(p['date'])}</span><span>{p['read_time']} min read</span><span>By {AUTHOR}</span></p>
</div></header>
<div class="post-body"><div class="wrap">
{p['body_html']}
</div></div>
</article>
{faq_html}
<section class="post-cta"><div class="wrap">
    <p class="eyebrow">See it first</p>
    <h2>Want a site that's fast by default?</h2>
    <p>Every site we build is hand-coded to score 95–100 on Google PageSpeed out of the box. Send a few sentences about your business and you'll get back a working preview — no commitment.</p>
    <a href="../contact.html" class="btn btn-primary">Start a project <span class="arrow">→</span></a>
</div></section>
{FOOTER}
{NAV_SCRIPT}
</body></html>"""
    out = OUT / f"{p['slug']}.html"
    out.write_text(head + body, encoding="utf-8")
    return out

def write_index(posts: list) -> Path:
    cards = "\n".join(
        f"""<a class="post-card" href="{p['slug']}.html">
            <p class="post-card-cat">{html.escape(p.get('category','Article'))}</p>
            <h2>{html.escape(p['title'])}</h2>
            <p>{html.escape(p['description'])}</p>
            <p class="post-card-meta">{pretty_date(p['date'])} &middot; {p['read_time']} min read</p>
        </a>""" for p in posts)
    ld = json.dumps({"@context": "https://schema.org", "@type": "Blog", "@id": SITE + "/blog/#blog",
                     "url": SITE + "/blog/", "name": "Northern Peak Systems Blog",
                     "description": "Plain-English guides on web design, performance, and SEO for small businesses.",
                     "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}.html",
                                    "datePublished": p["date"]} for p in posts]}, ensure_ascii=False, indent=2)
    head = HEAD.format(title="Web Design &amp; SEO Blog | Northern Peak Systems",
                       desc="Plain-English guides on web design, website speed, and SEO for small businesses — from Northern Peak Systems in Edmonton.",
                       canonical=SITE + "/blog/", og_type="website", ld_json=ld, styles=BLOG_CSS)
    body = f"""{nav_html()}
<main id="main">
<section class="blog-hero"><div class="wrap">
    <p class="eyebrow">The blog</p>
    <h1>Web design, speed &amp; <em>SEO,</em> in plain language.</h1>
    <p class="lede">Practical guides for small-business owners who want a website that loads fast, ranks well, and actually brings in work — no jargon, no fluff.</p>
</div></section>
<section class="post-list"><div class="wrap">
{cards}
</div></section>
{FOOTER}
{NAV_SCRIPT}
</body></html>"""
    out = OUT / "index.html"
    out.write_text(head + body, encoding="utf-8")
    return out

def update_sitemap(posts: list) -> None:
    sm = ROOT / "sitemap.xml"
    if not sm.exists():
        return
    text = sm.read_text(encoding="utf-8")
    text = re.sub(r'\s*<url>\s*<loc>https://northernpeaksystems\.ca/blog/[^<]*</loc>.*?</url>', '', text, flags=re.S)
    today = date.today().isoformat()
    entries = [f"  <url>\n    <loc>{SITE}/blog/</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.8</priority>\n  </url>"]
    for p in posts:
        entries.append(f"  <url>\n    <loc>{SITE}/blog/{p['slug']}.html</loc>\n    <lastmod>{p['date']}</lastmod>\n    <priority>0.7</priority>\n  </url>")
    text = text.replace("</urlset>", "\n".join(entries) + "\n</urlset>")
    sm.write_text(text, encoding="utf-8")

def main() -> None:
    posts = [parse_post(p) for p in sorted(POSTS_DIR.glob("*.md"))]
    posts.sort(key=lambda p: p["date"], reverse=True)
    for p in posts:
        write_post(p)
    write_index(posts)
    update_sitemap(posts)
    print(f"wrote {len(posts)} post(s) + index -> {OUT}")
    print(f"updated sitemap with blog URLs")

if __name__ == "__main__":
    main()
