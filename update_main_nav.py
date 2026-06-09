# -*- coding: utf-8 -*-
"""Inject the Locations dropdown into the 9 main pages.

Idempotent: skips files where the dropdown is already present.
"""

from __future__ import annotations
from pathlib import Path
from gen_locations import CITIES

ROOT = Path(__file__).parent
MAIN_PAGES = [
    "index.html", "about.html", "work.html", "how.html", "pricing.html",
    "faq.html", "contact.html", "privacy.html", "terms.html",
]

SENTINEL = "<!-- LOCATIONS_DROPDOWN_INJECTED -->"


# ---------------------------------------------------------------------------
# Pieces to inject
# ---------------------------------------------------------------------------

def desktop_dropdown_html(indent: str = "            ") -> str:
    out = []
    out.append(f"{SENTINEL}")
    out.append(f'<div class="nav-dd">')
    out.append(f'    <button type="button" class="nav-dd-trigger" aria-haspopup="true" aria-expanded="false">Locations</button>')
    out.append(f'    <ul class="nav-dd-panel">')
    for prov, abbr, cities in CITIES:
        out.append(f'        <li>')
        out.append(f'            <a href="locations.html#{abbr.lower()}">{prov}</a>')
        out.append(f'            <ul class="nav-dd-sub">')
        for slug, name, _intro in cities:
            out.append(f'                <li><a href="locations/{slug}.html">{name}</a></li>')
        out.append(f'            </ul>')
        out.append(f'        </li>')
    out.append(f'    </ul>')
    out.append(f'</div>')
    return "\n".join(indent + line if line.strip() else line for line in out)


DROPDOWN_CSS = """
    /* === LOCATIONS DROPDOWN === */
    .nav-links { position: relative; }
    .nav-dd { position: relative; display: inline-flex; align-items: center; }
    .nav-dd-trigger {
        font-size: 14px;
        color: var(--ink-2);
        position: relative;
        padding: 4px 0;
        background: none;
        border: none;
        font-family: inherit;
        cursor: pointer;
        transition: color 200ms ease;
    }
    .nav-dd-trigger::after {
        content: "";
        position: absolute;
        left: -4px; right: -4px; bottom: -8px;
        height: 9px;
        background-image: url("img/brush-underline.png");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 100% 100%;
        transform: scaleX(0);
        transform-origin: right;
        transition: transform 360ms cubic-bezier(.2,.7,.2,1);
    }
    .nav-dd:hover > .nav-dd-trigger { color: var(--ink); }
    .nav-dd:hover > .nav-dd-trigger::after {
        transform: scaleX(1); transform-origin: left;
    }
    .nav-dd-panel {
        position: absolute;
        top: 100%;
        right: 0;
        background: var(--paper);
        background-clip: padding-box;
        border: 1px solid var(--rule);
        box-shadow: 0 24px 56px -28px rgba(19,22,19,0.32);
        padding: 14px 0;
        min-width: 240px;
        list-style: none;
        margin: 0;
        margin-top: 14px;
        opacity: 0;
        pointer-events: none;
        transform: translateY(-4px);
        transition: opacity 200ms ease 80ms, transform 220ms cubic-bezier(.2,.7,.2,1) 80ms;
        z-index: 60;
    }
    /* Invisible bridge so the cursor can cross the 14px gap between the
       trigger and the panel without losing :hover state. */
    .nav-dd-panel::before {
        content: "";
        position: absolute;
        left: 0; right: 0;
        top: -16px; height: 16px;
    }
    .nav-dd:hover > .nav-dd-panel,
    .nav-dd:focus-within > .nav-dd-panel {
        opacity: 1; pointer-events: auto; transform: translateY(0);
    }
    .nav-dd-panel li { position: relative; list-style: none; }
    .nav-dd-panel > li > a {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 9px 22px;
        font-size: 13.5px;
        color: var(--ink-2);
        font-family: var(--sans);
        transition: background 160ms ease, color 160ms ease;
    }
    .nav-dd-panel > li > a::after {
        content: "›";
        font-size: 18px;
        color: var(--ink-3);
        margin-left: 16px;
        transition: transform 200ms ease, color 200ms ease;
    }
    .nav-dd-panel > li:hover > a {
        background: color-mix(in oklch, var(--ink) 6%, transparent);
        color: var(--ink);
    }
    .nav-dd-panel > li:hover > a::after { transform: translateX(3px); color: var(--rust); }

    .nav-dd-sub {
        position: absolute;
        top: -14px;
        left: 100%;
        min-width: 220px;
        list-style: none;
        margin: 0;
        background: var(--paper);
        border: 1px solid var(--rule);
        box-shadow: 0 24px 56px -28px rgba(19,22,19,0.32);
        padding: 14px 0;
        opacity: 0;
        pointer-events: none;
        transform: translateX(-4px);
        transition: opacity 200ms ease 80ms, transform 220ms cubic-bezier(.2,.7,.2,1) 80ms;
    }
    /* Bridge so the cursor can move from a province li into its sub-panel
       without losing :hover state. */
    .nav-dd-panel > li::after {
        content: "";
        position: absolute;
        top: 0; bottom: 0;
        right: -8px; width: 8px;
        pointer-events: none;
    }
    .nav-dd-panel > li:hover::after { pointer-events: auto; }
    .nav-dd-panel > li:hover > .nav-dd-sub,
    .nav-dd-panel > li:focus-within > .nav-dd-sub {
        opacity: 1; pointer-events: auto; transform: translateX(0);
    }
    .nav-dd-sub a {
        display: block;
        padding: 7px 22px;
        font-size: 13px;
        color: var(--ink-2);
        transition: background 140ms ease, color 140ms ease;
    }
    .nav-dd-sub a:hover {
        background: color-mix(in oklch, var(--ink) 6%, transparent);
        color: var(--ink);
    }

    @media (max-width: 1100px) {
        .nav-dd-panel { right: auto; left: 0; }
    }
    @media (max-width: 760px) {
        .nav-dd { display: none; }
    }
    /* === END LOCATIONS DROPDOWN === */
"""


# ---------------------------------------------------------------------------
# Updaters
# ---------------------------------------------------------------------------

def inject(file_path: Path) -> bool:
    text = file_path.read_text(encoding="utf-8")
    if SENTINEL in text:
        return False  # already injected

    # 1. Inject dropdown CSS just before .nav-cta block.
    needle_css = "    .nav-cta {"
    if needle_css in text:
        text = text.replace(needle_css, DROPDOWN_CSS + "\n" + needle_css, 1)

    # 2. Insert desktop dropdown HTML before the Contact link in nav-links.
    #    Match the exact line `<a href="contact.html">Contact</a>` indented within nav-links.
    desktop_anchor = '            <a href="contact.html">Contact</a>'
    if desktop_anchor in text:
        text = text.replace(
            desktop_anchor,
            desktop_dropdown_html() + "\n" + desktop_anchor,
            1,
        )
    else:
        # some pages have different indentation
        alt = '<a href="contact.html">Contact</a>'
        # do not double-touch — only do the first occurrence inside primary nav
        # to be safe, fall back skipped
        pass

    # 3. Insert Locations into mobile nav.
    mobile_anchor = '<li><a href="contact.html">Contact</a></li>'
    if mobile_anchor in text:
        text = text.replace(
            mobile_anchor,
            '<li><a href="locations.html">Locations</a></li>\n        ' + mobile_anchor,
            1,
        )

    # 4. Insert "All locations" into footer Site list (before Contact link).
    footer_anchor = '<li><a href="contact.html">Contact</a></li>'
    # already replaced once for mobile; do a second replacement for footer.
    # Now there is exactly one remaining occurrence (the footer one) — insert before it.
    if footer_anchor in text:
        text = text.replace(
            footer_anchor,
            '<li><a href="locations.html">All locations</a></li>\n                    ' + footer_anchor,
            1,
        )

    file_path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    for name in MAIN_PAGES:
        p = ROOT / name
        if not p.exists():
            print(f"  skip (missing): {name}")
            continue
        changed = inject(p)
        print(f"  {'updated' if changed else 'already done'}: {name}")


if __name__ == "__main__":
    main()
