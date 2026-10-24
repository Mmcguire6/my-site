# -*- coding: utf-8 -*-
"""Generate SEO-optimized Alberta-city landing pages for northernpeaksystems.ca.

Each page targets the high-intent local keyword pattern "[city] web designer"
with a keyword-targeted title/H1/H2 hierarchy, a "{city} at a glance" section built
from sourced local facts (LOCAL), an FAQ block (FAQPage schema), and internal links
to nearby cities.

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
         "Edmonton is home base &mdash; Northern Peak Systems is based here. We build websites, and the follow-up system behind them, for Edmonton plumbers, electricians, HVAC companies, roofers, landscapers, and contractors: the owner-operators and small crews who can't afford to let a call go to voicemail. Your website is built free, and the same team that sets everything up is the one that answers when something needs to change."),
        ("calgary", "Calgary",
         "Calgary homeowners have plenty of contractors to choose from, so the businesses that answer fast and follow up on every quote stand out. We build websites with missed-call text-back and estimate follow-up for Calgary trades, from inner-city renovations to the newer communities on the city's edges. Every demo, build, edit, and launch call happens online or by phone &mdash; no in-person meeting required."),
        ("st-albert", "St. Albert",
         "St. Albert homeowners expect a small, owner-run crew to look as professional online as a big company &mdash; and to reply just as fast. We build the website and the follow-up behind it for St. Albert contractors, plumbers, electricians, and landscapers who are too small for a big-city agency but too busy to answer every call. That's the gap Northern Peak Systems is built for."),
        ("sherwood-park", "Sherwood Park",
         "Sherwood Park is the urban heart of Strathcona County, and the trades working here serve everything from homes in town to rural properties and the County's industrial areas. They all need the same thing: a credible website, a system that texts back every missed call, and local SEO &mdash; without an enterprise budget. Your website is built free, with plans from $97/month and no contracts."),
        ("leduc", "Leduc",
         "Leduc businesses serve a busy corridor south of Edmonton: Edmonton International Airport, the Nisku industrial area, and nearby Beaumont. Customers might find you on a phone in a parking lot or at a desk in an office, so we build fast, mobile-first websites with missed-call text-back and estimate follow-up wired in."),
        ("spruce-grove", "Spruce Grove",
         "For trades serving Spruce Grove, Stony Plain, and rural Parkland County, the work is spread out and the phone rings while you're on a job. We build for home service businesses growing in that market &mdash; contractors adding a second crew, landscapers taking on staff &mdash; with a website and follow-up system that grows with you, from $97/month with no contract."),
        ("airdrie", "Airdrie",
         "Airdrie sits just north of Calgary on the QE2. If you're an owner-operator here &mdash; a solo trade or a small crew running the business from your phone &mdash; a custom website with missed-call text-back and estimate follow-up, without an enterprise budget, is exactly the gap Northern Peak Systems fills."),
        ("red-deer", "Red Deer",
         "Red Deer businesses serve a regional customer base stretching from Olds to Lacombe, and that reach deserves a system that works as hard as you do. We build websites with missed-call text-back and estimate follow-up for central Alberta trades, all remotely: the demo happens over the phone, the preview shows up in your browser, and your site goes live without anyone having to drive Highway 2."),
    ]),
]

# Per-city extras: areas served, nearby city slugs.
# `areas` is a one-line phrase: "Where we work in {name}: {areas}."
# `nearby` is a list of slugs (must exist elsewhere in CITIES).
EXTRAS: dict[str, dict] = {
    # St. Albert and Sherwood Park have their own pages, so Edmonton's line doesn't list them.
    "edmonton":      {"areas": "the mature neighbourhoods around downtown, newer districts like West Henday, Ellerslie and Horse Hill, and the rest of the capital region", "nearby": ["st-albert", "sherwood-park", "leduc"]},
    "calgary":       {"areas": "downtown and the Beltline, established communities like Kensington and Mission, and growth areas like Nolan Hill, Saddle Ridge, Mahogany, Seton and Walden", "nearby": ["airdrie", "red-deer", "edmonton"]},
    "st-albert":     {"areas": "Mission, Braeside along the Sturgeon River, Akinsdale, Erin Ridge, Jensen Lakes, downtown, and the Sturgeon County edge", "nearby": ["edmonton", "sherwood-park", "spruce-grove"]},
    "sherwood-park": {"areas": "Summerwood, Emerald Hills, Salisbury Village, Cambrian Crossing, Lakeland Ridge, Heritage Hills, Glen Allan and Sherwood Heights, plus rural hamlets like Ardrossan, Josephburg and South Cooking Lake", "nearby": ["edmonton", "st-albert", "leduc"]},
    "leduc":         {"areas": "downtown Leduc, Woodbend, West Creek Estates, Black Stone, Meadowview Park and Southfork, plus Beaumont, Nisku and the airport corridor", "nearby": ["edmonton", "sherwood-park", "spruce-grove"]},
    "spruce-grove":  {"areas": "Spruce Grove, Stony Plain, rural Parkland County, and the Acheson area along Highway 16", "nearby": ["edmonton", "st-albert", "leduc"]},
    "airdrie":       {"areas": "Reunion, Sagewood, Kings Heights, Coopers Crossing, Bayside, Ravenswood, Windsong and Old Town, new communities like Southwinds, and nearby Crossfield, Carstairs and Irricana", "nearby": ["calgary", "red-deer", "edmonton"]},
    "red-deer":      {"areas": "downtown, Timberlands North and the city's newest neighbourhoods, plus Sylvan Lake, Lacombe, Blackfalds, Penhold, Innisfail and Olds", "nearby": ["calgary", "edmonton", "airdrie"]},
}

# ---------------------------------------------------------------------------
# LOCAL: what makes each city page about that city (Matt, 2026-10-21: "make it real and per city").
# Every figure is from the linked source (checked 2026-10-21); a percentage marked "(calc)" in a comment
# is our own arithmetic on Statistics Canada counts. Keep it that way: no number goes in without a source,
# and time-sensitive items (rebates, restrictions) stay out unless they're dated in the copy.
#   h / lede  -> heading and intro of the "{name} at a glance" section
#   glance    -> (figure, label, [source keys]) stat tiles
#   cards     -> (title, body HTML, [source keys]) local-conditions cards
#   faqs      -> (question, answer HTML, [source keys]); shown before the general FAQs
#   src       -> key: (label, url)
# ---------------------------------------------------------------------------

def _census(dguid: str) -> str:
    return ("https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?Lang=E&DGUIDlist="
            f"{dguid}&GENDERlist=1&STATISTIClist=1&HEADERlist=0")


CMHC_EDM_CSD = ("https://www03.cmhc-schl.gc.ca/hmip-pimh/en/TableMapChart/Table?TableId=1.1.1.9&GeographyId=0340"
                "&GeographyTypeId=3&DisplayAs=Table&GeograghyName=Edmonton")
IBC_SUMMER_2026 = ("https://www.ibc.ca/news-insights/news/"
                   "summer-storms-across-alberta-saskatchewan-and-manitoba-cause-more-than-1-8-billion-in-insured-losses")

LOCAL: dict[str, dict] = {
    "edmonton": {
        "h": "Floods, deep freezes and a building boom. <em>The phone rings through all of it.</em>",
        "lede": "Edmonton is a big, growing city with a lot of older houses, and its weather sends homeowners to the phone in waves. Here's what that looks like for the trades who work here.",
        "glance": [
            ("1,010,899", "people in Edmonton at the 2021 Census, up 8.3% from 2016", ["census"]),
            ("40.5%", "of occupied homes were built in 1980 or earlier", ["census"]),  # 160,615 of 396,400 (calc)
            ("15,902", "housing starts in the city in 2025, up from 13,484 in 2024", ["cmhc"]),
        ],
        "cards": [
            ("Storm season fills basements",
             "Record rain in June and July 2026 overwhelmed Edmonton's sewers again and again. The Insurance Bureau of Canada put the May 31&ndash;June 2 flooding alone at more than $80 million in insured losses in the Edmonton area. When basements flood, homeowners call down the list of plumbers and restoration crews, and every call that rings out goes to the next name.",
             ["ibc26"]),
            ("Deep freezes mean after-hours calls",
             "In January 2024, Edmonton spent four straight days between -40 and -45°C. The Insurance Bureau of Canada says that cold snap caused more than $180 million in insured damage across Western Canada, much of it from frozen and burst pipes. No-heat and burst-pipe calls don't wait for business hours; a text back within seconds lets the homeowner know you've seen it.",
             ["freeze"]),
            ("Rebates that need a plumber",
             "EPCOR offers up to $800 toward a backwater valve for eligible older homes while funding lasts, and the valve must be installed by a professional plumber whose invoice shows a City of Edmonton business licence or GST number. EPCOR's RainWise pilot adds rebates of up to $2,000 for downspout disconnections, rain barrels and rain gardens. A plain-language page about each program helps homeowners find you.",
             ["epcor", "rainwise"]),
            ("Permits and licences",
             "The City requires a gas permit to install or alter furnaces and water heaters and says contractors must be licensed with the City; businesses based outside Edmonton need an out-of-town business licence. Basement development and flood repairs need permits, while replacing shingles or same-size windows doesn't. If you're licensed and pull permits, say so plainly on your website.",
             ["gas", "bizlic", "reno"]),
        ],
        "faqs": [
            ("Do contractors need a City of Edmonton business licence?",
             "For gas work, yes: the City's gas permit page says contractors must be licensed with the City of Edmonton. Businesses based outside Edmonton apply for an out-of-town (non-resident) business licence, which carries an extra fee. Check the City's business licence page for the rules for your trade.",
             ["gas", "bizlic"]),
            ("Can my website explain EPCOR's backwater valve subsidy?",
             "Yes. If you install backwater valves or do other rebate-eligible work, we can add a page that explains the program in plain language, links to EPCOR's official details, and makes it easy to book you. Unlimited edits mean we can update it whenever the program changes.",
             ["epcor"]),
        ],
        "src": {
            "census": ("Statistics Canada, 2021 Census Profile: Edmonton", _census("2021A00054811061")),
            "cmhc": ("CMHC Housing Market Information Portal", CMHC_EDM_CSD),
            "ibc26": ("Insurance Bureau of Canada, Sep 22, 2026", IBC_SUMMER_2026),
            "freeze": ("Insurance Bureau of Canada, Mar 11, 2024", "https://www.ibc.ca/news-insights/news/western-canada-deep-freeze-causes-over-180-million-in-insured-damage"),
            "epcor": ("EPCOR, Backwater Valve Subsidy", "https://www.epcor.com/ca/en/ab/edmonton/safety/home/flood-prevention-at-home/backwater-valve-subsidy.html"),
            "rainwise": ("EPCOR, RainWise Rebate Program", "https://www.epcor.com/ca/en/ab/edmonton/conservation/incentives/rainwise-stormwater-rebate-program.html"),
            "gas": ("City of Edmonton, Gas Permits", "https://www.edmonton.ca/residential_neighbourhoods/gas-permit"),
            "bizlic": ("City of Edmonton, Business Licences", "https://www.edmonton.ca/business_economy/licences_permits/apply-for-a-business-licence"),
            "reno": ("City of Edmonton, Renovations and Basement Development", "https://www.edmonton.ca/residential_neighbourhoods/renovations-basement-development"),
        },
    },
    "st-albert": {
        "h": "Owner-occupied homes, older houses, <em>and a licence for every contractor.</em>",
        "lede": "St. Albert is a city of owner-occupied houses, a lot of them built in the 1960s and '70s, and it has its own rules for contractors coming in from Edmonton.",
        "glance": [
            ("68,232", "people in St. Albert at the 2021 Census, up 4.0% from 2016", ["census"]),
            ("82.9%", "of households own their home", ["census"]),  # 21,505 of 25,935 (calc)
            ("8,345", "homes built from 1961 to 1980, the city's biggest building period", ["census"]),
        ],
        "cards": [
            ("June 2026: sewers at capacity",
             "On June 21, 2026, heavy rain pushed St. Albert's wastewater system to capacity. With local flooding and sewer backups reported, the City sent an Alberta Emergency Alert asking every resident to stop non-essential water use until the next afternoon. On a day like that, a text back in seconds keeps the homeowner talking to you instead of the next plumber.",
             ["aea", "ban"]),
            ("Your Edmonton licence doesn't count here",
             "Anyone doing business in St. Albert needs a City of St. Albert business licence, including businesses based elsewhere, and a licence from another municipality doesn't count. The out-of-town licence is $683 if issued by April 30, against $150 for a business located in the city, and the fee drops later in the year.",
             ["fees", "apply"]),
            ("Thousands of houses past 45",
             "35% of St. Albert's homes were built in 1980 or earlier, and neighbourhoods like Akinsdale are mostly 1970s and '80s single-family homes. That's thousands of houses now more than 45 years old.",
             ["census", "hoods"]),  # 9,075 of 25,935 (calc)
            ("Permits for the common jobs",
             "St. Albert requires a gas permit for furnaces, boilers and water heaters and a plumbing permit for work like backwater valves; contractors applying need a Certificate of Proficiency number and a City business licence. Decks more than 0.6 m above grade, and basement finishing, need both a development permit and a building permit.",
             ["gas", "decks", "basement"]),
        ],
        "faqs": [
            ("Do I need a St. Albert business licence if I'm based in Edmonton?",
             "Yes. The City of St. Albert says anyone doing business in St. Albert needs a City business licence, including businesses based elsewhere, and a licence from another municipality doesn't count. The out-of-town licence is $683 if issued by April 30, dropping to $512.25 from May 1 and $341.50 from September 1.",
             ["fees", "apply"]),
        ],
        "src": {
            "census": ("Statistics Canada, 2021 Census Profile: St. Albert", _census("2021A00054811062")),
            "aea": ("Alberta Emergency Alert, Jun 21, 2026", "https://www.alberta.ca/aea/cap/2026/06/21/2026-06-21T13_56_15-06_00=CityofSt.Albert=EE0F1336-A979-4E49-AA2D-755F589CA1B8.htm"),
            "ban": ("City of St. Albert, water use ban lifted", "https://stalbert.ca/cosa/news/releases/residents-must-cease-non-essential-water-use-immediately/"),
            "fees": ("City of St. Albert, Licence Types &amp; Fees", "https://stalbert.ca/dev/business/stalbert/licensing/types-and-fees/"),
            "apply": ("City of St. Albert, Apply for a Business Licence", "https://stalbert.ca/dev/business/stalbert/licensing/apply/"),
            "hoods": ("City of St. Albert, Neighbourhoods", "https://stalbert.ca/home/move/neighbourhoods/"),
            "gas": ("City of St. Albert, Gas Permits brochure", "https://stalbert.ca/site/assets/files/5885/gas_permits_brochure.pdf"),
            "decks": ("City of St. Albert, Building a Deck", "https://stalbert.ca/city/approvals/development/decks/"),
            "basement": ("City of St. Albert, Basement Finishing", "https://stalbert.ca/city/approvals/development/basement-finishing/"),
        },
    },
    "calgary": {
        "h": "Hailstorm Alley, a record building year, <em>and a phone that won't stop.</em>",
        "lede": "Calgary grows fast, builds fast, and sits under some of the most expensive hailstorms in Canadian history. That's a lot of calls for the trades who work here.",
        "glance": [
            ("$3.25B", "in insured losses from the August 5, 2024 hailstorm, with more than 130,000 claims", ["hail24"]),
            ("6.2%", "population growth in 2024, by the City's estimate; 1,306,784 people at the 2021 Census", ["growth", "census"]),
            ("27,684", "housing starts across the Calgary metro area in 2025, a record", ["cmhc"]),
        ],
        "cards": [
            ("When hail hits, everyone calls at once",
             "The August 5, 2024 hailstorm mainly hit northern Calgary: $3.25 billion in insured losses, more than 130,000 claims, and nearly 60,000 homes impacted in the Calgary area. The Insurance Bureau of Canada said building supplies and repair contractor services were strained by the scale of it. When demand spikes like that, homeowners call down the list, and a text back in seconds keeps you on it.",
             ["hail24"]),
            ("Class 4 roofs are a real conversation",
             "The City's Climate Ready guide says Class 4 impact-resistant shingles can add about 50% to a roof's cost but cut the chance of damage 15 times, paying for themselves in about 5 years on average. The City's $3,000 Resilient Roofing Rebate has ended, so homeowners weigh that cost on their own, and a clear explanation on your website helps them decide.",
             ["roofs", "rebate"]),
            ("Licences and permits",
             "Calgary requires a City business licence for builders, general contractors, handyman services, landscapers who build, electricians, gasfitters and plumbers, with a surcharge for out-of-town businesses. Replacing roofing materials or same-size windows needs no permit; a furnace or hot water tank needs a gas permit, and an electrical panel needs an electrical permit.",
             ["bizlic", "storm"]),
            ("Growth on the edges",
             "The City's suburban growth report expected 87% of new-community housing growth from 2022 to 2026 in the north, northeast, southeast and south, in communities like Nolan Hill, Livingston, Saddle Ridge, Cornerstone, Cranston, Mahogany, Seton and Walden.",
             ["growthrep"]),
        ],
        "faqs": [
            ("Do I need a City of Calgary business licence?",
             "Most trades do. The City lists builders, general contractors, handyman services, landscapers who build (retaining walls, decks, sprinkler systems, patios), electricians, gasfitters and plumbers among the businesses that need one. Lawn care and snow removal don't, and businesses based outside Calgary pay a non-resident surcharge.",
             ["bizlic"]),
            ("Do I need a permit to replace a roof after hail in Calgary?",
             "Usually not. The City says replacing roofing materials, same-material siding, or same-size windows and doors doesn't need a permit, though switching from shingles to clay roofing does. Replacing a furnace or hot water tank needs a gas permit.",
             ["storm"]),
        ],
        "src": {
            "census": ("Statistics Canada, 2021 Census Profile: Calgary", _census("2021A00054806016")),
            "growth": ("City of Calgary, Economic Outlook, Spring 2026", "https://www.calgary.ca/cfod/finance/corporate-economics/economic-outlook-population-outlook.html"),
            "cmhc": ("CMHC, housing starts, Jan 16, 2026", "https://www.cmhc-schl.gc.ca/media-newsroom/news-releases/2026/housing-starts-december-2025"),
            "hail24": ("Insurance Bureau of Canada, Feb 11, 2025", "https://www.ibc.ca/news-insights/news/cost-of-historic-calgary-hailstorm-continues-to-rise"),
            "roofs": ("City of Calgary, Climate ready measures: Roofs", "https://www.calgary.ca/environment/resources/climate-ready-measures--roofs.html"),
            "rebate": ("Global News, Jun 12, 2025", "https://globalnews.ca/news/11238172/resilient-roofing-calgary-rebate-wont-return"),
            "bizlic": ("City of Calgary, Open a contractor business", "https://www.calgary.ca/for-business/licences/builders-contractors.html"),
            "storm": ("City of Calgary, Damage from storms", "https://www.calgary.ca/emergencies/recover-from-storm-damage.html"),
            "growthrep": ("City of Calgary, Suburban Residential Growth 2022&ndash;2026", "https://www.calgary.ca/content/dam/www/pda/pd/documents/development/PD-Suburban-Residential-Growth-2022-2026-Web-Posting-Final.pdf"),
        },
    },
    "airdrie": {
        "h": "93,957 people and counting. <em>Most of the houses are new.</em>",
        "lede": "Airdrie's own census counted 93,957 residents in April 2026, and the City calls itself the fastest-growing city in Alberta. Most homes here are young and owner-occupied, and the city sits on the corridor the Insurance Bureau of Canada calls Hailstorm Alley.",
        "glance": [
            ("93,957", "residents at Airdrie's April 2026 census, up 4.35% in a year", ["mcensus"]),
            ("1,623", "new-home permits issued by the City in 2025", ["mcensus_pdf"]),
            ("73%", "of homes were built in 2001 or later (2021 Census)", ["census"]),  # 19,140 of 26,295 (calc)
        ],
        "cards": [
            ("Young homes, new owners",
             "About 73% of Airdrie's homes were built in 2001 or later, and about 79% of households own their home. The City issued 1,623 new-home permits in 2025 and forecasts 134,710 residents by 2034. New houses usually still need decks, fences, landscaping and basement development.",
             ["census", "mcensus_pdf", "growth"]),  # 20,850 of 26,295 owners (calc)
            ("In Hailstorm Alley",
             "The Insurance Bureau of Canada describes Hailstorm Alley as running from High River, just south of Calgary, north to central Alberta. The June 13, 2020 hailstorm hit Calgary, Airdrie and Rocky View County, causing almost $1.2 billion in insured damage, and IBC says Alberta has had a major hailstorm every year for the past decade.",
             ["alley", "hail20", "hail26"]),
            ("Licences on both sides of the city line",
             "Contractors working in Airdrie need valid trade certificates and a City of Airdrie business licence: $165 a year if you're based in Airdrie, $503 if you're not, and half price from July 1. Airdrie trades working in Calgary need a Calgary business licence too.",
             ["bizlic", "gas", "cgy_bizlic"]),
            ("Permits for the everyday jobs",
             "Installing or relocating a hot water tank needs a permit, but a like-for-like replacement doesn't. Installing or replacing a furnace needs a gas permit, and underground sprinkler systems need a permit plus a backflow device that's inspected every year.",
             ["plumb", "gas"]),
        ],
        "faqs": [
            ("Do I need an Airdrie business licence if I'm based in Calgary?",
             "Yes. The City of Airdrie says contractors working in Airdrie need a City business licence and valid trade certificates. The non-resident licence is $503 a year (half price from July 1), against $165 for businesses based in Airdrie.",
             ["bizlic", "gas"]),
        ],
        "src": {
            "census": ("Statistics Canada, 2021 Census Profile: Airdrie", _census("2021A00054806021")),
            "mcensus": ("City of Airdrie, Census results", "https://www.airdrie.ca/index.cfm?serviceID=1965"),
            "mcensus_pdf": ("City of Airdrie, Census 2026 results", "https://www.airdrie.ca/getDocument.cfm?ID=13033"),
            "growth": ("City of Airdrie, Population growth", "https://www.airdrie.ca/index.cfm?serviceID=2324"),
            "alley": ("Insurance Bureau of Canada, Oct 10, 2024", "https://www.ibc.ca/news-insights/in-focus/alberta-continues-to-see-large-scale-impacts-from-hailstorms"),
            "hail20": ("Insurance Bureau of Canada, Jul 8, 2020", "https://www.ibc.ca/news-insights/news/insurers-to-pay-a-record-1-2-billion-to-albertans-recovering-from-calgary-hailstorm"),
            "hail26": ("Insurance Bureau of Canada, Jun 23, 2026", "https://www.ibc.ca/news-insights/news/protect-your-property-albertans-urged-to-prepare-for-2026-hail-season"),
            "bizlic": ("City of Airdrie, Business licence fees", "https://www.airdrie.ca/index.cfm?serviceID=2327"),
            "gas": ("City of Airdrie, Gas permits", "https://www.airdrie.ca/index.cfm?serviceID=3007"),
            "plumb": ("City of Airdrie, Plumbing, hot water tanks and irrigation", "https://www.airdrie.ca/index.cfm?serviceID=3008"),
            "cgy_bizlic": ("City of Calgary, Open a contractor business", "https://www.calgary.ca/for-business/licences/builders-contractors.html"),
        },
    },
    "leduc": {
        "h": "A record building year <em>next door to the airport.</em>",
        "lede": "Leduc sits next door to Edmonton International Airport along Highway 2, about 15 minutes south of Edmonton, and 2025 was its biggest building year yet.",
        "glance": [
            ("1,017", "new homes in 2025's building permits, a record year", ["amr"]),
            ("+13.7%", "population growth from 2016 to 2021, to 34,094 people", ["census"]),
            ("49%", "of Leduc's homes were built in 2006 or later (2021 Census)", ["census"]),  # 6,325 of 12,965 (calc)
        ],
        "cards": [
            ("New neighbourhoods, new homeowners",
             "The City's 2025 Annual Monitoring Report counts 1,331 building permits worth $331 million, and 88% of the year's new homes went into Woodbend, West Creek Estates, Black Stone, Meadowview Park and Southfork. Four more neighbourhoods opened: Fraser, Grayson Estates, Anderson and Leduc Landing.",
             ["amr"]),
            ("Beaumont is growing even faster",
             "Next door, Beaumont went from 17,457 people in 2016 to 20,888 in 2021, and the Government of Alberta estimates 26,305 for 2025, up 6.32% in a single year.",
             ["beaumont_census", "beaumont"]),
            ("Cold that doesn't keep office hours",
             "At the Edmonton International Airport weather station next door, Environment Canada's 1981&ndash;2010 climate normals average about 37 days a year with lows below -20°C and about 10 below -30°C. No-heat and frozen-pipe calls come whenever they come, and a text back within seconds lets the homeowner know you've seen it.",
             ["climate"]),
            ("A licence for every business",
             "Every business operating in Leduc needs a City business licence; the non-resident licence for out-of-town businesses is $390 a year. Safety Codes permits are required for electrical, gas, plumbing and HVAC work, contractors apply through the City's CityView portal, and decks 0.6 m or higher need both a development permit and a building permit.",
             ["bizlic", "permits", "deck"]),
        ],
        "faqs": [
            ("Do I need a Leduc business licence if I'm based in Edmonton?",
             "Yes. The City of Leduc says every business operating in Leduc needs a City business licence. A one-year non-resident licence costs $390, or $195 if you apply after October 1.",
             ["bizlic"]),
        ],
        "src": {
            "census": ("Statistics Canada, 2021 Census Profile: Leduc", _census("2021A00054811016")),
            "amr": ("City of Leduc, 2025 Annual Monitoring Report", "https://www.leduc.ca/wp-content/uploads/2026/05/Leduc-2025-Annual-Monitoring-Report.pdf"),
            "beaumont_census": ("Statistics Canada, 2021 Census Profile: Beaumont", _census("2021A00054811013")),
            "beaumont": ("Government of Alberta, Regional Dashboard: Beaumont", "https://regionaldashboard.alberta.ca/region/beaumont/population/"),
            "climate": ("Environment and Climate Change Canada, Climate Normals", "https://api.weather.gc.ca/collections/climate-normals/items?CLIMATE_IDENTIFIER=3012205&f=json"),
            "bizlic": ("City of Leduc, Business Licences", "https://leduc.ca/business-licences-permits"),
            "permits": ("City of Leduc, Permits, Licences &amp; Inspections", "https://www.leduc.ca/residents/housing-building-development/permits-licences-inspections"),
            "deck": ("City of Leduc, Building a Deck brochure", "https://www.leduc.ca/wp-content/uploads/2025/02/Leduc-Deck-Brochure.pdf"),
        },
    },
    "red-deer": {
        "h": "Halfway between Calgary and Edmonton, <em>with a whole region to serve.</em>",
        "lede": "Red Deer sits on the QEII, 150 km from Calgary and 154 km from Edmonton, at the centre of a ring of towns from Olds to Lacombe.",
        "glance": [
            ("100,844", "people in Red Deer at the 2021 Census; the province estimates 115,409 for 2025", ["census", "dash"]),
            ("34%", "of Red Deer's homes were built in 1980 or earlier", ["census"]),  # 13,830 of 40,510 (calc)
            ("60,539", "more people in Sylvan Lake, Lacombe, Blackfalds, Olds, Innisfail and Penhold (2021 Census)", ["region"]),
        ],
        "cards": [
            ("Hail and wind on the doorstep",
             "On August 23, 2026, a large-hail storm caused nearly $40 million in insured damage in central Alberta, according to the Insurance Bureau of Canada; Springbrook, just south of Red Deer, was hit hardest, with siding shredded and windows smashed. In June 2017, winds over 100 km/h caused more than $30 million in insured damage across Red Deer, Innisfail and Pine Lake.",
             ["ibc26", "wind17"]),
            ("A lot of older houses",
             "About a third of Red Deer's occupied homes, 13,830 of them, were built in 1980 or earlier, and the City's community profile says 72% of dwellings were built before 2005. The City's flood advice tells homeowners to install sump pumps and zero reverse flow valves in basement floor drains.",
             ["census", "profile", "flood"]),
            ("One licence to work in the city",
             "Red Deer requires a business licence from anyone providing goods or services in the city, and names &ldquo;a contractor coming in from out of town&rdquo; as an example. The 2026 non-resident licence is $496.20 a year, and contractors need a Red Deer licence to pull permits.",
             ["bizlic", "subtrades"]),
            ("Which jobs need a permit",
             "Replacing a water heater doesn't need a gas permit in Red Deer, but installing any HVAC or hydronic heating system needs a heating permit from a licensed contractor, and new or altered wiring needs an electrical permit. Decks 24 inches or more above the ground need a building permit; fences don't need one.",
             ["subtrades", "respermits"]),
        ],
        "faqs": [
            ("Do I need a Red Deer business licence if I'm based in Lacombe or Sylvan Lake?",
             "Yes. The City of Red Deer requires a business licence from anyone providing goods or services in the city, including contractors coming in from out of town. A full-year non-resident licence is $496.20 in 2026, against $127.65 for a business based in Red Deer.",
             ["bizlic"]),
        ],
        "src": {
            "census": ("Statistics Canada, 2021 Census Profile: Red Deer", _census("2021A00054808011")),
            "dash": ("Government of Alberta, Regional Dashboard: Red Deer", "https://regionaldashboard.alberta.ca/region/red-deer/population/"),
            "region": ("Statistics Canada, 2021 Census Profiles", _census("2021A00054806034,2021A00054808008,2021A00054808009,2021A00054808012,2021A00054808029,2021A00054808031")),
            "profile": ("City of Red Deer, 2025 Community Profile", "https://secure.reddeer.ca/media/reddeerca/business-in-red-deer/economic-development/City-of-Red-Deer-2025-Community-Profile.pdf"),
            "ibc26": ("Insurance Bureau of Canada, Sep 22, 2026", IBC_SUMMER_2026),
            "wind17": ("Canadian Underwriter, June 2017", "https://canadianunderwriter.ca/news/claims/estimated-insured-damage-for-june-storm-in-central-alberta-upwards-of-30-million"),
            "flood": ("City of Red Deer, Flood Resources", "https://reddeer.ca/city-services/ambulance-fire-and-emergencies/emergency-preparedness-and-public-safety/flood-resources/"),
            "bizlic": ("City of Red Deer, Business Licences", "https://reddeer.ca/city-services/licences/business-licences/"),
            "subtrades": ("City of Red Deer, Residential Subtrades permits", "https://reddeer.ca/business/permits-and-inspections/residential-permits-and-applications/residential-subtrades/"),
            "respermits": ("City of Red Deer, Residential Permits", "https://reddeer.ca/business/permits-and-inspections/residential-permits-and-applications/"),
        },
    },
    "sherwood-park": {
        "h": "No business licence, a lot of older houses, <em>and a county that keeps growing.</em>",
        "lede": "Sherwood Park isn't a town or a city: it's the urban part of Strathcona County, and the Province treats it as equivalent to a city. It started as a planned hamlet in the 1950s, and it's still growing.",
        "glance": [
            ("103,829", "residents in Strathcona County at its 2024 census, 75,575 of them in Sherwood Park's urban area", ["census24"]),
            ("86.8%", "of county households own their home (2021 Census)", ["census"]),  # 32,215 of 37,130 (calc)
            ("1 in 3", "county homes were built in 1980 or earlier (2021 Census)", ["census"]),  # 12,165 of 37,130 (calc)
        ],
        "cards": [
            ("No business licence needed",
             "Strathcona County doesn't require business licences and has no extra municipal registration for businesses, unlike neighbouring Edmonton and St. Albert. Running a business from home does need a development permit, and trade permits go through the County's ePermits system.",
             ["bizlic"]),
            ("Like-for-like swaps need no permit",
             "Replacing a furnace or water heater with a similar unit that doesn't change the venting or piping needs no permit in Strathcona County; a replacement that does change them needs a $90 gas permit under the 2026 fee schedule. Decks more than two feet above grade need a building permit, and basement development needs a building permit plus an electrical permit for new wiring.",
             ["fees", "deck", "basement"]),
            ("June 2026 flooding",
             "The County says significant rainfall in June 2026 caused widespread localized flooding across Strathcona County, washing out bridge culverts and closing roads for months. County rules say sump pumps can't connect to the sanitary sewer, and homeowners are responsible for water and sewer pipe repairs between the house and the property line.",
             ["roads", "sump", "pipes"]),
            ("Older streets and newer ones",
             "Sherwood Park's first model homes opened on Birch Avenue in 1955, and about a third of the county's homes were built in 1980 or earlier. The County's 2024 profiles list 37 urban neighbourhoods, from Glen Allan and Sherwood Heights to Summerwood, Cambrian Crossing and Salisbury Village.",
             ["history", "census", "hoods"]),
        ],
        "faqs": [
            ("Do I need a business licence to work in Sherwood Park?",
             "No. Strathcona County says it doesn't require business licences and has no additional registration requirements for businesses. Federal and provincial rules still apply, a home-based business needs a development permit, and trade permits (electrical, plumbing, gas) go through the County's ePermits system.",
             ["bizlic"]),
            ("Is Sherwood Park a city?",
             "Not officially. Sherwood Park is the urban part of Strathcona County, which became a specialized municipality in 1996. The Province treats Sherwood Park and the Urban Service Area around it as equivalent to a city for programs and grants.",
             ["status"]),
        ],
        "src": {
            "census": ("Statistics Canada, 2021 Census Profile: Strathcona County", _census("2021A00054811052")),
            "census24": ("Strathcona County, 2024 municipal census", "https://www.strathcona.ca/council-county/news/news/2024/9/17/census-24-3"),
            "status": ("Strathcona County, A specialized municipality", "https://strathcona.ca/local-government/about-strathcona-county/specialized-municipality-status/"),
            "bizlic": ("Strathcona County, Permits, licenses and registration", "https://www.strathcona.ca/business-and-development/business/supports/start-your-business/permits-licenses-and-registration/"),
            "fees": ("Strathcona County, 2026 Fees, Rates and Charges Bylaw", "https://storagecdn.strathcona.ca/files/files/mco-bylaw-43-2025-2026-fees-rates-and-charges.pdf"),
            "deck": ("Strathcona County, Building an uncovered deck", "https://www.strathcona.ca/your-property-utilities/residential-permits/residential-improvement/building-an-uncovered-deck/"),
            "basement": ("Strathcona County, Basement development", "https://www.strathcona.ca/your-property-utilities/residential-permits/residential-improvement/basement-development/"),
            "roads": ("Strathcona County, 2026 road closures", "https://www.strathcona.ca/transportation-roads/construction/2026-road-closures/"),
            "sump": ("Strathcona County, Sump pumps", "https://www.strathcona.ca/your-property-utilities/water-and-sewer/wastewater/sump-pump/"),
            "pipes": ("Strathcona County, Homeowner pipe repairs", "https://www.strathcona.ca/your-property-utilities/water-and-sewer/water/water-service/homeowner-responsibilities-for-pipe-repairs/"),
            "history": ("Strathcona County, Sherwood Park history: Housing", "https://www.strathcona.ca/council-county/history-and-heritage/places/sherwood-park/history-of-sherwood-park/sherwood-park-history-housing/"),
            "hoods": ("Strathcona County, 2024 neighbourhood profiles", "https://www.strathcona.ca/business-and-development/development/growth-and-change-monitoring/2024-neighbourhood-profiles/"),
        },
    },
    "spruce-grove": {
        "h": "One licence for two towns, <em>and a city still building fast.</em>",
        "lede": "Spruce Grove sits about 11 kilometres west of Edmonton, next to Stony Plain and rural Parkland County. Its homes are young, its permit counts keep climbing, and 2026 brought historic rainfall.",
        "glance": [
            ("38,985", "residents at Spruce Grove's 2023 census, after ten years of 3.41% average yearly growth", ["mcensus"]),
            ("783", "new homes in building permits from January to September 2026", ["permits"]),
            ("4,517", "electrical, plumbing and gas permits issued January to September 2026", ["permits"]),
        ],
        "cards": [
            ("One licence, two communities",
             "Spruce Grove requires a business licence from everyone providing goods or services in the city, contractors and sub-contractors included, and contractors need one to apply for trade permits. Under the Intermunicipal Business Licence Arrangement, Spruce Grove and Stony Plain businesses can get the other community's licence at no charge, and Parkland County businesses can get a $150 flat-rate intermunicipal licence.",
             ["bizlic", "apply"]),
            ("Stony Plain and Parkland County",
             "Stony Plain also licenses every business working in town; for businesses based outside Stony Plain, Spruce Grove and Parkland County, the licence is $440 a year. Parkland County doesn't require a business licence at all, and about 89% of its homes are single-detached houses spread over 2,375 square kilometres.",
             ["stony", "parkland", "parkland_census"]),  # 10,550 of 11,915 (calc)
            ("A young, growing city",
             "About half of Spruce Grove's homes were built in 2006 or later, and the City issued 1,015 residential building permits worth $248 million from January to September 2026, up from 833 over the same months of 2025.",
             ["census", "permits"]),  # 7,105 of 14,275 (calc)
            ("A historically wet 2026",
             "The City called 2026 a year of unprecedented rainfall. The June 21 storm flooded roads and closed Century Road north of Grove Drive, and the wet conditions cost the Boundary Road project about 40 construction days. Back in August 2019, a hailstorm damaged siding and vehicles in west Edmonton, Spruce Grove and Stony Plain.",
             ["rain", "rain_jun", "hail19"]),
        ],
        "faqs": [
            ("Does my Spruce Grove business licence cover Stony Plain?",
             "It can. Under the Intermunicipal Business Licence Arrangement, eligible Spruce Grove and Stony Plain businesses can get the other community's licence at no charge, and Parkland County businesses can get a reduced $150 flat-rate intermunicipal licence. Contractors applying for trade permits in Spruce Grove need a valid Spruce Grove licence.",
             ["apply", "stony", "bizlic"]),
        ],
        "src": {
            "mcensus": ("City of Spruce Grove, Census", "https://www.sprucegrove.org/government/census/"),
            "census": ("Statistics Canada, 2021 Census Profile: Spruce Grove", _census("2021A00054811049")),
            "permits": ("City of Spruce Grove, Safety Codes Permits Summary, Sep 2026", "https://www.sprucegrove.org/media/10065/safety-codes-permits-summary-september-2026.pdf"),
            "bizlic": ("City of Spruce Grove, Business Licensing", "https://www.sprucegrove.org/business/business-licensing"),
            "apply": ("City of Spruce Grove, Apply for a Business Licence", "https://sprucegrove.org/business/business-licensing/apply-for-a-business-licence"),
            "stony": ("Town of Stony Plain, Business Licences", "https://www.stonyplain.com/work/business-licences/"),
            "parkland": ("Parkland County, Business Development Process", "https://www.parklandcounty.com/en/business-and-development/business-development-process.aspx"),
            "parkland_census": ("Statistics Canada, 2021 Census Profile: Parkland County", _census("2021A00054811034")),
            "rain": ("City of Spruce Grove, Oct 13, 2026", "https://www.sprucegrove.org/government/news/historic-rainfall-impacts-boundary-road-completion-revised-to-august-2027/"),
            "rain_jun": ("City of Spruce Grove, Jun 21, 2026", "https://www.sprucegrove.org/government/news/city-crews-responding-to-rainfall-event/"),
            "hail19": ("Insurance Bureau of Canada via Insurance-Canada.ca, Aug 2019", "https://insurance-canada.ca/2019/08/30/ibc-edmonton-hailstorm-millions-insured-damages/"),
        },
    },
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
            <a href="../pricing.html#plans" class="btn btn-gold" data-cta-loc="city-hero">Get Started <span class="arr">→</span></a>
            <a href="../book.html" class="btn btn-ghost" data-cta-loc="city-hero">Book a Demo</a>
        </div>
    </div>
</section>

<!-- LOCAL: sourced facts about this city (LOCAL data) -->
<section class="section section-dark">
    <div class="wrap">
        <span class="eyebrow">{name} at a glance</span>
        <h2 class="section-h">{local_h}</h2>
        <p class="section-lede">{local_lede}</p>
        <ul class="glance">
{local_glance}
        </ul>
        <div class="local-grid">
{local_cards}
        </div>
        <p class="local-areas"><b>Where we work in {name}:</b> {areas}.</p>
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
                <p>A custom website designed for your business and built free, with hosting, security, unlimited edits, local SEO so {name} customers find you on Google, and direct support from our team. Included in every plan.</p>
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

<!-- PROCESS -->
<section class="section section-dark">
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
                <p>You message us when something needs to change: a new hire, a new service, a new photo, new copy. Unlimited edits are included in the monthly fee, and we keep the site and system up to date as your business grows.</p>
            </li>
        </ol>
    </div>
</section>

<!-- PRICING -->
<section class="section section-dark-2">
    <div class="wrap">
        <span class="eyebrow">Pricing</span>
        <h2 class="section-h">{name} pricing, <em>simplified.</em></h2>
        <div class="pricing-row">
            <div class="pricing-card">
                <p class="pricing-card-name">Base System</p>
                <p class="pricing-card-price"><strong>$97</strong>/mo</p>
                <p class="pricing-card-sub">website built free</p>
                <p class="pricing-card-body">We design and build your custom website free. The monthly covers hosting, security, unlimited edits, local SEO, and direct support from our team.</p>
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
<section class="section section-dark">
    <div class="wrap">
        <span class="eyebrow">FAQ</span>
        <h2 class="section-h">{name} <em>questions.</em></h2>
        <dl class="faq-list">
{faq_items}
        </dl>
    </div>
</section>

<!-- NEARBY -->
<section class="section section-dark-2">
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
        <p>Subscribe online in minutes and we handle the setup, or book a free 15-minute demo and we&rsquo;ll build a free custom preview before you decide.</p>
        <div class="hcta-actions">
            <a href="../pricing.html#plans" class="btn btn-gold" data-cta-loc="city-cta">Get Started <span class="arr">→</span></a>
            <a href="../book.html" class="btn btn-dark" data-cta-loc="city-cta">Book a Free Demo</a>
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


# Only the city pages use the LOCAL section; kept out of CITY_STYLES because gen_blog.py and the
# locations index reuse that stylesheet.
LOCAL_STYLES = """
/* LOCAL (sourced, city-specific facts) */
.glance{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(16px,2vw,24px);margin-bottom:clamp(30px,3.6vw,48px);}
.glance li{background:var(--bg-3);border:1px solid var(--line);border-top:2px solid var(--gold);border-radius:16px;padding:clamp(22px,2.4vw,30px);display:flex;flex-direction:column;gap:10px;}
.glance b{font-family:var(--display);font-size:clamp(34px,3.4vw,46px);font-weight:800;color:var(--white);line-height:1;letter-spacing:-0.02em;}
.glance span{font-size:15px;line-height:1.55;color:var(--mist);}
.glance small,.local-card .local-src,.faq-src{font-size:12px;line-height:1.5;color:var(--mist-2);}
.glance small{margin-top:auto;padding-top:4px;}
.glance a,.local-src a,.faq-src a{color:inherit;text-decoration:underline;text-decoration-color:rgba(255,255,255,0.22);text-underline-offset:2px;transition:color .18s;}
.glance a:hover,.local-src a:hover,.faq-src a:hover{color:var(--gold);}
.local-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:clamp(18px,2vw,28px);}
.local-card{background:var(--bg-2);border:1px solid var(--line);border-radius:16px;padding:clamp(24px,2.6vw,34px);display:flex;flex-direction:column;gap:12px;}
.local-card h3{font-family:var(--display);font-size:clamp(20px,1.7vw,24px);font-weight:700;color:var(--white);line-height:1.25;}
.local-card p{font-size:15px;line-height:1.7;color:var(--mist);}
.local-card .local-src{margin-top:auto;padding-top:4px;}
.local-areas{margin-top:clamp(28px,3vw,40px);font-size:15.5px;line-height:1.7;color:var(--mist);max-width:80ch;}
.local-areas b{color:var(--white);font-weight:700;}
.faq-src{display:block;margin-top:10px;}
@media(max-width:860px){.glance,.local-grid{grid-template-columns:1fr;}}
"""

# ---------------------------------------------------------------------------
# SCHEMA
# ---------------------------------------------------------------------------

PLANS = [
    # (name, monthly price, description) - mirrors the Base System / The Peak System cards
    ("Base System", "97",
     "Custom website designed and built free. $97/month covers hosting, security, unlimited edits, "
     "local SEO, and direct support. No setup fees, no contracts."),
    ("The Peak System", "297",
     "Everything in the Base System plus Missed Call Recovery, Estimate Follow-Up, Lead Management & booking, "
     "Reputation Management, and Customer Retention. $297/month flat, no setup fees, no contracts."),
]


def _src_links(slug: str, keys: list[str]) -> str:
    """LOCAL source keys -> linked source labels."""
    src = LOCAL[slug]["src"]
    return " &middot; ".join(
        f'<a href="{htmllib.escape(src[k][1])}" target="_blank" rel="noopener">{src[k][0]}</a>' for k in keys)


def _sources_line(slug: str, keys: list[str]) -> str:
    return ("Source: " if len(keys) == 1 else "Sources: ") + _src_links(slug, keys)


def city_faqs(slug: str, name: str, province: str) -> list[tuple[str, str, str]]:
    """(question, answer HTML, sources HTML) triples, the city's own questions first.
    The visible FAQ and the FAQPage schema both come from here (the schema leaves the sources out)."""
    local = [(q, a, _sources_line(slug, keys)) for q, a, keys in LOCAL[slug]["faqs"]]
    if slug == "edmonton":
        where = ("No. Edmonton is home base, but we work with home service businesses across "
                 f"{province}, and across Canada and the US.")
    else:
        where = ("No. We're based in Edmonton and work with home service businesses across "
                 f"{province}, and across Canada and the US.")
    general = [
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
         "support from our team. The Peak System is $297/month flat and adds Missed Call Recovery, Estimate "
         "Follow-Up, Lead Management &amp; booking, Reputation Management, and Customer Retention. You always "
         "keep your domain and any content you provided."),
    ]
    return local + [(q, a, "") for q, a in general]


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
                for q, a, _sources in city_faqs(slug, name, province)
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
    for q, a, sources in city_faqs(slug, name, province):
        if sources:
            a += f'<span class="faq-src">{sources}</span>'
        out.append(f'            <div class="faq-item">\n'
                   f'                <dt>{q}</dt>\n'
                   f'                <dd>{a}</dd>\n'
                   f'            </div>')
    return "\n".join(out)


def local_glance_html(slug: str) -> str:
    return "\n".join(
        f'            <li><b>{fig}</b><span>{label}</span><small>{_sources_line(slug, keys)}</small></li>'
        for fig, label, keys in LOCAL[slug]["glance"])


def local_cards_html(slug: str) -> str:
    return "\n".join(
        f'            <article class="local-card">\n'
        f'                <h3>{title}</h3>\n'
        f'                <p>{body}</p>\n'
        f'                <p class="local-src">{_sources_line(slug, keys)}</p>\n'
        f'            </article>'
        for title, body, keys in LOCAL[slug]["cards"])


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
        local_h=LOCAL[slug]["h"],
        local_lede=LOCAL[slug]["lede"],
        local_glance=local_glance_html(slug),
        local_cards=local_cards_html(slug),
        styles=CITY_STYLES + LOCAL_STYLES,
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
            Alberta trades don't need a big-agency retainer or a slow, template-heavy website. They need a fast site that shows up when people in their own town search, and a system that answers the leads it brings in. That's what we build: hand-coded websites tuned for local search, paired with missed call recovery, estimate follow-up, lead management and booking, reputation management, and customer retention &mdash; all from our team right here in Edmonton.
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
ROOT_ORDER = ["index.html", "platform.html", "about.html", "how.html", "pricing.html", "faq.html",
              "locations.html", "contact.html", "book.html"]
FEATURE_ORDER = ["website", "missed-call-text-back", "review-automation", "lead-follow-up",
                 "marketing-campaigns", "crm-and-booking"]
PRIORITY = {
    "/": 1.0, "/platform": 0.85, "/about": 0.8, "/how": 0.75, "/pricing": 0.9, "/faq": 0.7,
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
