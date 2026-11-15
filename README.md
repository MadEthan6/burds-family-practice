# Burds Family Practice: Redesigned Static Website

A complete redesign and self-contained static build of **Burds Family Practice** (`burdsfamilypractice.com`), migrating off Squarespace into a fast, accessible, 32-page static site grounded in the practice's official Facebook banner/logo, 8-color brand palette, and self-hosted typography.

## Structure

```text
build.py            # builds 9 core pages (incl. New Patients + 404), sitemap.xml, robots.txt, + 8 Learning Hub guides + 15 Blog posts -> dist/
tools_emblem.py     # generates emblem-dark.svg, emblem-light.svg, favicon.svg
src/layout.html     # shared header (Facebook emblem + script lockup), Deep Green footer (Facebook banner), schema.org
src/pages/*.html    # core pages (home, new patients, services, DPC, occupational health, about, resources, contact, 404)
src/assets/         # css, js, self-hosted fonts (Cormorant Garamond, Josefin Sans, Allura), photos & Facebook brand assets
mirror/             # archived Squarespace reference pages used to generate local learn/ and blog/ pages
dist/               # generated 32-page static site ready to deploy
```

## Build & Preview

```bash
python3 tools_emblem.py   # regenerate SVG emblems
python3 build.py          # build all 32 pages into dist/
python3 build.py serve    # build + serve on http://localhost:8080
```

## Official Brand System

- **Facebook Assets Pulled**: `src/assets/img/fb-banner.png` (`960×355` cover banner) and `src/assets/img/fb-logo.jpg` (`720×720` profile emblem).
- **Fonts (Self-Hosted WOFF2)**: `Source Sans 3` (variable 400–700 + italic) for all body copy, `Cormorant Garamond` (500, 500 italic, 600) for headings, `Josefin Sans` (400, 600) for labels/nav/buttons only, and `Allura` (400) for the script wordmark.
- **Brand Colors**:
  - **Deep Green**: `#003C42` (PMS 2217 C)
  - **Rooted Sage**: `#6F8371` (PMS 5625 C)
  - **Hometown Aqua**: `#98BEAE` (PMS 558 C)
  - **Warm Glow**: `#D6A379` (PMS 2430 C)
  - **Familiar Ground**: `#DAC6B6` (PMS 482 C)
  - **Gentle Light**: `#E9E6DC`
  - **Steady Stone**: `#58595B`
  - **Warm Glow Ink**: `#8A5A36`

## Key Features & Content

- **Unified Branding**: Official Facebook profile emblem in the sticky header with `Allura` + `Josefin Sans` wordmark lockup, Facebook banner featured in the Deep Green hero and footer, and `Cormorant Garamond` editorial headings.
- **Direct Primary Care Pricing**: Transparent rates integrated across Home, Services, and DPC ($99/mo adult, $79/mo spouse/partner, $49/mo child, $276/mo family of 4).
- **Occupational Health Showcase**: Facebook campaign styling (*"Built for the people who build Peosta"* with `01–04` clearances) and FMCSA National Registry Certified Medical Examiner details.
- **SkinRx by Burds & Community**: SkinBetter Science aesthetics, Cherry monthly financing, `'Be A Light' 5K` sponsorship, and all 6 local *Our Favorites* community partners.
- **100% Local Migration**: All 8 Learning Hub guides (`dist/learn/*.html`) and 15 Blog articles (`dist/blog/*.html`) built locally with no reliance on Squarespace.

## v2 Overhaul (Nov 2026)

- **Readability**: body text moved from Josefin Sans to self-hosted Source Sans 3 at 18px; no descriptive copy below ~16px.
- **Home page**: photo-led hero with live open/closed status card; "How can we help today?" task grid (sick today, new patients, DPC, employers, mental health, portal) replaces the logo hero, duplicate trust bar, filler photo strip and redundant path cards.
- **New Patients page** (`new-patients.html`): 3-step getting-started, what to bring, insurance vs. DPC, where-to-go (us / urgent care / ER), and FAQ. Added to main nav and footer.
- **DPC calculator**: removed the "effective $/visit" line (it showed ~$414/visit, which argued against membership); now reinforces flat pricing.
- **About**: team grid centers its last row instead of leaving an orphan card.
- **SEO/hosting**: generated `sitemap.xml`, `robots.txt`, and a `404.html` with root-absolute asset paths.

## Review QR Landing Page

- `src/review/index.html` → `dist/review/index.html` (served at `/review/`). Standalone, mobile-first, `noindex`, excluded from the sitemap.
- Links: Google (listing via CID; swap in the Business Profile "Ask for reviews" `g.page/r/.../review` link when available), Facebook reviews, Tebra.
- `qr/review-qr.svg` / `qr/review-qr.png` point at `https://www.burdsfamilypractice.com/review/`. Regenerate if the page is hosted elsewhere.
