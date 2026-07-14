# -*- coding: utf-8 -*-
"""Generate the /features/ sub-pages in the Business Growth System design language.

Run:  python gen_features.py
Writes one standalone HTML file per feature into features/.
Edit PAGES below and re-run to regenerate. All copy must stay 100% factual —
product-truth claims only, no invented stats or testimonials.
"""
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "features")

# ---------------------------------------------------------------- icons
IC = {
    "phone":    '<path d="M4 5a2 2 0 0 1 2-2h2l1.5 4-2 1.5a12 12 0 0 0 6 6l1.5-2 4 1.5V18a2 2 0 0 1-2 2A15 15 0 0 1 4 5z"/>',
    "headset":  '<path d="M4 12a8 8 0 0 1 16 0v4a2 2 0 0 1-2 2h-2v-6h4M4 12v4a2 2 0 0 0 2 2h2v-6H4"/>',
    "chat":     '<path d="M21 11.5a7.5 7.5 0 0 1-10.9 6.7L4 20l1.8-5.1A7.5 7.5 0 1 1 21 11.5z"/>',
    "star":     '<path d="M12 3l2.6 5.3 5.9.9-4.2 4.1 1 5.8L12 16.9 6.7 19.2l1-5.8L3.5 9.2l5.9-.9z"/>',
    "globe":    '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>',
    "pin":      '<path d="M12 21s7-6.3 7-11a7 7 0 1 0-14 0c0 4.7 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "search":   '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "send":     '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>',
    "cal":      '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M8 3v4M16 3v4M4 11h16"/>',
    "chart":    '<path d="M4 20V10M10 20V4M16 20v-8M21 20H3"/>',
    "check":    '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5 5-5.5"/>',
    "refresh":  '<path d="M17 2v6h-6M3 12a9 9 0 0 1 15-6.7L17 8"/><path d="M7 22v-6h6M21 12a9 9 0 0 1-15 6.7L7 16"/>',
    "layers":   '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="8.5" y="14" width="7" height="7" rx="1.5"/><path d="M6.5 10v2h11v-2M12 12v2"/>',
}

def esc(s):
    """HTML-escape raw ampersands in copy strings (entities are not used in data)."""
    return s.replace("&", "&amp;")


def ic(name, cls=""):
    c = ' class="%s"' % cls if cls else ""
    return ('<svg%s viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>') % (c, IC[name])

CHECK = ic("check")

# ---------------------------------------------------------------- page data
# Every claim below is product-truth (mirrors fact-checked copy already live on the site).
# PARKED: AI receptionist axed from the offer (July 2026) — page data kept in
# PARKED_PAGES in case it comes back. Not generated, not linked anywhere.
PARKED_PAGES = [
    {
        "slug": "ai-receptionist",
        "label": "AI Receptionist",
        "icon": "headset",
        "short": "24/7 call answering that qualifies leads and books appointments.",
        "title": "24/7 AI Receptionist for Small Business · Answers Every Call | Northern Peak Systems",
        "desc": "An AI receptionist that answers every call on the first ring, 24/7 — qualifies the caller, books the appointment into your calendar, and texts you the details. Hear it live: 587-415-7649.",
        "eyebrow": "Included · AI Receptionist",
        "h1": 'A 24/7 AI receptionist that <span class="gold">answers every call.</span>',
        "sub": "It picks up on the first ring, day or night — qualifies the caller, books the appointment into your calendar, and texts you the lead before it ever hits voicemail.",
        "split_head": "Your phone gets answered. Every single time.",
        "split_copy": "Most businesses lose leads in the moments they can’t pick up — after hours, on the job, on the other line. The receptionist never has those moments. It answers instantly, has a natural conversation, and does the admin work before the call even ends.",
        "checks": [
            "Answers 24/7, on the first ring",
            "Natural voice — judge it yourself on the live line",
            "Qualifies the caller and captures the details",
            "Books appointments straight into your calendar",
            "Texts you a summary of every call instantly",
            "Knows when to hand off — it won’t fake answers",
        ],
        "mock": """
<div class="mock">
  <div class="mcard">
    <div class="lbl">%(phone)s Call summary · 7:42 PM</div>
    <div class="krow"><span>Caller</span><b>Daniel R.</b></div>
    <div class="krow"><span>Reason</span><b>Needs a quote</b></div>
    <div class="krow"><span>Callback</span><b>587-555-0148</b></div>
    <div class="krow"><span>Booked</span><b>Fri 10:00 AM</b></div>
    <div class="badge">%(check)s Texted to your phone</div>
  </div>
  <div class="mcard note">
    <div class="lbl">%(chat)s SMS to caller</div>
    <p>Hi Daniel! You’re confirmed for Friday at 10:00 AM. Reply here if anything changes.</p>
  </div>
</div>""" % {"phone": ic("phone"), "chat": ic("chat"), "check": CHECK},
        "steps": [
            ("A call comes in", "Any hour, any day. First ring, it answers with your business name and a natural voice."),
            ("It qualifies and books", "Asks the right questions for your business, captures the details, and books the appointment into your real calendar."),
            ("You get the lead by text", "A clean summary lands on your phone the moment the call ends — name, reason, callback number, booking."),
        ],
        "faq": [
            ("Will it sound like a robot?", "Call the live line — 587‑415‑7649 — and judge for yourself. That’s why we lead with it. Natural voice, real conversation, and it knows when it can’t help. If it ever sounds off to you, it’s not going live for your customers."),
            ("Does it work with my current phone number?", "Yes. You keep the number you already have — we point it at the receptionist. Cancel anytime and the number stays yours."),
            ("What happens when it can't answer a question?", "It says so honestly, takes a message, and texts you immediately. It never invents answers about your business."),
        ],
        "cta": "Hear it answer a real call, right now.",
        "cta_sub": "Call the live line, or book a demo and we’ll show it running for your business.",
    },
]

PAGES = [
    {
        "slug": "missed-call-text-back",
        "custom": True,  # hand-built page; excluded from regeneration
        "label": "Missed Call Text-Back",
        "icon": "phone",
        "short": "Instantly respond to missed calls by text, 24/7.",
        "title": "Missed Call Text-Back for Local Business | Northern Peak Systems",
        "desc": "Every missed call gets an instant text-back, so the lead books with you instead of calling the next name on the list. Works 24/7, after hours and weekends. Part of the $297/mo Business Growth System.",
        "eyebrow": "Included · Missed Call Text-Back",
        "h1": 'Miss a call? It <span class="gold">texts them back.</span>',
        "sub": "Everyone misses calls. Few text back. Yours does — instantly — so the lead books with you instead of calling the next name on their list.",
        "split_head": "The lead doesn’t wait. Neither should your reply.",
        "split_copy": "When a call slips — after hours, busy day, bad timing — the system fires a text within seconds. The conversation starts before your competitor’s phone even rings, and every reply lands in one inbox with an alert to your phone.",
        "checks": [
            "Instant text the moment a call slips",
            "Runs 24/7 — after hours and weekends",
            "Turns a missed call into a booking",
            "Custom message written for your business",
            "Replies alert your phone immediately",
            "Keeps the lead from moving on to a competitor",
        ],
        "mock": """
<div class="mock">
  <div class="mcard note">
    <div class="lbl">%(phone)s Missed call · 7:52 PM</div>
    <p>Caller hung up before voicemail.</p>
  </div>
  <div class="mcard note">
    <div class="lbl">%(chat)s Auto text-back · 7:52 PM</div>
    <p>Sorry we missed you! Want us to book you in? Reply here and we’ll help.</p>
  </div>
  <div class="mcard note">
    <div class="lbl">%(check)s Reply · 7:53 PM</div>
    <p>Yes please — anything Friday?</p>
  </div>
</div>""" % {"phone": ic("phone"), "chat": ic("chat"), "check": CHECK},
        "steps": [
            ("A call slips through", "After hours, on the job, on the other line — the system sees the missed call instantly."),
            ("The text goes out in seconds", "A friendly, custom message that acknowledges the miss and starts the conversation."),
            ("The lead stays yours", "They reply, you get alerted, and the booking happens with you — not the next name on their list."),
        ],
        "faq": [
            ("How fast does the text go out?", "Within seconds of the missed call — day or night, automatically."),
            ("Can I customize the message?", "Yes. We write it with you during the build so it sounds like your business, not a bot."),
            ("Does it work with my existing number?", "Yes — it runs on the number you already have. Nothing changes for your customers."),
        ],
        "cta": "Try it: call, hang up, watch the text arrive.",
        "cta_sub": "Book a call and watch the text-back fire in real time.",
    },
    {
        "slug": "website",
        "custom": True,  # hand-built page; excluded from regeneration
        "hero_art": True,
        "hero_bg": "custom-websites-hero.webp",
        "label": "Website",
        "icon": "globe",
        "short": "A fast, hand-built website that converts visitors into leads.",
        "title": "Custom Small Business Websites That Convert · Canada | Northern Peak Systems",
        "desc": "A hand-coded, mobile-first website built around one job: turning visitors into booked appointments. Every form and chat becomes a text conversation. Hosting, updates, and local SEO included.",
        "eyebrow": "Included · Website",
        "h1": 'A website that turns visitors into <span class="gold">texts.</span>',
        "sub": "Fast, mobile, and hand-built for you — every button, form, and chat is wired to text you and the lead, not bury a message in an inbox nobody checks.",
        "split_head": "Hand-coded. Not a template on rented software.",
        "split_copy": "We build your site from scratch — no page builders, no bloat — so it loads fast, ranks locally, and looks like your business instead of everyone else’s. And because it’s wired into the rest of the system, every visitor action becomes a text thread you can actually close.",
        "checks": [
            "Built for you — not a template",
            "Fast load times, mobile-first",
            "Forms and chat become text conversations",
            "Optimized for local Google searches",
            "Hosting, updates, and changes included",
            "Every lead lands on your phone by text",
        ],
        "mock": """
<div class="mock">
  <div class="mcard">
    <div class="lbl">%(globe)s Your website</div>
    <div class="krow"><span>Visitor</span><b>Taps “Book now”</b></div>
    <div class="krow"><span>Contact form</span><b>Fires a text, not an email</b></div>
    <div class="badge">%(check)s Lead texted to your phone</div>
  </div>
  <div class="mcard note">
    <div class="lbl">%(chat)s To the lead</div>
    <p>Thanks! We’ve got your request — someone will text you right back.</p>
  </div>
</div>""" % {"globe": ic("globe"), "chat": ic("chat"), "check": CHECK},
        "steps": [
            ("We learn your business", "A short intake covers your services, area, photos, and what makes you the right call."),
            ("We build it by hand", "Custom design and code, written for speed and local search — done in 7–10 days as part of your system build."),
            ("It starts converting", "Every button and form is wired to the text-back and follow-up system from day one."),
        ],
        "faq": [
            ("I already have a website. Do I have to replace it?", "No. We can build you a new site as part of the $297 — or wire the automations onto the site you’ve got."),
            ("Who owns the website?", "It’s built for your business and runs as part of your system. No long-term contract — if you leave, you keep your domain and content."),
            ("Are changes extra?", "No. Updates and changes are included in the flat monthly price — just ask."),
        ],
        "cta": "See what a site built to convert looks like.",
        "cta_sub": "Book a call and we’ll walk you through real builds.",
    },
    {
        "slug": "review-automation",
        "custom": True,
        "label": "Review Automation",
        "icon": "star",
        "short": "Get more 5-star Google reviews on autopilot.",
        "title": "Google Review Automation for Local Business | Northern Peak Systems",
        "desc": "The system asks every happy customer for a Google review at the right moment and reminds them until they leave it — so your profile fills up on autopilot and you outrank competitors.",
        "eyebrow": "Included · Review Automation",
        "h1": 'Turn happy customers into <span class="gold">five-star reviews.</span>',
        "sub": "The system asks for the review at the right moment and reminds them until they leave it — so your Google profile fills up on autopilot.",
        "split_head": "Reviews win the customers you never meet.",
        "split_copy": "Before anyone calls you, they compare you. A steady stream of recent five-star reviews is what makes them pick your name — and the reason most businesses don’t have one is simply that nobody asks. The system asks, politely and persistently, every time.",
        "checks": [
            "Asks automatically, at the right time",
            "Guides customers straight to your Google profile",
            "Gentle reminders until the review is left",
            "Every review request goes out by text",
            "More recent reviews, better local ranking",
            "Works for past customers too — not just new ones",
        ],
        "mock": """
<div class="mock">
  <div class="mcard">
    <div class="lbl">%(star)s New Google review</div>
    <div class="stars">★★★★★</div>
    <p class="quote">“Answered right away and booked me the same day. Couldn’t recommend them more.”</p>
    <div class="badge">%(check)s Posted to your profile</div>
  </div>
  <div class="mcard note">
    <div class="lbl">%(chat)s Review request · sent by text</div>
    <p>Thanks for choosing us! Mind sharing your experience? It takes 30 seconds: [your review link]</p>
  </div>
</div>""" % {"star": ic("star"), "chat": ic("chat"), "check": CHECK},
        "steps": [
            ("The job wraps up", "You mark the customer done — or the system picks it up from your calendar."),
            ("The ask goes out", "A friendly text with your direct Google review link, followed by gentle reminders until it’s done."),
            ("Your profile compounds", "Every new review makes the next customer’s choice easier — and helps your local ranking."),
        ],
        "faq": [
            ("Do the requests annoy customers?", "No — the messages are short, polite, and spaced out. Happy customers usually just need the link and a nudge."),
            ("Is this allowed by Google?", "Asking customers for honest reviews is fine. We don’t buy reviews, post fake ones, or offer incentives — that’s against Google’s rules and we don’t touch it."),
            ("Can it ask my past customers too?", "Yes — we can run a catch-up campaign to your existing customer list when you launch."),
        ],
        "cta": "Start stacking five-star reviews.",
        "cta_sub": "Book a call and see the review engine running.",
    },
    {
        "slug": "lead-follow-up",
        "label": "Lead Follow-Up",
        "icon": "chat",
        "short": "Automated SMS & email follow-up that converts more leads.",
        "title": "Automated Lead Follow-Up by SMS & Email | Northern Peak Systems",
        "desc": "Every lead gets an instant text, every unclosed quote gets chased, and it all lives in one pipeline — so nothing falls through the cracks. Part of the $297/mo Business Growth System.",
        "eyebrow": "Included · Lead Follow-Up",
        "h1": 'Chase the leads most businesses <span class="gold">let slip.</span>',
        "sub": "Every lead gets an instant text, unclosed business gets followed up, and it all lives in one pipeline so nothing falls through the cracks.",
        "split_head": "Speed wins the lead. Persistence wins the job.",
        "split_copy": "The first business to respond usually gets the work — and the quote that never gets a second touch usually dies. The system does both without you thinking about it: instant response to every new lead, and automatic follow-up on everything still open.",
        "checks": [
            "Instant SMS to every new lead",
            "Follows up on unclosed quotes automatically",
            "Email sequences for longer decisions",
            "One clean pipeline — nothing lost",
            "Instant alerts to your phone",
            "You jump in personally whenever you want",
        ],
        "mock": """
<div class="mock">
  <div class="mcard">
    <div class="lbl">%(phone)s New lead</div>
    <div class="krow"><span>Name</span><b>Sarah K.</b></div>
    <div class="krow"><span>Wants</span><b>Quote · this week</b></div>
    <div class="krow"><span>Source</span><b>Website form</b></div>
    <div class="badge">%(check)s Instant text sent · follow-up scheduled</div>
  </div>
  <div class="mcard note">
    <div class="lbl">%(refresh)s Day 3 · auto follow-up</div>
    <p>Hi Sarah — just checking in on that quote. Want us to pencil you in for this week?</p>
  </div>
</div>""" % {"phone": ic("phone"), "refresh": ic("refresh"), "check": CHECK},
        "steps": [
            ("A lead comes in", "Call, form, or chat — the system captures it and responds by text within seconds."),
            ("Follow-up runs on schedule", "Open leads get texted and emailed at sensible intervals until they book or say no."),
            ("You close the ones that matter", "Every conversation and status lives in one pipeline, with alerts to your phone."),
        ],
        "faq": [
            ("Will it spam my leads?", "No. Messages are spaced out, sound human, and stop the moment someone books or opts out."),
            ("Can I take over a conversation?", "Anytime. Every thread is yours — jump in from your phone and the automation steps aside."),
            ("What counts as a lead?", "Calls, missed calls, website forms, and chat messages all flow into the same pipeline automatically."),
        ],
        "cta": "Stop losing the leads you already paid for.",
        "cta_sub": "Book a call and watch the follow-up engine work.",
    },
    {
        "slug": "local-seo",
        "custom": True,  # hand-built page; excluded from regeneration
        "label": "Local SEO",
        "icon": "search",
        "short": "Rank higher on Google and get found by local customers.",
        "title": "Local SEO & Google Business Profile for Alberta Small Business | Northern Peak Systems",
        "desc": "On-site SEO, technical foundations, and a fully optimized Google Business Profile — built in from launch so local customers actually find you. Included in the $297/mo system.",
        "eyebrow": "Included · Local SEO",
        "h1": 'Get found by the customers <span class="gold">already searching.</span>',
        "sub": "On-site SEO and a fully optimized Google Business Profile, built in from day one — so when someone nearby searches for what you do, you’re the one they find.",
        "split_head": "Local search is where the buying happens.",
        "split_copy": "People searching “near me” aren’t browsing — they’re hiring. We build the technical foundations into your site from launch, optimize your Google Business Profile, and keep both aligned with what your customers actually search for.",
        "checks": [
            "On-site SEO built into every page we ship",
            "Google Business Profile set up and optimized",
            "Fast, mobile-first site — Google rewards it",
            "Local keywords for your city and services",
            "Reviews feed your ranking (see Review Automation)",
            "Honest scope: no backlink schemes, no snake oil",
        ],
        "mock": """
<div class="mock">
  <div class="mcard">
    <div class="lbl">%(search)s Local ranking</div>
    <div class="krow"><span>“your service + your city”</span><b>Climbing</b></div>
    <div class="krow"><span>Google profile</span><b>Optimized</b></div>
    <div class="krow"><span>Site speed</span><b>Fast</b></div>
    <div class="badge">%(check)s Found by local customers</div>
  </div>
  <div class="mcard note">
    <div class="lbl">%(pin)s Google Business Profile</div>
    <p>Complete, accurate, photo-rich, and connected to your review engine — the profile customers trust.</p>
  </div>
</div>""" % {"search": ic("search"), "pin": ic("pin"), "check": CHECK},
        "steps": [
            ("Foundations at launch", "Clean code, fast loads, proper structure, and local keywords — baked into the build, not bolted on."),
            ("Profile optimization", "Your Google Business Profile gets completed, categorized, and connected to your reviews."),
            ("Compounding gains", "New reviews and content keep the profile fresh — the signals Google’s local results reward."),
        ],
        "faq": [
            ("Do you guarantee first-page rankings?", "No — and be wary of anyone who does. We build the real foundations and we’ll tell you straight what’s realistic for your market."),
            ("Is this included or an add-on?", "The on-site SEO and Google Business Profile optimization are included in the $297. No surprise line items."),
            ("How long until I see movement?", "Local results usually take weeks to months depending on competition. Reviews are the fastest lever — which is why the review engine is part of the same system."),
        ],
        "cta": "Be the business local searchers find first.",
        "cta_sub": "Book a call and we’ll look at your local market together.",
    },
    {
        "slug": "marketing-campaigns",
        "label": "Marketing Campaigns",
        "icon": "send",
        "short": "One-click SMS & email campaigns that bring customers back.",
        "title": "One-Click SMS & Email Marketing Campaigns | Northern Peak Systems",
        "desc": "Referral, repeat-customer, and seasonal campaigns you send with one click — texted and emailed to the customer list you already have. Included in the $297/mo Business Growth System.",
        "eyebrow": "Included · Marketing Campaigns",
        "h1": 'Your past customers are your <span class="gold">cheapest leads.</span>',
        "sub": "One-click campaigns bring back past customers and turn them into referrals — texted and emailed to the list you already own.",
        "split_head": "The list you already have is worth money.",
        "split_copy": "Every past customer is a warm lead for repeat work and referrals — most businesses just never reach out. We pre-build the campaigns with you, and when it’s time, sending one takes a single click.",
        "checks": [
            "One-click referral campaigns",
            "Repeat-customer win-back campaigns",
            "Seasonal and promo sends",
            "Goes out by text and email",
            "Written with you — sounds like your business",
            "Replies land in your inbox with phone alerts",
        ],
        "mock": """
<div class="mock">
  <div class="mcard note">
    <div class="lbl">%(send)s Referral campaign · sent</div>
    <p>“Know someone who needs us? Send them our way.” — texted to your past-customer list in one tap.</p>
  </div>
  <div class="mcard">
    <div class="lbl">%(chat)s Replies</div>
    <div class="krow"><span>Mike T.</span><b>“My neighbour needs a quote”</b></div>
    <div class="krow"><span>Dana W.</span><b>“Can you come back this fall?”</b></div>
    <div class="badge">%(check)s Alerts sent to your phone</div>
  </div>
</div>""" % {"send": ic("send"), "chat": ic("chat"), "check": CHECK},
        "steps": [
            ("We build the campaigns with you", "Referral, win-back, and seasonal messages written in your voice during the system build."),
            ("You click send", "Pick the campaign, pick the list, one click. That’s genuinely the whole job."),
            ("The replies come to you", "Every response lands in your inbox and pings your phone — ready to book."),
        ],
        "faq": [
            ("I don't have a customer list. Does this still help?", "The system starts building one from day one — every call, form, and booking adds to it. Campaigns get more valuable every month."),
            ("Is this compliant with Canadian anti-spam rules?", "We set campaigns up to message your own customers and honour opt-outs — and we’ll flag anything that wouldn’t fly under CASL."),
            ("Can I write my own campaigns?", "Absolutely. We’ll load your words in — or draft them for you and you approve."),
        ],
        "cta": "Turn your customer list into this month’s revenue.",
        "cta_sub": "Book a call and we’ll sketch your first campaign together.",
    },
    {
        "slug": "crm-and-booking",
        "custom": True,  # hand-built page; excluded from regeneration
        "label": "CRM & Booking",
        "icon": "cal",
        "short": "One pipeline for every lead, plus booking synced to your calendar.",
        "title": "Simple CRM & Appointment Booking for Small Business | Northern Peak Systems",
        "desc": "Every call, text, and form in one pipeline — plus appointment booking that syncs with your calendar and reminds customers so they actually show up. Included in the $297/mo system.",
        "eyebrow": "Included · CRM & Booking",
        "h1": 'One pipeline. Every lead, call, and <span class="gold">booking.</span>',
        "sub": "Every conversation in one place, every appointment synced to your real calendar, and reminders that make sure customers actually show up.",
        "split_head": "Know where every lead stands, at a glance.",
        "split_copy": "Sticky notes and memory don’t scale. The pipeline shows every lead, what stage it’s at, and what happens next — and because the text-back, follow-up, and booking tools all feed it automatically, it stays current without data entry.",
        "checks": [
            "Every lead and conversation in one place",
            "Fills itself — no manual data entry",
            "Booking synced to the calendar you already use",
            "Automatic appointment reminders cut no-shows",
            "Simple stages: new, quoted, booked, done",
            "Works from your phone",
        ],
        "mock": """
<div class="mock">
  <div class="mcard">
    <div class="lbl">%(layers)s Pipeline</div>
    <div class="krow"><span>New leads</span><b>3</b></div>
    <div class="krow"><span>Quoted</span><b>2</b></div>
    <div class="krow"><span>Booked this week</span><b>4</b></div>
    <div class="badge">%(check)s Updated automatically</div>
  </div>
  <div class="mcard note">
    <div class="lbl">%(cal)s Reminder · sent</div>
    <p>Hi James — reminder: you’re booked for tomorrow at 9:00 AM. Reply if you need to change it.</p>
  </div>
</div>""" % {"layers": ic("layers"), "cal": ic("cal"), "check": CHECK},
        "steps": [
            ("Leads flow in automatically", "Calls, texts, forms, and chats all land in the pipeline the moment they happen."),
            ("Bookings hit your real calendar", "Appointments sync to the calendar you already use — no double-booking, no new app to learn."),
            ("Reminders do the chasing", "Customers get texted before their appointment, so your day doesn’t get wrecked by no-shows."),
        ],
        "faq": [
            ("Do I have to learn a new CRM?", "There’s barely anything to learn — the system fills it in for you, and we walk you through the rest on your launch call. Most owners just work from the text alerts."),
            ("Which calendars does it work with?", "Google Calendar and the common booking setups. Tell us what you run and we’ll wire it up during the build."),
            ("Can my staff use it too?", "Yes — whoever answers leads can work out of the same inbox and pipeline."),
        ],
        "cta": "Never lose track of a lead again.",
        "cta_sub": "Book a call and see the pipeline fill itself.",
    },
]

# ---------------------------------------------------------------- template
CSS = """
@font-face{font-family:'Inter';font-style:normal;font-weight:400;font-display:swap;src:url(/fonts/inter-400-normal.woff2) format('woff2');}
@font-face{font-family:'Inter';font-style:normal;font-weight:500;font-display:swap;src:url(/fonts/inter-500-normal.woff2) format('woff2');}
@font-face{font-family:'Inter';font-style:normal;font-weight:600;font-display:swap;src:url(/fonts/inter-600-normal.woff2) format('woff2');}
@font-face{font-family:'Inter';font-style:normal;font-weight:700;font-display:swap;src:url(/fonts/inter-700-normal.woff2) format('woff2');}
@font-face{font-family:'Plus Jakarta Sans';font-style:normal;font-weight:700;font-display:swap;src:url(/fonts/plus-jakarta-sans-700-normal.woff2) format('woff2');}
@font-face{font-family:'Plus Jakarta Sans';font-style:normal;font-weight:800;font-display:swap;src:url(/fonts/plus-jakarta-sans-800-normal.woff2) format('woff2');}
@font-face{font-family:'Inter';font-style:normal;font-weight:800;font-display:swap;src:url(/fonts/inter-800-normal.woff2) format('woff2');}
:root{
  --bg:#0a0a0c; --bg-2:#0f0f12; --card:#131317; --card-2:#17171c;
  --line:rgba(255,255,255,0.08); --line-2:rgba(255,255,255,0.14);
  --gold:#d2a24c; --gold-2:#e6be6e; --gold-deep:#a97c33;
  --gold-line:rgba(210,162,76,0.28); --gold-soft:rgba(210,162,76,0.12);
  --white:#f5f2ec; --mist:#a9a49a; --mist-2:#7b766c;
  --cream:#f7f5f0; --ink:#16140f; --ink-2:#6f695d; --cream-line:#e8e2d4;
  --sans:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
  --display:'Plus Jakarta Sans','Inter',system-ui,sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased;overflow-x:clip;}
body{font-family:var(--sans);color:var(--white);background:var(--bg);line-height:1.6;overflow-x:clip;overflow-wrap:break-word;}
a{color:inherit;text-decoration:none;}
img{max-width:100%;display:block;}
button{font-family:inherit;cursor:pointer;}
.wrap{max-width:1480px;margin:0 auto;padding:0 clamp(18px,3.2vw,44px);}
.eyebrow{display:inline-block;font-size:11px;font-weight:700;letter-spacing:0.22em;text-transform:uppercase;color:var(--gold);}
.gold{color:var(--gold);}
section{position:relative;}
h1,h2,h3{letter-spacing:-0.02em;}
h1,h2{font-family:var(--display);}
.h-lg{font-size:clamp(28px,3.4vw,46px);font-weight:800;line-height:1.08;margin-top:14px;}
.lede{font-size:clamp(15px,1.25vw,17px);color:var(--mist);margin-top:16px;line-height:1.65;}
.light{background:var(--cream);color:var(--ink);}
.light .lede{color:var(--ink-2);}
.sec{padding:clamp(64px,8vw,110px) 0;}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;font-size:13px;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;padding:12px 58px;border-radius:10px;border:1px solid transparent;transition:transform .2s,background .2s,box-shadow .2s,border-color .2s,color .2s;}
.btn .arr{transition:transform .22s;}
.btn:hover .arr{transform:translateX(4px);}
.btn-gold{background:linear-gradient(180deg,#e0b360,#c2903c);color:#181207;box-shadow:0 16px 40px -14px rgba(210,162,76,0.5);}
.btn-gold:hover{background:linear-gradient(180deg,#eabf6c,#cd9a42);transform:translateY(-2px);box-shadow:0 22px 48px -14px rgba(210,162,76,0.6);}
.btn-line{background:transparent;color:var(--gold);border-color:var(--gold-line);}
.btn-line:hover{border-color:var(--gold);color:var(--gold-2);transform:translateY(-2px);}
.btn-ghost{background:#17171c;color:var(--white);border-color:var(--line-2);}
.btn-ghost:hover{border-color:var(--gold);color:var(--gold);transform:translateY(-2px);}
.btn-dark{background:#16140f;color:#fff;box-shadow:0 16px 38px -18px rgba(0,0,0,0.5);}
.btn-dark:hover{background:#000;transform:translateY(-2px);}
.nav{position:sticky;top:0;z-index:50;background:rgba(10,10,12,0.85);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border-bottom:1px solid var(--line);}
.nav-inner{display:flex;align-items:center;justify-content:space-between;gap:24px;height:76px;}
.brand{display:inline-flex;flex-shrink:0;}
.brand-logo{height:46px;width:auto;display:block;}
.nav-links{display:flex;align-items:center;gap:26px;}
.nav-links > a{font-size:15px;color:#d8d3c9;transition:color .18s;position:relative;padding:6px 0;}
.nav-links > a:hover{color:var(--white);}
.nav-dd{position:relative;}
.nav-dd::after{content:"";position:absolute;top:100%;left:-12px;right:-12px;height:16px;}
.nav-dd-toggle{background:none;border:none;padding:6px 0;font-family:inherit;font-size:15px;color:#d8d3c9;display:inline-flex;align-items:center;gap:5px;cursor:pointer;transition:color .18s;}
.nav-dd-toggle svg{width:10px;height:10px;transition:transform .2s;}
.nav-dd:hover .nav-dd-toggle{color:var(--white);}
.nav-dd:hover .nav-dd-toggle svg{transform:rotate(180deg);}
.nav-dd-menu{position:absolute;top:calc(100% + 12px);left:50%;transform:translateX(-50%) translateY(8px);min-width:190px;background:var(--card-2);border:1px solid var(--line-2);border-radius:12px;padding:8px;display:flex;flex-direction:column;gap:1px;box-shadow:0 26px 54px -22px rgba(0,0,0,0.85);opacity:0;visibility:hidden;transition:opacity .18s ease .25s,transform .18s ease .25s,visibility 0s linear .45s;z-index:70;}
.nav-dd:hover .nav-dd-menu{opacity:1;visibility:visible;transform:translateX(-50%) translateY(0);transition-delay:0s,0s,0s;}
.nav-dd-menu a{display:block;padding:9px 14px;font-size:13.5px;color:var(--mist);border-radius:7px;white-space:nowrap;transition:background .15s,color .15s;}
.nav-dd-menu a:hover{background:rgba(255,255,255,0.05);color:var(--white);}
.nav-dd-menu a.here{color:var(--gold);}
.nav-dd-menu.cols{display:grid;grid-template-columns:1fr 1fr;min-width:300px;}
.nav-dd-menu .dd-all{grid-column:1 / -1;color:var(--gold);border-top:1px solid var(--line);margin-top:5px;padding-top:11px;}
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
.nav-dd-menu a.m2-card.here b{color:#d2a24c;}
.m2-foot{grid-column:span 2;background:#101014;padding:14px 16px;display:flex;gap:12px;align-items:flex-start;}
.m2-foot .chk{width:30px;height:30px;border-radius:50%;background:linear-gradient(180deg,#e0b360,#c2903c);color:#181207;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.m2-foot .chk svg{width:15px;height:15px;}
.m2-foot b{display:block;font-size:12.5px;font-weight:700;color:#fff;}
.m2-foot p{font-size:11px;color:#a9a49a;line-height:1.5;margin-top:3px;white-space:normal;}
.m2-strip{display:flex;gap:14px;margin-top:10px;flex-wrap:wrap;}
.m2-strip span{display:flex;flex-direction:column;align-items:center;gap:3px;font-size:9px;color:#7b766c;}
.m2-strip svg{width:13px;height:13px;color:#d2a24c;}
.nav-cta{display:flex;align-items:center;gap:14px;}
.nav-cta .btn{padding:10px 32px;}
.nav-burger{display:none;width:42px;height:42px;border:1px solid var(--line-2);border-radius:9px;background:transparent;color:var(--white);align-items:center;justify-content:center;}
.nav-burger svg{width:20px;height:20px;}
@media(max-width:1120px){.nav-links,.nav-cta .btn{display:none;}.nav-burger{display:inline-flex;}}
.mnav{position:fixed;inset:0;z-index:60;background:var(--bg);transform:translateY(-100%);transition:transform .4s cubic-bezier(.5,0,.1,1);display:flex;flex-direction:column;padding:24px clamp(22px,6vw,40px);overflow-y:auto;}
.mnav.open{transform:translateY(0);}
.mnav-top{display:flex;align-items:center;justify-content:space-between;height:50px;}
.mnav-close{width:42px;height:42px;border:1px solid var(--line-2);border-radius:9px;background:transparent;color:var(--white);display:flex;align-items:center;justify-content:center;}
.mnav-links{display:flex;flex-direction:column;gap:2px;margin-top:34px;}
.mnav-links a{font-size:clamp(22px,4.6vw,28px);font-weight:700;color:var(--white);padding:9px 0;border-bottom:1px solid var(--line);}
.mnav-foot{margin-top:auto;padding-top:24px;display:flex;flex-direction:column;gap:14px;}
.fhero{overflow:hidden;padding:clamp(48px,6vw,84px) 0;background:var(--bg);}
.fhero-bg{position:absolute;inset:0;z-index:0;pointer-events:none;opacity:.85;}
.fhero-bg img{width:100%;height:100%;object-fit:cover;object-position:center;}
.fhero.fhero-art{display:flex;align-items:center;min-height:min(76vh,720px);}
.fhero.fhero-art > .wrap{width:100%;}
.fhero.fhero-art .fhero-bg{opacity:1;}
.fhero.fhero-art .fhero-bg::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,10,12,0.82) 0%,rgba(10,10,12,0.55) 34%,rgba(10,10,12,0.12) 58%,rgba(10,10,12,0) 74%),linear-gradient(to top,rgba(10,10,12,0.9),rgba(10,10,12,0) 30%);}
.fhero.fhero-art .fhero-grid{grid-template-columns:1fr;}
.fhero.fhero-art .fhero-grid > div:first-child{max-width:600px;}
.fhero .wrap{position:relative;z-index:2;}
.fhero-grid{display:grid;grid-template-columns:1.05fr 0.95fr;gap:clamp(30px,4vw,70px);align-items:center;}
.fhero h1{font-size:clamp(34px,4.2vw,56px);font-weight:800;line-height:1.06;margin:16px 0 14px;}
.fhero-sub{font-size:clamp(15px,1.25vw,17px);color:var(--mist);max-width:50ch;}
.fhero-actions{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin-top:26px;}
.fhero-note{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px;margin-top:16px;font-size:13px;color:var(--mist);}
.fhero-note b{color:var(--white);font-weight:600;}
.crumbs{font-size:12px;color:var(--mist-2);margin-bottom:18px;}
.crumbs a:hover{color:var(--gold);}
.mock{display:flex;flex-direction:column;gap:14px;max-width:460px;margin-left:auto;}
.mcard{background:linear-gradient(180deg,#15151a,#101014);border:1px solid var(--gold-line);border-radius:14px;padding:18px 20px;box-shadow:0 24px 50px -26px rgba(0,0,0,0.85);}
.mcard .lbl{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--gold);margin-bottom:10px;display:flex;align-items:center;gap:7px;}
.mcard .lbl svg{width:15px;height:15px;flex-shrink:0;}
.krow{display:flex;justify-content:space-between;gap:14px;font-size:13.5px;padding:6px 0;border-top:1px solid var(--line);}
.krow:first-of-type{border-top:none;}
.krow span{color:var(--mist);}
.krow b{color:var(--white);font-weight:600;text-align:right;}
.mcard.note p,.mcard p.quote{font-size:13.5px;color:#d8d3c9;line-height:1.55;}
.mcard .stars{color:var(--gold);letter-spacing:3px;font-size:15px;margin-bottom:8px;}
.badge{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;color:#6cc08a;margin-top:10px;}
.badge svg{width:15px;height:15px;flex-shrink:0;}
@media(max-width:1000px){.fhero-grid{grid-template-columns:1fr;}.mock{margin:0 auto;}}
.split{display:grid;grid-template-columns:0.9fr 1.1fr;gap:clamp(30px,4vw,64px);align-items:center;}
.split-checks{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:12px;}
.split-checks li{display:flex;align-items:flex-start;gap:10px;font-size:14px;color:var(--ink);font-weight:600;background:#fff;border:1px solid var(--cream-line);border-radius:12px;padding:14px 16px;line-height:1.45;}
.split-checks svg{width:19px;height:19px;color:var(--gold-deep);flex-shrink:0;margin-top:2px;}
@media(max-width:900px){.split{grid-template-columns:1fr;}}
@media(max-width:560px){.split-checks{grid-template-columns:1fr;}}
.steps-grid{display:grid;grid-template-columns:0.75fr 1.7fr;gap:clamp(30px,4vw,64px);align-items:center;}
.steps-row{display:flex;align-items:flex-start;gap:8px;}
.step{flex:1;text-align:center;padding:0 8px;}
.step .circ{position:relative;width:72px;height:72px;border-radius:50%;background:var(--card);border:1px solid var(--gold-line);display:flex;align-items:center;justify-content:center;margin:0 auto 18px;}
.step .circ svg{width:30px;height:30px;color:var(--gold);}
.step .num{position:absolute;top:-6px;right:-6px;width:26px;height:26px;border-radius:50%;background:linear-gradient(180deg,#e0b360,#c2903c);color:#181207;font-size:12px;font-weight:800;display:flex;align-items:center;justify-content:center;border:3px solid var(--bg);}
.step b{display:block;font-size:15.5px;font-weight:700;color:var(--white);}
.step p{font-size:12.5px;color:var(--mist);line-height:1.55;margin-top:6px;max-width:26ch;margin-left:auto;margin-right:auto;}
.step-arr{margin-top:28px;color:rgba(210,162,76,0.5);flex-shrink:0;}
.step-arr svg{width:22px;height:22px;}
@media(max-width:1000px){.steps-grid{grid-template-columns:1fr;}}
@media(max-width:640px){.steps-row{flex-direction:column;gap:28px;}.step-arr{display:none;}}
.xlink-head{text-align:center;max-width:620px;margin:0 auto clamp(30px,4vw,44px);}
.xlink-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}
.xlink{background:#fff;border:1px solid var(--cream-line);border-radius:13px;padding:18px 16px;display:flex;gap:12px;align-items:flex-start;transition:transform .25s,box-shadow .25s,border-color .25s;}
.xlink:hover{transform:translateY(-4px);border-color:#dcc9a2;box-shadow:0 20px 40px -26px rgba(60,45,20,0.35);}
.xlink svg{width:22px;height:22px;color:var(--gold-deep);flex-shrink:0;margin-top:2px;}
.xlink b{display:block;font-size:13.5px;font-weight:700;color:var(--ink);line-height:1.3;}
.xlink span{display:block;font-size:12px;color:var(--ink-2);line-height:1.5;margin-top:4px;}
@media(max-width:1000px){.xlink-grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:520px){.xlink-grid{grid-template-columns:1fr;}}
.faq-grid{display:grid;grid-template-columns:0.8fr 1.5fr;gap:clamp(30px,4vw,64px);align-items:start;}
.faq-list{display:flex;flex-direction:column;gap:12px;}
.faq-list details{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:2px 22px;}
.faq-list summary{list-style:none;cursor:pointer;padding:17px 0;font-weight:700;font-size:15.5px;color:var(--white);display:flex;justify-content:space-between;gap:16px;align-items:center;}
.faq-list summary::-webkit-details-marker{display:none;}
.faq-list summary::after{content:"+";font-size:22px;color:var(--gold);font-weight:400;flex-shrink:0;}
.faq-list details[open] summary::after{content:"\\2013";}
.faq-list p{padding:0 0 18px;color:var(--mist);font-size:14px;line-height:1.7;}
@media(max-width:900px){.faq-grid{grid-template-columns:1fr;}}
.fcta{background:radial-gradient(800px 340px at 50% 115%,rgba(210,162,76,0.18),transparent 70%),var(--bg);border-top:1px solid var(--line);text-align:center;padding:clamp(64px,8vw,104px) 0;}
.fcta h2{font-size:clamp(28px,3.6vw,48px);font-weight:800;line-height:1.08;max-width:20ch;margin:0 auto;}
.fcta p{font-size:clamp(15px,1.3vw,17px);color:var(--mist);margin:16px auto 28px;max-width:48ch;}
.fcta-actions{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;}
.foot{background:#060607;border-top:1px solid var(--line);padding:clamp(56px,7vw,88px) 0 40px;}
.foot-grid{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:clamp(30px,4vw,56px);}
.foot-brand .brand-logo{height:52px;}
.foot-copy{font-size:13px;color:var(--mist-2);line-height:1.7;margin-top:18px;max-width:32ch;}
.foot-col h4{font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:var(--mist-2);margin-bottom:18px;font-weight:700;}
.foot-col a{display:block;font-size:14px;color:var(--mist);padding:6px 0;transition:color .18s;}
.foot-col a:hover{color:var(--gold);}
.foot-bottom{display:flex;flex-wrap:wrap;justify-content:space-between;gap:14px;align-items:center;margin-top:clamp(44px,5vw,64px);padding-top:26px;border-top:1px solid var(--line);font-size:12.5px;color:var(--mist-2);}
.foot-social{display:flex;gap:14px;align-items:center;}
.foot-social a{width:36px;height:36px;border:1px solid var(--line-2);border-radius:9px;display:flex;align-items:center;justify-content:center;color:var(--mist);transition:color .18s,border-color .18s;}
.foot-social a:hover{color:var(--gold);border-color:var(--gold);}
.foot-social svg{width:17px;height:17px;}
@media(max-width:940px){.foot-grid{grid-template-columns:1fr 1fr;}}
@media(max-width:520px){.foot-grid{grid-template-columns:1fr;}}
.reveal{opacity:0;transform:translateY(26px);transition:opacity .7s cubic-bezier(.2,.7,.2,1),transform .7s cubic-bezier(.2,.7,.2,1);}
.reveal.in{opacity:1;transform:none;}
@media(prefers-reduced-motion:reduce){.reveal{opacity:1;transform:none;transition:none;}}
"""

DD_CHEVRON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<polyline points="6 9 12 15 18 9"/></svg>')

ARROW_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')


M2_CARDS = [('website', 'website', 'Custom Website', 'Lead-generating websites built to convert visitors into customers.'), ('review-automation', 'reviews', '5-Star Review Funnel', 'Get more five-star reviews on autopilot and build instant trust.'), ('local-seo', 'seo', 'Local SEO', 'Show up at the top of Google when local customers are searching.'), ('missed-call-text-back', 'textback', 'Missed Call Text Back', 'Never miss another lead. We text back missed calls instantly.'), ('crm-and-booking', 'crm', 'CRM &amp; Booking', 'Manage leads, book jobs, and keep everything organized in one place.'), ('lead-follow-up', 'followup', 'Lead Follow-Up', 'Automated follow-ups via text so you stay top of mind and win more jobs.'), ('marketing-campaigns', 'marketing', 'Marketing Campaigns', 'One-click campaigns that bring past customers back and fill your pipeline.')]
M2_STRIP = [('website', 'Website'), ('search', 'SEO'), ('reviews', 'Reviews'), ('textback', 'Text Back'), ('crm', 'CRM'), ('followup', 'Follow-Up'), ('marketing', 'Marketing')]
M2_ICONS = {'website': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>', 'reviews': '<path d="M12 3l2.6 5.3 5.9.9-4.2 4.1 1 5.8L12 16.9 6.7 19.2l1-5.8L3.5 9.2l5.9-.9z"/>', 'seo': '<path d="M12 21s7-6.3 7-11a7 7 0 1 0-14 0c0 4.7 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>', 'textback': '<path d="M4 5a2 2 0 0 1 2-2h2l1.5 4-2 1.5a12 12 0 0 0 6 6l1.5-2 4 1.5V18a2 2 0 0 1-2 2A15 15 0 0 1 4 5z"/>', 'crm': '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M8 3v4M16 3v4M4 11h16"/>', 'followup': '<path d="M21 11.5a7.5 7.5 0 0 1-10.9 6.7L4 20l1.8-5.1A7.5 7.5 0 1 1 21 11.5z"/>', 'marketing': '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>', 'check': '<path d="M20 6 9 17l-5-5"/>', 'search': '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>'}

def m2svg(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round">' + M2_ICONS[name] + '</svg>')

def features_dd(current_slug):
    """Emit the mega2 panel body (rail + cards); links are ../-relative for feature pages."""
    cards = ''
    for slug, ic, title, desc in M2_CARDS:
        here = ' here' if slug == current_slug else ''
        cards += ('<a href="../features/' + slug + '.html" class="m2-card' + here + '">'
                  '<span class="ic">' + m2svg(ic) + '</span><b>' + title + '</b><span>' + desc + '</span></a>\n                        ')
    strip = ''.join('<span>' + m2svg(k) + lbl + '</span>' for k, lbl in M2_STRIP)
    return ('<div class="mega2-grid">\n'
            '                        <aside class="mega2-rail">\n'
            '                            <span class="m2-eyebrow">The Complete Solution</span>\n'
            '                            <div class="m2-title">Business <span>Growth</span> System</div>\n'
            '                            <p>Everything works together to attract more leads, build trust, and book more jobs.</p>\n'
            '                            <a href="../how.html" class="m2-btn">See How It Works <span class="arr">&rarr;</span></a>\n'
            '                        </aside>\n'
            '                        <div class="mega2-cards">\n'
            '                        ' + cards + '<div class="m2-foot">\n'
            '                            <span class="chk">' + m2svg('check') + '</span>\n'
            '                            <div>\n'
            '                                <b>Everything Working Together</b>\n'
            '                                <p>One connected system designed to attract, convert, and retain more customers so you can focus on the work.</p>\n'
            '                                <div class="m2-strip">' + strip + '</div>\n'
            '                            </div>\n'
            '                        </div>\n'
            '                        </div>\n'
            '                    </div>')


def nav_html(current_slug):
    return """<header class="nav">
    <div class="wrap nav-inner">
        <a href="/" class="brand" aria-label="Northern Peak Systems, home">
            <img src="../img/nps-logo-white.webp" alt="Northern Peak Systems" class="brand-logo" width="1432" height="391">
        </a>
        <nav class="nav-links" aria-label="Primary">
            <a href="/">Home</a>
            <div class="nav-dd nav-dd-static">
                <button type="button" class="nav-dd-toggle" aria-haspopup="true">Products %(chev)s</button>
                <div class="nav-dd-menu mega">
                    %(feats)s
                </div>
            </div>
            <a href="../pricing.html">Pricing</a>
            <a href="../about.html">About</a>
            <div class="nav-dd">
                <button type="button" class="nav-dd-toggle" aria-haspopup="true">Studio %(chev)s</button>
                <div class="nav-dd-menu">
                    <a href="../work.html">Work</a>
                    <a href="../how.html">How we work</a>
                    <a href="../faq.html">FAQ</a>
                    <a href="../blog/">Blog</a>
                </div>
            </div>
            <div class="nav-dd">
                <button type="button" class="nav-dd-toggle" aria-haspopup="true">Locations %(chev)s</button>
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
            <a href="../contact.html" class="btn btn-line">Book a Call</a>
            <button type="button" class="nav-burger" id="burger" aria-label="Open menu" aria-expanded="false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="7" x2="21" y2="7"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="17" x2="21" y2="17"/></svg>
            </button>
        </div>
    </div>
</header>

<div class="mnav" id="mnav" inert>
    <div class="mnav-top">
        <span class="brand"><img src="../img/nps-logo-white.webp" alt="Northern Peak Systems" class="brand-logo" width="1432" height="391"></span>
        <button type="button" class="mnav-close" id="mclose" aria-label="Close menu">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>
        </button>
    </div>
    <nav class="mnav-links" aria-label="Mobile">
        <a href="/">Home</a>
        <a href="/#features">Products</a>
        <a href="../pricing.html">Pricing</a>
        <a href="../about.html">About</a>
        <a href="../work.html">Work</a>
        <a href="../locations.html">Locations</a>
        <a href="../contact.html">Contact</a>
    </nav>
    <div class="mnav-foot">
        <a href="../contact.html" class="btn btn-gold">Book a Call <span class="arr">&rarr;</span></a>
    </div>
</div>""" % {"chev": DD_CHEVRON, "feats": features_dd(current_slug)}


FOOTER = """<footer class="foot">
    <div class="wrap">
        <div class="foot-grid">
            <div class="foot-brand">
                <span class="brand"><img src="../img/nps-logo-white.webp" alt="Northern Peak Systems" class="brand-logo" width="1432" height="391"></span>
                <p class="foot-copy">Growth systems that help service businesses capture more leads and grow on autopilot.</p>
            </div>
            <div class="foot-col">
                <h4>Company</h4>
                <a href="../about.html">About</a>
                <a href="../how.html">How it works</a>
                <a href="../work.html">Work</a>
                <a href="../pricing.html">Pricing</a>
                <a href="../blog/">Blog</a>
            </div>
            <div class="foot-col">
                <h4>Features</h4>
                %(feat_links)s
            </div>
            <div class="foot-col">
                <h4>Support</h4>
                <a href="../faq.html">FAQ</a>
                <a href="../contact.html">Contact</a>
                <a href="../locations.html">Locations</a>
                <a href="mailto:matt@northernpeaksystems.ca">Email us</a>
            </div>
        </div>
        <div class="foot-bottom">
            <span>&copy; <span id="yr">2026</span> Northern Peak Systems &middot; Founder-led in Edmonton, Alberta &middot; Serving Canada &amp; the US</span>
            <div class="foot-social">
                <a href="https://www.linkedin.com/in/matthew-mcguire-44666b389" aria-label="LinkedIn" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.5 8.5h-3v11h3v-11zM5 7a1.7 1.7 0 1 0 0-3.4A1.7 1.7 0 0 0 5 7zm15.5 12.5v-6c0-3-1.6-4.4-3.8-4.4-1.7 0-2.5 1-3 1.6V8.5h-3v11h3v-6.1c0-1.4.9-2.1 1.9-2.1s1.9.7 1.9 2.1v6.1h3z"/></svg></a>
                <a href="../privacy.html" aria-label="Privacy" style="width:auto;padding:0 14px;font-size:13px;">Privacy</a>
                <a href="../terms.html" aria-label="Terms" style="width:auto;padding:0 14px;font-size:13px;">Terms</a>
            </div>
        </div>
    </div>
</footer>""" % {"feat_links": "\n                ".join(
    '<a href="/features/%s.html">%s</a>' % (p["slug"], esc(p["label"])) for p in PAGES[:5]
)}

JS = """<script>
document.getElementById('yr').textContent=new Date().getFullYear();
var burger=document.getElementById('burger'),mnav=document.getElementById('mnav'),mclose=document.getElementById('mclose');
function openM(){mnav.classList.add('open');mnav.removeAttribute('inert');burger.setAttribute('aria-expanded','true');document.body.style.overflow='hidden';}
function closeM(){mnav.classList.remove('open');mnav.setAttribute('inert','');burger.setAttribute('aria-expanded','false');document.body.style.overflow='';}
burger.addEventListener('click',openM);
mclose.addEventListener('click',closeM);
mnav.querySelectorAll('a').forEach(function(a){a.addEventListener('click',closeM);});
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:0.12});
document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});
</script>"""


def steps_html(page):
    parts = []
    for i, (title, text) in enumerate(page["steps"], 1):
        parts.append("""<div class="step">
                    <div class="circ"><span class="num">%d</span>%s</div>
                    <b>%s</b>
                    <p>%s</p>
                </div>""" % (i, ic(page["icon"]), esc(title), esc(text)))
    arrow = '<div class="step-arr">%s</div>' % ARROW_SVG
    return ("\n                " + arrow + "\n                ").join(parts)


def xlinks_html(current_slug):
    cards = []
    for p in PAGES:
        if p["slug"] == current_slug:
            continue
        cards.append("""<a class="xlink" href="/features/%s.html">%s<div><b>%s</b><span>%s</span></div></a>"""
                     % (p["slug"], ic(p["icon"]), esc(p["label"]), esc(p["short"])))
    return "\n            ".join(cards)


def faq_html(page):
    items = []
    for q, a in page["faq"]:
        items.append("""<details>
                    <summary>%s</summary>
                    <p>%s</p>
                </details>""" % (esc(q), esc(a)))
    return "\n                ".join(items)


def faq_schema(page):
    import json
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a.replace("‑", "-")}}
            for q, a in page["faq"]
        ]
    }, ensure_ascii=False, indent=2)


def page_html(page):
    url = "https://northernpeaksystems.ca/features/%s" % page["slug"]
    schema = """{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Service",
      "@id": "%(url)s#service",
      "name": "%(label)s",
      "serviceType": "%(label)s",
      "description": "%(desc)s",
      "provider": { "@id": "https://northernpeaksystems.ca/#org" },
      "areaServed": { "@type": "Country", "name": "Canada" },
      "url": "%(url)s"
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://northernpeaksystems.ca/" },
        { "@type": "ListItem", "position": 2, "name": "Products", "item": "https://northernpeaksystems.ca/#features" },
        { "@type": "ListItem", "position": 3, "name": "%(label)s", "item": "%(url)s" }
      ]
    }
  ]
}""" % {"url": url, "label": page["label"], "desc": page["desc"].replace('"', "'")}

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="../favicon.ico?v=2" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="../favicon-32.png?v=2">
<link rel="apple-touch-icon" href="../apple-touch-icon.png?v=2">

<title>%(title)s</title>
<meta name="description" content="%(desc)s">

<meta property="og:type" content="website">
<link rel="canonical" href="%(url)s">
<meta property="og:url" content="%(url)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:site_name" content="Northern Peak Systems">
<meta name="twitter:card" content="summary_large_image">

<script type="application/ld+json">
%(schema)s
</script>
<script type="application/ld+json">
%(faq_schema)s
</script>

<style>%(css)s</style>

<script async src="https://www.googletagmanager.com/gtag/js?id=G-CR8009ZP6T"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-CR8009ZP6T');</script>
<script>(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script","wh3e6pv2u4");</script>
</head>
<body>

%(nav)s

<main id="main">

<!-- HERO -->
<section class="fhero%(hero_art_class)s">
    <div class="fhero-bg" aria-hidden="true">
        <img src="../img/%(hero_bg)s" alt="" fetchpriority="high" decoding="async" width="1648" height="954">
    </div>
    <div class="wrap">
        <div class="fhero-grid">
            <div>
                <p class="crumbs"><a href="/">Home</a> &nbsp;/&nbsp; <a href="/#features">Products</a> &nbsp;/&nbsp; %(label)s</p>
                <span class="eyebrow">%(eyebrow)s</span>
                <h1>%(h1)s</h1>
                <p class="fhero-sub">%(sub)s</p>
                <div class="fhero-actions">
                    <a href="../contact.html" class="btn btn-gold">Book a Call <span class="arr">&rarr;</span></a>
                </div>
                <p class="fhero-note"><b>Included in the $297/mo system</b> &middot; No setup fee &middot; Cancel anytime</p>
            </div>
%(hero_visual)s
        </div>
    </div>
</section>

<!-- SPLIT -->
<section class="light sec reveal">
    <div class="wrap">
        <div class="split">
            <div>
                <span class="eyebrow">Why it matters</span>
                <h2 class="h-lg">%(split_head)s</h2>
                <p class="lede">%(split_copy)s</p>
            </div>
            <ul class="split-checks">
                %(checks)s
            </ul>
        </div>
    </div>
</section>

<!-- STEPS -->
<section class="sec reveal">
    <div class="wrap">
        <div class="steps-grid">
            <div>
                <span class="eyebrow">How it works</span>
                <h2 class="h-lg">Running for you in 7&ndash;10 days.</h2>
                <p class="lede">Set up as part of your system build &mdash; we wire it around your business, then walk you through it on the launch call.</p>
            </div>
            <div class="steps-row">
                %(steps)s
            </div>
        </div>
    </div>
</section>

<!-- FAQ -->
<section class="sec reveal" style="padding-top:0;">
    <div class="wrap">
        <div class="faq-grid">
            <div>
                <span class="eyebrow">Questions?</span>
                <h2 class="h-lg">Straight answers.</h2>
                <p class="lede">More in the full FAQ.</p>
                <a href="../faq.html" class="btn btn-ghost" style="margin-top:24px;">View All FAQs <span class="arr">&rarr;</span></a>
            </div>
            <div class="faq-list">
                %(faq)s
            </div>
        </div>
    </div>
</section>

<!-- CROSS-LINKS -->
<section class="light sec reveal">
    <div class="wrap">
        <div class="xlink-head">
            <span class="eyebrow">One system. Everything works together.</span>
            <h2 class="h-lg">The rest of your growth system.</h2>
        </div>
        <div class="xlink-grid">
            %(xlinks)s
        </div>
    </div>
</section>

<!-- FINAL CTA -->
<section class="fcta reveal">
    <div class="wrap">
        <h2>%(cta)s</h2>
        <p>%(cta_sub)s</p>
        <div class="fcta-actions">
            <a href="../contact.html" class="btn btn-gold">Book a Call <span class="arr">&rarr;</span></a>
        </div>
    </div>
</section>

</main>

%(footer)s

%(js)s
</body>
</html>
""" % {
        "title": esc(page["title"]), "desc": esc(page["desc"]), "url": url,
        "schema": schema, "faq_schema": faq_schema(page), "css": CSS,
        "nav": nav_html(page["slug"]), "label": esc(page["label"]),
        "eyebrow": esc(page["eyebrow"]), "h1": page["h1"], "sub": esc(page["sub"]),
        "mock": page["mock"],
        "hero_bg": page.get("hero_bg", "hero-bg.webp"),
        "hero_art_class": " fhero-art" if page.get("hero_art") else "",
        "hero_visual": ("" if page.get("hero_art")
                        else '            <div aria-hidden="true">' + page["mock"] + '</div>'),
        "split_head": esc(page["split_head"]), "split_copy": esc(page["split_copy"]),
        "checks": "\n                ".join("<li>%s%s</li>" % (CHECK, esc(c)) for c in page["checks"]),
        "steps": steps_html(page), "faq": faq_html(page),
        "xlinks": xlinks_html(page["slug"]),
        "cta": esc(page["cta"]), "cta_sub": esc(page["cta_sub"]),
        "footer": FOOTER, "js": JS,
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for page in PAGES:
        if page.get("custom"):
            continue
        path = os.path.join(OUT_DIR, page["slug"] + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(page_html(page))
        print("wrote", path)


if __name__ == "__main__":
    main()
