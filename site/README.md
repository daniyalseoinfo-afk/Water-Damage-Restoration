# Empire State Restoration — Statewide New York Website

A complete, SEO-optimized static website for a water/fire/mold emergency
restoration company serving all of New York State. Built as a static HTML
site so it can be pushed straight to a GitHub repo and hosted on GitHub
Pages, Netlify, Vercel, or any static host — no backend required.

## What's included

```
index.html                 Homepage
about.html                 About / EEAT page
contact.html               Contact + estimate request form (template)
services/
  index.html                Services hub
  water-damage-restoration.html
  flood-cleanup.html
  fire-damage-restoration.html
  mold-remediation.html
  sewage-cleanup.html
  basement-water-removal.html
  storm-damage-restoration.html
  commercial-restoration.html
  insurance-claim-assistance.html
locations/
  index.html                 Locations hub
  new-york-city.html          + 9 more NY regions (statewide coverage)
  ...
blog/
  index.html
  how-long-does-water-damage-restoration-take.html
  mold-prevention-checklist-for-new-york-homes.html
  filing-a-new-york-water-damage-insurance-claim.html
css/style.css               Design system (single stylesheet)
js/main.js                  Mobile nav toggle
sitemap.xml                 Auto-generated, submit to Google Search Console
robots.txt                  Points crawlers at the sitemap
images/favicon.svg
build.py                    Python generator — the site's source of truth
```

Every page is a pre-rendered static `.html` file, generated from `build.py`.
**Edit `build.py`, not the individual HTML files** — re-run `python3 build.py`
to regenerate the whole site consistently after any content change.

## Design

A "dispatch console" visual system: deep water-navy (`#0E2A47`) with a
signal-amber accent (`#F0A202`) used for CTAs and gauge dials, a condensed
display face (Barlow Condensed) for headlines, and a monospace face (IBM
Plex Mono) for phone numbers, stats and the header ticker — meant to evoke
an emergency dispatch board rather than a generic contractor template.
Fully responsive, keyboard-focus-visible, and respects `prefers-reduced-motion`.

## SEO implementation

- **60/40 content ratio** — every service page leads with deep service
  content (causes, signs, process, FAQs) and closes with a New York
  regional-risk section; every location page leads with local risk factors
  and closes with the full service list — mirroring the 60% service / 40%
  location split used across the site.
- **Meta titles & descriptions** — unique, keyword-targeted `<title>` and
  `<meta name="description">` on all 27 pages.
- **Schema.org JSON-LD** — `HomeAndConstructionBusiness`/`LocalBusiness`,
  `Service`, `FAQPage`, `BreadcrumbList`, and `Article` markup throughout.
- **Internal linking** — every service page links to related services and
  sample locations; every location page links to all services and nearby
  regions; blog posts link back to relevant service pages.
- **Outbound authority linking** — pages cite IICRC, EPA, FEMA, NOAA/NWS,
  CDC, NY DFS, NY DEC, OSHA and the U.S. Fire Administration where relevant
  (`rel="noopener noreferrer"`, opens in a new tab) to support E-E-A-T.
- **`sitemap.xml`** lists all 27 URLs; **`robots.txt`** points to it.
- One `<h1>` per page, logical `H2`/`H3` hierarchy, descriptive alt text
  pattern ready for real photography (see "Before you launch" below).

## Before you launch (required)

This is a template built with a **fictional business name, phone number,
address and domain** — replace these in `build.py` (top of the file) and
re-run the build:

- `DOMAIN` — your real domain
- `PHONE_DISPLAY` / `PHONE_TEL` — your real phone number
- `BRAND` — your real business name
- Office address inside `local_business_schema()` and `footer()`
- Google Business Profile / social links in `local_business_schema()`
- Replace stock testimonial copy with real, verifiable customer reviews
- Add real photography (the site currently ships without photos —
  `images/` only has a placeholder favicon)
- Wire the contact form in `contact.html` to a real backend (Formspree,
  Netlify Forms, or your CRM) — it's a static template right now
- Verify licensing/insurance claims and IICRC certification numbers are
  accurate before publishing EEAT/trust copy

## Local preview

```
python3 -m http.server 8080
# then open http://localhost:8080/index.html
```

## Deploy to GitHub Pages

```
git init
git add .
git commit -m "Initial site"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
# In GitHub: Settings → Pages → Deploy from branch → main → / (root)
```
