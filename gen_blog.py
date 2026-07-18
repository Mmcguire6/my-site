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

from gen_locations import CITY_STYLES

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
    return """<header class="nav">
    <div class="wrap nav-inner">
        <a href="../index.html" class="brand" aria-label="Northern Peak Systems, home"><img src="../img/nps-logo-white.webp" alt="Northern Peak Systems" class="brand-logo" width="1432" height="391"></a>
        <nav class="nav-links" aria-label="Primary">
            <a href="../index.html">Home</a>
            <a href="../work.html">Work</a>
            <a href="../pricing.html">Pricing</a>
            <div class="nav-dd">
                <button class="nav-dd-toggle" aria-haspopup="true">Studio <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg></button>
                <div class="nav-dd-menu">
                    <a href="../about.html">About</a>
                    <a href="../how.html">How it works</a>
                    <a href="../faq.html">FAQ</a>
                    <a href="index.html" class="active">Blog</a>
                </div>
            </div>
            <div class="nav-dd">
                <button class="nav-dd-toggle" aria-haspopup="true">Locations <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg></button>
                <div class="nav-dd-menu cols">
                    <a href="../locations/edmonton.html">Edmonton</a>
                    <a href="../locations/calgary.html">Calgary</a>
                    <a href="../locations/st-albert.html">St. Albert</a>
                    <a href="../locations/sherwood-park.html">Sherwood Park</a>
                    <a href="../locations/leduc.html">Leduc</a>
                    <a href="../locations/spruce-grove.html">Spruce Grove</a>
                    <a href="../locations/airdrie.html">Airdrie</a>
                    <a href="../locations/red-deer.html">Red Deer</a>
                    <a href="../locations.html" class="dd-all">All locations &rarr;</a>
                </div>
            </div>
            <a href="../contact.html">Contact</a>
        </nav>
        <div class="nav-cta">
            <a href="../contact.html" class="btn btn-gold">Book a free preview <span class="arr">→</span></a>
            <button class="nav-burger" id="burger" aria-label="Open menu" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="7" x2="21" y2="7"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="17" x2="21" y2="17"/></svg></button>
        </div>
    </div>
</header>

<div class="mnav" id="mnav" aria-hidden="true">
    <div class="mnav-top">
        <span class="brand"><img src="../img/nps-logo-white.webp" alt="Northern Peak Systems" class="brand-logo" width="1432" height="391"></span>
        <button class="mnav-close" id="mclose" aria-label="Close menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg></button>
    </div>
    <nav class="mnav-links" aria-label="Mobile">
        <a href="../index.html"><span class="gold">Home</span></a>
        <a href="../work.html"><span class="gold">Work</span></a>
        <a href="../pricing.html"><span class="gold">Pricing</span></a>
        <a href="../about.html"><span class="gold">About</span></a>
        <a href="../how.html">How it <span class="gold">works</span></a>
        <a href="index.html"><span class="gold">Blog</span></a>
        <a href="../contact.html"><span class="gold">Contact</span></a>
    </nav>
    <div class="mnav-foot">
        <a href="../contact.html" class="btn btn-gold">Book a free preview <span class="arr">→</span></a>
        <a href="../contact.html" class="btn btn-ghost">Get in touch</a>
    </div>
</div>"""

FOOTER = """<footer class="foot">
    <div class="wrap">
        <div class="foot-grid">
            <div class="foot-brand">
                <span class="brand"><img src="../img/nps-logo-white.webp" alt="Northern Peak Systems" class="brand-logo" width="1432" height="391"></span>
                <p class="foot-copy">&copy; <span id="yr">2026</span> Northern Peak Systems<br>All rights reserved.</p>
            </div>
            <div class="foot-col">
                <h4>Services</h4>
                <a href="../index.html#services">AI automation</a>
                <a href="../index.html#services">Web design</a>
                <a href="../index.html#services">SEO &amp; local search</a>
            </div>
            <div class="foot-col">
                <h4>Company</h4>
                <a href="../about.html">About</a>
                <a href="../work.html">Work</a>
                <a href="../how.html">How it works</a>
                <a href="../pricing.html">Pricing</a>
                <a href="../faq.html">FAQ</a>
            </div>
            <div class="foot-col">
                <h4>Get started</h4>
                <a href="../contact.html">Free preview</a>
                <a href="../contact.html">Contact</a>
                <a href="../locations.html">Locations</a>
                <a href="mailto:matt@northernpeaksystems.ca">Email us</a>
            </div>
        </div>
        <div class="foot-bottom">
            <span>Founder-led in Edmonton, Alberta &middot; Serving Canada &amp; the US</span>
            <div class="foot-social">
                <a href="https://www.linkedin.com/in/matthew-mcguire-44666b389" aria-label="LinkedIn" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.5 8.5h-3v11h3v-11zM5 7a1.7 1.7 0 1 0 0-3.4A1.7 1.7 0 0 0 5 7zm15.5 12.5v-6c0-3-1.6-4.4-3.8-4.4-1.7 0-2.5 1-3 1.6V8.5h-3v11h3v-6.1c0-1.4.9-2.1 1.9-2.1s1.9.7 1.9 2.1v6.1h3z"/></svg></a>
                <a href="../privacy.html" style="width:auto;padding:0 14px;font-size:13px;">Privacy</a>
                <a href="../terms.html" style="width:auto;padding:0 14px;font-size:13px;">Terms</a>
            </div>
        </div>
    </div>
</footer>"""

NAV_SCRIPT = """<script>
document.getElementById('yr').textContent=new Date().getFullYear();
var burger=document.getElementById('burger'),mnav=document.getElementById('mnav'),mclose=document.getElementById('mclose');
function openM(){mnav.classList.add('open');mnav.setAttribute('aria-hidden','false');burger.setAttribute('aria-expanded','true');document.body.style.overflow='hidden';}
function closeM(){mnav.classList.remove('open');mnav.setAttribute('aria-hidden','true');burger.setAttribute('aria-expanded','false');document.body.style.overflow='';}
burger.addEventListener('click',openM);mclose.addEventListener('click',closeM);
mnav.querySelectorAll('a').forEach(function(a){a.addEventListener('click',closeM);});

var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:0.12});
document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});
</script>"""

# Blog-specific CSS appended to the shared dark site styles (CITY_STYLES supplies
# the dark :root vars, nav, mnav, footer, buttons and .reveal animation).
BLOG_CSS = CITY_STYLES + """
.skip-link{position:absolute;top:-48px;left:8px;background:var(--gold);color:#fff;padding:8px 14px;font-size:13px;font-weight:600;border-radius:6px;z-index:200;transition:top .2s;}
.skip-link:focus{top:8px;}

/* ===== POST HERO ===== */
.bhero{background:#000;border-bottom:1px solid var(--line);position:relative;overflow:hidden;}
.bhero-bg{position:absolute;inset:0;z-index:0;}
.bhero-bg img{width:100%;height:100%;object-fit:cover;object-position:center;opacity:0.32;}
.bhero-scrim{position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(8,9,11,0.94),rgba(8,9,11,0.7)),linear-gradient(to top,var(--bg) 1%,transparent 60%);}
.bhero .wrap{position:relative;z-index:2;max-width:820px;padding-top:clamp(56px,7vw,104px);padding-bottom:clamp(36px,4vw,56px);}
.bhero h1{font-family:var(--display);font-weight:600;font-size:clamp(34px,5vw,62px);line-height:1.06;letter-spacing:-0.022em;max-width:20ch;margin:16px 0 18px;}
.bhero h1 em{font-style:italic;color:var(--gold);}
.post-meta{font-size:13px;letter-spacing:0.02em;color:var(--mist-2);display:flex;gap:14px;flex-wrap:wrap;align-items:center;}
.post-meta span + span::before{content:"·";margin-right:14px;color:var(--mist-2);}

/* ===== POST BODY ===== */
.post-body{padding:clamp(40px,5vw,72px) 0 clamp(48px,6vw,88px);}
.post-body .wrap{max-width:760px;}
.post-body p,.post-body li{font-size:clamp(16.5px,1.2vw,18px);line-height:1.8;color:var(--mist);}
.post-body p{margin:0 0 22px;}
.post-body > p:first-of-type{font-size:clamp(18px,1.4vw,21px);color:var(--white);line-height:1.72;}
.post-body h2{font-family:var(--display);font-weight:600;font-size:clamp(25px,2.8vw,36px);line-height:1.18;letter-spacing:-0.018em;color:var(--white);margin:52px 0 16px;}
.post-body h3{font-family:var(--display);font-weight:500;font-size:clamp(19px,1.8vw,24px);color:var(--gold-2);margin:34px 0 10px;}
.post-body ul,.post-body ol{margin:0 0 22px;padding-left:24px;}
.post-body li{margin-bottom:10px;}
.post-body ul li{list-style:none;position:relative;}
.post-body ul li::before{content:"";position:absolute;left:-18px;top:13px;width:6px;height:6px;background:var(--gold);border-radius:999px;}
.post-body ol{list-style:none;counter-reset:li;}
.post-body ol li{counter-increment:li;position:relative;}
.post-body ol li::before{content:counter(li);position:absolute;left:-26px;top:1px;font-size:13px;font-weight:700;color:var(--gold);font-variant-numeric:tabular-nums;}
.post-body a{color:var(--gold-2);border-bottom:1px solid rgba(197,137,74,0.4);transition:color .18s,border-color .18s;}
.post-body a:hover{color:var(--gold);border-bottom-color:var(--gold);}
.post-body strong{color:var(--white);font-weight:700;}
.post-body em{color:var(--mist);}
.post-body code{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:.88em;background:var(--bg-3);border:1px solid var(--line);color:var(--gold-2);padding:2px 7px;border-radius:6px;}
.post-body blockquote{margin:30px 0;padding:6px 0 6px 26px;border-left:3px solid var(--gold);}
.post-body blockquote p{font-family:var(--display);font-style:italic;font-size:clamp(19px,1.8vw,24px);color:var(--white);}

/* ===== POST FAQ ===== */
.post-faq{background:var(--bg-2);padding:clamp(48px,6vw,88px) 0;border-top:1px solid var(--line);}
.post-faq .wrap{max-width:760px;}
.post-faq .eyebrow{margin-bottom:16px;}
.post-faq h2{font-family:var(--display);font-weight:600;font-size:clamp(26px,3vw,40px);color:var(--white);margin-bottom:32px;letter-spacing:-0.018em;}
.faq-q{border-top:1px solid var(--line);padding-top:24px;margin-top:24px;}
.faq-q:first-of-type{border-top:none;padding-top:0;margin-top:0;}
.faq-q dt{font-family:var(--display);font-weight:600;font-size:clamp(18px,1.7vw,23px);color:var(--white);margin-bottom:10px;}
.faq-q dd{margin:0;font-size:16px;line-height:1.75;color:var(--mist);}
.faq-q dd a{color:var(--gold-2);border-bottom:1px solid rgba(197,137,74,0.4);}
.faq-q dd a:hover{color:var(--gold);}

/* ===== CTA ===== */
.post-cta{background:#0a0b0c;padding:clamp(56px,7vw,96px) 0;border-top:1px solid var(--line);}
.post-cta .wrap{max-width:760px;}
.post-cta .eyebrow{margin-bottom:14px;}
.post-cta h2{font-family:var(--display);font-weight:600;font-size:clamp(28px,3.6vw,46px);color:var(--white);margin:0 0 16px;max-width:20ch;letter-spacing:-0.018em;}
.post-cta h2 em{font-style:italic;color:var(--gold);}
.post-cta p{color:var(--mist);font-size:clamp(15px,1.3vw,17px);line-height:1.7;max-width:54ch;margin-bottom:30px;}
.post-cta-actions{display:flex;flex-wrap:wrap;gap:14px;align-items:center;}
.post-back{display:inline-flex;align-items:center;gap:9px;font-size:13px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--mist);transition:color .18s;}
.post-back:hover{color:var(--gold);}

/* ===== BLOG INDEX ===== */
.blog-hero{padding:clamp(72px,9vw,130px) 0 clamp(32px,4vw,56px);}
.blog-hero h1{font-family:var(--display);font-weight:600;font-size:clamp(40px,5.4vw,76px);letter-spacing:-0.022em;color:var(--white);margin:16px 0 18px;}
.blog-hero h1 em{font-style:italic;color:var(--gold);}
.blog-hero .lede{max-width:60ch;font-size:clamp(16px,1.4vw,19px);color:var(--mist);}
.post-list{padding:clamp(40px,5vw,80px) 0 clamp(60px,8vw,110px);}
.post-card{display:block;border-top:1px solid var(--line);padding:32px 0;transition:padding .22s cubic-bezier(.2,.7,.2,1);}
.post-card:last-child{border-bottom:1px solid var(--line);}
.post-card:hover{padding-left:8px;}
.post-card-cat{font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);}
.post-card h2{font-family:var(--display);font-weight:600;font-size:clamp(24px,2.6vw,34px);line-height:1.15;letter-spacing:-0.018em;color:var(--white);margin:12px 0 12px;max-width:26ch;transition:color .2s;}
.post-card:hover h2{color:var(--gold-2);}
.post-card p{font-size:16px;line-height:1.6;color:var(--mist);max-width:62ch;margin:0 0 14px;}
.post-card-meta{font-size:12.5px;letter-spacing:.02em;color:var(--mist-2);}

/* ============================================================
   LIGHT EDITORIAL THEME — post + index pages sit light between
   the dark nav and dark footer. More air, warmer paper, imagery.
   ============================================================ */
:root{--ink:#191b1f;--body:#42454c;--muted:#7a7e87;--paper:#fdfcfa;--paper-2:#f7f5f1;--paper-3:#f4f1ea;--gline:#e6e1d8;--glink:#a76f2c;--glink-hi:#875619;}
main#main{background:var(--paper);}

/* hero (light) */
.bhero{background:var(--paper-2);border-bottom:1px solid var(--gline);}
.bhero-bg,.bhero-scrim{display:none;}
.bhero .wrap{max-width:860px;padding-top:clamp(52px,6.5vw,92px);padding-bottom:clamp(26px,3vw,38px);}
.bhero .eyebrow{color:var(--glink);}
.bhero h1{color:var(--ink);margin:18px 0 20px;}
.bhero h1 em{color:var(--gold);}
.post-meta{color:var(--muted);}
.post-meta span + span::before{color:#c2bcae;}

/* featured cover band (imagery) */
.bcover{background:var(--paper-2);}
.bcover .wrap{max-width:1080px;padding-top:clamp(20px,2.6vw,34px);padding-bottom:4px;}
.bcover-inner{position:relative;border-radius:22px;overflow:hidden;aspect-ratio:16/6;min-height:200px;
  background:#0e1526;border:1px solid var(--gline);box-shadow:0 34px 70px -46px rgba(18,24,40,.55);
  display:flex;align-items:center;justify-content:center;}
.bcover-inner img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.5;}
.bcover-inner::after{content:"";position:absolute;inset:0;
  background:linear-gradient(115deg,rgba(12,18,34,.9),rgba(12,18,34,.4)),radial-gradient(75% 130% at 88% 92%,rgba(197,137,74,.42),transparent 60%);}
.bcover-cat{position:absolute;left:clamp(20px,3vw,34px);top:clamp(16px,2.4vw,26px);z-index:2;
  font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:rgba(244,231,206,.9);}
.bcover-ic{position:relative;z-index:2;color:rgba(246,234,210,.92);display:inline-flex;}
.bcover-ic svg{width:clamp(52px,7vw,96px);height:clamp(52px,7vw,96px);stroke-width:1.1;}

/* body (light + airy) */
.post-body{background:var(--paper);padding:clamp(52px,6.5vw,96px) 0 clamp(56px,7vw,104px);}
.post-body .wrap{max-width:720px;}
.post-body p,.post-body li{color:var(--body);line-height:1.85;}
.post-body > p:first-of-type{color:var(--ink);}
.post-body h2{color:var(--ink);margin:clamp(48px,6vw,72px) 0 18px;}
.post-body h3{color:var(--glink);margin:40px 0 12px;}
.post-body strong{color:var(--ink);}
.post-body em{color:var(--body);}
.post-body a{color:var(--glink);border-bottom-color:rgba(167,111,44,.32);}
.post-body a:hover{color:var(--glink-hi);border-bottom-color:var(--glink-hi);}
.post-body ol li::before{color:var(--glink);}
.post-body blockquote p{color:var(--ink);}
.post-body code{background:var(--paper-3);border-color:var(--gline);color:var(--glink-hi);}

/* faq (light tint) */
.post-faq{background:var(--paper-3);border-top:1px solid var(--gline);}
.post-faq .eyebrow{color:var(--glink);}
.post-faq h2{color:var(--ink);}
.faq-q{border-top-color:#e2ddd2;}
.faq-q dt{color:var(--ink);}
.faq-q dd{color:#4a4d54;}
.faq-q dd a{color:var(--glink);}
.faq-q dd a:hover{color:var(--glink-hi);}

/* cta (warm light band, gold button pops) */
.post-cta{background:#f6efe1;border-top:1px solid #ece0cb;}
.post-cta .eyebrow{color:var(--glink);}
.post-cta h2{color:var(--ink);}
.post-cta h2 em{color:var(--gold);}
.post-cta p{color:#4a4d54;}
.post-back{color:var(--muted);}
.post-back:hover{color:var(--glink-hi);}

/* index (light) */
.blog-hero{background:var(--paper);}
.blog-hero .eyebrow{color:var(--glink);}
.blog-hero h1{color:var(--ink);}
.blog-hero h1 em{color:var(--gold);}
.blog-hero .lede{color:#4a4d54;}
.post-list{background:var(--paper);}
.post-card{border-top-color:var(--gline);}
.post-card:last-child{border-bottom-color:var(--gline);}
.post-card-cat{color:var(--glink);}
.post-card h2{color:var(--ink);}
.post-card:hover h2{color:var(--glink-hi);}
.post-card p{color:#4a4d54;}
.post-card-meta{color:var(--muted);}
"""

COVER_ICONS = {
    "Performance": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M4 18a8 8 0 1 1 16 0"/><path d="M12 14l4.5-4.5"/><circle cx="12" cy="14" r="1.4"/></svg>',
    "Lead Generation": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/></svg>',
    "Local SEO": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-6.5-5.7-6.5-10.2A6.5 6.5 0 0 1 18.5 10.8C18.5 15.3 12 21 12 21z"/><circle cx="12" cy="10.6" r="2.4"/></svg>',
    "Websites": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="15" rx="2"/><path d="M3 9h18"/><path d="M6.2 6.7h.01M8.5 6.7h.01"/></svg>',
    "_default": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/></svg>',
}

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="../favicon.ico?v=2" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="../favicon-32.png?v=2">
<link rel="apple-touch-icon" href="../apple-touch-icon.png?v=2">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Northern Peak Systems">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,144,400;0,144,500;0,144,600;0,144,700;1,144,500;1,144,600&display=swap" rel="stylesheet">
<script type="application/ld+json">
{ld_json}
</script>
<style>
{styles}
</style>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-CR8009ZP6T"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-CR8009ZP6T');</script>
<script type="text/javascript">(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","wh3e6pv2u4");</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
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

    head = HEAD.format(title=html.escape(p.get("title_tag", p["title"] + " | Northern Peak Systems")),
                       desc=html.escape(p["description"]), canonical=url, og_type="article",
                       ld_json=post_schema(p, url), styles=BLOG_CSS)
    cta_eyebrow = p.get("cta_eyebrow", "See it first")
    cta_title = p.get("cta_title", "Want a site that's <em>fast by default?</em>")
    cta_body = p.get("cta_body", "Every site we build is hand-coded to score 95–100 on Google PageSpeed out of the box — from $97/month, no long-term contracts. Send a few sentences about your business and you'll get back a working preview, no commitment.")
    cover_svg = COVER_ICONS.get(p.get("category", "").strip(), COVER_ICONS["_default"])
    body = f"""{nav_html()}
<main id="main">
<article>
<header class="bhero">
    <div class="bhero-bg"><img src="../img/work-hero-bg.webp" alt="" decoding="async" width="1536" height="1024"></div>
    <div class="bhero-scrim"></div>
    <div class="wrap">
        <span class="eyebrow">{html.escape(p.get('category','Article'))}</span>
        <h1>{html.escape(p['title'])}</h1>
        <p class="post-meta"><span>{pretty_date(p['date'])}</span><span>{p['read_time']} min read</span><span>By {AUTHOR}</span></p>
    </div>
</header>
<section class="bcover"><div class="wrap"><div class="bcover-inner">
    <img src="../img/work-hero-bg.webp" alt="" loading="lazy" decoding="async">
    <span class="bcover-cat">{html.escape(p.get('category','Article'))}</span>
    <span class="bcover-ic" aria-hidden="true">{cover_svg}</span>
</div></div></section>
<div class="post-body"><div class="wrap">
{p['body_html']}
</div></div>
</article>
{faq_html}
<section class="post-cta"><div class="wrap">
    <p class="eyebrow">{cta_eyebrow}</p>
    <h2>{cta_title}</h2>
    <p>{cta_body}</p>
    <div class="post-cta-actions">
        <a href="../contact.html" class="btn btn-gold">Book a free preview <span class="arr">→</span></a>
        <a href="index.html" class="post-back">← Back to blog</a>
    </div>
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
