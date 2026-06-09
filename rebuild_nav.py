# -*- coding: utf-8 -*-
"""Rebuild the Locations dropdown (desktop) and Locations panel (mobile)
in the main pages, sourced from CITIES in gen_locations.

Idempotent: replaces the existing blocks in place via well-known anchors
(<!-- LOCATIONS_DROPDOWN_INJECTED --> for the dropdown, the
<aside class="nav-mobile-locations"> for the slide-in panel). Safe to
re-run any time CITIES changes.

This supersedes update_main_nav.py, which was a one-time injector.
"""

from __future__ import annotations
import re
from pathlib import Path

from gen_locations import CITIES, mobile_loc_provinces_html

ROOT = Path(__file__).parent
MAIN_PAGES = [
    "index.html", "about.html", "work.html", "how.html", "pricing.html",
    "faq.html", "contact.html", "privacy.html", "terms.html",
]
SENTINEL = "<!-- LOCATIONS_DROPDOWN_INJECTED -->"


def desktop_dropdown_block(indent: str = "            ") -> str:
    """Sentinel-led dropdown block. First line has no leading indent so
    callers can drop it in at the position of the existing sentinel
    (which already sits at the file's natural indent)."""
    lines = [SENTINEL]
    lines.append(indent + '<div class="nav-dd">')
    lines.append(indent + '    <button type="button" class="nav-dd-trigger" aria-haspopup="true" aria-expanded="false">Locations</button>')
    lines.append(indent + '    <ul class="nav-dd-panel">')
    for prov, abbr, cities in CITIES:
        lines.append(indent + '        <li>')
        lines.append(indent + f'            <a href="locations.html#{abbr.lower()}">{prov}</a>')
        lines.append(indent + '            <ul class="nav-dd-sub">')
        for slug, name, _intro in cities:
            lines.append(indent + f'                <li><a href="locations/{slug}.html">{name}</a></li>')
        lines.append(indent + '            </ul>')
        lines.append(indent + '        </li>')
    lines.append(indent + '    </ul>')
    lines.append(indent + '</div>')
    return "\n".join(lines)


def mobile_locations_aside() -> str:
    return (
        '<aside class="nav-mobile-locations" id="nav-mobile-locations" aria-label="Locations menu" aria-hidden="true">\n'
        '    <button type="button" class="nm-loc-back" aria-label="Back to main menu">\n'
        '        <span class="nm-loc-back-arrow" aria-hidden="true">←</span>\n'
        '        <span class="nm-loc-back-label">Back</span>\n'
        '    </button>\n'
        '    <div class="nm-loc-content">\n'
        '        <p class="eyebrow">Locations</p>\n'
        '        <h2 class="nm-loc-h">Web designer <em>across Alberta.</em></h2>\n'
        f'{mobile_loc_provinces_html("locations/")}\n'
        '        <a href="locations.html" class="nm-loc-all-link">See all locations <span class="arrow">→</span></a>\n'
        '    </div>\n'
        '</aside>'
    )


def rebuild(file_path: Path) -> tuple[bool, bool]:
    text = file_path.read_text(encoding="utf-8")
    changed_dd = False
    changed_panel = False

    if SENTINEL in text:
        # Replace from sentinel through first </div>. The dropdown block
        # contains no nested <div>, so this is unambiguous.
        new_block = desktop_dropdown_block()
        new_text = re.sub(
            re.escape(SENTINEL) + r"[\s\S]*?</div>",
            lambda _m: new_block,
            text,
            count=1,
        )
        if new_text != text:
            text = new_text
            changed_dd = True

    if '<aside class="nav-mobile-locations"' in text:
        new_aside = mobile_locations_aside()
        new_text = re.sub(
            r'<aside class="nav-mobile-locations"[\s\S]*?</aside>',
            lambda _m: new_aside,
            text,
            count=1,
        )
        if new_text != text:
            text = new_text
            changed_panel = True

    if changed_dd or changed_panel:
        file_path.write_text(text, encoding="utf-8")
    return changed_dd, changed_panel


def main() -> None:
    for name in MAIN_PAGES:
        p = ROOT / name
        if not p.exists():
            print(f"  skip (missing): {name}")
            continue
        dd, panel = rebuild(p)
        flags = []
        if dd: flags.append("dropdown")
        if panel: flags.append("mobile-panel")
        print(f"  {name}: {', '.join(flags) if flags else 'unchanged'}")


if __name__ == "__main__":
    main()
