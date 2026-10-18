# -*- coding: utf-8 -*-
"""Sync the site-wide header to every page, using index.html as the single source of truth.

What gets copied from index.html:
  - the desktop header   <header class="nav"> ... </header>
  - the mobile menu      <div class="mnav" id="mnav"> ... </div>
  - every CSS rule the header needs (nav, dropdowns, mobile menu, header buttons,
    the header's CSS variables and its heading font), injected into each page as
    <style id="nav-sync-css"> just before </head> so it overrides older nav styles

Links and images are rewritten for each page's folder depth, and links to homepage
anchors (#trades, #features) become index.html#... on other pages.

Usage:  edit the header in index.html, then run   python sync_nav.py
The generators (gen_blog.py, gen_features.py, gen_locations.py) call apply_nav() on
their output, so regenerated pages keep the current header too.
"""
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE = ROOT / "index.html"
CSS_ID = "nav-sync-css"

ROOT_PAGES = ["404.html", "about.html", "book.html", "contact.html", "faq.html", "how.html",
              "locations.html", "pricing.html", "privacy.html", "terms.html", "work.html"]
SUB_DIRS = ["features", "locations", "blog"]

NAV_SELECTOR = re.compile(r"\.(?:nav|brand|mnav|mega|m2-|mx-|ix-|m3-)|btn-tc")
BTN_SELECTOR = re.compile(r"^\.btn(?:-gold|-line|-tc)?(?::hover)?(?:\s+\.arr)?$")


# ---------------------------------------------------------------- extraction

def _matching_div(html, start):
    """Index just past the </div> that closes the <div ...> opening at `start`."""
    i, depth = start, 0
    while True:
        o, c = html.find("<div", i), html.find("</div>", i)
        if c == -1:
            raise ValueError("unbalanced <div> after index %d" % start)
        if o != -1 and o < c:
            depth += 1
            i = o + 4
        else:
            depth -= 1
            i = c + 6
            if depth == 0:
                return i


def _header_span(html):
    s = html.index('<header class="nav">')
    return s, html.index("</header>", s) + len("</header>")


def _mnav_span(html):
    s = html.index('<div class="mnav" id="mnav"')
    return s, _matching_div(html, s)


def _split_css(css):
    """Split a stylesheet into top-level statements (rules and @-blocks)."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(css):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append(css[start:i + 1].strip())
                start = i + 1
    return [s for s in out if s]


def _scope_btn(rule):
    sel, body = rule.split("{", 1)
    sels = [s.strip() for s in sel.split(",")]
    if not all(BTN_SELECTOR.match(s) for s in sels):
        return None
    return ",".join(f".nav {s},.mnav {s}" for s in sels) + "{" + body


def _nav_css(index_html):
    style = max(re.findall(r"<style>(.*?)</style>", index_html, re.S), key=lambda s: s.count(".nav"))
    style = re.sub(r"/\*.*?\*/", "", style, flags=re.S)
    keep = []
    root = re.search(r":root\{(.*?)\}", style, re.S)
    if root:  # the header's own copy of the palette, so pages with other :root values still match
        keep.append(".nav,.mnav{" + " ".join(root.group(1).split()) + "}")
    for st in _split_css(style):
        if st.startswith("@font-face"):
            if "Plus Jakarta Sans" in st:
                keep.append(st)
        elif st.startswith("@media"):
            head, inner = st.split("{", 1)
            rules = [r for r in _split_css(inner[:-1]) if NAV_SELECTOR.search(r.split("{", 1)[0])]
            if rules:
                keep.append(head.strip() + "{" + "".join(rules) + "}")
        elif st.startswith("@"):
            continue
        else:
            # header buttons are scoped to .nav/.mnav so page buttons are untouched; .btn-tc is
            # scoped too, otherwise the scoped .btn rules would outrank it
            scoped = _scope_btn(st)
            if scoped:
                keep.append(scoped)
            elif st.startswith(".wrap{"):  # header uses the homepage's container padding on every page
                keep.append(".nav " + st)
            elif NAV_SELECTOR.search(st.split("{", 1)[0]):
                keep.append(st)
    return "\n".join(keep)


@lru_cache(maxsize=1)
def _source():
    html = SOURCE.read_text(encoding="utf-8").replace("\r\n", "\n")
    hs, he = _header_span(html)
    ms, me = _mnav_span(html)
    return html[hs:he], html[ms:me], _nav_css(html)


# ---------------------------------------------------------------- per-page

def _relink(block, depth):
    pre = "../" * depth

    def fix(m):
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if url.startswith(("http:", "https:", "/", "mailto:", "tel:", "data:")):
            return m.group(0)
        if url.startswith("#"):
            url = "index.html" + url
        return f"{attr}={q}{pre}{url}{q}"

    return re.sub(r'(href|src)=(["\'])([^"\']*)\2', fix, block)


def _mark_active(header, page):
    if page == "pricing.html":
        header = header.replace('<a href="pricing.html">Pricing</a>', '<a href="pricing.html" class="on">Pricing</a>', 1)
    return header


def apply_nav(html, depth=0, page=None):
    """Return `html` with the header, mobile menu and nav CSS replaced by index.html's."""
    header, mnav, css = _source()
    nl = "\r\n" if "\r\n" in html else "\n"
    header = _mark_active(_relink(header, depth), page)
    mnav = _relink(mnav, depth)

    def fit(block):
        return block.replace("\r\n", "\n").replace("\n", nl)

    hs, he = _header_span(html)
    html = html[:hs] + fit(header) + html[he:]
    ms, me = _mnav_span(html)
    html = html[:ms] + fit(mnav) + html[me:]

    tag = f'<style id="{CSS_ID}">{nl}{fit(css)}{nl}</style>'
    existing = re.search(r'<style id="%s">.*?</style>' % CSS_ID, html, re.S)
    if existing:
        html = html[:existing.start()] + tag + html[existing.end():]
    else:
        i = html.index("</head>")
        html = html[:i] + tag + nl + html[i:]
    assert "\r\r\n" not in html
    return html


def pages():
    for name in ROOT_PAGES:
        yield ROOT / name, 0
    for d in SUB_DIRS:
        for p in sorted((ROOT / d).glob("*.html")):
            yield p, 1


def main():
    changed = 0
    for path, depth in pages():
        with open(path, encoding="utf-8", newline="") as f:
            old = f.read()
        new = apply_nav(old, depth, path.name if depth == 0 else None)
        if new != old:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            changed += 1
            print("synced ", path.relative_to(ROOT).as_posix())
        else:
            print("current", path.relative_to(ROOT).as_posix())
    print(f"{changed} page(s) updated")


if __name__ == "__main__":
    main()
