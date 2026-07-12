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
        '<a href="/#included" class="mega-item">'
        '<span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M5 12h14M13 6l6 6-6 6"/></svg></span>'
        '<div><b>Everything Included</b><span>See the whole system at a glance</span></div></a>')
    return "\n                        ".join(out)


def nav_links(p):
    cities = "\n                    ".join(
        f'<a href="{p}locations/{slug}.html">{name}</a>' for slug, name in CITIES)
    return f'''<nav class="nav-links" aria-label="Primary">
            <a href="/">Home</a>
            <div class="nav-dd">
                <button type="button" class="nav-dd-toggle" aria-haspopup="true">Products {CHEV}</button>
                <div class="nav-dd-menu mega">
                    <div class="mega-head">Systems &amp; Features</div>
                    <div class="mega-grid">
                        {mega_items(p)}
                    </div>
                </div>
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
        <a href="/#included">Products</a>
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
.nav-dd-menu.mega{background:#fff;border-color:#e8e2d4;min-width:620px;padding:18px 20px 14px;box-shadow:0 30px 64px -24px rgba(0,0,0,0.5);}
.mega-head{font-size:13.5px;font-weight:600;color:#16140f;padding-bottom:12px;border-bottom:1px solid #ece5d6;margin-bottom:8px;}
.mega-grid{display:grid;grid-template-columns:1fr 1fr;gap:2px 16px;}
.nav-dd-menu a.mega-item{display:flex;gap:12px;align-items:flex-start;padding:10px;border-radius:10px;white-space:normal;transition:background .15s;}
.nav-dd-menu a.mega-item:hover{background:#f7f3ea;}
.mega-item .mi{width:38px;height:38px;border-radius:10px;background:#f7f3ea;border:1px solid #e8e2d4;display:flex;align-items:center;justify-content:center;color:#a97c33;flex-shrink:0;}
.mega-item .mi svg{width:18px;height:18px;stroke-width:1.7;}
.mega-item b{display:block;font-size:13.5px;font-weight:700;color:#16140f;line-height:1.3;}
.mega-item span{display:block;font-size:12px;color:#8a8478;line-height:1.45;margin-top:2px;}
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
SUB_PAGES = ["blog/index.html", "blog/why-is-my-website-so-slow.html"]


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
