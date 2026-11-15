#!/usr/bin/env python3
"""Build publishable social/display ads for Burds Family Practice.

Each campaign is rendered in three formats with headless Chrome:
  square    1080x1080  Facebook/Instagram feed
  story     1080x1920  Instagram/Facebook Stories & Reels (keeps text out of the
                       top 250px / bottom 340px UI safe zones)
  landscape 1200x628   Facebook link ads, Google Display, LinkedIn, Nextdoor

Usage:  python3 ads/build_ads.py            -> ads/out/<campaign>-<format>.png
"""
import html
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "src" / "assets"
OUT = ROOT / "ads" / "out"
CHROME = shutil.which("google-chrome") or shutil.which("chromium") or "chromium-browser"

PHONE = "(563) 588-6659"
URL = "burdsfamilypractice.com"

FORMATS = {
    "square": (1080, 1080),
    "story": (1080, 1920),
    "landscape": (1200, 628),
}

# --------------------------------------------------------------------------
# Campaigns. Copy avoids implying knowledge of the viewer's health (Meta
# personal-attributes policy) and uses only facts published on the site.
# --------------------------------------------------------------------------
CAMPAIGNS = [
    {
        "slug": "01-direct-primary-care",
        "layout": "photo",
        "photo": "img/infant-exam.jpg",
        "pos": "50% 35%",
        "eyebrow": "Direct Primary Care · Peosta, IA",
        "headline": "Unlimited visits.<br><em>One flat monthly fee.</em>",
        "sub": "$0 copays. Same- or next-day appointments. Unlimited routine visits.",
        "prices": [("$99", "adult / mo"), ("$79", "partner / mo"), ("$49", "child / mo")],
        "cta": f"Call {PHONE}",
    },
    {
        "slug": "02-new-patients",
        "layout": "photo",
        "photo": "img/front-desk.jpg",
        "pos": "50% 40%",
        "eyebrow": "Now accepting new patients",
        "headline": "Your whole family.<br><em>One Peosta practice.</em>",
        "sub": "Care for newborns through older adults. Same provider every visit. Most insurance accepted.",
        "cta": f"Call {PHONE}",
    },
    {
        "slug": "03-same-day-sick-visits",
        "layout": "photo",
        "photo": "img/jenny-heart-exam.jpg",
        "pos": "60% 40%",
        "eyebrow": "Primary care · Peosta, IA",
        "headline": "Sick days happen.<br><em>We save room for them.</em>",
        "sub": "Same-day slots for colds, flu, sore throats, ear infections, and minor injuries right here in Peosta.",
        "cta": f"Call {PHONE}",
    },
    {
        "slug": "04-occupational-health",
        "layout": "type",
        "eyebrow": "Occupational Health · Peosta, IA",
        "headline": "Workplace health<br><em>right here in Peosta.</em>",
        "sub": "Pre-employment exams and certified DOT physicals, usually scheduled the same week.",
        "list": [
            ("01", "Pre-employment physicals"),
            ("02", "DOT physicals (FMCSA certified)"),
            ("03", "12-panel drug screening"),
            ("04", "Work injury care"),
        ],
        "cta": f"Employers: call {PHONE}",
    },
    {
        "slug": "05-locally-owned",
        "layout": "photo",
        "photo": "img/storefront.jpg",
        "pos": "50% 30%",
        "eyebrow": "Independent · Locally owned",
        "headline": "Care that knows you.<br><em>Right here at home.</em>",
        "hs": 0.8,
        "sub": "Independent and locally owned in Peosta. When you call, you reach the clinic team who knows you and your family.",
        "cta": f"Call {PHONE}",
    },
]

CSS = """
@font-face{font-family:Allura;src:url(ASSETS/fonts/allura-400.woff2)}
@font-face{font-family:Cormorant;font-weight:500;src:url(ASSETS/fonts/cormorant-garamond-500.woff2)}
@font-face{font-family:Cormorant;font-weight:500;font-style:italic;src:url(ASSETS/fonts/cormorant-garamond-500-italic.woff2)}
@font-face{font-family:Cormorant;font-weight:600;src:url(ASSETS/fonts/cormorant-garamond-600.woff2)}
@font-face{font-family:Josefin;font-weight:400;src:url(ASSETS/fonts/josefin-sans-400.woff2)}
@font-face{font-family:Josefin;font-weight:600;src:url(ASSETS/fonts/josefin-sans-600.woff2)}
@font-face{font-family:Source;font-weight:400 700;src:url(ASSETS/fonts/source-sans-3-400.woff2)}
:root{--green:#003C42;--green2:#00282c;--sage:#6F8371;--aqua:#98BEAE;--glow:#D6A379;
 --ground:#DAC6B6;--light:#E9E6DC;--stone:#58595B;--ink:#8A5A36}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:WPX;height:HPX;overflow:hidden;background:var(--green)}
.ad{position:relative;width:WPX;height:HPX;color:var(--light);font-family:Source,sans-serif;overflow:hidden;
 background:radial-gradient(120% 90% at 85% 10%,#0a5159 0%,var(--green) 55%,var(--green2) 100%)}
.photo{position:absolute;background-size:cover}
.panel{position:absolute;display:flex;flex-direction:column}
.eyebrow{font-family:Josefin;font-weight:600;text-transform:uppercase;letter-spacing:.16em;color:var(--aqua)}
h1{font-size:calc(var(--h1) * var(--hs,1)) !important;font-family:Cormorant;font-weight:600;line-height:1.02;color:#fff;letter-spacing:-.005em}
h1 em{font-style:italic;font-weight:500;color:var(--glow)}
.sub{color:var(--light);opacity:.92;line-height:1.35}
.prices{display:flex}
.price{flex:1;border:2px solid rgba(152,190,174,.45);border-radius:14px;text-align:center}
.price b{display:block;font-variant-numeric:lining-nums;font-family:Cormorant;font-weight:600;color:#fff;line-height:1.1}
.price span{display:block;margin-top:2px;font-family:Josefin;text-transform:uppercase;letter-spacing:.1em;color:var(--aqua)}
.foot{display:flex;align-items:center;justify-content:space-between;margin-top:auto}
.cta{display:inline-block;background:var(--glow);color:var(--green2);font-family:Josefin;font-weight:600;
 letter-spacing:.06em;border-radius:999px;white-space:nowrap}
.mark{text-align:right;line-height:1}
.mark .script{font-family:Allura;color:#fff;display:block}
.mark .fp{font-family:Josefin;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--light);display:block}
.mark .url{font-family:Josefin;letter-spacing:.08em;color:var(--aqua);display:block}
.badge{position:absolute;border-radius:50%;background:var(--green);border:5px solid var(--light);
 display:flex;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(0,0,0,.25)}
.badge img{width:78%;height:78%}
.water{position:absolute;opacity:.07;pointer-events:none}
.list{list-style:none}
.list li{display:flex;align-items:baseline;border-top:1.5px solid rgba(152,190,174,.35)}
.list li:last-child{border-bottom:1.5px solid rgba(152,190,174,.35)}
.list .n{font-family:Josefin;font-weight:600;color:var(--glow);flex:0 0 auto;width:1.9em;font-variant-numeric:tabular-nums}
.list .t{font-family:Source;font-weight:600;color:#fff}

/* ---------- square 1080 ---------- */
.square .photo{left:0;top:0;width:1080px;height:480px}
.square .panel{left:0;top:480px;width:1080px;height:600px;padding:60px 70px 54px}
.square .badge{width:130px;height:130px;right:70px;top:415px}
.square .eyebrow{font-size:22px;margin-bottom:18px}
.square h1{--h1:70px}
.square .sub{font-size:28px;margin-top:20px;max-width:900px}
.square .prices{gap:18px;margin-top:22px}
.square .price{padding:12px 0 10px}.square .price b{font-size:50px}.square .price span{font-size:16px}
.square .cta{font-size:26px;padding:20px 34px 16px}
.square .mark .script{font-size:58px;margin-bottom:-6px}.square .mark .fp{font-size:15px}.square .mark .url{font-size:15px;margin-top:8px}
.square.type .panel{top:0;height:1080px;padding:90px 80px 64px}
.square.type h1{--h1:92px;margin-top:6px}
.square.type .sub{margin-top:24px}
.square.type .list{margin-top:46px}
.square.type .list li{padding:22px 0 17px;gap:18px}.square.type .n{font-size:24px}.square.type .t{font-size:40px}
.square .water{width:900px;right:-260px;top:-180px}

/* ---------- story 1080x1920 (UI safe zones: top 250, bottom 340) ---------- */
.story .photo{left:0;top:0;width:1080px;height:780px}
.story .panel{left:0;top:780px;width:1080px;height:1140px;padding:96px 80px 350px}
.story .badge{width:160px;height:160px;right:80px;top:700px}
.story .eyebrow{font-size:27px;margin-bottom:24px}
.story h1{--h1:94px}
.story .sub{font-size:37px;margin-top:30px}
.story .prices{gap:22px;margin-top:36px}
.story .price{padding:18px 0 14px}.story .price b{font-size:64px}.story .price span{font-size:19px}
.story .foot{padding-top:40px}
.story .cta{font-size:32px;padding:26px 44px 22px}
.story .mark .script{font-size:70px;margin-bottom:-6px}.story .mark .fp{font-size:18px}.story .mark .url{font-size:19px;margin-top:10px}
.story.type .panel{top:0;height:1920px;padding:270px 80px 360px}
.story.type h1{--h1:118px;margin-top:10px}
.story.type .sub{margin-top:30px}
.story.type .list{margin-top:50px}
.story.type .list li{padding:30px 0 24px;gap:20px}.story.type .n{font-size:28px}.story.type .t{font-size:44px}
.story .water{width:1300px;right:-500px;top:120px}

/* ---------- landscape 1200x628 ---------- */
.landscape .photo{left:0;top:0;width:520px;height:628px}
.landscape .panel{left:520px;top:0;width:680px;height:628px;padding:56px 56px 44px 84px}
.landscape .badge{width:104px;height:104px;left:466px;top:40px;border-width:4px}
.landscape .eyebrow{font-size:17px;margin-bottom:14px}
.landscape h1{--h1:60px}
.landscape .sub{font-size:23px;margin-top:18px}
.landscape .prices{gap:12px;margin-top:24px}
.landscape .price{padding:8px 0 6px;border-radius:10px}.landscape .price b{font-size:36px}.landscape .price span{font-size:12px}
.landscape .cta{font-size:19px;padding:15px 24px 12px}
.landscape .mark .script{font-size:44px;margin-bottom:-4px}.landscape .mark .fp{font-size:11px}.landscape .mark .url{font-size:12px;margin-top:6px}
.landscape.type .panel{left:0;width:1200px;padding:60px 64px 48px;display:grid;
 grid-template-columns:560px 1fr;grid-template-rows:auto auto 1fr auto;column-gap:56px}
.landscape.type .eyebrow{grid-column:1;grid-row:1}.landscape.type h1{grid-column:1;grid-row:2}
.landscape.type .sub{grid-column:1;grid-row:3;align-self:start}
.landscape.type h1{--h1:66px}
.landscape.type .list{grid-column:2;grid-row:1/5;align-self:center}
.landscape.type .list li{padding:15px 0 11px;gap:12px}.landscape.type .n{font-size:17px}.landscape.type .t{font-size:24px}
.landscape.type .foot{grid-column:1;grid-row:4}
.landscape .water{width:760px;right:-200px;top:-160px}
"""


def render_html(c, fmt):
    w, h = FORMATS[fmt]
    css = CSS.replace("ASSETS", ASSETS.as_uri()).replace("WPX", f"{w}px").replace("HPX", f"{h}px")
    parts = []
    if c["layout"] == "photo":
        parts.append(f'<div class="photo" style="background-image:url({(ASSETS / c["photo"]).as_uri()});'
                     f'background-position:{c.get("pos", "50% 50%")}"></div>')
    else:
        parts.append(f'<img class="water" src="{(ASSETS / "img/emblem-light.svg").as_uri()}" alt="">')
    body = [f'<div class="eyebrow">{html.escape(c["eyebrow"])}</div>', f'<h1>{c["headline"]}</h1>']
    if c.get("sub"):
        body.append(f'<p class="sub">{html.escape(c["sub"])}</p>')
    if c.get("prices"):
        body.append('<div class="prices">' + "".join(
            f'<div class="price"><b>{p}</b><span>{l}</span></div>' for p, l in c["prices"]) + "</div>")
    if c.get("list"):
        body.append('<ul class="list">' + "".join(
            f'<li><span class="n">{n}</span><span class="t">{html.escape(t)}</span></li>' for n, t in c["list"]) + "</ul>")
    body.append(
        f'<div class="foot"><span class="cta">{html.escape(c["cta"])}</span>'
        f'<div class="mark"><span class="script">Burds</span><span class="fp">Family Practice</span>'
        f'<span class="url">{URL}</span></div></div>')
    parts.append('<div class="panel">' + "".join(body) + "</div>")
    if c["layout"] == "photo":
        parts.append(f'<div class="badge"><img src="{(ASSETS / "img/emblem-light.svg").as_uri()}" alt=""></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>'
            f'<body><div class="ad {fmt} {c["layout"]}" style="--hs:{c.get("hs", 1)}">{"".join(parts)}</div></body></html>')


def screenshot(html_path, png_path, w, h):
    subprocess.run([
        CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--allow-file-access-from-files", "--force-device-scale-factor=1",
        "--virtual-time-budget=3000", f"--window-size={w},{h}",
        f"--screenshot={png_path}", html_path.as_uri(),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    only = set(sys.argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for c in CAMPAIGNS:
            if only and not any(o in c["slug"] for o in only):
                continue
            for fmt, (w, h) in FORMATS.items():
                src = pathlib.Path(tmp) / f'{c["slug"]}-{fmt}.html'
                src.write_text(render_html(c, fmt), encoding="utf-8")
                png = OUT / f'{c["slug"]}-{fmt}.png'
                screenshot(src, png, w, h)
                print("wrote", png.relative_to(ROOT))


if __name__ == "__main__":
    main()
