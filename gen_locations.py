# -*- coding: utf-8 -*-
"""Generate SEO-optimized Canadian-city landing pages for matthewmcguire.ca.

Each page targets the high-intent local keyword pattern "[city] web designer"
with a keyword-targeted title/H1/H2 hierarchy, ~1000 words of body, an FAQ
block (FAQPage schema), and internal links to nearby cities.

Run from the my-site directory:  python gen_locations.py
Outputs:
  - locations/<slug>.html   (55 pages)
  - locations.html          (index page grouping cities by province)
  - sitemap.xml             (regenerated with all city URLs)
"""

from __future__ import annotations
import json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
OUT = ROOT / "locations"
OUT.mkdir(exist_ok=True)

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
         "Edmonton is home base — the studio works out of here, and most of my clients are firms within an hour's drive of downtown. From Whyte Avenue lawyers to clinics in Sherwood Park to CPAs in St. Albert, I build websites for the kinds of small Edmonton-area practices that can't justify a $15,000 agency build but still need a presence that does justice to their work."),
        ("calgary", "Calgary",
         "Calgary's professional-services market moves fast. A modern, hand-coded site sets the right tone with clients researching counsel from Mission, Beltline, or one of the suburban office parks. I work with Calgary law firms, accounting practices, and consultancies remotely — every build, edit round, and hosting handover happens online, with no in-person discovery call required."),
        ("st-albert", "St. Albert",
         "St. Albert is a quiet, prosperous suburb full of two- and three-person professional practices — family lawyers, dental clinics, financial planners. Most of these firms are too small to bother with a Toronto agency, but their clients still expect a website that looks like 2026. That's the gap I'm built for."),
        ("sherwood-park", "Sherwood Park",
         "Sherwood Park has one of the densest concentrations of small professional firms in Alberta. Strathcona County clinics, Baseline Road lawyers, and accountants serving the industrial corridor all need the same thing: a credible website without an enterprise build budget. $0 down, $199 a month, everything included."),
        ("red-deer", "Red Deer",
         "Red Deer firms serve a regional client base stretching from Olds to Lacombe, and that reach deserves a website that works as hard as the practice does. I build for central Alberta lawyers, CPAs, and clinics remotely — discovery happens over email, design happens in the browser, and your firm's site goes live without anyone having to drive Highway 2."),
        ("lethbridge", "Lethbridge",
         "Lethbridge is a university town with a professional-services backbone — agriculture lawyers, regional accounting practices, family clinics. The studio works with southern Alberta firms the same way it works with everyone: clear pricing, hand-coded sites, and an ongoing relationship that doesn't disappear after launch."),
        ("medicine-hat", "Medicine Hat",
         "Medicine Hat firms serve clients across the southeast — Brooks, Redcliff, the Hutterite colonies, the Saskatchewan border towns. The website should communicate that range without feeling like a template. Every Medicine Hat build is custom-designed and coded by hand, then handed back to you with hosting included."),
        ("fort-mcmurray", "Fort McMurray",
         "Fort McMurray firms work with a workforce that's half rotational, half rooted — and a website needs to communicate to both. Most of my Fort Mac clients are professional-services practices serving the camps and the community: family lawyers, accounting firms, medical clinics. The remote workflow suits the city well."),
        ("camrose", "Camrose",
         "Camrose is a small city with a disproportionately strong professional-services base — Augustana spillover, regional law and accounting practices, agricultural consultancies. I build the kind of website that travels well: looks credible to a client three hours away, edits cleanly when the firm grows, and doesn't require a marketing manager to maintain."),
        ("wetaskiwin", "Wetaskiwin",
         "Wetaskiwin is one of those Alberta cities where the firms are smaller than the work they do — solo lawyers handling estate files, two-person accounting practices, family clinics serving generations of patients. A modern website signals to younger clients that the firm has moved with the times. That's what the studio is for."),
        ("leduc", "Leduc",
         "Leduc firms serve a corridor that's exploded in the last decade — international airport workers, Nisku industry, Beaumont commuters. A website needs to communicate to all of them at once. The studio builds clean, fast, mobile-first sites that load on a phone in a parking lot just as well as on a desk in a downtown office."),
        ("grande-prairie", "Grande Prairie",
         "Grande Prairie is the professional hub for the Peace Country, which means firms here serve clients from Beaverlodge to Fairview to the BC border. A website should reflect that reach without overcomplicating the message. I work with GP practices remotely — every build, every edit, every conversation happens online."),
        ("spruce-grove", "Spruce Grove",
         "Spruce Grove and Stony Plain together form one of the fastest-growing professional markets in the Edmonton region. I build for the small firms that are growing into that market — family lawyers expanding to two associates, CPAs adding a junior, clinics opening a second location. The $199/month plan grows with the practice."),
        ("airdrie", "Airdrie",
         "Airdrie has tripled in population in twenty years, and the professional-services market is still catching up. Most Airdrie firms are bootstrapping — solo lawyers, single-CPA practices, two-doctor clinics. A custom website without an enterprise budget is exactly the gap the studio fills."),
    ]),
    ("British Columbia", "BC", [
        ("vancouver", "Vancouver",
         "Vancouver's professional-services market is one of the most design-aware in the country, which means a generic Squarespace template gets noticed for the wrong reasons. The studio builds hand-coded sites for boutique Vancouver firms that want their website to read at the level of their work — without paying $20,000 for a downtown agency build."),
        ("victoria", "Victoria",
         "Victoria firms serve a clientele that values craft — government workers, retirees with assets, established Island families. A website should feel as considered as the practice. Every Victoria build is custom-designed for the firm, hand-coded, and hosted on infrastructure that loads in under a second from the Inner Harbour."),
        ("surrey", "Surrey",
         "Surrey's professional-services market is multilingual, multicultural, and one of the fastest-growing in BC. The studio builds sites that communicate clearly across that diversity — no jargon, no template clichés, just clear copy and a design that respects the firm's clientele."),
        ("burnaby", "Burnaby",
         "Burnaby sits between Vancouver's design expectations and the suburban firms growing along the SkyTrain line. Whatever side of that divide your practice is on, the studio builds the same way: hand-coded, custom-designed, $0 down and $199 a month all-inclusive."),
        ("kelowna", "Kelowna",
         "Kelowna is now a serious professional-services market — Okanagan lawyers, CPAs serving wineries and orchards, clinics handling a steady stream of new residents. A modern website tells incoming clients the firm is part of where the city is going, not where it was twenty years ago."),
        ("nanaimo", "Nanaimo",
         "Nanaimo firms serve a corridor running from Cobble Hill to Campbell River, and the website should travel as well as the practice does. I build clean, fast sites that work for clients researching from a ferry, a coffee shop, or a kitchen table. The remote workflow suits Island firms well."),
        ("kamloops", "Kamloops",
         "Kamloops is the regional hub for the BC Interior — TRU, the railway, professional firms serving the entire Thompson-Nicola region. A custom site without an enterprise build budget is exactly the kind of work the studio is built for."),
        ("abbotsford", "Abbotsford",
         "Abbotsford and the Fraser Valley are full of established family firms — multi-generation farms, second-generation lawyers, accounting practices that have served the same clients for thirty years. A modern website signals to the next generation of clients that the firm has kept pace, without abandoning what made it work."),
    ]),
    ("Saskatchewan", "SK", [
        ("saskatoon", "Saskatoon",
         "Saskatoon firms serve a province-wide professional network — University of Saskatchewan spillover, downtown lawyers, regional accounting practices, family clinics. The studio builds custom-coded websites that communicate the practice's actual character, not a template's idea of what a 'professional services site' looks like."),
        ("regina", "Regina",
         "Regina is Saskatchewan's government and legal hub, which means the firms here are used to communicating clearly and without fluff. The studio's design language matches that: editorial typography, restrained colour, and copy that says exactly what the firm does. $0 down, $199 a month, everything included."),
        ("prince-albert", "Prince Albert",
         "Prince Albert firms serve clients across the northern half of the province — communities most national agencies forget exist. A custom website signals to those clients that the firm is investing in how it presents itself. That's what the studio does."),
        ("moose-jaw", "Moose Jaw",
         "Moose Jaw is a small city with a deep professional-services base — military, corrections, healthcare, established family firms. The studio works with Moose Jaw practices remotely, the same way it works with Edmonton or Calgary. The location of the firm doesn't change the build."),
    ]),
    ("Manitoba", "MB", [
        ("winnipeg", "Winnipeg",
         "Winnipeg firms serve a clientele that's seen plenty of agency work and plenty of bad templates. A hand-coded, editorial-quality site stands out in that market without trying too hard. I work with Winnipeg lawyers, CPAs, and clinics remotely — the discovery, design, and launch all happen online."),
        ("brandon", "Brandon",
         "Brandon firms serve the southwestern corner of the province, which means clients are spread across hundreds of kilometres of farmland. A fast, mobile-first website is non-negotiable. Every build the studio ships is hand-coded, optimized, and fast enough to load on a tractor cab phone."),
        ("steinbach", "Steinbach",
         "Steinbach is one of Canada's fastest-growing small cities, with a professional-services market expanding to match. The studio builds for the firms growing into that market — solo lawyers adding partners, family CPAs hiring juniors, clinics opening second locations. The $199/month plan scales with the practice."),
    ]),
    ("Ontario", "ON", [
        ("toronto", "Toronto",
         "Toronto's professional-services market expects polish. The studio's editorial design language — Playfair Display headlines, restrained colour, careful typography — was built with downtown firms in mind. Every Toronto build is hand-coded, custom-designed, and lives at $0 down with $199 a month covering hosting, edits, and support."),
        ("ottawa", "Ottawa",
         "Ottawa firms serve government clients, federal regulators, and a professional-class clientele that notices when a website looks like a 2014 template. The studio builds custom sites that read at the level of the work — for boutique law firms, consultancies, and clinics across the National Capital Region."),
        ("hamilton", "Hamilton",
         "Hamilton's professional-services market has been transformed by the last fifteen years of Toronto spillover. Mid-size firms are hiring, growing, and rebranding. A modern website is part of that — and the studio builds the kind of custom site that signals the firm has joined the new Hamilton, without losing sight of the old one."),
        ("london", "London",
         "London firms serve a corridor running from Sarnia to Woodstock, and a website needs to work for clients across that whole range. I build clean, hand-coded sites for southwestern Ontario law firms, accounting practices, and clinics — $0 down, $199 a month, everything included for as long as you stay."),
        ("kitchener", "Kitchener",
         "Kitchener-Waterloo's professional-services firms work alongside one of the most tech-aware client bases in Canada. Templates get noticed. The studio builds custom-coded sites for KW law firms, CPAs, and clinics — sites that load fast, look considered, and signal the firm is serious about its presence."),
        ("mississauga", "Mississauga",
         "Mississauga is a professional-services market that's outgrown 'suburb of Toronto' as a description. The firms here are full-service, multi-generational, and competing for the same clients as downtown practices. A custom website is part of that competitive position — and the studio builds it without the downtown agency price tag."),
        ("brampton", "Brampton",
         "Brampton's professional-services market is multilingual, multicultural, and one of the fastest-growing in the GTA. The studio builds websites that communicate clearly across that diversity — no agency jargon, no template clichés, just clear copy and a design that respects the firm's clientele."),
        ("windsor", "Windsor",
         "Windsor firms serve a cross-border professional clientele — Detroit business, automotive, healthcare. A website needs to read credibly to clients on either side of the river. The studio builds Windsor sites the same way it builds everywhere else: hand-coded, custom-designed, hosted, and supported on a $199-a-month plan."),
        ("kingston", "Kingston",
         "Kingston is a small professional city with disproportionately strong legal, medical, and academic firms. The clients these practices serve — Queen's faculty, military, government workers — notice when a website looks considered. That's what the studio builds."),
        ("sudbury", "Sudbury",
         "Sudbury firms serve a vast Northeastern Ontario clientele, and a website is often the first impression a client three hours away ever gets. The studio builds custom sites that load fast, read clearly, and represent the practice as well in Timmins as they do in downtown Sudbury."),
    ]),
    ("Quebec", "QC", [
        ("montreal", "Montreal",
         "Montreal's professional-services market is bilingual, design-aware, and one of the most discerning in Canada. The studio builds English-language and bilingual sites for Montreal law firms, consultancies, and clinics — hand-coded, editorial in feel, and priced at $0 down with $199 a month covering hosting and edits."),
        ("quebec-city", "Quebec City",
         "Quebec City firms serve a francophone professional clientele that values craft and continuity — and a website should feel that way too. The studio builds bilingual sites for Quebec City practices remotely, with the same design discipline and pricing model as every other build."),
        ("gatineau", "Gatineau",
         "Gatineau firms serve a cross-river professional market, with clients on both sides of the Ottawa River. A bilingual, fast-loading, custom-coded site is non-negotiable. The studio builds Gatineau sites at $0 down, $199 a month, everything included."),
        ("sherbrooke", "Sherbrooke",
         "Sherbrooke is the regional professional hub for the Eastern Townships, with firms serving a mix of francophone, anglophone, and cross-border clients. A custom website that handles that range without feeling generic is exactly what the studio is built to deliver."),
        ("trois-rivieres", "Trois-Rivières",
         "Trois-Rivières firms serve a regional professional clientele between Montreal and Quebec City — manufacturing, healthcare, family law, accounting. A modern, hand-coded website signals to that clientele that the practice has kept pace with the rest of the corridor."),
    ]),
    ("New Brunswick", "NB", [
        ("moncton", "Moncton",
         "Moncton firms serve a bilingual Maritime clientele, and a website needs to work in English, French, and across three provinces. The studio builds custom sites for Moncton practices remotely — every build is hand-coded, fast, and priced at $0 down with $199 a month all-inclusive."),
        ("saint-john", "Saint John",
         "Saint John is one of New Brunswick's oldest professional-services markets — multi-generation law firms, established CPAs, family clinics. A modern website signals to the next generation of clients that the practice has moved with the times, without losing what made it work for the previous generation."),
        ("fredericton", "Fredericton",
         "Fredericton firms serve a government, university, and professional clientele used to clean, considered design. The studio builds custom-coded sites that read at the level of the work — for boutique New Brunswick law firms, consultancies, and clinics."),
    ]),
    ("Nova Scotia", "NS", [
        ("halifax", "Halifax",
         "Halifax's professional-services market is the design-aware hub of Atlantic Canada, and templates get noticed in the wrong way. The studio builds custom-coded, editorial-quality sites for Halifax law firms, CPAs, and clinics — hand-built, hosted, and supported at $0 down and $199 a month."),
        ("dartmouth", "Dartmouth",
         "Dartmouth firms work alongside Halifax's professional-services market while serving their own communities — a website should communicate that local rootedness without feeling provincial. The studio builds Dartmouth sites the same way it builds everywhere else: custom-designed, hand-coded, and priced honestly."),
    ]),
    ("Prince Edward Island", "PE", [
        ("charlottetown", "Charlottetown",
         "Charlottetown firms serve an Island-wide professional clientele — generations-deep family law practices, regional CPAs, family clinics. A modern, hand-coded website signals that the practice has invested in how it presents to clients, without losing the small-Island character that made it work in the first place."),
    ]),
    ("Newfoundland and Labrador", "NL", [
        ("st-johns", "St. John's",
         "St. John's firms serve a Newfoundland-wide professional clientele, often from a single downtown office. A custom website is the studio's specialty — hand-coded, fast, and hosted on infrastructure that loads quickly even on rural Newfoundland connections."),
        ("corner-brook", "Corner Brook",
         "Corner Brook firms serve western Newfoundland from one of the province's two regional professional hubs. The studio builds Corner Brook sites the same way it builds everywhere else: custom-designed, hand-coded, $0 down, $199 a month all-inclusive."),
    ]),
    ("Yukon", "YT", [
        ("whitehorse", "Whitehorse",
         "Whitehorse firms serve a Yukon-wide professional clientele, often as the only practice of their kind in the territory. A custom website is non-negotiable — and the studio builds it without forcing northern firms to fly south for a discovery call. Every build, edit, and conversation happens online."),
    ]),
    ("Northwest Territories", "NT", [
        ("yellowknife", "Yellowknife",
         "Yellowknife firms serve a vast NWT clientele, often as the only specialist practice within hundreds of kilometres. A hand-coded, fast-loading site is essential — and the studio's remote workflow means a Yellowknife firm can launch a new website without anyone leaving the territory."),
    ]),
    ("Nunavut", "NU", [
        ("iqaluit", "Iqaluit",
         "Iqaluit firms serve a Nunavut-wide professional clientele, with logistical realities that no national agency understands. The studio builds remotely for Iqaluit practices — hand-coded sites, fast hosting, and a $199-a-month plan that covers everything for as long as you stay."),
    ]),
]

# Per-city extras: areas served, nearby city slugs.
# `areas` is a one-line phrase that gets dropped into "across {areas}".
# `nearby` is a list of slugs (must exist elsewhere in CITIES).
EXTRAS: dict[str, dict] = {
    "edmonton":       {"areas": "downtown, Whyte Avenue, the west end, St. Albert, Sherwood Park, and the surrounding capital region", "nearby": ["st-albert", "sherwood-park", "leduc"]},
    "calgary":        {"areas": "downtown, the Beltline, Mission, Kensington, and the suburban office parks of Mahogany, Tuscany, and Auburn Bay", "nearby": ["airdrie", "red-deer", "lethbridge"]},
    "st-albert":      {"areas": "downtown St. Albert, Erin Ridge, Mission, and the Sturgeon County edge", "nearby": ["edmonton", "sherwood-park", "spruce-grove"]},
    "sherwood-park":  {"areas": "Baseline Road, Sherwood Drive, Centre in the Park, and Strathcona County's industrial corridor", "nearby": ["edmonton", "st-albert", "camrose"]},
    "red-deer":       {"areas": "downtown, Riverside, Oriole Park, and the QE2 corridor stretching to Penhold and Innisfail", "nearby": ["calgary", "edmonton", "camrose"]},
    "lethbridge":     {"areas": "downtown, the University, and the agricultural belt around Coaldale and Coalhurst", "nearby": ["medicine-hat", "calgary", "red-deer"]},
    "medicine-hat":   {"areas": "downtown, the Flats, Crescent Heights, and the southeast Alberta border country", "nearby": ["lethbridge", "calgary", "moose-jaw"]},
    "fort-mcmurray":  {"areas": "downtown, Thickwood, Timberlea, and the regional camps", "nearby": ["edmonton", "grande-prairie", "red-deer"]},
    "camrose":        {"areas": "downtown Camrose, Augustana, and the Beaver County region", "nearby": ["edmonton", "wetaskiwin", "red-deer"]},
    "wetaskiwin":     {"areas": "downtown, Millet, Pigeon Lake, and the Highway 13 corridor", "nearby": ["edmonton", "camrose", "leduc"]},
    "leduc":          {"areas": "downtown Leduc, Nisku, Beaumont, and the airport corridor", "nearby": ["edmonton", "wetaskiwin", "spruce-grove"]},
    "grande-prairie": {"areas": "downtown, Hillside, Beaverlodge, and the Peace Country region stretching to Dawson Creek", "nearby": ["edmonton", "fort-mcmurray", "red-deer"]},
    "spruce-grove":   {"areas": "Spruce Grove proper, Stony Plain, Parkland County, and the western Edmonton region", "nearby": ["edmonton", "st-albert", "leduc"]},
    "airdrie":        {"areas": "downtown, Bayside, the QE2 corridor, and the bedroom communities north of Calgary", "nearby": ["calgary", "red-deer", "edmonton"]},

    "vancouver":      {"areas": "downtown, Yaletown, Kitsilano, Mount Pleasant, and the surrounding Lower Mainland", "nearby": ["burnaby", "surrey", "victoria"]},
    "victoria":       {"areas": "downtown, Oak Bay, Saanich, and the Inner Harbour", "nearby": ["vancouver", "nanaimo", "burnaby"]},
    "surrey":         {"areas": "Whalley, Newton, Cloverdale, South Surrey, and the Fraser River corridor", "nearby": ["vancouver", "burnaby", "abbotsford"]},
    "burnaby":        {"areas": "Metrotown, Brentwood, Burnaby Heights, and the SkyTrain spine", "nearby": ["vancouver", "surrey", "abbotsford"]},
    "kelowna":        {"areas": "downtown, Mission, Glenmore, and the Okanagan Lake region", "nearby": ["kamloops", "vancouver", "victoria"]},
    "nanaimo":        {"areas": "downtown, Departure Bay, Lantzville, and the central Island region", "nearby": ["victoria", "vancouver", "burnaby"]},
    "kamloops":       {"areas": "downtown, Sahali, Aberdeen, and the Thompson Valley", "nearby": ["kelowna", "vancouver", "abbotsford"]},
    "abbotsford":     {"areas": "downtown, Clearbrook, the Fraser Valley, and the corridor to Mission and Chilliwack", "nearby": ["surrey", "burnaby", "vancouver"]},

    "saskatoon":      {"areas": "downtown, the U of S district, Riversdale, and the Saskatchewan Valley", "nearby": ["regina", "prince-albert", "moose-jaw"]},
    "regina":         {"areas": "downtown, Cathedral, Lakeview, and the Wascana corridor", "nearby": ["saskatoon", "moose-jaw", "winnipeg"]},
    "prince-albert":  {"areas": "downtown, the West Hill, and the gateway to northern Saskatchewan", "nearby": ["saskatoon", "regina", "edmonton"]},
    "moose-jaw":      {"areas": "downtown, the Crescents, and the Trans-Canada corridor", "nearby": ["regina", "saskatoon", "medicine-hat"]},

    "winnipeg":       {"areas": "downtown, the Exchange District, Osborne Village, and the Manitoba capital region", "nearby": ["brandon", "steinbach", "regina"]},
    "brandon":        {"areas": "downtown, the BU campus, and the southwestern Manitoba region", "nearby": ["winnipeg", "saskatoon", "regina"]},
    "steinbach":      {"areas": "downtown, the Mennonite Heritage area, and the southeastern Manitoba region", "nearby": ["winnipeg", "brandon", "saskatoon"]},

    "toronto":        {"areas": "downtown, King West, Yorkville, Liberty Village, and the GTA from Mississauga to Markham", "nearby": ["mississauga", "brampton", "hamilton"]},
    "ottawa":         {"areas": "downtown, the ByWard Market, the Glebe, Westboro, and the National Capital Region", "nearby": ["kingston", "gatineau", "toronto"]},
    "hamilton":       {"areas": "downtown, Westdale, Stoney Creek, Ancaster, and the Niagara Escarpment region", "nearby": ["toronto", "mississauga", "kitchener"]},
    "london":         {"areas": "downtown, Old North, Wortley Village, and the Highway 401 corridor", "nearby": ["kitchener", "windsor", "hamilton"]},
    "kitchener":      {"areas": "downtown Kitchener, Uptown Waterloo, and the KW innovation corridor", "nearby": ["london", "hamilton", "toronto"]},
    "mississauga":    {"areas": "Port Credit, Streetsville, Square One, and the Lakeshore corridor", "nearby": ["toronto", "brampton", "hamilton"]},
    "brampton":       {"areas": "downtown, Heart Lake, Mount Pleasant, and the Peel Region", "nearby": ["mississauga", "toronto", "kitchener"]},
    "windsor":        {"areas": "downtown, Walkerville, Riverside, and the Detroit-Windsor corridor", "nearby": ["london", "kitchener", "toronto"]},
    "kingston":       {"areas": "downtown, the Queen's University district, Cataraqui, and the eastern Lake Ontario shore", "nearby": ["ottawa", "toronto", "kitchener"]},
    "sudbury":        {"areas": "downtown, the Donovan, New Sudbury, and Northeastern Ontario", "nearby": ["toronto", "ottawa", "kingston"]},

    "montreal":       {"areas": "downtown, the Plateau, Mile End, Old Montreal, and the West Island", "nearby": ["quebec-city", "sherbrooke", "trois-rivieres"]},
    "quebec-city":    {"areas": "Vieux-Québec, Saint-Roch, Sainte-Foy, and the Capitale-Nationale region", "nearby": ["montreal", "trois-rivieres", "sherbrooke"]},
    "gatineau":       {"areas": "downtown Hull, Aylmer, the Outaouais, and the Ottawa-Gatineau capital region", "nearby": ["ottawa", "montreal", "kingston"]},
    "sherbrooke":     {"areas": "downtown, the Université de Sherbrooke district, and the Estrie region", "nearby": ["montreal", "trois-rivieres", "quebec-city"]},
    "trois-rivieres": {"areas": "downtown, Cap-de-la-Madeleine, and the Mauricie region", "nearby": ["montreal", "quebec-city", "sherbrooke"]},

    "moncton":        {"areas": "downtown, Riverview, Dieppe, and the southeastern New Brunswick region", "nearby": ["saint-john", "fredericton", "halifax"]},
    "saint-john":     {"areas": "Uptown, the West Side, Rothesay, and the Bay of Fundy region", "nearby": ["moncton", "fredericton", "halifax"]},
    "fredericton":    {"areas": "downtown, the UNB district, and the central New Brunswick region", "nearby": ["moncton", "saint-john", "halifax"]},

    "halifax":        {"areas": "downtown, the South End, the North End, Bedford, and the Halifax Regional Municipality", "nearby": ["dartmouth", "moncton", "charlottetown"]},
    "dartmouth":      {"areas": "downtown, Cole Harbour, Burnside, and the Halifax-Dartmouth corridor", "nearby": ["halifax", "moncton", "charlottetown"]},

    "charlottetown":  {"areas": "downtown, Stratford, Cornwall, and the Island-wide region", "nearby": ["halifax", "moncton", "dartmouth"]},

    "st-johns":       {"areas": "downtown, Quidi Vidi, Mount Pearl, and the Avalon Peninsula", "nearby": ["corner-brook", "halifax", "moncton"]},
    "corner-brook":   {"areas": "downtown, Curling, and the Bay of Islands region", "nearby": ["st-johns", "halifax", "moncton"]},

    "whitehorse":     {"areas": "downtown, Riverdale, Porter Creek, and the Yukon-wide region", "nearby": ["yellowknife", "edmonton", "vancouver"]},
    "yellowknife":    {"areas": "downtown, Old Town, Frame Lake, and the NWT-wide region", "nearby": ["whitehorse", "edmonton", "iqaluit"]},
    "iqaluit":        {"areas": "downtown, Apex, and the Nunavut-wide region", "nearby": ["ottawa", "yellowknife", "halifax"]},
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
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<meta name="description" content="{meta_desc}" />

<link rel="canonical" href="https://matthewmcguire.ca/locations/{slug}.html" />
<link rel="icon" href="../mm-favicon.svg" type="image/svg+xml" />
<link rel="icon" href="../mm-favicon.png" />

<meta property="og:type" content="website" />
<meta property="og:url" content="https://matthewmcguire.ca/locations/{slug}.html" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{meta_desc}" />
<meta name="twitter:card" content="summary_large_image" />

<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500;1,600;1,700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />

<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-CR8009ZP6T"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {{ dataLayer.push(arguments); }}
    gtag('js', new Date());
    gtag('config', 'G-CR8009ZP6T');
</script>

<script type="application/ld+json">
{ld_json}
</script>

<style>
{styles}
</style>
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<div class="masthead">
    <div class="wrap masthead-inner">
        <span class="masthead-edition">Web Design Studio &middot; Edmonton</span>
        <span class="masthead-meta">Vol. I &middot; MMXXVI</span>
    </div>
</div>

<header class="nav" id="site-nav">
    <div class="wrap nav-inner">
        <a href="../index.html" class="nav-mark" aria-label="Matthew McGuire — home">
            <span class="nav-mark-letters">Matthew McGuire</span>
            <span class="nav-mark-name">Designer · developer</span>
        </a>
        <nav class="nav-links" aria-label="Primary">
            <a href="../index.html">Home</a>
            <a href="../about.html">About</a>
            <a href="../work.html">Work</a>
            <a href="../how.html">How I work</a>
            <a href="../pricing.html">Pricing</a>
{nav_dropdown_desktop}
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
        <li><a href="../about.html">About</a></li>
        <li><a href="../work.html">Work</a></li>
        <li><a href="../how.html">How I work</a></li>
        <li><a href="../pricing.html">Pricing</a></li>
        <li><button type="button" class="nm-loc-trigger" aria-haspopup="true" aria-controls="nav-mobile-locations" aria-expanded="false">Locations <span class="nm-loc-chev" aria-hidden="true">→</span></button></li>
        <li><a href="../contact.html">Contact</a></li>
    </ul>
    <a href="../contact.html" class="nav-mobile-cta">Start a project →</a>
</aside>

<aside class="nav-mobile-locations" id="nav-mobile-locations" aria-label="Locations menu" aria-hidden="true">
    <button type="button" class="nm-loc-back" aria-label="Back to main menu">
        <span class="nm-loc-back-arrow" aria-hidden="true">←</span>
        <span class="nm-loc-back-label">Back</span>
    </button>
    <div class="nm-loc-content">
        <p class="eyebrow">Locations</p>
        <h2 class="nm-loc-h">Web designer <em>across Canada.</em></h2>
{mobile_loc_provinces}
        <a href="../locations.html" class="nm-loc-all-link">See all locations <span class="arrow">→</span></a>
    </div>
</aside>

<main id="main">

<section id="top" class="hero">
    <div class="wrap">
        <p class="hero-availability">{name}, {province} &middot; Now accepting new projects</p>
        <h1 class="hero-name">{name} <span class="last">Web Designer</span></h1>
        <p class="hero-tag">Custom website design and development for {name} firms — built by hand, hosted, and supported.</p>
        <p class="hero-price">
            <strong>$0 down</strong> &middot; <strong>$199 / month</strong> all-inclusive
            <span class="hero-price-term">12-month minimum &middot; or $3,800 lump sum</span>
        </p>
        <p class="hero-lede">
            {intro}
        </p>
        <div class="hero-actions">
            <a href="../contact.html" class="btn btn-primary">Start a project <span class="arrow">→</span></a>
            <a href="../work.html" class="btn btn-secondary">See selected work <span class="arrow">→</span></a>
        </div>
    </div>
</section>

<section class="section section-areas">
    <div class="wrap">
        <p class="eyebrow">Areas served</p>
        <h2 class="display section-h">Web design and development across {name}.</h2>
        <p class="section-body">
            The studio works with professional-services firms in {areas}. Most of my {name} clients are solo or small-team practices &mdash; lawyers, accountants, dentists, medical clinics, consultancies &mdash; that need a credible web presence without spending the kind of money downtown agencies charge.
        </p>
        <p class="section-body">
            The work is the same whether your firm is headquartered in {name} or in a community an hour's drive away. Discovery happens over email, design happens in the browser as a working preview, and the finished site is hosted, supported, and edited by the same person who built it. There's no account-management layer, no offshore dev team, no hidden hand-offs. Just one designer-developer, one codebase, and a website that does the work it's supposed to do.
        </p>
    </div>
</section>

<section class="section section-services">
    <div class="wrap">
        <p class="eyebrow">Web design services in {name}</p>
        <h2 class="display section-h">What's included with every {name} website.</h2>
        <p class="lede section-lede">Every {name} build runs on the same all-inclusive plan. There are no add-ons hidden behind a sales call, no pay-per-edit tickets, no surprise hosting bills.</p>
        <ul class="svc-list">
            <li>
                <h3>Custom website design in {name}</h3>
                <p>Designed for your firm specifically &mdash; not picked from a template gallery. Every {name} project is wireframed, styled, and refined for your practice's voice, clients, and competitive position.</p>
            </li>
            <li>
                <h3>Hand-coded website development</h3>
                <p>No WordPress bloat, no page-builder slop, no plugin sprawl. Clean semantic HTML and CSS that loads instantly on any device and ages gracefully &mdash; the way a {name} firm's website should.</p>
            </li>
            <li>
                <h3>{name} website hosting &amp; security</h3>
                <p>Fast, redundant hosting with SSL certificates, daily backups, and automatic security updates included in the monthly fee. No separate hosting bill, no security plugin maintenance, no surprise renewals.</p>
            </li>
            <li>
                <h3>Unlimited edits</h3>
                <p>Send a message; the change goes live within one to two business days. New staff bio, updated services, fresh photo, revised hours &mdash; no per-hour billing, no ticket queues, no waiting on a copy-paste agency.</p>
            </li>
            <li>
                <h3>SEO foundation for {name} search visibility</h3>
                <p>Schema markup, sitemap, semantic HTML, fast Core Web Vitals, and clean metadata. The technical groundwork search engines reward, built into every {name} website from day one &mdash; not a $500 SEO upsell.</p>
            </li>
            <li>
                <h3>Direct one-on-one support</h3>
                <p>You email me directly &mdash; not a help-desk queue. The same person who designed and built your {name} website is the same person who answers when something needs to change. That doesn't scale to thousands of clients, which is the point.</p>
            </li>
        </ul>
    </div>
</section>

<section class="section section-why">
    <div class="wrap">
        <p class="eyebrow">Why custom</p>
        <h2 class="display section-h">Why {name} firms choose custom over templates.</h2>
        <p class="section-body">
            A template is faster and cheaper up front. It's also why most professional-services websites in {name} look like every other professional-services website in {name}. The hero photo is from the same stock library; the colour palette is two clicks deep in a Squarespace settings panel; the typography is whatever Wix shipped that quarter. Clients notice. Younger clients especially notice. And firms that compete on credibility cannot afford to be visually indistinguishable from the firm down the street.
        </p>
        <p class="section-body">
            Hand-coded, custom-designed websites take longer to build but pay back in three places: clients trust them more, search engines rank them better (because clean code loads faster and structures content more clearly), and the firm doesn't end up locked into a platform's roadmap. When the time comes to update the site, expand it, or move it, your {name} website is just files &mdash; not someone else's hostage. That's the deal the studio offers, and it's the same deal whether you're a solo practitioner or a fifteen-lawyer regional firm.
        </p>
    </div>
</section>

<section class="section section-process">
    <div class="wrap">
        <p class="eyebrow">Process</p>
        <h2 class="display section-h">The {name} web design process.</h2>
        <ol class="process-list">
            <li>
                <span class="process-n">01</span>
                <h3>Discovery</h3>
                <p>You send a few sentences about your {name} firm: what you do, who you serve, and what's not working with the current site (or the absence of one). I come back with thoughts, a rough scope, and a fixed-fee or subscription quote within one business day.</p>
            </li>
            <li>
                <span class="process-n">02</span>
                <h3>Working preview</h3>
                <p>Within a week or two, you have a live URL with your actual content in a real design &mdash; not a mockup, not a Figma file, the real thing. We iterate on it together over email until it feels right for your {name} practice.</p>
            </li>
            <li>
                <span class="process-n">03</span>
                <h3>Launch</h3>
                <p>The site goes live on your domain, hosted on the studio's infrastructure with SSL, backups, and the SEO foundation already wired up. The whole {name} project usually takes three to five weeks end to end.</p>
            </li>
            <li>
                <span class="process-n">04</span>
                <h3>Ongoing edits &amp; support</h3>
                <p>You email me when something needs to change &mdash; new partner, new service line, new photo, new copy. Edits go live within one to two business days, included in the monthly fee. No tickets, no agency middlemen, no surprise invoices.</p>
            </li>
        </ol>
    </div>
</section>

<section class="section section-pricing">
    <div class="wrap">
        <p class="eyebrow">Pricing</p>
        <h2 class="display section-h">{name} web design pricing.</h2>
        <div class="pricing-row">
            <div class="pricing-card">
                <p class="pricing-card-name">Monthly subscription</p>
                <p class="pricing-card-price"><strong>$0</strong> down</p>
                <p class="pricing-card-sub">$199 / month all-inclusive &middot; 12-month minimum</p>
                <p class="pricing-card-body">Design, development, hosting, edits, security, and direct support &mdash; one monthly fee for as long as you stay. Site stays live as long as the subscription is active.</p>
            </div>
            <div class="pricing-card">
                <p class="pricing-card-name">Lump sum</p>
                <p class="pricing-card-price"><strong>$3,800</strong> one-time</p>
                <p class="pricing-card-sub">Plus $25 / month standalone hosting</p>
                <p class="pricing-card-body">Pay once, own the site outright. Hosting becomes a separate $25-a-month service. Same design quality, same hand-coded build, same {name} support.</p>
            </div>
        </div>
        <p class="pricing-foot"><a href="../pricing.html" class="link-arrow">See full pricing details <span class="arrow">→</span></a></p>
    </div>
</section>

<section class="section section-faq">
    <div class="wrap">
        <p class="eyebrow">FAQ</p>
        <h2 class="display section-h">{name} web design FAQ.</h2>
        <dl class="faq-list">
            <div class="faq-item">
                <dt>Do you only work with firms in {name}?</dt>
                <dd>Most of my clients are in {name} and the surrounding region, but the studio's remote workflow handles firms anywhere in {province} &mdash; and across Canada generally. Whether your practice is in {name} proper or in a nearby community, the build, edit, and support process is identical. Nothing about the work depends on being in the same room.</dd>
            </div>
            <div class="faq-item">
                <dt>How long does a website build take in {name}?</dt>
                <dd>From the first email to a live site is usually three to five weeks for most {name} firms. Discovery happens over email, the working preview goes up within a week or two, we iterate, the site polishes, and it goes live on your domain. There's no in-person meeting required at any step &mdash; though you're welcome to schedule a call if you'd rather talk things through.</dd>
            </div>
            <div class="faq-item">
                <dt>What kinds of {name} firms do you build for?</dt>
                <dd>The studio specializes in professional-services firms &mdash; {name} law practices, accounting and bookkeeping firms, medical and dental clinics, consultancies, and other practices where the website needs to communicate trust, credibility, and clarity to a serious clientele. If your {name} firm sells expertise rather than products, the design language fits.</dd>
            </div>
            <div class="faq-item">
                <dt>Do I own my {name} website?</dt>
                <dd>On the $3,800 lump-sum plan, yes &mdash; you own the site outright, and hosting becomes a $25-a-month standalone service. On the $0-down, $199-a-month subscription, the site is hosted and supported as long as you stay on the plan; if you cancel before twelve months, the early-termination amount is $3,800 minus what you've paid, after which you can take the code with you. Either way, no {name} firm is ever locked into anything that wasn't agreed to upfront.</dd>
            </div>
        </dl>
    </div>
</section>

<section class="section section-nearby">
    <div class="wrap">
        <p class="eyebrow">Also serving</p>
        <h2 class="display section-h">Web design services near {name}.</h2>
        <p class="section-body">
            The studio works with professional-services firms across {province} and beyond. If your firm is outside {name} proper, the same hand-coded design, all-inclusive pricing, and remote workflow apply.
        </p>
        <ul class="nearby-list">
{nearby_links}
            <li class="nearby-all"><a href="../locations.html">See all locations across Canada <span class="arrow">→</span></a></li>
        </ul>
    </div>
</section>

<section class="section section-cta">
    <div class="wrap cta-band">
        <p class="eyebrow">Start a project</p>
        <h2 class="display cta-band-h">A modern {name} website that finally matches the work behind it.</h2>
        <p class="cta-band-sub">Send a few sentences about your {name} firm. I'll come back with thoughts, a rough scope, and &mdash; often &mdash; a working preview within a few days.</p>
        <div class="cta-band-actions">
            <a href="../contact.html" class="btn btn-primary">Start a project <span class="arrow">→</span></a>
            <a href="../pricing.html" class="btn btn-secondary">See pricing <span class="arrow">→</span></a>
        </div>
    </div>
</section>

</main>

<footer class="footer">
    <div class="wrap">
        <div class="footer-grid">
            <div>
                <p class="footer-brand">Matthew McGuire</p>
                <p class="footer-blurb">Small firms deserve websites that feel like the work behind them. That's what the studio is for.</p>
                <p class="footer-credit"><span class="footer-credit-dot" aria-hidden="true"></span>Canadian owned &middot; Based in Edmonton, Alberta</p>
            </div>
            <div class="footer-col">
                <h5 class="footer-h5">Site</h5>
                <ul>
                    <li><a href="../about.html">About</a></li>
                    <li><a href="../work.html">Selected work</a></li>
                    <li><a href="../how.html">How I work</a></li>
                    <li><a href="../pricing.html">Pricing</a></li>
                    <li><a href="../faq.html">FAQ</a></li>
                    <li><a href="../locations.html">All locations</a></li>
                    <li><a href="../contact.html">Contact</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h5 class="footer-h5">Reach</h5>
                <ul>
                    <li><a href="mailto:matt@mattmcguiredesign.com">matt@mattmcguiredesign.com</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h5 class="footer-h5">Based</h5>
                <ul>
                    <li>Edmonton, Alberta</li>
                    <li>Working with firms across Canada</li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <span>© <span id="footer-year">2026</span> Matthew McGuire. All rights reserved.</span>
            <span class="footer-bottom-links">
                <a href="../privacy.html">Privacy</a><span class="dot">·</span><a href="../terms.html">Terms</a>
            </span>
            <span>Designed &amp; built by hand</span>
        </div>
    </div>
</footer>

<script>
    var nav = document.getElementById('site-nav');
    if (nav) {{
        var onScroll = function () {{
            if (window.scrollY > 12) nav.classList.add('scrolled');
            else nav.classList.remove('scrolled');
        }};
        window.addEventListener('scroll', onScroll, {{ passive: true }});
        onScroll();
    }}
    var yearEl = document.getElementById('footer-year');
    if (yearEl) yearEl.textContent = new Date().getFullYear();

    var navToggle = document.querySelector('.nav-toggle');
    var navMobile = document.querySelector('.nav-mobile');
    var navMobileLoc = document.querySelector('.nav-mobile-locations');
    function setLoc(open) {{
        document.body.classList.toggle('nav-loc-open', open);
        if (navMobileLoc) navMobileLoc.setAttribute('aria-hidden', open ? 'false' : 'true');
        var trig = document.querySelector('.nm-loc-trigger');
        if (trig) trig.setAttribute('aria-expanded', open ? 'true' : 'false');
    }}
    function setNav(open) {{
        document.body.classList.toggle('nav-open', open);
        if (!open) setLoc(false);
        if (navToggle) {{
            navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        }}
    }}
    if (navToggle) navToggle.addEventListener('click', function () {{
        setNav(!document.body.classList.contains('nav-open'));
    }});
    document.addEventListener('keydown', function (e) {{
        if (e.key === 'Escape') {{
            if (document.body.classList.contains('nav-loc-open')) setLoc(false);
            else if (document.body.classList.contains('nav-open')) setNav(false);
        }}
    }});
    if (navMobile) navMobile.querySelectorAll('a').forEach(function (a) {{
        a.addEventListener('click', function () {{ setNav(false); }});
    }});
    document.querySelectorAll('.nm-loc-trigger').forEach(function (b) {{
        b.addEventListener('click', function () {{ setLoc(true); }});
    }});
    document.querySelectorAll('.nm-loc-back').forEach(function (b) {{
        b.addEventListener('click', function () {{ setLoc(false); }});
    }});
    if (navMobileLoc) navMobileLoc.querySelectorAll('a').forEach(function (a) {{
        a.addEventListener('click', function () {{ setLoc(false); setNav(false); }});
    }});

    document.addEventListener('click', function (e) {{
        var a = e.target.closest('a');
        if (!a) return;
        var href = a.getAttribute('href');
        if (!href) return;
        if (
            a.target === '_blank' ||
            e.metaKey || e.ctrlKey || e.shiftKey || e.altKey ||
            href.charAt(0) === '#' ||
            href.indexOf('mailto:') === 0 ||
            href.indexOf('tel:') === 0 ||
            a.hasAttribute('download')
        ) return;
        var url = new URL(a.href, window.location.href);
        if (url.origin !== window.location.origin) return;
        if (url.pathname === window.location.pathname) return;
        e.preventDefault();
        document.body.classList.add('is-leaving');
        setTimeout(function () {{ window.location.href = a.href; }}, 220);
    }});
</script>

</body>
</html>
"""

# ---------------------------------------------------------------------------
# CITY STYLES
# ---------------------------------------------------------------------------

CITY_STYLES = """
:root {
    --paper:        #EFE7D2;
    --paper-soft:   #E6DBC0;
    --paper-deeper: #D6C8A8;
    --ink:          #1A1813;
    --ink-2:        #4A4339;
    --ink-3:        #847B6B;
    --rule:         #CFC2A6;
    --rule-soft:    #DDD2BA;
    --accent:       #2C3D24;
    --accent-deep:  #1A2516;
    --accent-soft:  #C0CCB0;
    --rust:         #7A4A28;
    --rust-deep:    #4A2E1F;
    --stone:        #5C5848;

    --serif: 'Playfair Display', 'Source Serif 4', Georgia, serif;
    --sans:  'Inter', ui-sans-serif, -apple-system, 'Helvetica Neue', Arial, sans-serif;
    --mono:  'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;

    --max:    1240px;
    --gutter: clamp(20px, 4vw, 56px);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
    font-family: var(--sans); font-size: 16px; line-height: 1.55;
    color: var(--ink); background: var(--paper);
    -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
    animation: pageEnter 380ms cubic-bezier(.2,.7,.2,1) both;
}
@keyframes pageEnter { from { opacity: 0; } to { opacity: 1; } }
@keyframes pageLeave { from { opacity: 1; } to { opacity: 0; } }
body.is-leaving { animation: pageLeave 260ms cubic-bezier(.4,.1,.3,1) forwards; }
@media (prefers-reduced-motion: reduce) {
    body, body.is-leaving { animation: none !important; }
}
img { max-width: 100%; display: block; }
a { color: inherit; text-decoration: none; }
button { font: inherit; cursor: pointer; border: none; background: none; color: inherit; }
ul, ol { list-style: none; }

.eyebrow {
    font-family: var(--mono); font-size: 11px; font-weight: 500;
    letter-spacing: 0.18em; text-transform: uppercase; color: var(--accent-deep);
    display: inline-flex; align-items: center; gap: 12px;
}
.eyebrow::before { content: ""; width: 28px; height: 1px; background: var(--accent); }
.display {
    font-family: var(--serif); font-weight: 700; letter-spacing: -0.022em;
    line-height: 1.05; color: var(--ink);
}
.display em { font-style: italic; font-weight: 500; color: var(--ink-2); }
.lede {
    font-family: var(--sans); font-size: clamp(17px, 1.3vw, 19px);
    line-height: 1.6; color: var(--ink-2); max-width: 60ch;
}

.wrap { max-width: var(--max); margin: 0 auto; padding: 0 var(--gutter); }
.section { padding: clamp(72px, 8vw, 120px) 0; }
.section + .section { border-top: 1px solid var(--rule); }
.section-h { font-size: clamp(30px, 4vw, 50px); margin: 18px 0 24px; max-width: 22ch; }
.section-lede { margin-bottom: 56px; }
.section-body {
    font-size: clamp(15.5px, 1.15vw, 17.5px); line-height: 1.7;
    color: var(--ink-2); max-width: 68ch; margin-bottom: 22px;
}

.skip-link {
    position: absolute; top: -40px; left: 8px;
    background: var(--ink); color: var(--paper);
    padding: 8px 14px; font-size: 13px; font-weight: 500;
    border-radius: 4px; z-index: 200; transition: top 200ms ease;
}
.skip-link:focus { top: 8px; }

/* MASTHEAD */
.masthead {
    background: var(--ink); color: color-mix(in oklch, var(--paper) 78%, transparent);
    border-bottom: 1px solid color-mix(in oklch, var(--paper) 14%, transparent);
}
.masthead-inner {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0; gap: 16px; font-family: var(--mono); font-size: 10px;
    font-weight: 500; letter-spacing: 0.22em; text-transform: uppercase;
}
.masthead-edition { display: inline-flex; align-items: center; gap: 12px; }
.masthead-edition::before {
    content: ""; width: 22px; height: 1px;
    background: color-mix(in oklch, var(--rust) 90%, transparent);
}
.masthead-meta { color: color-mix(in oklch, var(--paper) 60%, transparent); }
@media (max-width: 600px) {
    .masthead-meta { display: none; }
    .masthead-edition::before { width: 16px; }
    .masthead-inner { font-size: 9px; letter-spacing: 0.18em; }
}

/* NAV */
.nav {
    position: sticky; top: 0; z-index: 50; background: transparent;
    border-bottom: 1px solid transparent;
    transition: background 240ms ease, border-color 240ms ease;
}
.nav.scrolled { background: var(--paper); border-bottom-color: var(--rule); }
.nav-inner {
    display: flex; align-items: center; justify-content: space-between;
    padding: 22px clamp(28px, 4vw, 56px); gap: 24px;
}
.nav-mark {
    display: inline-flex; flex-direction: column; align-items: flex-start;
    gap: 4px; color: var(--ink); line-height: 1;
}
.nav-mark-letters {
    font-family: var(--serif); font-size: 22px; font-style: italic;
    font-weight: 500; letter-spacing: -0.01em;
}
.nav-mark-name {
    font-family: var(--mono); font-size: 11px; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--ink-3);
}
.nav-links { display: flex; gap: 32px; align-items: center; position: relative; }
.nav-links > a, .nav-links > .nav-dd > .nav-dd-trigger {
    font-size: 14px; color: var(--ink-2); position: relative; padding: 4px 0;
    transition: color 200ms ease; background: none; border: none;
    font-family: inherit; cursor: pointer;
}
.nav-links > a::after, .nav-links > .nav-dd > .nav-dd-trigger::after {
    content: ""; position: absolute; left: -4px; right: -4px; bottom: -8px;
    height: 9px; background-image: url("../img/brush-underline.png");
    background-repeat: no-repeat; background-position: center; background-size: 100% 100%;
    transform: scaleX(0); transform-origin: right;
    transition: transform 360ms cubic-bezier(.2,.7,.2,1);
}
.nav-links > a:hover, .nav-links > .nav-dd:hover > .nav-dd-trigger { color: var(--ink); }
.nav-links > a:hover::after, .nav-links > .nav-dd:hover > .nav-dd-trigger::after {
    transform: scaleX(1); transform-origin: left;
}
.nav-links > .nav-dd[aria-current="page"] > .nav-dd-trigger { color: var(--ink); }
.nav-links > .nav-dd[aria-current="page"] > .nav-dd-trigger::after {
    transform: scaleX(1); transform-origin: left;
}

/* DROPDOWN */
.nav-dd { position: relative; }
.nav-dd-panel {
    position: absolute; top: 100%; right: 0;
    background: var(--paper); border: 1px solid var(--rule);
    background-clip: padding-box;
    box-shadow: 0 24px 56px -28px rgba(19,22,19,0.32);
    padding: 14px 0; min-width: 240px; list-style: none; margin: 0;
    margin-top: 14px;
    opacity: 0; pointer-events: none; transform: translateY(-4px);
    transition: opacity 200ms ease 80ms, transform 220ms cubic-bezier(.2,.7,.2,1) 80ms;
    z-index: 60;
}
/* Invisible bridge: closes the 14px gap between trigger and panel
   so the mouse can traverse without losing :hover state. */
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
    display: flex; align-items: center; justify-content: space-between;
    padding: 9px 22px; font-size: 13.5px; color: var(--ink-2);
    font-family: var(--sans);
    transition: background 160ms ease, color 160ms ease;
}
.nav-dd-panel > li > a::after {
    content: "›"; font-size: 18px; color: var(--ink-3); margin-left: 16px;
    transition: transform 200ms ease, color 200ms ease;
}
.nav-dd-panel > li:hover > a {
    background: color-mix(in oklch, var(--ink) 6%, transparent); color: var(--ink);
}
.nav-dd-panel > li:hover > a::after { transform: translateX(3px); color: var(--rust); }

.nav-dd-sub {
    position: absolute; top: -14px; left: 100%; min-width: 220px;
    list-style: none; margin: 0;
    background: var(--paper); border: 1px solid var(--rule);
    box-shadow: 0 24px 56px -28px rgba(19,22,19,0.32);
    padding: 14px 0;
    opacity: 0; pointer-events: none; transform: translateX(-4px);
    transition: opacity 200ms ease 80ms, transform 220ms cubic-bezier(.2,.7,.2,1) 80ms;
}
/* Bridge so the cursor can move between province li and sub-panel without
   losing :hover state. */
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
    display: block; padding: 7px 22px; font-size: 13px; color: var(--ink-2);
    transition: background 140ms ease, color 140ms ease;
}
.nav-dd-sub a:hover { background: color-mix(in oklch, var(--ink) 6%, transparent); color: var(--ink); }

@media (max-width: 1100px) { .nav-dd-panel { right: auto; left: 0; } }

.nav-cta {
    font-family: var(--mono); font-size: 11px; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--ink); padding: 8px 20px;
    border: 1px solid var(--ink); border-radius: 8px;
    transition: background 200ms ease, color 200ms ease;
}
.nav-cta:hover { background: var(--ink); color: var(--paper); }

.nav-toggle {
    display: none; width: 44px; height: 44px; align-items: center;
    justify-content: center; background: transparent; border: 1px solid var(--rule);
    border-radius: 999px; cursor: pointer; padding: 0;
}
.nav-toggle-bars { position: relative; width: 18px; height: 12px; }
.nav-toggle-bars::before, .nav-toggle-bars::after {
    content: ""; position: absolute; left: 0; width: 100%; height: 1.5px;
    background: var(--ink);
    transition: top 200ms ease 200ms, transform 240ms cubic-bezier(.2,.7,.2,1);
}
.nav-toggle-bars::before { top: 2px; }
.nav-toggle-bars::after  { top: 8px; }
.nav-toggle[aria-expanded="true"] .nav-toggle-bars::before { top: 5px; transform: rotate(45deg); transition: top 200ms ease, transform 240ms cubic-bezier(.2,.7,.2,1) 200ms; }
.nav-toggle[aria-expanded="true"] .nav-toggle-bars::after  { top: 5px; transform: rotate(-45deg); transition: top 200ms ease, transform 240ms cubic-bezier(.2,.7,.2,1) 200ms; }

.nav-mobile { display: none; }
@media (max-width: 880px) {
    .nav-links { display: none; }
    .nav-mark-name { display: none; }
    .nav-cta { display: none; }
    .nav-toggle { display: inline-flex; }
    #site-nav { z-index: 70; }

    .nav-mobile {
        display: flex; flex-direction: column; justify-content: flex-start;
        position: fixed; inset: 0; background: var(--paper);
        padding: 110px 32px 56px; opacity: 0; pointer-events: none;
        transform: translateY(8px);
        transition: opacity 280ms ease, transform 320ms cubic-bezier(.2,.7,.2,1);
        z-index: 60; overflow-y: auto;
    }
    body.nav-open .nav-mobile { opacity: 1; pointer-events: auto; transform: translateY(0); }
    body.nav-open { overflow: hidden; }

    .nav-mobile-links { display: flex; flex-direction: column; gap: 4px; }
    .nav-mobile-links a, .nav-mobile-links .nm-loc-trigger {
        display: inline-flex; align-items: baseline; gap: 12px;
        padding: 8px 0; font-family: var(--serif);
        font-style: italic; font-size: clamp(30px, 7vw, 48px); color: var(--ink);
        letter-spacing: -0.022em; line-height: 1; position: relative;
        background: none; border: none; cursor: pointer; text-align: left;
    }
    .nav-mobile-links a[aria-current="page"] { color: var(--rust-deep); }
    .nm-loc-chev {
        font-family: var(--mono); font-style: normal; font-weight: 400;
        font-size: 0.36em; color: var(--ink-3);
        align-self: center; transition: transform 200ms ease, color 200ms ease;
    }
    .nm-loc-trigger:active .nm-loc-chev { transform: translateX(4px); color: var(--rust); }
    .nav-mobile-cta {
        display: inline-flex; align-self: flex-start; margin-top: 28px;
        font-family: var(--mono); font-size: 11px; letter-spacing: 0.16em;
        text-transform: uppercase; color: var(--paper); background: var(--ink);
        padding: 10px 22px; border-radius: 8px;
    }

    /* MOBILE LOCATIONS PANEL — slides in from right when triggered */
    .nav-mobile-locations {
        display: flex; flex-direction: column;
        position: fixed; inset: 0; background: var(--paper);
        padding: 88px 28px 56px;
        opacity: 0; pointer-events: none;
        transform: translateX(100%);
        transition: transform 320ms cubic-bezier(.2,.7,.2,1), opacity 240ms ease;
        z-index: 80; overflow-y: auto;
    }
    body.nav-loc-open .nav-mobile-locations {
        opacity: 1; pointer-events: auto; transform: translateX(0);
    }
    .nm-loc-back {
        position: fixed; top: 22px; left: 22px; z-index: 90;
        display: inline-flex; align-items: center; gap: 8px;
        font-family: var(--mono); font-size: 10.5px;
        letter-spacing: 0.16em; text-transform: uppercase;
        color: var(--ink); padding: 7px 14px;
        background: var(--paper); border: 1px solid var(--rule);
        border-radius: 8px; cursor: pointer;
        transition: background 180ms ease, color 180ms ease, transform 160ms cubic-bezier(.2,.7,.2,1);
    }
    .nm-loc-back:active { background: var(--ink); color: var(--paper); transform: scale(0.96); }
    .nm-loc-back-arrow { font-size: 14px; line-height: 1; }
    .nm-loc-content { padding-top: 8px; }
    .nm-loc-h {
        font-family: var(--serif); font-style: italic; font-weight: 700;
        font-size: clamp(34px, 7vw, 52px); letter-spacing: -0.022em;
        line-height: 1.05; color: var(--ink); margin: 14px 0 32px;
    }
    .nm-loc-h em { font-style: italic; color: var(--rust-deep); }
    .nm-loc-prov {
        margin-bottom: 24px; border-top: 1px solid var(--rule); padding-top: 18px;
    }
    .nm-loc-prov h3 {
        font-family: var(--mono); font-size: 10.5px; font-weight: 600;
        letter-spacing: 0.18em; text-transform: uppercase;
        color: var(--rust-deep); margin-bottom: 12px;
    }
    .nm-loc-prov ul {
        list-style: none; display: grid;
        grid-template-columns: 1fr 1fr; gap: 2px 18px;
    }
    .nm-loc-prov ul a {
        display: block; padding: 8px 0;
        font-family: var(--serif); font-style: italic;
        font-size: 17px; line-height: 1.2; color: var(--ink);
        transition: color 160ms ease, padding 200ms ease;
    }
    .nm-loc-prov ul a:active { color: var(--rust-deep); padding-left: 4px; }
    @media (max-width: 380px) {
        .nm-loc-prov ul { grid-template-columns: 1fr; }
    }
    .nm-loc-all-link {
        display: inline-flex; align-items: center; gap: 10px;
        margin-top: 24px; font-family: var(--mono);
        font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
        color: var(--rust-deep); padding: 10px 0;
    }
    .nm-loc-all-link .arrow { transition: transform 200ms ease; }
    .nm-loc-all-link:active { color: var(--ink); }
    .nm-loc-all-link:active .arrow { transform: translateX(3px); }
}

/* Hide the locations panel completely above mobile breakpoint. */
@media (min-width: 881px) {
    .nav-mobile-locations { display: none !important; }
}

/* HERO */
.hero {
    position: relative;
    padding: clamp(56px, 7vw, 96px) 0 clamp(64px, 7vw, 104px);
    background:
        linear-gradient(100deg,
            var(--paper) 0%, var(--paper) 40%,
            color-mix(in oklch, var(--paper) 65%, transparent) 60%,
            color-mix(in oklch, var(--paper) 18%, transparent) 80%,
            transparent 100%),
        url('../img/hero-pnw-5.jpg') right center / cover no-repeat,
        var(--paper);
}
.hero::after {
    content: ""; position: absolute; left: var(--gutter); right: var(--gutter);
    bottom: 0; height: 1px; background: var(--rule);
}
.hero .wrap { position: relative; z-index: 1; max-width: 880px; }
@media (max-width: 980px) {
    .hero {
        background:
            linear-gradient(180deg, var(--paper) 0%, var(--paper) 60%,
                color-mix(in oklch, var(--paper) 30%, transparent) 100%),
            url('../img/hero-pnw-5.jpg') center 40% / cover no-repeat,
            var(--paper);
    }
}
.hero-availability {
    display: inline-flex; align-items: center; gap: 10px; font-family: var(--mono);
    font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--ink-3); margin-bottom: 32px;
}
.hero-availability::before {
    content: ""; width: 8px; height: 8px; border-radius: 999px; background: var(--accent);
    box-shadow: 0 0 0 4px color-mix(in oklch, var(--accent) 18%, transparent);
}
.hero-name {
    font-family: var(--serif); font-size: clamp(40px, 5.4vw, 76px);
    font-style: italic; font-weight: 700; letter-spacing: -0.022em;
    line-height: 1.04; color: var(--ink); margin: 0 0 18px; max-width: 18ch;
}
.hero-name .last { color: var(--rust-deep); }
.hero-tag {
    font-family: var(--serif); font-size: clamp(19px, 1.7vw, 24px);
    font-style: italic; font-weight: 400; line-height: 1.3; color: var(--ink-2);
    margin: 0 0 28px; max-width: 38ch; letter-spacing: -0.012em;
}
.hero-price {
    display: flex; flex-wrap: wrap; align-items: baseline;
    column-gap: 14px; row-gap: 8px; margin: 0 0 28px;
    padding: 16px 0 18px; border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule); max-width: 56ch;
    font-family: var(--serif); font-size: clamp(19px, 1.7vw, 25px);
    font-weight: 500; color: var(--ink); letter-spacing: -0.008em;
}
.hero-price strong {
    font-weight: 700; font-style: italic; color: var(--rust-deep);
    background-image: url("../img/brush-underline.png");
    background-repeat: no-repeat; background-position: 0 100%;
    background-size: 100% 0.55em; padding-bottom: 0.05em;
}
.hero-price-term {
    flex-basis: 100%; font-family: var(--mono); font-size: 10.5px;
    font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--ink-3); margin-top: 4px;
}
.hero-lede {
    font-size: clamp(15.5px, 1.15vw, 17.5px); line-height: 1.7;
    color: var(--ink-2); max-width: 64ch; margin: 0 0 32px;
}
.hero-actions { display: flex; gap: 16px; flex-wrap: wrap; align-items: center; }

.btn {
    display: inline-flex; align-items: center; gap: 12px;
    font-family: var(--mono); font-size: 11.5px; font-weight: 500;
    letter-spacing: 0.16em; text-transform: uppercase;
    padding: 10px 22px; border-radius: 8px;
    transition: background 200ms ease, color 200ms ease, transform 160ms cubic-bezier(.2,.7,.2,1);
}
.btn .arrow { transition: transform 220ms cubic-bezier(.2,.7,.2,1); }
.btn:hover .arrow { transform: translateX(4px); }
.btn:active { transform: scale(0.97); }
.btn-primary { background: var(--ink); color: var(--paper); }
.btn-primary:hover { background: var(--rust-deep); }
.btn-secondary { background: transparent; color: var(--ink); border: 1px solid var(--ink); }
.btn-secondary:hover { background: var(--ink); color: var(--paper); }
.link-arrow {
    font-family: var(--mono); font-size: 11.5px; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--rust-deep);
    border-bottom: 1px solid currentColor; padding-bottom: 4px;
    display: inline-flex; align-items: center; gap: 8px;
}
.link-arrow:hover { color: var(--ink); }

/* SECTIONS */
.section-areas { background: var(--paper); }
.section-services { background: var(--paper-soft); }
.svc-list {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px 40px;
    margin: 0;
}
.svc-list li { border-top: 1px solid var(--rule); padding-top: 22px; list-style: none; }
.svc-list h3 {
    font-family: var(--serif); font-size: 22px; font-weight: 600;
    color: var(--ink); margin-bottom: 10px; line-height: 1.2;
}
.svc-list p { font-size: 14.5px; line-height: 1.65; color: var(--ink-2); }
@media (max-width: 880px) { .svc-list { grid-template-columns: 1fr 1fr; } }
@media (max-width: 600px) { .svc-list { grid-template-columns: 1fr; } }

.section-why { background: var(--paper); }

/* PROCESS */
.section-process { background: var(--paper-soft); }
.process-list {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 36px 40px;
    margin: 0;
}
.process-list li { list-style: none; border-top: 2px solid var(--rust); padding-top: 22px; }
.process-n {
    font-family: var(--mono); font-size: 11px; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--rust-deep);
    font-weight: 600; display: block; margin-bottom: 8px;
}
.process-list h3 {
    font-family: var(--serif); font-size: 24px; font-weight: 600;
    color: var(--ink); margin-bottom: 10px; line-height: 1.2;
}
.process-list p { font-size: 15px; line-height: 1.65; color: var(--ink-2); }
@media (max-width: 760px) { .process-list { grid-template-columns: 1fr; } }

/* PRICING */
.section-pricing { background: var(--paper); }
.pricing-row {
    display: grid; grid-template-columns: 1fr 1fr; gap: 28px;
    margin-top: 8px;
}
.pricing-card {
    background: var(--paper-soft); border: 1px solid var(--rule);
    padding: clamp(28px, 3vw, 40px); border-radius: 8px;
}
.pricing-card-name {
    font-family: var(--mono); font-size: 11px; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--ink-3); margin-bottom: 16px;
}
.pricing-card-price {
    font-family: var(--serif); font-size: clamp(32px, 4vw, 44px);
    font-weight: 600; color: var(--ink); line-height: 1;
}
.pricing-card-price strong { color: var(--rust-deep); font-style: italic; font-weight: 700; }
.pricing-card-sub {
    font-family: var(--mono); font-size: 11px; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--ink-3);
    margin: 14px 0 22px;
}
.pricing-card-body { font-size: 15px; line-height: 1.65; color: var(--ink-2); }
.pricing-foot { margin-top: 36px; }
@media (max-width: 760px) { .pricing-row { grid-template-columns: 1fr; } }

/* FAQ */
.section-faq { background: var(--paper-soft); }
.faq-list { display: flex; flex-direction: column; gap: 22px; max-width: 76ch; }
.faq-item { border-top: 1px solid var(--rule); padding-top: 22px; }
.faq-item dt {
    font-family: var(--serif); font-size: clamp(20px, 1.8vw, 26px);
    font-weight: 600; color: var(--ink); line-height: 1.25;
    margin-bottom: 12px; letter-spacing: -0.012em;
}
.faq-item dd {
    font-size: 15.5px; line-height: 1.7; color: var(--ink-2); margin-left: 0;
}

/* NEARBY */
.section-nearby { background: var(--paper); }
.nearby-list {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px 28px;
    margin-top: 28px; max-width: 1000px;
}
.nearby-list li { list-style: none; }
.nearby-list a {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 0; font-family: var(--serif); font-size: 19px;
    font-style: italic; color: var(--ink); border-bottom: 1px solid var(--rule-soft);
    transition: padding 220ms ease, color 200ms ease;
}
.nearby-list a::after {
    content: "→"; color: var(--ink-3); font-style: normal;
    transition: transform 220ms ease, color 200ms ease;
}
.nearby-list a:hover { color: var(--rust-deep); padding-left: 4px; }
.nearby-list a:hover::after { transform: translateX(4px); color: var(--rust); }
.nearby-list .nearby-all { grid-column: 1 / -1; margin-top: 22px; }
.nearby-list .nearby-all a {
    border-bottom: none; font-family: var(--mono); font-style: normal;
    font-size: 11.5px; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--rust-deep); padding-left: 0; gap: 12px;
}
.nearby-list .nearby-all a::after { display: none; }
.nearby-list .nearby-all a:hover { color: var(--ink); }
@media (max-width: 760px) { .nearby-list { grid-template-columns: 1fr; } }

/* CTA BAND */
.section-cta { background: var(--ink); color: var(--paper); }
.cta-band { text-align: left; max-width: 760px; }
.cta-band .eyebrow { color: color-mix(in oklch, var(--paper) 70%, transparent); }
.cta-band .eyebrow::before { background: color-mix(in oklch, var(--rust) 90%, transparent); }
.cta-band-h {
    color: var(--paper); font-size: clamp(30px, 4vw, 52px);
    margin: 18px 0 18px; max-width: 22ch;
}
.cta-band-sub {
    color: color-mix(in oklch, var(--paper) 76%, transparent);
    font-size: 16px; line-height: 1.65; max-width: 56ch; margin-bottom: 32px;
}
.cta-band-actions { display: flex; flex-wrap: wrap; gap: 16px; }
.cta-band .btn-primary { background: var(--paper); color: var(--ink); }
.cta-band .btn-primary:hover { background: var(--rust); color: var(--paper); }
.cta-band .btn-secondary { color: var(--paper); border-color: color-mix(in oklch, var(--paper) 50%, transparent); }
.cta-band .btn-secondary:hover { background: var(--paper); color: var(--ink); border-color: var(--paper); }

/* FOOTER */
.footer { background: var(--ink); color: color-mix(in oklch, var(--paper) 70%, transparent); padding: 80px 0 32px; }
.footer-grid {
    display: grid; grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 48px; margin-bottom: 64px;
}
.footer-brand { font-family: var(--serif); font-style: italic; font-size: 26px; color: var(--paper); margin-bottom: 14px; }
.footer-blurb { font-size: 14px; line-height: 1.6; color: color-mix(in oklch, var(--paper) 60%, transparent); max-width: 36ch; margin-bottom: 22px; }
.footer-credit { font-family: var(--mono); font-size: 10.5px; letter-spacing: 0.18em; text-transform: uppercase; display: inline-flex; align-items: center; gap: 10px; }
.footer-credit-dot { width: 6px; height: 6px; border-radius: 999px; background: var(--rust); }
.footer-h5 { font-family: var(--mono); font-size: 10.5px; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: color-mix(in oklch, var(--paper) 50%, transparent); margin-bottom: 18px; }
.footer-col ul { display: flex; flex-direction: column; gap: 9px; }
.footer-col a, .footer-col li { font-size: 13.5px; color: color-mix(in oklch, var(--paper) 78%, transparent); transition: color 200ms ease; }
.footer-col a:hover { color: var(--paper); }
.footer-bottom {
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 16px; padding-top: 28px;
    border-top: 1px solid color-mix(in oklch, var(--paper) 14%, transparent);
    font-family: var(--mono); font-size: 10.5px; letter-spacing: 0.16em;
    text-transform: uppercase; color: color-mix(in oklch, var(--paper) 50%, transparent);
}
.footer-bottom-links a { transition: color 200ms ease; }
.footer-bottom-links a:hover { color: var(--paper); }
.footer-bottom-links .dot { margin: 0 10px; }
@media (max-width: 880px) { .footer-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 540px) { .footer-grid { grid-template-columns: 1fr; } }
"""


# ---------------------------------------------------------------------------
# DROPDOWN HTML for city-page nav (paths relative to /locations/)
# ---------------------------------------------------------------------------

def mobile_loc_provinces_html(prefix: str) -> str:
    """Build the province blocks for the slide-in mobile locations panel.

    `prefix` is the relative path to the city pages (e.g. "../locations/" or "locations/").
    """
    out = []
    for prov, _abbr, cities in CITIES:
        out.append('        <div class="nm-loc-prov">')
        out.append(f'            <h3>{prov}</h3>')
        out.append('            <ul>')
        for slug, name, _intro in cities:
            out.append(f'                <li><a href="{prefix}{slug}.html">{name}</a></li>')
        out.append('            </ul>')
        out.append('        </div>')
    return "\n".join(out)


def desktop_dropdown() -> str:
    out = []
    out.append('            <div class="nav-dd" aria-current="page">')
    out.append('                <button type="button" class="nav-dd-trigger" aria-haspopup="true" aria-expanded="false">Locations</button>')
    out.append('                <ul class="nav-dd-panel">')
    for prov, abbr, cities in CITIES:
        out.append('                    <li>')
        out.append(f'                        <a href="../locations.html#{abbr.lower()}">{prov}</a>')
        out.append('                        <ul class="nav-dd-sub">')
        for slug, name, _intro in cities:
            out.append(f'                            <li><a href="../locations/{slug}.html">{name}</a></li>')
        out.append('                        </ul>')
        out.append('                    </li>')
    out.append('                </ul>')
    out.append('            </div>')
    return "\n".join(out)


def desktop_dropdown_for_root(active: bool = False) -> str:
    aria = ' aria-current="page"' if active else ""
    out = []
    out.append(f'            <div class="nav-dd"{aria}>')
    out.append('                <button type="button" class="nav-dd-trigger" aria-haspopup="true" aria-expanded="false">Locations</button>')
    out.append('                <ul class="nav-dd-panel">')
    for prov, abbr, cities in CITIES:
        out.append('                    <li>')
        out.append(f'                        <a href="locations.html#{abbr.lower()}">{prov}</a>')
        out.append('                        <ul class="nav-dd-sub">')
        for slug, name, _intro in cities:
            out.append(f'                            <li><a href="locations/{slug}.html">{name}</a></li>')
        out.append('                        </ul>')
        out.append('                    </li>')
    out.append('                </ul>')
    out.append('            </div>')
    return "\n".join(out)


# ---------------------------------------------------------------------------
# SCHEMA
# ---------------------------------------------------------------------------

def build_ld_json(slug: str, name: str, province: str, intro: str) -> str:
    studio_id = "https://matthewmcguire.ca/#studio"
    desc = (f"Custom-coded websites for {name} law firms, accounting practices, "
            f"medical and dental clinics, consultancies, and other professional-services "
            f"firms. $0 down, $199 a month all-inclusive — design, hosting, edits, "
            f"and security included — 12-month minimum, or $3,800 lump sum.")

    graph = [
        {
            "@type": ["ProfessionalService", "LocalBusiness"],
            "@id": studio_id,
            "name": "Matthew McGuire — Web Design Studio",
            "url": "https://matthewmcguire.ca/",
            "image": "https://matthewmcguire.ca/img/headshot/matt-headshot.png",
            "telephone": "",
            "priceRange": "$$",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Edmonton",
                "addressRegion": "AB",
                "addressCountry": "CA",
            },
            "geo": {"@type": "GeoCoordinates", "latitude": 53.5461, "longitude": -113.4938},
            "areaServed": {"@type": "Country", "name": "Canada"},
            "sameAs": [
                "https://github.com/mmcguire6",
                "https://www.linkedin.com/in/matthew-mcguire-44666b389",
            ],
        },
        {
            "@type": "Service",
            "name": f"Web Design and Development in {name}, {province}",
            "serviceType": "Web Design and Development",
            "provider": {"@id": studio_id},
            "areaServed": {
                "@type": "City",
                "name": name,
                "addressRegion": province,
                "addressCountry": "CA",
            },
            "description": desc,
            "offers": [
                {
                    "@type": "Offer",
                    "name": "Monthly subscription",
                    "price": "199",
                    "priceCurrency": "CAD",
                    "description": "$0 down, $199/month all-inclusive (12-month minimum). Design, development, hosting, edits, security, support.",
                },
                {
                    "@type": "Offer",
                    "name": "Lump sum",
                    "price": "3800",
                    "priceCurrency": "CAD",
                    "description": "One-time $3,800 build, plus $25/month standalone hosting. You own the site outright.",
                },
            ],
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f"Do you only work with firms in {name}?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": (f"Most of my clients are in {name} and the surrounding region, "
                                 f"but the studio's remote workflow handles firms anywhere in {province} "
                                 f"and across Canada. The build, edit, and support process is identical "
                                 f"whether you're in {name} proper or a nearby community."),
                    },
                },
                {
                    "@type": "Question",
                    "name": f"How long does a website build take in {name}?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": (f"From the first email to a live site is usually three to five weeks "
                                 f"for most {name} firms. Discovery is over email; the working preview goes "
                                 f"up within a week or two; we iterate; the site polishes; it goes live."),
                    },
                },
                {
                    "@type": "Question",
                    "name": f"What kinds of {name} firms do you build for?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": (f"Professional-services firms — {name} law practices, accounting and "
                                 f"bookkeeping firms, medical and dental clinics, consultancies, and "
                                 f"other practices where the website needs to communicate trust, "
                                 f"credibility, and clarity."),
                    },
                },
                {
                    "@type": "Question",
                    "name": f"Do I own my {name} website?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": ("On the $3,800 lump-sum plan, you own the site outright and hosting "
                                 "becomes a $25/month standalone service. On the $0-down, $199/month "
                                 "subscription, the site is hosted and supported as long as you stay "
                                 "on the plan. Early-termination math: $3,800 minus what's already "
                                 "been paid."),
                    },
                },
            ],
        },
    ]
    payload = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# WRITERS
# ---------------------------------------------------------------------------

def nearby_links_html(nearby_slugs: list[str]) -> str:
    out = []
    for s in nearby_slugs:
        if s in SLUG_TO_NAME:
            n, _p = SLUG_TO_NAME[s]
            out.append(f'            <li><a href="../locations/{s}.html">{n} web designer</a></li>')
    return "\n".join(out)


def write_city_page(slug: str, name: str, province: str, intro: str) -> Path:
    extras = EXTRAS.get(slug, {"areas": "the surrounding region", "nearby": []})
    title = (f"{name} Web Designer | Custom Website Design & Development "
             f"— Matthew McGuire")
    meta_desc = (f"{name} web designer building custom-coded websites for law firms, "
                 f"accounting practices, and clinics. $0 down, $199/month all-inclusive "
                 f"— design, hosting, edits, security included. 12-month minimum or "
                 f"$3,800 lump sum.")

    html = CITY_PAGE.format(
        slug=slug,
        title=title,
        meta_desc=meta_desc,
        name=name,
        province=province,
        intro=intro,
        areas=extras["areas"],
        styles=CITY_STYLES,
        ld_json=build_ld_json(slug, name, province, intro),
        nav_dropdown_desktop=desktop_dropdown(),
        nearby_links=nearby_links_html(extras["nearby"]),
        mobile_loc_provinces=mobile_loc_provinces_html("../locations/"),
    )
    path = OUT / f"{slug}.html"
    path.write_text(html, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# LOCATIONS INDEX
# ---------------------------------------------------------------------------

LOCATIONS_INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Web Designer Across Canada — Custom Websites for Local Firms — Matthew McGuire</title>
<meta name="description" content="Web designer serving professional-services firms in every province and territory across Canada. Custom-coded websites, $0 down, $199/month all-inclusive." />
<link rel="canonical" href="https://matthewmcguire.ca/locations.html" />
<link rel="icon" href="mm-favicon.svg" type="image/svg+xml" />
<link rel="icon" href="mm-favicon.png" />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://matthewmcguire.ca/locations.html" />
<meta property="og:title" content="Web Designer Across Canada — Matthew McGuire" />
<meta property="og:description" content="Custom-coded websites for firms in every province and territory across Canada." />
<meta name="twitter:card" content="summary_large_image" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,400;1,500;1,600;1,700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />

<script async src="https://www.googletagmanager.com/gtag/js?id=G-CR8009ZP6T"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {{ dataLayer.push(arguments); }}
    gtag('js', new Date());
    gtag('config', 'G-CR8009ZP6T');
</script>

<style>
{styles_root}

.loc-hero {{
    padding: clamp(80px, 9vw, 140px) 0 clamp(40px, 5vw, 72px);
    background:
        linear-gradient(100deg, var(--paper) 0%, var(--paper) 50%,
            color-mix(in oklch, var(--paper) 30%, transparent) 100%),
        url('img/hero-pnw-5.jpg') right center / cover no-repeat,
        var(--paper);
}}
.loc-hero h1 {{
    font-family: var(--serif); font-style: italic; font-weight: 700;
    font-size: clamp(40px, 5.6vw, 80px); letter-spacing: -0.022em;
    line-height: 1.04; color: var(--ink); margin: 18px 0 24px; max-width: 18ch;
}}
.loc-hero h1 em {{ font-style: italic; color: var(--rust-deep); }}
.loc-hero .lede {{ max-width: 60ch; }}
.loc-grid {{ padding: clamp(60px, 8vw, 110px) 0; }}
.prov-block {{
    border-top: 1px solid var(--rule);
    padding: 44px 0 36px;
    display: grid; grid-template-columns: 0.9fr 2.1fr; gap: 40px;
    scroll-margin-top: 90px;
}}
.prov-block:first-of-type {{ border-top: none; }}
.prov-h {{
    font-family: var(--serif); font-style: italic; font-weight: 600;
    font-size: clamp(28px, 3vw, 38px); color: var(--ink); letter-spacing: -0.016em;
    line-height: 1.1;
}}
.prov-h-sub {{
    font-family: var(--mono); font-size: 11px; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--ink-3); margin-top: 8px;
}}
.prov-cities {{
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 4px 28px;
}}
.prov-cities a {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 11px 0; font-size: 15px; color: var(--ink-2);
    border-bottom: 1px solid var(--rule-soft);
    transition: color 180ms ease, padding 180ms ease;
}}
.prov-cities a::after {{
    content: "→"; color: var(--ink-3); transition: transform 220ms ease, color 200ms ease;
}}
.prov-cities a:hover {{ color: var(--ink); padding-left: 4px; }}
.prov-cities a:hover::after {{ transform: translateX(4px); color: var(--rust); }}
@media (max-width: 880px) {{
    .prov-block {{ grid-template-columns: 1fr; gap: 18px; }}
    .prov-cities {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<div class="masthead">
    <div class="wrap masthead-inner">
        <span class="masthead-edition">Web Design Studio &middot; Edmonton</span>
        <span class="masthead-meta">Vol. I &middot; MMXXVI</span>
    </div>
</div>

<header class="nav" id="site-nav">
    <div class="wrap nav-inner">
        <a href="index.html" class="nav-mark" aria-label="Matthew McGuire — home">
            <span class="nav-mark-letters">Matthew McGuire</span>
            <span class="nav-mark-name">Designer · developer</span>
        </a>
        <nav class="nav-links" aria-label="Primary">
            <a href="index.html">Home</a>
            <a href="about.html">About</a>
            <a href="work.html">Work</a>
            <a href="how.html">How I work</a>
            <a href="pricing.html">Pricing</a>
{nav_dropdown_root}
            <a href="contact.html">Contact</a>
        </nav>
        <a href="contact.html" class="nav-cta">Start a project →</a>
        <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="nav-mobile">
            <span class="nav-toggle-bars" aria-hidden="true"></span>
        </button>
    </div>
</header>

<aside class="nav-mobile" id="nav-mobile" aria-label="Mobile menu">
    <ul class="nav-mobile-links">
        <li><a href="index.html">Home</a></li>
        <li><a href="about.html">About</a></li>
        <li><a href="work.html">Work</a></li>
        <li><a href="how.html">How I work</a></li>
        <li><a href="pricing.html">Pricing</a></li>
        <li><button type="button" class="nm-loc-trigger" aria-haspopup="true" aria-controls="nav-mobile-locations" aria-expanded="false">Locations <span class="nm-loc-chev" aria-hidden="true">→</span></button></li>
        <li><a href="contact.html">Contact</a></li>
    </ul>
    <a href="contact.html" class="nav-mobile-cta">Start a project →</a>
</aside>

<aside class="nav-mobile-locations" id="nav-mobile-locations" aria-label="Locations menu" aria-hidden="true">
    <button type="button" class="nm-loc-back" aria-label="Back to main menu">
        <span class="nm-loc-back-arrow" aria-hidden="true">←</span>
        <span class="nm-loc-back-label">Back</span>
    </button>
    <div class="nm-loc-content">
        <p class="eyebrow">Locations</p>
        <h2 class="nm-loc-h">Web designer <em>across Canada.</em></h2>
{mobile_loc_provinces_root}
        <a href="locations.html" class="nm-loc-all-link">See all locations <span class="arrow">→</span></a>
    </div>
</aside>

<main id="main">

<section class="loc-hero">
    <div class="wrap">
        <p class="eyebrow">Locations</p>
        <h1>Web designer serving firms <em>across Canada.</em></h1>
        <p class="lede">The studio is based in Edmonton, but works remotely with professional-services firms in every province and territory. Custom-coded websites, $0 down, $199 a month all-inclusive (12-month minimum) — or $3,800 lump sum if you'd rather own the site outright.</p>
    </div>
</section>

<section class="loc-grid">
    <div class="wrap">
{prov_blocks}
    </div>
</section>

<section class="section section-cta">
    <div class="wrap cta-band">
        <p class="eyebrow">Start a project</p>
        <h2 class="display cta-band-h">Don't see your city? The studio works everywhere there's a firm worth building for.</h2>
        <p class="cta-band-sub">If your practice is anywhere in Canada, send a few sentences about your firm. The remote workflow handles the rest.</p>
        <div class="cta-band-actions">
            <a href="contact.html" class="btn btn-primary">Start a project <span class="arrow">→</span></a>
            <a href="pricing.html" class="btn btn-secondary">See pricing <span class="arrow">→</span></a>
        </div>
    </div>
</section>

</main>

<footer class="footer">
    <div class="wrap">
        <div class="footer-grid">
            <div>
                <p class="footer-brand">Matthew McGuire</p>
                <p class="footer-blurb">Small firms deserve websites that feel like the work behind them. That's what the studio is for.</p>
                <p class="footer-credit"><span class="footer-credit-dot" aria-hidden="true"></span>Canadian owned &middot; Based in Edmonton, Alberta</p>
            </div>
            <div class="footer-col">
                <h5 class="footer-h5">Site</h5>
                <ul>
                    <li><a href="about.html">About</a></li>
                    <li><a href="work.html">Selected work</a></li>
                    <li><a href="how.html">How I work</a></li>
                    <li><a href="pricing.html">Pricing</a></li>
                    <li><a href="faq.html">FAQ</a></li>
                    <li><a href="locations.html">All locations</a></li>
                    <li><a href="contact.html">Contact</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h5 class="footer-h5">Reach</h5>
                <ul>
                    <li><a href="mailto:matt@mattmcguiredesign.com">matt@mattmcguiredesign.com</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h5 class="footer-h5">Based</h5>
                <ul>
                    <li>Edmonton, Alberta</li>
                    <li>Working with firms across Canada</li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <span>© <span id="footer-year">2026</span> Matthew McGuire. All rights reserved.</span>
            <span class="footer-bottom-links">
                <a href="privacy.html">Privacy</a><span class="dot">·</span><a href="terms.html">Terms</a>
            </span>
            <span>Designed &amp; built by hand</span>
        </div>
    </div>
</footer>

<script>
    var nav = document.getElementById('site-nav');
    if (nav) {{
        var onScroll = function () {{
            if (window.scrollY > 12) nav.classList.add('scrolled');
            else nav.classList.remove('scrolled');
        }};
        window.addEventListener('scroll', onScroll, {{ passive: true }});
        onScroll();
    }}
    var yearEl = document.getElementById('footer-year');
    if (yearEl) yearEl.textContent = new Date().getFullYear();

    var navToggle = document.querySelector('.nav-toggle');
    var navMobile = document.querySelector('.nav-mobile');
    var navMobileLoc = document.querySelector('.nav-mobile-locations');
    function setLoc(open) {{
        document.body.classList.toggle('nav-loc-open', open);
        if (navMobileLoc) navMobileLoc.setAttribute('aria-hidden', open ? 'false' : 'true');
        var trig = document.querySelector('.nm-loc-trigger');
        if (trig) trig.setAttribute('aria-expanded', open ? 'true' : 'false');
    }}
    function setNav(open) {{
        document.body.classList.toggle('nav-open', open);
        if (!open) setLoc(false);
        if (navToggle) {{
            navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        }}
    }}
    if (navToggle) navToggle.addEventListener('click', function () {{
        setNav(!document.body.classList.contains('nav-open'));
    }});
    document.addEventListener('keydown', function (e) {{
        if (e.key === 'Escape') {{
            if (document.body.classList.contains('nav-loc-open')) setLoc(false);
            else if (document.body.classList.contains('nav-open')) setNav(false);
        }}
    }});
    if (navMobile) navMobile.querySelectorAll('a').forEach(function (a) {{
        a.addEventListener('click', function () {{ setNav(false); }});
    }});
    document.querySelectorAll('.nm-loc-trigger').forEach(function (b) {{
        b.addEventListener('click', function () {{ setLoc(true); }});
    }});
    document.querySelectorAll('.nm-loc-back').forEach(function (b) {{
        b.addEventListener('click', function () {{ setLoc(false); }});
    }});
    if (navMobileLoc) navMobileLoc.querySelectorAll('a').forEach(function (a) {{
        a.addEventListener('click', function () {{ setLoc(false); setNav(false); }});
    }});

    document.addEventListener('click', function (e) {{
        var a = e.target.closest('a');
        if (!a) return;
        var href = a.getAttribute('href');
        if (!href) return;
        if (
            a.target === '_blank' ||
            e.metaKey || e.ctrlKey || e.shiftKey || e.altKey ||
            href.charAt(0) === '#' ||
            href.indexOf('mailto:') === 0 ||
            href.indexOf('tel:') === 0 ||
            a.hasAttribute('download')
        ) return;
        var url = new URL(a.href, window.location.href);
        if (url.origin !== window.location.origin) return;
        if (url.pathname === window.location.pathname) return;
        e.preventDefault();
        document.body.classList.add('is-leaving');
        setTimeout(function () {{ window.location.href = a.href; }}, 220);
    }});
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
            f'                <a href="locations/{slug}.html">{name} web designer<span></span></a>'
            for slug, name, _intro in cities
        )
        blocks.append(f"""
        <div class="prov-block" id="{abbr.lower()}">
            <div>
                <h2 class="prov-h">{prov}</h2>
                <p class="prov-h-sub">{len(cities)} {'city' if len(cities) == 1 else 'cities'}</p>
            </div>
            <div class="prov-cities">
{rows}
            </div>
        </div>""")
    html = LOCATIONS_INDEX.format(
        styles_root=styles_for_root(),
        nav_dropdown_root=desktop_dropdown_for_root(active=True),
        prov_blocks="\n".join(blocks),
        mobile_loc_provinces_root=mobile_loc_provinces_html("locations/"),
    )
    path = ROOT / "locations.html"
    path.write_text(html, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# SITEMAP
# ---------------------------------------------------------------------------

def build_sitemap() -> Path:
    today = date.today().isoformat()
    base = "https://matthewmcguire.ca/"
    main_pages = [
        ("", 1.0),
        ("about.html", 0.8),
        ("work.html", 0.85),
        ("how.html", 0.75),
        ("pricing.html", 0.9),
        ("faq.html", 0.7),
        ("locations.html", 0.85),
        ("contact.html", 0.8),
        ("privacy.html", 0.4),
        ("terms.html", 0.4),
        ("skills.html", 0.6),
        ("work/fwsllp/", 0.7),
        ("work/kjicpa/", 0.7),
        ("work/sockettlaw-squarespace/", 0.7),
    ]
    urls = []
    for path, prio in main_pages:
        urls.append(
            f"  <url>\n    <loc>{base}{path}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n    <priority>{prio}</priority>\n  </url>"
        )
    for prov, abbr, cities in CITIES:
        for slug, _name, _intro in cities:
            urls.append(
                f"  <url>\n    <loc>{base}locations/{slug}.html</loc>\n"
                f"    <lastmod>{today}</lastmod>\n    <priority>0.6</priority>\n  </url>"
            )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n"
    )
    path = ROOT / "sitemap.xml"
    path.write_text(sitemap, encoding="utf-8")
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
