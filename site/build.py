#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static site generator for Empire State Restoration (fictional NY-statewide
water / fire / mold restoration company). Produces a GitHub-ready static
HTML site with shared design system, per-page SEO meta, JSON-LD schema,
and a 60% service / 40% location+outbound-linking content ratio.
"""
import os, re, json

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://www.empirestaterestoration.com"
PHONE_DISPLAY = "(800) 555-0143"
PHONE_TEL = "+18005550143"
BRAND = "Empire State Restoration"

# ---------------------------------------------------------------- helpers --

def gauge(dial_id, label, value_text, pct=76):
    """Decorative SVG gauge dial used as the site's signature visual motif."""
    r = 33
    circ = 2 * 3.14159265 * r
    dash = circ * pct / 100
    return f"""
    <div class="gauge">
      <div class="gauge__dial">
        <svg viewBox="0 0 78 78" role="img" aria-label="{label}: {value_text}">
          <circle cx="39" cy="39" r="{r}" fill="none" stroke="rgba(255,255,255,.14)" stroke-width="6"/>
          <circle cx="39" cy="39" r="{r}" fill="none" stroke="#F0A202" stroke-width="6"
                  stroke-dasharray="{dash:.1f} {circ:.1f}" stroke-linecap="round"
                  transform="rotate(-90 39 39)"/>
        </svg>
        <div class="gauge__num">{value_text}</div>
      </div>
      <div class="gauge__label">{label}</div>
    </div>"""

def gauges_block(items):
    return '<div class="gauges">' + "".join(gauge(*i) for i in items) + "</div>"

def ticker_items(items):
    return " ".join(f"<span>&#9679;</span> {i}" for i in items)

SERVICES = [
    dict(slug="water-damage-restoration", name="Water Damage Restoration",
         short="24/7 extraction, structural drying and moisture mapping for burst pipes, appliance leaks and roof intrusion."),
    dict(slug="flood-cleanup", name="Flood Cleanup",
         short="Rapid-response flood water extraction, contamination assessment and full structural dry-out after a flood event."),
    dict(slug="fire-damage-restoration", name="Fire &amp; Smoke Damage Restoration",
         short="Soot removal, odor neutralization, and structural rebuild after a residential or commercial fire."),
    dict(slug="mold-remediation", name="Mold Remediation",
         short="Certified containment, air scrubbing and removal of mold colonies caused by hidden moisture."),
    dict(slug="sewage-cleanup", name="Sewage Cleanup",
         short="Category 3 blackwater extraction, sanitization and disposal following backups and septic failures."),
    dict(slug="basement-water-removal", name="Basement Water Removal",
         short="Sump failure and seepage response with dehumidification to stop water damage from spreading upward."),
    dict(slug="storm-damage-restoration", name="Storm Damage Restoration",
         short="Wind, hail and downed-tree damage stabilization, tarping and full restoration after severe weather."),
    dict(slug="commercial-restoration", name="Commercial Restoration",
         short="Minimal-downtime water, fire and mold response for offices, retail, multifamily and industrial sites."),
    dict(slug="insurance-claim-assistance", name="Insurance Claim Assistance",
         short="Documentation, scope-of-loss reporting and direct adjuster coordination so your claim moves faster."),
]

LOCATIONS = [
    dict(slug="new-york-city", name="New York City", region="NYC Metro",
         blurb="Manhattan, Brooklyn, Queens, the Bronx and Staten Island — dense multifamily buildings and aging co-op plumbing."),
    dict(slug="long-island", name="Long Island", region="Nassau &amp; Suffolk Counties",
         blurb="Coastal exposure from Nassau to the East End brings nor'easter surge and high water tables."),
    dict(slug="westchester-county", name="Westchester County", region="Lower Hudson Valley",
         blurb="Older housing stock in Yonkers, New Rochelle and White Plains means frequent pipe and foundation failures."),
    dict(slug="hudson-valley", name="Hudson Valley", region="Mid-Hudson Region",
         blurb="Poughkeepsie, Newburgh and Kingston sit along a flood-prone river corridor with seasonal ice-jam risk."),
    dict(slug="albany-capital-region", name="Albany &amp; the Capital Region", region="Capital District",
         blurb="Albany, Troy and Schenectady see spring snowmelt flooding and basement seepage each year."),
    dict(slug="buffalo-western-ny", name="Buffalo &amp; Western New York", region="Western New York",
         blurb="Lake-effect snow loads and rapid thaw cycles drive roof leaks and basement flooding across Erie County."),
    dict(slug="rochester-finger-lakes", name="Rochester &amp; the Finger Lakes", region="Finger Lakes Region",
         blurb="Lake Ontario shoreline flooding and older Monroe County housing stock create recurring water-loss risk."),
    dict(slug="syracuse-central-ny", name="Syracuse &amp; Central New York", region="Central New York",
         blurb="Heavy snowfall and freeze-thaw cycles in Onondaga County are a leading cause of winter pipe bursts."),
    dict(slug="utica-mohawk-valley", name="Utica &amp; the Mohawk Valley", region="Mohawk Valley",
         blurb="The Mohawk River corridor and older mill-town infrastructure bring both flood and sewage-backup calls."),
    dict(slug="binghamton-southern-tier", name="Binghamton &amp; the Southern Tier", region="Southern Tier",
         blurb="The Susquehanna and Chenango Rivers have produced some of the state's most damaging flood events."),
]

BLOG = [
    dict(slug="how-long-does-water-damage-restoration-take",
         title="How Long Does Water Damage Restoration Take in New York?",
         desc="A realistic, day-by-day timeline for water extraction, drying and rebuild — and the factors that speed up or slow down a New York restoration project."),
    dict(slug="mold-prevention-checklist-for-new-york-homes",
         title="Mold Prevention Checklist for New York Homes",
         desc="A room-by-room checklist for reducing indoor humidity and catching hidden moisture before it becomes a mold problem in New York's climate."),
    dict(slug="filing-a-new-york-water-damage-insurance-claim",
         title="Filing a New York Homeowners Insurance Claim for Water Damage",
         desc="Step-by-step guidance on documenting a water loss, understanding New York claim timelines, and working with your adjuster."),
]

EXTERNAL_AUTHORITY_LINKS = {
    "iicrc": ("https://www.iicrc.org", "IICRC certification standards"),
    "epa_mold": ("https://www.epa.gov/mold", "EPA guidance on mold and moisture"),
    "fema_flood": ("https://www.fema.gov/flood-insurance", "FEMA National Flood Insurance Program"),
    "ny_dfs": ("https://www.dfs.ny.gov/complaints_and_disputes", "NY Department of Financial Services"),
    "noaa_nws": ("https://www.weather.gov", "National Weather Service"),
    "cdc_mold": ("https://www.cdc.gov/mold/", "CDC mold and health guidance"),
    "redcross": ("https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/flood.html", "American Red Cross flood safety"),
    "ny_dec": ("https://dec.ny.gov/", "NY State Dept. of Environmental Conservation"),
    "osha_water": ("https://www.osha.gov/water-damage", "OSHA water-damage worksite guidance"),
    "usfa": ("https://www.usfa.fema.gov/", "U.S. Fire Administration"),
}

def ext(key):
    url, label = EXTERNAL_AUTHORITY_LINKS[key]
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'

print("Loaded", len(SERVICES), "services,", len(LOCATIONS), "locations,", len(BLOG), "blog posts")

# ------------------------------------------------------------------ head --

def head(title, description, canonical_path, schema_list, og_type="website"):
    canonical = DOMAIN + canonical_path
    schema_json = "\n".join(
        f'<script type="application/ld+json">{json.dumps(s)}</script>' for s in schema_list
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index, follow">
<link rel="icon" href="/images/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Source+Sans+3:wght@400;600;700&family=IBM+Plex+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
{schema_json}
</head>"""

def local_business_schema():
    return {
        "@context": "https://schema.org",
        "@type": "HomeAndConstructionBusiness",
        "name": BRAND,
        "image": DOMAIN + "/images/og-cover.jpg",
        "@id": DOMAIN,
        "url": DOMAIN,
        "telephone": PHONE_TEL,
        "priceRange": "$$",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "500 Dispatch Way, Suite 210",
            "addressLocality": "Albany",
            "addressRegion": "NY",
            "postalCode": "12207",
            "addressCountry": "US"
        },
        "areaServed": [{"@type": "State", "name": "New York"}] + [
            {"@type": "City", "name": loc["name"].replace("&amp;", "&")} for loc in LOCATIONS
        ],
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            "opens": "00:00", "closes": "23:59"
        }],
        "sameAs": ["https://www.facebook.com/", "https://www.linkedin.com/"]
    }

def breadcrumb_schema(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i+1, "name": name, "item": DOMAIN + path}
            for i, (name, path) in enumerate(items)
        ]
    }

def faq_schema(pairs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs
        ]
    }

def service_schema(s):
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": s["name"].replace("&amp;", "&"),
        "provider": {"@type": "HomeAndConstructionBusiness", "name": BRAND, "telephone": PHONE_TEL},
        "areaServed": {"@type": "State", "name": "New York"},
        "url": f"{DOMAIN}/services/{s['slug']}.html"
    }


# --------------------------------------------------------------- chrome ---

def header(active, depth=""):
    d = depth
    return f"""
<div class="ticker"><div class="ticker__track">{ticker_items([
        'CREWS DISPATCHED STATEWIDE', '24/7/365 EMERGENCY LINE ' + PHONE_DISPLAY,
        'IICRC CERTIFIED TECHNICIANS', 'DIRECT INSURANCE BILLING AVAILABLE',
        'SERVING ALL 62 NEW YORK COUNTIES'])}</div></div>
<header class="site-header">
  <div class="site-header__row">
    <a class="brand" href="{d}/index.html"><span class="brand__mark">ESR</span>{BRAND}</a>
    <button class="menu-toggle" aria-expanded="false" aria-label="Toggle navigation">MENU</button>
    <nav class="main-nav">
      <a href="{d}/index.html" {'class="active"' if active=='home' else ''}>Home</a>
      <a href="{d}/about.html" {'class="active"' if active=='about' else ''}>About</a>
      <a href="{d}/services/index.html" {'class="active"' if active=='services' else ''}>Services</a>
      <a href="{d}/locations/index.html" {'class="active"' if active=='locations' else ''}>Locations</a>
      <a href="{d}/blog/index.html" {'class="active"' if active=='blog' else ''}>Blog</a>
      <a href="{d}/contact.html" {'class="active"' if active=='contact' else ''}>Contact</a>
    </nav>
    <div class="header-cta">
      <a class="call-now" href="tel:{PHONE_TEL}">&#9742; {PHONE_DISPLAY}</a>
    </div>
  </div>
</header>"""

def footer(d=""):
    svc_links = "".join(f'<li><a href="{d}/services/{s["slug"]}.html">{s["name"]}</a></li>' for s in SERVICES[:6])
    loc_links = "".join(f'<li><a href="{d}/locations/{l["slug"]}.html">{l["name"]}</a></li>' for l in LOCATIONS)
    return f"""
<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <h4>{BRAND}</h4>
      <p style="max-width:32ch;color:var(--text-inverse-2);font-size:14px;">
      IICRC-certified water, fire and mold restoration teams stationed across
      New York State. Licensed, insured, and available 24 hours a day, 7 days a week.
      </p>
      <p class="tag-source">500 Dispatch Way, Suite 210 &middot; Albany, NY 12207</p>
      <a class="call-now" href="tel:{PHONE_TEL}" style="display:inline-block;margin-top:10px;">&#9742; {PHONE_DISPLAY}</a>
    </div>
    <div><h4>Services</h4><ul>{svc_links}<li><a href="{d}/services/index.html">All Services &rarr;</a></li></ul></div>
    <div><h4>New York Service Areas</h4><ul>{loc_links}</ul></div>
    <div>
      <h4>Company</h4>
      <ul>
        <li><a href="{d}/about.html">About Us</a></li>
        <li><a href="{d}/blog/index.html">Blog</a></li>
        <li><a href="{d}/contact.html">Contact</a></li>
        <li><a href="{d}/services/insurance-claim-assistance.html">Insurance Claim Help</a></li>
      </ul>
      <h4 style="margin-top:22px;">Verify Our Credentials</h4>
      <ul>
        <li>{ext('iicrc')}</li>
        <li>{ext('ny_dfs')}</li>
      </ul>
    </div>
  </div>
  <div class="container footer-bottom">
    <span>&copy; 2026 {BRAND}. All rights reserved.</span>
    <span>Licensed &amp; Insured in New York State &middot; IICRC Certified Firm</span>
  </div>
</footer>
<a href="tel:{PHONE_TEL}" class="sticky-call">&#9742; Call Now — {PHONE_DISPLAY}</a>
<script src="{d}/js/main.js"></script>"""

def page(title, description, canonical_path, active, body, schema_list, depth=""):
    return f"""{head(title, description, canonical_path, schema_list)}
<body>
{header(active, depth)}
{body}
{footer(depth)}
</body>
</html>"""


# ---------------------------------------------------------------- HOME ----

def service_cards(items, depth=""):
    out = []
    for s in items:
        out.append(f"""
        <div class="card">
          <span class="card__icon">SERVICE</span>
          <h3>{s['name']}</h3>
          <p>{s['short']}</p>
          <a class="card-link" href="{depth}/services/{s['slug']}.html">View Service &rarr;</a>
        </div>""")
    return "".join(out)

def location_chips(items, depth=""):
    return "".join(f'<a class="chip" href="{depth}/locations/{l["slug"]}.html">{l["name"]}</a>' for l in items)

def build_home():
    body = f"""
<section class="hero">
  <div class="container hero__grid">
    <div>
      <span class="eyebrow">LIVE DISPATCH &middot; RESPONDING NOW ACROSS NEW YORK STATE</span>
      <h1>Water, Fire &amp; Mold Damage? <em>We're Already En Route.</em></h1>
      <p class="lede">{BRAND} sends IICRC-certified restoration crews to homes and
      businesses in every region of New York — from Manhattan walk-ups to Buffalo
      snow-belt basements — with an average on-site arrival of under 60 minutes
      for active emergencies.</p>
      <div class="hero__ctas">
        <a class="btn btn--primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn--ghost" href="/contact.html">Request Free Inspection</a>
      </div>
    </div>
    <div class="console">
      <div class="console__title">Dispatch Readout</div>
      {gauges_block([
          ("Avg. Arrival","&lt;60min",82),
          ("Availability","24/7",100),
          ("NY Counties","62",95),
          ("Properties Restored","5K+",88),
          ("Certified Techs","IICRC",90),
          ("Years Active","18",70),
      ])}
    </div>
  </div>
</section>

<div class="trust-bar">
  <div class="container trust-bar__row">
    <span>&#9733;&#9733;&#9733;&#9733;&#9733; <strong>4.9</strong> average rating</span>
    <span><strong>Licensed</strong> &amp; Insured in NY</span>
    <span><strong>IICRC</strong> Certified Firm</span>
    <span><strong>Direct</strong> Insurance Billing</span>
    <span><strong>24/7/365</strong> Emergency Line</span>
  </div>
</div>

<section id="services">
  <div class="container">
    <div class="section-head">
      <span class="kicker">What We Do</span>
      <h2>Full-Scope Restoration Services</h2>
      <p>Every {BRAND} crew is trained and equipped to handle the complete
      restoration lifecycle — from the first extraction pump to the final
      insurance sign-off — so you work with one company from start to finish.</p>
    </div>
    <div class="grid-3">{service_cards(SERVICES)}</div>
  </div>
</section>

<section class="section--alt">
  <div class="container split">
    <div>
      <span class="kicker">Why New York Chooses Us</span>
      <h2>Built for New York's Buildings, Weather and Insurance Rules</h2>
      <p>New York's housing stock ranges from pre-war Manhattan co-ops to
      Adirondack-adjacent farmhouses, and each one fails differently. We staff
      crews who understand local plumbing codes, co-op board requirements, and
      the documentation New York insurers expect — so restoration doesn't stall
      on paperwork while damage spreads.</p>
      <ul class="checklist">
        <li>24/7 emergency dispatch, including holidays and storm events</li>
        <li>IICRC-certified technicians on every job, not just supervisors</li>
        <li>Industrial-grade extraction, drying and air-scrubbing equipment</li>
        <li>Transparent, itemized pricing before work begins</li>
        <li>In-house insurance coordination and direct adjuster communication</li>
        <li>Same-day service for active water, fire and sewage emergencies</li>
      </ul>
    </div>
    <div class="split-visual">
      <div class="stat"><span class="stat__num">18 yrs</span><span class="stat__label">Restoring New York properties</span></div>
      <div class="stat"><span class="stat__num">5,200+</span><span class="stat__label">Emergency jobs completed statewide</span></div>
      <div class="stat"><span class="stat__num">62/62</span><span class="stat__label">New York counties served</span></div>
      <div class="stat" style="border-bottom:none;"><span class="stat__num">4.9/5</span><span class="stat__label">Average verified customer rating</span></div>
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="kicker">Our Process</span>
      <h2>How We Work, From First Call to Final Walkthrough</h2>
      <p>Restoration moves fastest when every step is sequenced correctly.
      Here's exactly what happens after you call.</p>
    </div>
    <div class="process">
      <div class="process__step"><div class="process__num">1</div><h3>Call</h3><p>Speak with a live dispatcher, not a call center script, any hour of the day.</p></div>
      <div class="process__step"><div class="process__num">2</div><h3>Inspection</h3><p>On-site moisture mapping and damage assessment, usually within the hour.</p></div>
      <div class="process__step"><div class="process__num">3</div><h3>Extraction</h3><p>Standing water, debris and contaminated material removed immediately.</p></div>
      <div class="process__step"><div class="process__num">4</div><h3>Drying</h3><p>Commercial dehumidifiers and air movers run until readings confirm dry.</p></div>
      <div class="process__step"><div class="process__num">5</div><h3>Restoration</h3><p>Repairs, rebuild and a final walkthrough before we close the file.</p></div>
    </div>
  </div>
</section>

<section class="section--dark">
  <div class="container">
    <div class="section-head">
      <span class="kicker">Statewide Coverage</span>
      <h2>Serving Every Region of New York State</h2>
      <p>New York's flood, fire and mold risks change block by block —
      coastal surge on Long Island, spring snowmelt in the Capital Region,
      lake-effect thaw around Buffalo and Rochester, and river-corridor
      flooding through the Southern Tier. {BRAND} keeps crews and equipment
      staged across all 62 counties so response time doesn't depend on
      how rural or urban your address is. Reference {ext('noaa_nws')} and
      {ext('ny_dec')} for regional weather and flood-risk advisories that
      inform how we stage equipment ahead of major storms.</p>
    </div>
    <div class="chip-grid">{location_chips(LOCATIONS)}</div>
  </div>
</section>

<section>
  <div class="container">
    <div class="section-head">
      <span class="kicker">Who We Restore For</span>
      <h2>Residential &amp; Commercial Restoration</h2>
    </div>
    <div class="grid-4">
      <div class="card"><span class="card__icon">RESIDENTIAL</span><h3>Homeowners</h3><p>Single-family homes, condos and co-ops across every borough and county.</p></div>
      <div class="card"><span class="card__icon">MULTIFAMILY</span><h3>Property Managers</h3><p>Apartment buildings and rental portfolios needing fast, tenant-safe turnaround.</p></div>
      <div class="card"><span class="card__icon">COMMERCIAL</span><h3>Business Owners</h3><p>Retail, office and hospitality spaces where downtime has a real cost.</p></div>
      <div class="card"><span class="card__icon">INDUSTRIAL</span><h3>Facilities Teams</h3><p>Warehouses and industrial sites requiring OSHA-aware crews and documentation.</p></div>
    </div>
  </div>
</section>

<section class="section--alt">
  <div class="container">
    <div class="section-head">
      <span class="kicker">Customer Reviews</span>
      <h2>What New York Homeowners Say</h2>
    </div>
    <div class="grid-3">
      <div class="testimonial"><div class="testimonial__stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
      <p>"A pipe burst in our Astoria co-op at 2am and a crew was inspecting the unit before 3am. They also handled the entire claim with our insurer."</p>
      <div class="testimonial__name">— Homeowner, Queens, NY</div></div>
      <div class="testimonial"><div class="testimonial__stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
      <p>"Basement flooded during spring melt outside Albany. Dehumidifiers were running within two hours and the mold never got a chance to start."</p>
      <div class="testimonial__name">— Homeowner, Capital Region, NY</div></div>
      <div class="testimonial"><div class="testimonial__stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
      <p>"Our Rochester retail space flooded overnight. They worked around our reopening deadline and kept us updated every step of the way."</p>
      <div class="testimonial__name">— Business Owner, Rochester, NY</div></div>
    </div>
  </div>
</section>

<section>
  <div class="container two-col" style="grid-template-columns:1fr;max-width:900px;">
    <div>
      <div class="section-head">
        <span class="kicker">FAQ</span>
        <h2>Frequently Asked Questions</h2>
      </div>
      {faq_html(HOME_FAQ)}
    </div>
  </div>
</section>

<section>
  <div class="container">
    <div class="cta-band">
      <h2>Water, Fire or Mold Emergency Right Now?</h2>
      <p>Every hour a property sits wet or smoke-damaged increases the cost
      and health risk of the loss. Talk to a live dispatcher and get a
      crew moving toward your address today.</p>
      <div class="btns">
        <a class="btn btn--primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn--ghost" href="/contact.html">Request Free Estimate</a>
      </div>
    </div>
  </div>
</section>
"""
    schema = [local_business_schema(), faq_schema(HOME_FAQ)]
    title = "Emergency Water, Fire &amp; Mold Restoration in New York | " + BRAND
    title = "Emergency Water, Fire & Mold Restoration in New York State | " + BRAND
    desc = ("24/7 emergency water damage, fire damage and mold restoration serving all "
            "of New York State. IICRC-certified crews, direct insurance billing. Call now.")
    return page(title, desc, "/index.html", "home", body, schema)

HOME_FAQ = [
    ("How fast can a crew reach my property in New York?",
     "In most of our service areas we arrive within 45 to 90 minutes of your call for an active water, fire or sewage emergency. Response time varies by county and current dispatch load, which is why we stage crews across all 62 New York counties rather than from a single base."),
    ("Do you work directly with my homeowners insurance company?",
     "Yes. Our team documents the loss with photos, moisture readings and a scope of work, then communicates directly with your adjuster. Many customers pay only their deductible while we bill the insurer for the remainder."),
    ("What's the difference between water damage restoration and mold remediation?",
     "Water damage restoration focuses on extracting water and drying the structure before mold has a chance to establish itself. Mold remediation is a separate, contained process used once mold colonies are already present, typically 24 to 72 hours after unaddressed moisture."),
    ("Do you serve rural areas or just New York City?",
     "We serve all of New York State, including rural counties in the Southern Tier, North Country and Finger Lakes region, not just the five boroughs and Long Island."),
    ("Is emergency restoration available on nights, weekends and holidays?",
     "Yes, our dispatch line is staffed 24 hours a day, 7 days a week, including all holidays, because water and fire damage doesn't wait for business hours."),
]

def faq_html(pairs):
    out = []
    for q, a in pairs:
        out.append(f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>')
    return "".join(out)


# ------------------------------------------------------------- SERVICES --

SERVICE_DETAIL = {
"water-damage-restoration": dict(
    subtitle="Emergency extraction and structural drying for burst pipes, appliance failures and roof leaks.",
    intro=[
        "A water loss rarely announces itself politely. A supply line lets go behind a washing machine, a radiator fitting corrodes through, or an ice dam backs water under a roof deck, and within minutes it is moving through subfloor, drywall and insulation faster than most homeowners realize. The first 24 to 48 hours determine whether a loss stays a drying job or turns into a mold and structural-repair job.",
        f"{BRAND} treats water damage restoration as a race against the clock. Dispatch teams are staged across New York so a technician can begin extraction and moisture mapping quickly, then hold the structure at target drying benchmarks with commercial dehumidification until every reading confirms dry — not just visually dry."
    ],
    causes=["Burst or frozen supply pipes", "Washing machine and dishwasher hose failures",
            "Water heater and boiler leaks", "Roof and flashing intrusion",
            "HVAC condensate line backups", "Ice dam melt under roofing"],
    signs=["Discoloration or staining on ceilings and walls", "A persistent musty or damp odor",
           "Warped, cupped or soft flooring", "Peeling paint or bubbling drywall",
           "Higher-than-normal humidity in one area of the home"],
    local_note=("New York's older housing stock — pre-war Manhattan buildings, century-old "
                f"Capital Region homes, and Western New York properties built for heavy snow load — "
                f"often hides galvanized or cast-iron plumbing that fails without warning. We follow "
                f"the drying and moisture-documentation standards published by {ext('iicrc')} on every job, "
                "which also gives your insurance adjuster a clean, verifiable record."),
    faqs=[("How soon should water extraction start after a pipe bursts?",
           "Extraction should begin as soon as it is safe to enter the property, ideally within a few hours. Waiting longer than 24-48 hours significantly increases the risk of mold growth and permanent material damage."),
          ("Can you dry a structure without tearing out all the drywall?",
           "Often, yes. We use moisture meters and thermal imaging to target only the materials that are actually saturated, which keeps demolition and rebuild costs down when the structure allows it.")],
),
"flood-cleanup": dict(
    subtitle="Rapid extraction and contamination assessment after flood water enters your property.",
    intro=[
        "Flood water is treated differently from a clean supply-line leak because it usually carries contamination from soil, storm runoff or overwhelmed sewer systems. New York's flood risk isn't limited to coastal storm surge — spring snowmelt along the Mohawk and Hudson corridors and flash flooding in the Southern Tier's river valleys produce flood losses every year.",
        f"{BRAND}'s flood cleanup teams categorize incoming water, extract standing water, remove unsalvageable contaminated materials, and disinfect affected surfaces before structural drying begins, following flood-response guidance from {ext('fema_flood')}."
    ],
    causes=["River and creek overflow", "Storm surge and coastal flooding", "Flash flooding from heavy rainfall",
            "Overwhelmed municipal storm drains", "Snowmelt and ice-jam flooding"],
    signs=["Visible water line on walls or foundation", "Mud or silt residue on flooring",
           "Saturated insulation or drywall", "Sewage or chemical odor in flood water",
           "Electrical outlets or panels affected by rising water"],
    local_note=("Homeowners in flood-prone corridors along the Susquehanna, Mohawk and Hudson "
                f"Rivers should register with {ext('fema_flood')} well before storm season, since standard "
                "homeowners policies typically exclude flood water. We coordinate directly with NFIP claims "
                "adjusters in addition to standard homeowners insurance."),
    faqs=[("Is flood water covered by my homeowners insurance?",
           "Usually not. Most standard homeowners policies exclude flood damage, which requires separate flood insurance, often through the National Flood Insurance Program. We can help you understand which policy applies to your loss."),
          ("How do you dispose of flood-contaminated materials safely?",
           "Porous materials that absorbed contaminated flood water — carpet, insulation, some drywall — are typically removed and disposed of according to local waste regulations rather than dried, since contamination can't be fully removed from those materials.")],
),
"fire-damage-restoration": dict(
    subtitle="Soot removal, odor neutralization and rebuild after a residential or commercial fire.",
    intro=[
        "Fire damage restoration starts the moment the fire department clears a property, because soot becomes more corrosive and odor sets deeper into porous materials with every hour that passes. Water used to extinguish the fire also needs to be addressed immediately, which means most fire losses are really a combined fire, smoke and water damage job.",
        f"{BRAND} coordinates board-up and tarping for security, then works through a structured sequence of soot removal, HVAC system cleaning, odor neutralization and reconstruction, referencing safety practices from the {ext('usfa')}."
    ],
    causes=["Kitchen and cooking fires", "Electrical faults and wiring failures",
            "Heating equipment and chimney fires", "Wildfire smoke infiltration",
            "Candle, fireplace and space heater incidents"],
    signs=["Visible soot on walls, ceilings or contents", "Persistent smoke odor after a fire is out",
           "Warped or discolored surfaces near the fire origin", "Compromised structural framing",
           "Residue inside HVAC ductwork"],
    local_note=("Many New York City and Capital Region buildings share walls, ductwork or fire escapes "
                "with neighboring units, so smoke and soot damage frequently extends beyond the unit where "
                "a fire originated. We inspect adjoining units and shared systems as part of every fire "
                "damage assessment, not just the unit of origin."),
    faqs=[("Can smoke odor really be fully removed?",
           "In most cases, yes. Persistent odor comes from soot particles embedded in porous materials and HVAC systems. Thermal fogging, ozone or hydroxyl treatment and duct cleaning, combined with removing unsalvageable materials, typically eliminates odor rather than masking it."),
          ("Do you handle the board-up and security of a fire-damaged property?",
           "Yes, securing the property against weather and unauthorized entry is one of the first things we do, usually within hours of the fire department releasing the scene.")],
),
"mold-remediation": dict(
    subtitle="Certified containment, air scrubbing and removal for mold caused by hidden or unresolved moisture.",
    intro=[
        "Mold is a moisture problem wearing a different name. Colonies can establish on damp drywall or framing within 24 to 72 hours of unresolved water intrusion, which is why mold remediation calls so often trace back to a slow leak nobody noticed — behind a shower wall, under a sink, or inside a finished basement.",
        f"{BRAND}'s remediation process follows containment, negative air pressure and HEPA filtration protocols consistent with {ext('epa_mold')} and {ext('cdc_mold')} guidance, so spores are controlled rather than spread to unaffected areas during removal."
    ],
    causes=["Undetected slow leaks behind walls or under fixtures", "Poor bathroom or kitchen ventilation",
            "High indoor humidity, common in older New York basements", "Previous water damage that wasn't fully dried",
            "Condensation on cold surfaces in unheated spaces"],
    signs=["Visible mold growth on walls, ceilings or grout", "A persistent musty smell",
           "Unexplained allergy or respiratory symptoms indoors", "Warped or discolored surfaces",
           "Condensation on windows or cold pipes"],
    local_note=("Basements across the Capital Region, Western New York and the Hudson Valley are "
                "especially prone to humidity-driven mold because of clay-heavy soil and older foundation "
                f"waterproofing. The {ext('epa_mold')} recommends keeping indoor relative humidity below 60% "
                "year-round, and we install monitoring and dehumidification as part of many remediation plans."),
    faqs=[("Do I need to leave my home during mold remediation?",
           "For contained, localized remediation, most residents can typically remain in unaffected areas of the home. For larger jobs or if a household member has respiratory sensitivity, we may recommend temporary relocation during the active removal phase."),
          ("Will mold come back after remediation?",
           "Mold returns when the underlying moisture source isn't fixed. Remediation removes existing growth, but we also identify and address the moisture cause — a leak, ventilation gap or humidity issue — to prevent recurrence.")],
),
"sewage-cleanup": dict(
    subtitle="Category 3 blackwater extraction, sanitization and disposal after backups and septic failures.",
    intro=[
        "Sewage backups are classified as Category 3, or 'blackwater,' losses because the water carries bacteria, viruses and other pathogens that pose a real health risk. This is not a job for shop vacuums and bleach — it requires PPE, containment and proper disposal of contaminated materials.",
        f"{BRAND} technicians extract and dispose of contaminated water and materials, then sanitize and deodorize affected surfaces following {ext('epa_mold')} and municipal wastewater handling guidance, restoring the space to a safe, livable condition."
    ],
    causes=["Municipal sewer line backups", "Septic tank or leach field failure",
            "Tree root intrusion into sewer laterals", "Sump pump failure combined with heavy rainfall",
            "Clogged or collapsed drain lines"],
    signs=["Sewage odor from drains or fixtures", "Water backing up into tubs, sinks or floor drains",
           "Slow-draining fixtures throughout the property", "Visible waste material in flooded areas",
           "Gurgling sounds from plumbing during use"],
    local_note=("Older municipal sewer infrastructure in cities like Buffalo, Syracuse and parts of "
                "New York City combines stormwater and sewage in a single system, which means heavy rain "
                "events can push backups into basements even when a home's own plumbing is functioning "
                "correctly. We carry the containment equipment this specific failure mode requires."),
    faqs=[("Is it safe to clean up sewage backup myself?",
           "We don't recommend it. Category 3 water contains pathogens that require personal protective equipment, proper containment and regulated disposal — mistakes here create a real health risk for your household."),
          ("Does homeowners insurance cover sewage backup?",
           "Standard policies often exclude sewer backup unless you've added a specific endorsement. We can help document the loss clearly regardless of your coverage so you understand your options.")],
),
"basement-water-removal": dict(
    subtitle="Sump failure and seepage response with dehumidification to stop water from spreading upward.",
    intro=[
        "Basements sit at the lowest point of hydrostatic pressure in a home, which makes them the first place groundwater, snowmelt and heavy rainfall show up when a foundation, sump system or grading fails. Left alone, a wet basement becomes a mold source for the entire house within days.",
        f"{BRAND} pumps out standing water, identifies the entry point — a failed sump pump, a cracked foundation wall, or poor exterior grading — and dries the space with commercial dehumidifiers before finishing materials are reinstalled."
    ],
    causes=["Sump pump failure during heavy rain or power outage", "Foundation cracks and hydrostatic pressure",
            "Poor exterior grading or clogged gutters", "Window well failures",
            "Spring snowmelt and rising water tables"],
    signs=["Standing water or damp flooring in the basement", "Efflorescence (white mineral deposits) on foundation walls",
           "Musty odor even without visible water", "Warped baseboards or damp drywall near the floor",
           "A sump pump that runs constantly or not at all"],
    local_note=("Spring snowmelt across the Capital Region, Western New York and the Southern Tier "
                "raises water tables enough to overwhelm sump systems that worked fine the rest of the "
                f"year. We recommend a battery-backup sump pump for any New York basement, since {ext('noaa_nws')} "
                "storm data shows spring flooding events often coincide with power outages."),
    faqs=[("How long does it take to dry out a flooded basement?",
           "A typical basement reaches target dry-standard readings in 3 to 5 days with commercial dehumidification, though it depends on the volume of water, materials involved and ventilation."),
          ("Should I replace my sump pump after a failure?",
           "If a sump pump failed during a flood event, we generally recommend replacing it along with adding a battery or water-powered backup system, since a single point of failure is what caused the loss in the first place.")],
),
"storm-damage-restoration": dict(
    subtitle="Wind, hail and downed-tree stabilization and rebuild after severe New York weather.",
    intro=[
        "Severe storms across New York — nor'easters on Long Island, lake-effect systems around Buffalo and Rochester, and summer derechos through Central New York — can compromise a roof, window or exterior wall in minutes. The priority after any storm is stopping secondary water and weather intrusion before it compounds the original damage.",
        f"{BRAND} crews respond with emergency tarping, board-up and debris stabilization first, then move into full structural restoration once the property is secure, monitoring active systems through {ext('noaa_nws')} to stage crews ahead of major forecasted events."
    ],
    causes=["High wind and downed trees or limbs", "Hail impact on roofing and siding",
            "Lightning strikes", "Lake-effect snow load and roof collapse risk",
            "Wind-driven rain intrusion around windows and doors"],
    signs=["Missing, cracked or lifted roof shingles", "Water stains appearing after a storm",
           "Visible structural damage from fallen trees or debris", "Damaged gutters and downspouts",
           "Cracked or broken windows"],
    local_note=("Roof collapse risk from heavy, wet lake-effect snow is a recurring concern for flat "
                "and low-slope roofs around Buffalo and Rochester each winter. We prioritize emergency "
                "snow-load removal and tarping calls during active lake-effect events to prevent structural "
                "failure before it happens."),
    faqs=[("How quickly can you tarp a damaged roof?",
           "Emergency tarping is typically completed the same day the damage occurs, weather permitting, since it's the single most effective way to stop secondary water damage after a storm."),
          ("Do you work with my insurance company on storm claims?",
           "Yes, storm damage claims are one of the most common types we document and submit alongside homeowners, including photo evidence, moisture readings and a full scope of repair.")],
),
"commercial-restoration": dict(
    subtitle="Minimal-downtime water, fire and mold response for offices, retail, multifamily and industrial sites.",
    intro=[
        "Commercial losses carry a cost beyond the physical damage: every day a retail space, office or multifamily building stays closed is lost revenue or displaced tenants. Commercial restoration projects also involve more stakeholders — property managers, tenants, insurers and sometimes municipal inspectors — which makes clear communication as important as the physical work.",
        f"{BRAND} assigns a single project manager to commercial losses across New York, coordinating around business hours, tenant safety and code requirements while crews work in phases to bring parts of a property back online as soon as it's safe."
    ],
    causes=["Commercial pipe and sprinkler system failures", "HVAC and roofing system leaks",
            "Multifamily plumbing failures affecting several units", "Fire and electrical incidents",
            "Storm and flood damage to commercial structures"],
    signs=["Tenant complaints of odor, staining or leaks", "Sprinkler or fire suppression system discharge",
           "Elevated humidity readings in mechanical or storage areas", "Visible water intrusion in common areas",
           "Recurring HVAC condensation issues"],
    local_note=(f"Multifamily and mixed-use buildings in New York City and its suburbs bring "
                "additional coordination requirements — building management, multiple insurance carriers, "
                "and sometimes local housing code inspections. We document losses to a standard that holds "
                f"up with both insurers and municipal requirements, consistent with {ext('osha_water')} "
                "worksite safety guidance for occupied buildings."),
    faqs=[("Can you work in phases to keep part of my business open?",
           "In most cases, yes. We scope commercial jobs to isolate the affected area and work around occupied or operational sections wherever it's safe to do so."),
          ("Do you handle multi-unit residential losses?",
           "Yes, we regularly restore multifamily buildings, coordinating with property managers and multiple affected units on a single, unified timeline.")],
),
"insurance-claim-assistance": dict(
    subtitle="Documentation, scope-of-loss reporting and direct adjuster coordination for a faster claim.",
    intro=[
        "The restoration work and the insurance claim move on parallel tracks, and the biggest delays we see happen when those two tracks aren't communicating. Missing documentation, an incomplete scope of loss, or a homeowner unsure what their policy actually covers can stall a claim for weeks.",
        f"{BRAND} documents every loss with dated photos, moisture readings and a detailed scope of work from the first inspection, then communicates directly with your insurance adjuster so the claim and the physical restoration stay in sync. For a general understanding of your rights during a claim dispute, {ext('ny_dfs')} publishes consumer guidance for New York policyholders."
    ],
    causes=["Incomplete or missing loss documentation", "Confusion over what a policy actually covers",
            "Delayed or unresponsive adjuster communication", "Disputes over scope of repair versus replacement",
            "Uncertainty about deductibles and out-of-pocket costs"],
    signs=["An adjuster requesting documentation you don't have", "Uncertainty whether flood, sewer backup or mold is covered",
           "A claim that has stalled for more than two weeks", "A settlement offer that seems to underscope the damage"],
    local_note=("New York homeowners insurance policies vary widely in how they treat sewer backup, "
                f"mold and flood exclusions. We recommend reviewing your declarations page annually and "
                f"consulting {ext('ny_dfs')} if you believe a claim has been unfairly delayed or denied — "
                "we're glad to provide our own documentation to support that process."),
    faqs=[("Do you charge extra for insurance coordination?",
           "Insurance documentation and adjuster coordination is included as part of our standard restoration process, not billed as a separate service."),
          ("What if my claim is denied?",
           f"We provide detailed documentation you can use to appeal or dispute a denial, and can point you to resources like {ext('ny_dfs')} for formal complaint processes if needed.")],
),
}

def build_service(s):
    d = SERVICE_DETAIL[s["slug"]]
    related = [x for x in SERVICES if x["slug"] != s["slug"]][:5]
    intro_html = "".join(f"<p>{p}</p>" for p in d["intro"])
    causes_html = "".join(f"<li>{c}</li>" for c in d["causes"])
    signs_html = "".join(f"<li>{c}</li>" for c in d["signs"])
    faqs_html = "".join(f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>' for q,a in d["faqs"])
    related_html = "".join(f'<li><a href="/services/{r["slug"]}.html">{r["name"]}</a></li>' for r in related)
    loc_sample = LOCATIONS[:6]
    loc_html = "".join(f'<li><a href="/locations/{l["slug"]}.html">{l["name"]}</a></li>' for l in loc_sample)

    body = f"""
<div class="content-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/index.html">Home</a><span>/</span><a href="/services/index.html">Services</a><span>/</span>{s['name']}</div>
    <h1>{s['name']} in New York State</h1>
    <p>{d['subtitle']}</p>
  </div>
</div>
<section>
  <div class="container two-col">
    <div class="prose">
      {intro_html}
      <h2>Common Causes of {s['name']}</h2>
      <ul>{causes_html}</ul>
      <h2>Signs You Need {s['name']} Now</h2>
      <ul>{signs_html}</ul>
      <h2>Our {s['name']} Process</h2>
      <p>Every job starts with a documented inspection, moves through extraction or removal,
      then structural drying or repair, and closes with a final walkthrough and insurance
      paperwork if applicable — see our <a href="/index.html#services">full restoration process</a>
      for the step-by-step breakdown we follow on every call.</p>
      <h2>Serving All of New York State</h2>
      <p>{d['local_note']} Explore {s['name'].lower()} coverage in your area, or view our
      <a href="/locations/index.html">complete list of New York service areas</a>.</p>
      <h2>Frequently Asked Questions</h2>
      {faqs_html}
    </div>
    <aside>
      <div class="side-box">
        <h4>24/7 Emergency Line</h4>
        <p style="font-family:var(--font-mono);font-size:20px;color:var(--deep-water);margin-bottom:4px;">{PHONE_DISPLAY}</p>
        <p class="tag-source">Live dispatch, every hour of every day.</p>
        <a class="call-now" href="tel:{PHONE_TEL}">Call Now</a>
      </div>
      <div class="side-box">
        <h4>Related Services</h4>
        <ul>{related_html}</ul>
      </div>
      <div class="side-box">
        <h4>Popular Service Areas</h4>
        <ul>{loc_html}</ul>
      </div>
    </aside>
  </div>
</section>
<section class="section--alt">
  <div class="container">
    <div class="cta-band">
      <h2>Need {s['name']} Today?</h2>
      <p>Talk to a live dispatcher and get a certified crew moving toward your address.</p>
      <div class="btns">
        <a class="btn btn--primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn--ghost" href="/contact.html">Request Free Estimate</a>
      </div>
    </div>
  </div>
</section>
"""
    schema = [
        service_schema(s),
        breadcrumb_schema([("Home","/index.html"),("Services","/services/index.html"),(s["name"].replace("&amp;","&"),f"/services/{s['slug']}.html")]),
        faq_schema(d["faqs"]),
    ]
    plain_name = s["name"].replace("&amp;", "&")
    title = f"{plain_name} in New York | 24/7 Emergency Response | {BRAND}"
    desc = f"{d['subtitle']} IICRC-certified, licensed & insured, serving all of New York State. Call {PHONE_DISPLAY} for 24/7 dispatch."
    return page(title, desc, f"/services/{s['slug']}.html", "services", body, schema, depth="")

def build_services_index():
    cards = service_cards(SERVICES, depth="")
    body = f"""
<div class="content-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/index.html">Home</a><span>/</span>Services</div>
    <h1>Restoration Services Across New York State</h1>
    <p>From first extraction to final insurance sign-off, {BRAND} handles every
    stage of a water, fire, mold or storm loss for residential and commercial
    properties statewide.</p>
  </div>
</div>
<section><div class="container grid-3">{cards}</div></section>
<section class="section--alt">
  <div class="container">
    <div class="cta-band">
      <h2>Not Sure Which Service You Need?</h2>
      <p>Call our 24/7 dispatch line and describe what's happening — we'll route the right crew and equipment to your address.</p>
      <div class="btns"><a class="btn btn--primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a></div>
    </div>
  </div>
</section>
"""
    schema = [breadcrumb_schema([("Home","/index.html"),("Services","/services/index.html")])]
    title = f"Restoration Services in New York | Water, Fire & Mold | {BRAND}"
    desc = "Explore all water damage, fire damage, mold remediation, sewage cleanup and storm restoration services offered statewide across New York."
    return page(title, desc, "/services/index.html", "services", body, schema, depth="")


# ------------------------------------------------------------ LOCATIONS --

LOCATION_DETAIL = {
"new-york-city": dict(
    intro=("New York City's five boroughs combine some of the oldest plumbing infrastructure in "
           "the state with the highest building density, which means a single pipe failure in a "
           "Manhattan pre-war building or a Brooklyn brownstone can affect several units at once. "
           "Coastal flood risk from the Hudson and East Rivers adds a second layer of exposure, "
           "particularly in low-lying parts of Lower Manhattan, Red Hook and the Rockaways."),
    landmarks="Manhattan, Brooklyn, Queens, the Bronx, Staten Island, and the co-op corridors of the Upper West Side and Forest Hills",
    risk_note=f"Coastal storm surge risk is highest in flood zones mapped by {ext('fema_flood')}; NYC building co-ops and condo boards should keep current flood documentation on file.",
    weather_office="https://www.weather.gov/okx/",
),
"long-island": dict(
    intro=("Long Island's exposure runs from the North Shore's older estate homes to the barrier "
           "beaches of the South Shore, where nor'easters and hurricane remnants push storm surge "
           "directly into ground-floor living space. High water tables across Nassau and Suffolk "
           "Counties also make basement seepage a year-round issue independent of any single storm."),
    landmarks="Nassau County, Suffolk County, the North Shore, the South Shore and the East End",
    risk_note=f"Homeowners near the coast should check current flood zone maps through {ext('fema_flood')} before storm season and confirm whether a standard policy or NFIP coverage applies.",
    weather_office="https://www.weather.gov/okx/",
),
"westchester-county": dict(
    intro=("Westchester's older housing stock in Yonkers, New Rochelle, White Plains and the river "
           "towns along the Hudson combines aging copper and galvanized plumbing with steep, wooded "
           "lots that funnel stormwater toward foundations. Basement finishing is common here, which "
           "raises the stakes when water intrusion does occur."),
    landmarks="Yonkers, New Rochelle, White Plains, Mount Vernon and the Hudson River towns",
    risk_note=f"The county's hilly terrain concentrates runoff quickly during heavy rain events tracked by {ext('noaa_nws')}, so gutter and grading maintenance meaningfully reduces basement water risk.",
    weather_office="https://www.weather.gov/okx/",
),
"hudson-valley": dict(
    intro=("The Mid-Hudson region — Poughkeepsie, Newburgh, Kingston and the surrounding river "
           "towns — sits along a flood-prone corridor shaped by the Hudson River and its tributary "
           "creeks. Spring ice-jam flooding and summer flash flooding both show up regularly in "
           "county emergency management reports."),
    landmarks="Poughkeepsie, Newburgh, Kingston, Beacon and the Rondout Creek corridor",
    risk_note=f"Ice-jam flooding is a distinct regional risk the {ext('noaa_nws')} tracks separately from rainfall flooding, and it can happen with little warning during a fast winter thaw.",
    weather_office="https://www.weather.gov/aly/",
),
"albany-capital-region": dict(
    intro=("Albany, Troy, Schenectady and the surrounding Capital District see a predictable annual "
           "pattern: spring snowmelt raises the water table and overwhelms sump systems in older "
           "basements, particularly in neighborhoods built before modern foundation waterproofing "
           "standards."),
    landmarks="Albany, Troy, Schenectady, Saratoga Springs and the Mohawk-Hudson confluence",
    risk_note=f"Spring melt flooding often coincides with power outages, which is why we recommend a battery-backup sump pump for basements in this region — see {ext('redcross')} for broader flood preparedness guidance.",
    weather_office="https://www.weather.gov/aly/",
),
"buffalo-western-ny": dict(
    intro=("Buffalo and Western New York experience some of the heaviest lake-effect snowfall in "
           "the country, and the real risk often isn't the snow itself but the rapid thaw cycles "
           "that follow — roofs shed meltwater faster than gutters and drains can handle it, and "
           "basements flood as frozen ground fails to absorb runoff."),
    landmarks="Buffalo, Cheektowaga, Amherst, Niagara Falls and the Lake Erie shoreline",
    risk_note=f"Flat and low-slope roofs are at elevated collapse risk under wet, heavy lake-effect snow; the {ext('noaa_nws')} Buffalo office issues specific snow-load advisories worth monitoring each winter.",
    weather_office="https://www.weather.gov/buf/",
),
"rochester-finger-lakes": dict(
    intro=("Rochester and the Finger Lakes region combine Lake Ontario shoreline flood risk with "
           "an older Monroe County housing stock where deferred plumbing maintenance is a common "
           "cause of water loss. Lake-driven storms can also push wind-driven rain into homes along "
           "the shoreline corridor."),
    landmarks="Rochester, Irondequoit, Greece, Canandaigua and the Lake Ontario shoreline",
    risk_note=f"Shoreline flooding tied to Lake Ontario water levels is tracked separately from rainfall flooding; {ext('ny_dec')} publishes regional lake-level and shoreline data for homeowners in this corridor.",
    weather_office="https://www.weather.gov/buf/",
),
"syracuse-central-ny": dict(
    intro=("Syracuse and Central New York see some of the state's heaviest average snowfall, and "
           "winter pipe bursts from frozen, uninsulated plumbing are one of the most common calls "
           "we take across Onondaga County. Freeze-thaw cycles put ongoing stress on both plumbing "
           "and building envelopes."),
    landmarks="Syracuse, Onondaga County, Cicero, Liverpool and the Finger Lakes' northern edge",
    risk_note=f"Insulating exposed pipes in unheated crawlspaces and garages meaningfully reduces winter burst risk; {ext('noaa_nws')} publishes seasonal outlooks that help homeowners plan ahead of hard freezes.",
    weather_office="https://www.weather.gov/bgm/",
),
"utica-mohawk-valley": dict(
    intro=("Utica, Rome and the Mohawk Valley's mill-town infrastructure means a mix of aging "
           "municipal sewer systems and older residential plumbing, both of which contribute to "
           "the region's water and sewage-backup calls. The Mohawk River corridor itself carries "
           "seasonal flood risk tied to snowmelt."),
    landmarks="Utica, Rome, Herkimer and the Mohawk River corridor",
    risk_note=f"Combined sewer systems in some older Mohawk Valley municipalities can back up into basements during heavy rain; regional advisories are available through {ext('noaa_nws')}.",
    weather_office="https://www.weather.gov/bgm/",
),
"binghamton-southern-tier": dict(
    intro=("Binghamton and the Southern Tier sit at the confluence of the Susquehanna and Chenango "
           "Rivers, a location that has produced some of New York's most significant documented "
           "flood events. Homes and businesses near either river corridor carry meaningfully "
           "elevated flood risk compared to the regional average."),
    landmarks="Binghamton, Johnson City, Endicott and the Susquehanna-Chenango river confluence",
    risk_note=f"Given the area's flood history, confirming NFIP flood coverage through {ext('fema_flood')} is worth doing even for properties just outside the mapped floodplain.",
    weather_office="https://www.weather.gov/bgm/",
),
}

def build_location(l):
    d = LOCATION_DETAIL[l["slug"]]
    svc_html = "".join(f'<li><a href="/services/{s["slug"]}.html">{s["name"]}</a></li>' for s in SERVICES)
    others = [x for x in LOCATIONS if x["slug"] != l["slug"]][:6]
    other_html = "".join(f'<li><a href="/locations/{o["slug"]}.html">{o["name"]}</a></li>' for o in others)
    plain_name = l['name'].replace("&amp;","&")
    body = f"""
<div class="content-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/index.html">Home</a><span>/</span><a href="/locations/index.html">Locations</a><span>/</span>{l['name']}</div>
    <h1>Water, Fire &amp; Mold Restoration in {l['name']}, NY</h1>
    <p>{l['blurb']} &mdash; {d['landmarks']}.</p>
  </div>
</div>
<section>
  <div class="container two-col">
    <div class="prose">
      <h2>Restoration Coverage in {l['name']}</h2>
      <p>{d['intro']}</p>
      <p>{BRAND} keeps equipment and IICRC-certified crews staged in the {l['region'].replace('&amp;','&')} so
      response time to {plain_name} addresses stays consistent whether the call comes from a
      dense downtown block or a more rural stretch of the county.</p>
      <h2>Local Risk Factors</h2>
      <p>{d['risk_note']}</p>
      <h2>Services Available in {l['name']}</h2>
      <p>Every service we offer statewide is available in {plain_name}, including:</p>
      <ul>{svc_html}</ul>
      <h2>Check Current Weather &amp; Advisories</h2>
      <p>Before a forecasted storm, it's worth checking the local
      <a href="{d['weather_office']}" target="_blank" rel="noopener noreferrer">National Weather Service forecast office</a>
      covering {plain_name} for active watches and warnings.</p>
    </div>
    <aside>
      <div class="side-box">
        <h4>24/7 Emergency Line</h4>
        <p style="font-family:var(--font-mono);font-size:20px;color:var(--deep-water);margin-bottom:4px;">{PHONE_DISPLAY}</p>
        <p class="tag-source">Crews staged across {l['region'].replace('&amp;','&')}.</p>
        <a class="call-now" href="tel:{PHONE_TEL}">Call Now</a>
      </div>
      <div class="side-box">
        <h4>Other Service Areas</h4>
        <ul>{other_html}</ul>
      </div>
    </aside>
  </div>
</section>
<section class="section--alt">
  <div class="container">
    <div class="cta-band">
      <h2>Restoration Emergency in {l['name']}?</h2>
      <p>Call now for 24/7 dispatch to your address.</p>
      <div class="btns"><a class="btn btn--primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
      <a class="btn btn--ghost" href="/contact.html">Request Free Estimate</a></div>
    </div>
  </div>
</section>
"""
    schema = [
        breadcrumb_schema([("Home","/index.html"),("Locations","/locations/index.html"),(plain_name, f"/locations/{l['slug']}.html")]),
        {
            "@context":"https://schema.org","@type":"HomeAndConstructionBusiness",
            "name": f"{BRAND} — {plain_name}", "telephone": PHONE_TEL,
            "areaServed": {"@type":"City","name":plain_name},
            "parentOrganization": {"@type":"Organization","name":BRAND}
        }
    ]
    title = f"Water & Fire Damage Restoration in {plain_name}, NY | {BRAND}"
    desc = f"24/7 emergency water, fire, mold and storm damage restoration in {plain_name}, New York. IICRC-certified, insurance-friendly, rapid dispatch. Call {PHONE_DISPLAY}."
    return page(title, desc, f"/locations/{l['slug']}.html", "locations", body, schema, depth="")

def build_locations_index():
    chips = location_chips(LOCATIONS, depth="")
    cards = "".join(f"""<div class="card"><span class="card__icon">{l['region']}</span>
        <h3>{l['name']}</h3><p>{l['blurb']}</p>
        <a class="card-link" href="/locations/{l['slug']}.html">View Coverage &rarr;</a></div>""" for l in LOCATIONS)
    body = f"""
<div class="content-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/index.html">Home</a><span>/</span>Locations</div>
    <h1>New York Service Areas</h1>
    <p>{BRAND} stages restoration crews across all 62 New York counties — from the
    five boroughs to the North Country. Find local risk factors and coverage
    details for your region below.</p>
  </div>
</div>
<section><div class="container grid-3">{cards}</div></section>
"""
    schema = [breadcrumb_schema([("Home","/index.html"),("Locations","/locations/index.html")])]
    title = f"New York Service Areas | Statewide Restoration Coverage | {BRAND}"
    desc = "See 24/7 water, fire and mold restoration coverage across New York State, including NYC, Long Island, the Capital Region, Buffalo, Rochester and more."
    return page(title, desc, "/locations/index.html", "locations", body, schema, depth="")


# ------------------------------------------------------------------ ABOUT

def build_about():
    body = f"""
<div class="content-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/index.html">Home</a><span>/</span>About</div>
    <h1>About {BRAND}</h1>
    <p>An IICRC-certified restoration company built for New York's buildings, weather and insurance system.</p>
  </div>
</div>
<section>
  <div class="container two-col">
    <div class="prose">
      <h2>Why We Started With New York, Not a Franchise Map</h2>
      <p>{BRAND} was built specifically around New York State's restoration challenges rather
      than adapted from a national franchise template. That distinction matters: a company
      that only occasionally works here doesn't know that Capital Region basements flood every
      spring, that Buffalo's lake-effect thaw cycles put flat roofs at collapse risk, or that
      a Manhattan co-op board has different documentation requirements than a Long Island
      single-family home.</p>
      <p>Our technicians are IICRC-certified through {ext('iicrc')}, the industry's recognized
      standard-setting body for water, fire and mold restoration. We carry that certification
      into every job — not just as a credential, but as the actual drying, containment and
      documentation standard we follow.</p>
      <h2>How We're Different</h2>
      <ul class="checklist">
        <li>One point of contact from first call to final insurance sign-off</li>
        <li>Transparent, itemized pricing before any work begins</li>
        <li>Crews staged regionally, not dispatched from a single distant hub</li>
        <li>In-house insurance documentation and adjuster coordination</li>
        <li>Equipment and protocols matched to New York's specific climate risks</li>
      </ul>
      <h2>Licensing &amp; Credentials</h2>
      <p>{BRAND} is licensed and insured to operate throughout New York State. You can review
      consumer protection guidance and verify contractor standing through
      {ext('ny_dfs')}. Our teams also follow workplace safety practices consistent with
      {ext('osha_water')} on every jobsite.</p>
    </div>
    <aside>
      <div class="side-box">
        <h4>24/7 Emergency Line</h4>
        <p style="font-family:var(--font-mono);font-size:20px;color:var(--deep-water);margin-bottom:4px;">{PHONE_DISPLAY}</p>
        <a class="call-now" href="tel:{PHONE_TEL}">Call Now</a>
      </div>
      <div class="side-box">
        <h4>Explore</h4>
        <ul>
          <li><a href="/services/index.html">Our Services</a></li>
          <li><a href="/locations/index.html">Service Areas</a></li>
          <li><a href="/blog/index.html">Restoration Blog</a></li>
          <li><a href="/contact.html">Contact Us</a></li>
        </ul>
      </div>
    </aside>
  </div>
</section>
"""
    schema = [breadcrumb_schema([("Home","/index.html"),("About","/about.html")]), local_business_schema()]
    title = f"About {BRAND} | IICRC-Certified, Statewide New York Restoration"
    desc = f"Learn about {BRAND}, an IICRC-certified water, fire and mold restoration company licensed and insured to serve all of New York State."
    return page(title, desc, "/about.html", "about", body, schema)

# ---------------------------------------------------------------- CONTACT

def build_contact():
    body = f"""
<div class="content-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/index.html">Home</a><span>/</span>Contact</div>
    <h1>Contact {BRAND}</h1>
    <p>Call our 24/7 dispatch line for emergencies, or send details for a free, no-obligation estimate.</p>
  </div>
</div>
<section>
  <div class="container two-col">
    <div class="prose">
      <h2>Request a Free Estimate</h2>
      <p>For active emergencies — active leaks, flooding, fire or sewage backup —
      call {PHONE_DISPLAY} directly for the fastest response. For non-urgent
      estimates or questions, use the form below and a team member will follow up
      within one business day.</p>
      <form onsubmit="return false;" style="display:grid;gap:16px;max-width:520px;margin-top:24px;">
        <label>Full Name<br><input type="text" name="name" required style="width:100%;padding:12px;border:1px solid var(--line);border-radius:4px;margin-top:6px;"></label>
        <label>Phone Number<br><input type="tel" name="phone" required style="width:100%;padding:12px;border:1px solid var(--line);border-radius:4px;margin-top:6px;"></label>
        <label>New York City / Town<br><input type="text" name="city" required style="width:100%;padding:12px;border:1px solid var(--line);border-radius:4px;margin-top:6px;"></label>
        <label>What Happened?<br><textarea name="details" rows="4" style="width:100%;padding:12px;border:1px solid var(--line);border-radius:4px;margin-top:6px;"></textarea></label>
        <button type="submit" class="btn btn--primary" style="justify-self:start;">Request Free Estimate</button>
      </form>
      <p class="tag-source" style="margin-top:14px;">This form is a static template — connect it to your CRM, email service, or a form backend (e.g. Formspree, Netlify Forms) before publishing.</p>
    </div>
    <aside>
      <div class="side-box">
        <h4>24/7 Emergency Line</h4>
        <p style="font-family:var(--font-mono);font-size:20px;color:var(--deep-water);margin-bottom:4px;">{PHONE_DISPLAY}</p>
        <a class="call-now" href="tel:{PHONE_TEL}">Call Now</a>
      </div>
      <div class="side-box">
        <h4>Office</h4>
        <p style="font-size:14.5px;">500 Dispatch Way, Suite 210<br>Albany, NY 12207</p>
      </div>
      <div class="side-box">
        <h4>Service Areas</h4>
        <ul>{"".join(f'<li><a href="/locations/{l["slug"]}.html">{l["name"]}</a></li>' for l in LOCATIONS[:6])}
        <li><a href="/locations/index.html">View All &rarr;</a></li></ul>
      </div>
    </aside>
  </div>
</section>
"""
    schema = [breadcrumb_schema([("Home","/index.html"),("Contact","/contact.html")]), local_business_schema()]
    title = f"Contact {BRAND} | 24/7 New York Emergency Restoration"
    desc = f"Reach {BRAND}'s 24/7 dispatch line at {PHONE_DISPLAY} or request a free restoration estimate online. Serving all of New York State."
    return page(title, desc, "/contact.html", "contact", body, schema)


# ------------------------------------------------------------------- BLOG

BLOG_CONTENT = {
"how-long-does-water-damage-restoration-take": dict(
    body=[
        ("The Honest Timeline", [
        "Most straightforward water losses — a single-room leak caught within a day — take 3 to 5 days "
        "for extraction and drying, followed by 1 to 3 weeks for repairs depending on how much material "
        "needs to be replaced. Larger or delayed losses take longer, mainly because more material has "
        "absorbed water and needs to reach the same dry-standard readings before rebuild can start.",
        f"{BRAND} sets drying targets using moisture meters and, when needed, thermal imaging, rather "
        f"than guessing by sight or touch, which keeps the timeline honest rather than optimistic."]),
        ("Day-by-Day Breakdown", [
        "Day 1 is extraction and setup: standing water removed, damaged materials assessed, and "
        "dehumidifiers and air movers placed. Days 2 through 4 are active drying, with daily moisture "
        "checks. Once every material hits target readings, drying equipment comes down and repairs — "
        "drywall, flooring, paint — begin, typically taking anywhere from a few days to several weeks "
        "depending on scope."]),
        ("What Slows a Timeline Down", [
        "The most common delays are hidden moisture inside wall cavities or subfloor that wasn't caught "
        "in the initial inspection, insurance approval delays before rebuild can start, and material "
        "availability for specialty flooring or cabinetry. Choosing a restoration company that documents "
        f"thoroughly at the first visit — following standards from {ext('iicrc')} — reduces the chance "
        "of a delay caused by incomplete initial documentation."]),
    ],
),
"mold-prevention-checklist-for-new-york-homes": dict(
    body=[
        ("Why New York Homes Are Especially Susceptible", [
        f"New York's humid summers and older housing stock create ideal mold conditions when combined "
        f"with even minor, unresolved moisture. The {ext('epa_mold')} recommends keeping indoor relative "
        "humidity below 60%, and ideally between 30-50%, to meaningfully reduce mold risk regardless of "
        "climate."]),
        ("Room-by-Room Checklist", [
        "<strong>Bathrooms:</strong> Run the exhaust fan during and 20 minutes after showers; check "
        "grout and caulk annually for gaps. <strong>Kitchens:</strong> Check under the sink monthly for "
        "slow leaks; ensure range hood ventilation exhausts outside, not into the attic. "
        "<strong>Basements:</strong> Use a dehumidifier during humid months; inspect for efflorescence "
        "or musty odor. <strong>Attics:</strong> Confirm roof and bathroom vents exhaust outside; check "
        "for daylight or staining near roof penetrations after storms."]),
        ("When to Call a Professional", [
        "A DIY approach works for prevention, but visible mold growth larger than roughly 10 square feet, "
        f"or any mold following a water loss that wasn't fully dried, should be handled by a certified "
        f"remediation team rather than a household cleaner — see {ext('cdc_mold')} for health guidance on "
        "when professional remediation is warranted."]),
    ],
),
"filing-a-new-york-water-damage-insurance-claim": dict(
    body=[
        ("Document Before You Clean", [
        "Before any cleanup begins, photograph and video the damage from multiple angles, including "
        "close-ups of affected materials and wide shots showing the extent of the loss. This documentation "
        "is the foundation of your claim and is much harder to recreate after cleanup starts."]),
        ("Understand What Your Policy Covers", [
        "Standard New York homeowners policies typically cover sudden, accidental water damage — like a "
        "burst pipe — but usually exclude flood water and often exclude sewer backup unless you've added "
        f"a specific endorsement. Review your declarations page, and consult {ext('ny_dfs')} if the "
        "distinction in your specific policy is unclear."]),
        ("Working With Your Adjuster", [
        "Provide your restoration company's scope of work and moisture documentation directly to your "
        "adjuster rather than relying on a verbal description. If a settlement offer seems to underscope "
        f"the actual damage, you can request a re-inspection, and {ext('ny_dfs')} outlines a formal "
        "complaint process if a claim is unreasonably delayed or denied."]),
    ],
),
}

def build_blog_post(p):
    c = BLOG_CONTENT[p["slug"]]
    sections = "".join(f"<h2>{h}</h2>" + "".join(f"<p>{para}</p>" for para in paras) for h, paras in c["body"])
    other_posts = [x for x in BLOG if x["slug"] != p["slug"]]
    other_html = "".join(f'<li><a href="/blog/{o["slug"]}.html">{o["title"]}</a></li>' for o in other_posts)
    body = f"""
<div class="content-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/index.html">Home</a><span>/</span><a href="/blog/index.html">Blog</a><span>/</span>{p['title']}</div>
    <h1>{p['title']}</h1>
    <p>{p['desc']}</p>
  </div>
</div>
<section>
  <div class="container two-col">
    <div class="prose">
      {sections}
      <p><em>Have an active water, fire or mold issue right now? Call {BRAND} at
      <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> for 24/7 dispatch anywhere in New York State.</em></p>
    </div>
    <aside>
      <div class="side-box">
        <h4>24/7 Emergency Line</h4>
        <p style="font-family:var(--font-mono);font-size:20px;color:var(--deep-water);margin-bottom:4px;">{PHONE_DISPLAY}</p>
        <a class="call-now" href="tel:{PHONE_TEL}">Call Now</a>
      </div>
      <div class="side-box"><h4>More Articles</h4><ul>{other_html}</ul></div>
      <div class="side-box"><h4>Related Services</h4>
        <ul><li><a href="/services/water-damage-restoration.html">Water Damage Restoration</a></li>
        <li><a href="/services/mold-remediation.html">Mold Remediation</a></li>
        <li><a href="/services/insurance-claim-assistance.html">Insurance Claim Assistance</a></li></ul>
      </div>
    </aside>
  </div>
</section>
"""
    schema = [breadcrumb_schema([("Home","/index.html"),("Blog","/blog/index.html"),(p["title"], f"/blog/{p['slug']}.html")]),
              {"@context":"https://schema.org","@type":"Article","headline":p["title"],
               "description":p["desc"],"author":{"@type":"Organization","name":BRAND},
               "publisher":{"@type":"Organization","name":BRAND}}]
    title = f"{p['title']} | {BRAND} Blog"
    return page(title, p["desc"], f"/blog/{p['slug']}.html", "blog", body, schema, depth="")

def build_blog_index():
    cards = "".join(f"""<div class="card"><span class="card__icon">GUIDE</span>
        <h3>{p['title']}</h3><p>{p['desc']}</p>
        <a class="card-link" href="/blog/{p['slug']}.html">Read Article &rarr;</a></div>""" for p in BLOG)
    body = f"""
<div class="content-hero">
  <div class="container">
    <div class="breadcrumb"><a href="/index.html">Home</a><span>/</span>Blog</div>
    <h1>Restoration Guides &amp; New York Resources</h1>
    <p>Practical guidance on water damage timelines, mold prevention and insurance claims for New York property owners.</p>
  </div>
</div>
<section><div class="container grid-3">{cards}</div></section>
"""
    schema = [breadcrumb_schema([("Home","/index.html"),("Blog","/blog/index.html")])]
    title = f"Restoration Blog | New York Water, Fire & Mold Guides | {BRAND}"
    desc = "Guides on water damage restoration timelines, mold prevention and insurance claims for New York homeowners and businesses."
    return page(title, desc, "/blog/index.html", "blog", body, schema, depth="")


# ------------------------------------------------------------------- MAIN

def write(path, content):
    full = os.path.join(ROOT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)

def main():
    write("index.html", build_home())
    write("about.html", build_about())
    write("contact.html", build_contact())
    write("services/index.html", build_services_index())
    for s in SERVICES:
        write(f"services/{s['slug']}.html", build_service(s))
    write("locations/index.html", build_locations_index())
    for l in LOCATIONS:
        write(f"locations/{l['slug']}.html", build_location(l))
    write("blog/index.html", build_blog_index())
    for p in BLOG:
        write(f"blog/{p['slug']}.html", build_blog_post(p))

    # sitemap.xml
    urls = ["/index.html","/about.html","/contact.html","/services/index.html","/locations/index.html","/blog/index.html"]
    urls += [f"/services/{s['slug']}.html" for s in SERVICES]
    urls += [f"/locations/{l['slug']}.html" for l in LOCATIONS]
    urls += [f"/blog/{p['slug']}.html" for p in BLOG]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        priority = "1.0" if u == "/index.html" else ("0.9" if u.count("/")==2 and "index" in u else "0.8")
        sm.append(f"  <url><loc>{DOMAIN}{u}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm))

    # robots.txt
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")

    # simple favicon
    write("images/favicon.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#0E2A47"/><circle cx="32" cy="32" r="30" fill="none" stroke="#F0A202" stroke-width="4"/><text x="32" y="40" font-family="IBM Plex Mono, monospace" font-size="20" font-weight="700" fill="#F0A202" text-anchor="middle">ESR</text></svg>""")

if __name__ == "__main__":
    main()
    print("BUILD COMPLETE")
