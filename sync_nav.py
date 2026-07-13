# -*- coding: utf-8 -*-
"""Sync the site-wide navigation to the current design on every page.

Canonical nav: Home / Products (mega dropdown) / Pricing / About / Studio /
Locations / Contact + "Book a Call". Defined here once; run after changing it.

Patches:
  - root pages (about, how, faq, contact, work, locations, privacy, terms, 404)
  - blog pages (../-relative)
  - gen_locations.py templates (so regenerated location pages stay consistent)

index.html, pricing.html, and features/* already carry this nav natively.
Run:  python sync_nav.py   (then re-run gen_locations.py)
"""
import io
import re
from pathlib import Path

ROOT = Path(__file__).parent

FEATURES = [
    ("website", "Custom Website", "A lead-generating website, built in days",
     '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>'),
    ("missed-call-text-back", "Missed Call Text-Back", "Automatically text back missed calls",
     '<path d="M4 5a2 2 0 0 1 2-2h2l1.5 4-2 1.5a12 12 0 0 0 6 6l1.5-2 4 1.5V18a2 2 0 0 1-2 2A15 15 0 0 1 4 5z"/>'),
    ("review-automation", "5-Star Review Funnel", "Get more 5-star reviews on autopilot",
     '<path d="M12 3l2.6 5.3 5.9.9-4.2 4.1 1 5.8L12 16.9 6.7 19.2l1-5.8L3.5 9.2l5.9-.9z"/>'),
    ("lead-follow-up", "Lead Follow-Up", "Automatically follow up with leads via text",
     '<path d="M21 11.5a7.5 7.5 0 0 1-10.9 6.7L4 20l1.8-5.1A7.5 7.5 0 1 1 21 11.5z"/>'),
    ("local-seo", "Local SEO", "Actually get found on Google",
     '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>'),
    ("marketing-campaigns", "Marketing Campaigns", "Keep your customers thinking about you",
     '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>'),
    ("crm-and-booking", "CRM &amp; Booking", "Every lead and appointment in one place",
     '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M8 3v4M16 3v4M4 11h16"/>'),
]

CHEV = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<polyline points="6 9 12 15 18 9"/></svg>')

CITIES = [("edmonton", "Edmonton"), ("calgary", "Calgary"), ("st-albert", "St. Albert"),
          ("sherwood-park", "Sherwood Park"), ("leduc", "Leduc"), ("spruce-grove", "Spruce Grove"),
          ("airdrie", "Airdrie"), ("red-deer", "Red Deer")]


def mega_items(p):
    out = []
    for slug, label, desc, icon in FEATURES:
        out.append(
            f'<a href="{p}features/{slug}.html" class="mega-item">'
            f'<span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{icon}</svg></span>'
            f'<div><b>{label}</b><span>{desc}</span></div></a>')
    out.append(
        '<a href="/pricing.html" class="mega-item">'
        '<span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M5 12h14M13 6l6 6-6 6"/></svg></span>'
        '<div><b>Everything Included</b><span>See the whole system at a glance</span></div></a>')
    return "\n                        ".join(out)


MEGA2_CARDS = [('website', 'website', 'Custom Website', 'Lead-generating websites built to convert visitors into customers.'), ('review-automation', 'reviews', '5-Star Review Funnel', 'Get more five-star reviews on autopilot and build instant trust.'), ('local-seo', 'seo', 'Local SEO', 'Show up at the top of Google when local customers are searching.'), ('missed-call-text-back', 'textback', 'Missed Call Text Back', 'Never miss another lead. We text back missed calls instantly.'), ('crm-and-booking', 'crm', 'CRM &amp; Booking', 'Manage leads, book jobs, and keep everything organized in one place.'), ('lead-follow-up', 'followup', 'Lead Follow-Up', 'Automated follow-ups via text so you stay top of mind and win more jobs.'), ('marketing-campaigns', 'marketing', 'Marketing Campaigns', 'One-click campaigns that bring past customers back and fill your pipeline.')]
MEGA2_STRIP = [('website', 'Website'), ('search', 'SEO'), ('reviews', 'Reviews'), ('textback', 'Text Back'), ('crm', 'CRM'), ('followup', 'Follow-Up'), ('marketing', 'Marketing')]
MEGA2_ICONS = {'website': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>', 'reviews': '<path d="M12 3l2.6 5.3 5.9.9-4.2 4.1 1 5.8L12 16.9 6.7 19.2l1-5.8L3.5 9.2l5.9-.9z"/>', 'seo': '<path d="M12 21s7-6.3 7-11a7 7 0 1 0-14 0c0 4.7 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>', 'textback': '<path d="M4 5a2 2 0 0 1 2-2h2l1.5 4-2 1.5a12 12 0 0 0 6 6l1.5-2 4 1.5V18a2 2 0 0 1-2 2A15 15 0 0 1 4 5z"/>', 'crm': '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M8 3v4M16 3v4M4 11h16"/>', 'followup': '<path d="M21 11.5a7.5 7.5 0 0 1-10.9 6.7L4 20l1.8-5.1A7.5 7.5 0 1 1 21 11.5z"/>', 'marketing': '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>', 'check': '<path d="M20 6 9 17l-5-5"/>', 'search': '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>'}

def m2svg(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round">' + MEGA2_ICONS[name] + '</svg>')

def mega2_html(p):
    cards = ''
    for slug, ic, title, desc in MEGA2_CARDS:
        cards += ('<a href="' + p + 'features/' + slug + '.html" class="m2-card">'
                  '<span class="ic">' + m2svg(ic) + '</span><b>' + title + '</b><span>' + desc + '</span></a>\n                        ')
    strip = ''.join('<span>' + m2svg(k) + lbl + '</span>' for k, lbl in MEGA2_STRIP)
    chk = m2svg('check')
    return f'''<div class="nav-dd-menu mega">
                    <div class="mega2-grid">
                        <aside class="mega2-rail">
                            <span class="m2-eyebrow">The Complete Solution</span>
                            <div class="m2-title">Business <span>Growth</span> System</div>
                            <p>Everything works together to attract more leads, build trust, and book more jobs.</p>
                            <a href="{p}how.html" class="m2-btn">See How It Works <span class="arr">&rarr;</span></a>
                        </aside>
                        <div class="mega2-cards">
                        {cards}<div class="m2-foot">
                            <span class="chk">{chk}</span>
                            <div>
                                <b>Everything Working Together</b>
                                <p>One connected system designed to attract, convert, and retain more customers so you can focus on the work.</p>
                                <div class="m2-strip">{strip}</div>
                            </div>
                        </div>
                        </div>
                    </div>
                </div>'''

def nav_links(p):
    cities = "\n                    ".join(
        f'<a href="{p}locations/{slug}.html">{name}</a>' for slug, name in CITIES)
    return f'''<nav class="nav-links" aria-label="Primary">
            <a href="/">Home</a>
            <div class="nav-dd nav-dd-static">
                <button type="button" class="nav-dd-toggle" aria-haspopup="true">Products {CHEV}</button>
                {mega2_html(p)}
            </div>
            <a href="{p}pricing.html">Pricing</a>
            <a href="{p}about.html">About</a>
            <div class="nav-dd">
                <button type="button" class="nav-dd-toggle" aria-haspopup="true">Studio {CHEV}</button>
                <div class="nav-dd-menu">
                    <a href="{p}work.html">Work</a>
                    <a href="{p}how.html">How we work</a>
                    <a href="{p}faq.html">FAQ</a>
                    <a href="{p}blog/">Blog</a>
                </div>
            </div>
            <div class="nav-dd">
                <button type="button" class="nav-dd-toggle" aria-haspopup="true">Locations {CHEV}</button>
                <div class="nav-dd-menu cols">
                    {cities}
                    <a href="{p}locations.html" class="dd-all">All locations &rarr;</a>
                </div>
            </div>
            <a href="{p}contact.html">Contact</a>
        </nav>'''


def mnav_links(p):
    return f'''<nav class="mnav-links" aria-label="Mobile">
        <a href="/">Home</a>
        <a href="/#features">Products</a>
        <a href="{p}pricing.html">Pricing</a>
        <a href="{p}about.html">About</a>
        <a href="{p}work.html">Work</a>
        <a href="{p}locations.html">Locations</a>
        <a href="{p}contact.html">Contact</a>
    </nav>'''


def mnav_foot(p):
    return (f'<div class="mnav-foot">\n        <a href="{p}contact.html" class="btn btn-gold">'
            f'Book a Call <span class="arr">&rarr;</span></a>\n    </div>')


# Self-contained styles for the mega menu + outline nav button on legacy pages.
MEGA_CSS = '''<style id="nav-mega-css">
.nav-dd-menu{transition:opacity .18s ease .25s,transform .18s ease .25s,visibility 0s linear .45s;}
.nav-dd:hover .nav-dd-menu{transition-delay:0s,0s,0s;}
.nav-dd-static{position:static;}
.nav-dd-static::after{display:none;}
.nav-dd-menu.mega{top:100%;width:min(980px,calc(100vw - 28px));background:#101014;border:1px solid rgba(210,162,76,0.28);border-radius:0 0 18px 18px;padding:0;overflow:hidden;box-shadow:0 46px 90px -30px rgba(0,0,0,0.85);}
.mega2-grid{display:grid;grid-template-columns:255px 1fr;}
.mega2-rail{position:relative;background:#14110b url('/img/northern-peak-hero-bg.webp') bottom center/cover no-repeat;padding:22px 22px 150px;display:flex;flex-direction:column;align-items:flex-start;gap:10px;}
.mega2-rail::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,#16120c 0%,rgba(22,18,12,0.82) 45%,rgba(22,18,12,0.1) 100%);}
.mega2-rail > *{position:relative;z-index:1;}
.m2-eyebrow{font-size:9.5px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#d2a24c;}
.m2-title{font-family:var(--display,inherit);font-size:24px;font-weight:800;color:#fff;line-height:1.12;letter-spacing:-0.01em;}
.m2-title span{color:#d2a24c;}
.mega2-rail p{font-size:12px;color:#cfc9bd;line-height:1.55;white-space:normal;}
.m2-btn{display:inline-flex;align-items:center;gap:7px;font-size:10px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:#d2a24c;border:1px solid rgba(210,162,76,0.5);border-radius:8px;padding:9px 14px;margin-top:4px;transition:border-color .15s,color .15s;}
.m2-btn:hover{border-color:#d2a24c;color:#e6be6e;}
.mega2-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:rgba(255,255,255,0.07);}
.nav-dd-menu a.m2-card{display:block;background:#101014;padding:14px 16px;border-radius:0;white-space:normal;transition:background .15s;}
.nav-dd-menu a.m2-card:hover{background:#17171c;}
.m2-card .ic{display:flex;width:30px;height:30px;border-radius:8px;background:rgba(210,162,76,0.12);border:1px solid rgba(210,162,76,0.3);align-items:center;justify-content:center;color:#d2a24c;margin-bottom:9px;}
.m2-card .ic svg{width:15px;height:15px;}
.m2-card b{display:block;font-size:12.5px;font-weight:700;color:#fff;line-height:1.3;}
.m2-card span{display:block;font-size:11px;color:#a9a49a;line-height:1.45;margin-top:3px;}
.m2-foot{grid-column:span 2;background:#101014;padding:14px 16px;display:flex;gap:12px;align-items:flex-start;}
.m2-foot .chk{width:30px;height:30px;border-radius:50%;background:linear-gradient(180deg,#e0b360,#c2903c);color:#181207;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.m2-foot .chk svg{width:15px;height:15px;}
.m2-foot b{display:block;font-size:12.5px;font-weight:700;color:#fff;}
.m2-foot p{font-size:11px;color:#a9a49a;line-height:1.5;margin-top:3px;white-space:normal;}
.m2-strip{display:flex;gap:14px;margin-top:10px;flex-wrap:wrap;}
.m2-strip span{display:flex;flex-direction:column;align-items:center;gap:3px;font-size:9px;color:#7b766c;}
.m2-strip svg{width:13px;height:13px;color:#d2a24c;}
.nav-cta .btn-line{background:transparent;color:#d2a24c;border:1px solid rgba(210,162,76,0.35);}
.nav-cta .btn-line:hover{border-color:#d2a24c;color:#e6be6e;transform:translateY(-2px);}
</style>
'''

RE_NAV = re.compile(r'<nav class="nav-links"[^>]*>.*?</nav>', re.DOTALL)
RE_MNAV = re.compile(r'<nav class="mnav-links"[^>]*>.*?</nav>', re.DOTALL)
RE_MFOOT = re.compile(r'<div class="mnav-foot">.*?</div>', re.DOTALL)
# captures the ../ (or empty) prefix so it can be preserved
RE_NAVCTA = re.compile(r'(<div class="nav-cta">\s*)<a href="((?:\.\./)?)[^"]*"[^>]*class="btn[^"]*"[^>]*>.*?</a>', re.DOTALL)


def cta_anchor(prefix: str) -> str:
    return f'<a href="{prefix}contact.html" class="btn btn-line">Book a Call</a>'


def patch_html(path: Path, prefix: str) -> bool:
    s = io.open(path, encoding="utf-8").read()
    orig = s
    s = RE_NAV.sub(lambda m: nav_links(prefix), s, count=1)
    s = RE_MNAV.sub(lambda m: mnav_links(prefix), s, count=1)
    s = RE_MFOOT.sub(lambda m: mnav_foot(prefix), s, count=1)
    s = RE_NAVCTA.sub(lambda m: m.group(1) + cta_anchor(prefix), s, count=1)
    if "nav-mega-css" not in s:
        s = s.replace("</head>", MEGA_CSS + "</head>", 1)
    if s != orig:
        io.open(path, "w", encoding="utf-8").write(s)
        return True
    return False


def patch_gen_locations() -> None:
    """Patch both templates inside gen_locations.py: the first nav/mnav/foot/cta
    belongs to the city-page template (../ links), the second to locations.html
    (root links). CSS braces are doubled because templates go through str.format()."""
    path = ROOT / "gen_locations.py"
    s = io.open(path, encoding="utf-8").read()
    prefixes = ["../", ""]

    def sub_ordered(regex, builder):
        nonlocal s
        for i, prefix in enumerate(prefixes):
            matches = list(regex.finditer(s))
            if i < len(matches):
                mm = matches[i]
                s = s[:mm.start()] + builder(prefix) + s[mm.end():]

    sub_ordered(RE_NAV, nav_links)
    sub_ordered(RE_MNAV, mnav_links)
    sub_ordered(RE_MFOOT, mnav_foot)
    sub_ordered(RE_NAVCTA and re.compile(RE_NAVCTA.pattern, re.DOTALL),
                lambda p: f'<div class="nav-cta">\n            {cta_anchor(p)}')
    if "nav-mega-css" not in s:
        css_escaped = MEGA_CSS.replace("{", "{{").replace("}", "}}")
        s = s.replace("</head>", css_escaped + "</head>")
    io.open(path, "w", encoding="utf-8").write(s)
    print("patched gen_locations.py")


ROOT_PAGES = ["about.html", "how.html", "faq.html", "contact.html", "work.html",
              "locations.html", "privacy.html", "terms.html", "404.html"]
SUB_PAGES = ["blog/index.html", "blog/why-is-my-website-so-slow.html", "features/website.html"]


def main():
    for f in ROOT_PAGES:
        p = ROOT / f
        if p.exists():
            print(("patched " if patch_html(p, "") else "no change ") + f)
    for f in SUB_PAGES:
        p = ROOT / f
        if p.exists():
            print(("patched " if patch_html(p, "../") else "no change ") + f)
    patch_gen_locations()


if __name__ == "__main__":
    main()
