# -*- coding: utf-8 -*-
"""Reskin legacy pages onto the current design tokens (colors + fonts).

Maps the two old palettes (warm-brown #1c1a17 and near-black #0d0e10, muted
gold #aa733b, Fraunces/Playfair serif display) onto the new system used by
index/pricing/features: true black #0a0a0c, bright gold #d2a24c, Inter-only.

Run:  python reskin_tokens.py   (then re-run gen_locations.py)
Idempotent — replacements are no-ops once applied.
"""
import io
import re
from pathlib import Path

ROOT = Path(__file__).parent

# ordered: longer/more specific first
COLOR_MAP = [
    # backgrounds (warm-brown family)
    ("#1c1a17", "#0a0a0c"), ("#221f1a", "#0f0f12"), ("#26231e", "#131317"), ("#302b23", "#17171c"),
    # backgrounds (near-black family)
    ("#0d0e10", "#0a0a0c"), ("#121316", "#0f0f12"), ("#17181c", "#131317"), ("#1e2026", "#17171c"),
    # gold
    ("#aa733b", "#d2a24c"), ("#c5894a", "#e6be6e"),
    ("rgba(170,115,59", "rgba(210,162,76"),
    # gold button gradients (old muted -> new bright, with dark text)
    ("background:linear-gradient(180deg,#b27e45,#a06d38);color:#fff", "background:linear-gradient(180deg,#e0b360,#c2903c);color:#181207"),
    ("background:linear-gradient(180deg,#c08749,#ad7640)", "background:linear-gradient(180deg,#eabf6c,#cd9a42)"),
    ("#b27e45", "#e0b360"), ("#a06d38", "#c2903c"), ("#c08749", "#eabf6c"), ("#ad7640", "#cd9a42"),
    # neutrals
    ("#f4f1ea", "#f5f2ec"), ("#f3efe6", "#f7f5f0"),
    ("#b3ada2", "#a9a49a"), ("#a8a298", "#a9a49a"),
    ("#847f74", "#7b766c"), ("#7c786f", "#7b766c"),
    ("#191713", "#16140f"), ("#14120e", "#16140f"),
    ("#5f5a51", "#6f695d"), ("#5f5a4f", "#6f695d"),
    ("rgba(250,244,234", "rgba(255,255,255"),
    # nav glass background (old rgb of #0d0e10)
    ("rgba(13,14,16,0.82)", "rgba(10,10,12,0.85)"),
]

INTER_STACK = "'Inter',system-ui,-apple-system,'Segoe UI',sans-serif"
FONT_MAP = [
    ("--display:'Fraunces','Playfair Display',Georgia,serif;", "--display:%s;" % INTER_STACK),
    ("--display: 'Fraunces','Playfair Display',Georgia,serif;", "--display:%s;" % INTER_STACK),
    ("--serif:'Playfair Display',Georgia,serif;", "--serif:%s;" % INTER_STACK),
]

# drop the Google Fonts request for the serif faces (Inter is self-hosted)
RE_GFONT = re.compile(r'<link href="https://fonts\.googleapis\.com/css2\?family=(?:Fraunces|Caveat|Playfair)[^"]*" rel="stylesheet">\n?')

INTER_800 = "@font-face{font-family:'Inter';font-style:normal;font-weight:800;font-display:swap;src:url(/fonts/inter-800-normal.woff2) format('woff2');}"
INTER_700 = "@font-face{font-family:'Inter';font-style:normal;font-weight:700;font-display:swap;src:url(/fonts/inter-700-normal.woff2) format('woff2');}"

PAGES = ["about.html", "how.html", "faq.html", "contact.html", "work.html",
         "privacy.html", "terms.html", "404.html",
         "blog/index.html", "blog/why-is-my-website-so-slow.html",
         "gen_locations.py"]


def reskin(path: Path) -> bool:
    s = io.open(path, encoding="utf-8").read()
    orig = s
    for a, b in COLOR_MAP + FONT_MAP:
        s = s.replace(a, b)
    s = RE_GFONT.sub("", s)
    if INTER_800 not in s and INTER_700 in s:
        s = s.replace(INTER_700, INTER_700 + "\n" + INTER_800)
    if s != orig:
        io.open(path, "w", encoding="utf-8").write(s)
        return True
    return False


def main():
    for f in PAGES:
        p = ROOT / f
        if p.exists():
            print(("reskinned " if reskin(p) else "no change ") + f)


if __name__ == "__main__":
    main()
