#!/usr/bin/env python3
"""Static-site builder for Burds Family Practice.

Builds:
  - 8 core redesigned pages from src/pages/*.html -> dist/*.html
  - 8 Learning Hub guides from mirror/www.burdsfamilypractice.com/learn/*.html -> dist/learn/*.html
  - 15 Blog articles from mirror/www.burdsfamilypractice.com/blog/*.html -> dist/blog/*.html

Usage:
  python3 build.py          # build all 31 pages into dist/
  python3 build.py serve    # build, then serve dist/ on http://localhost:8080
"""
import datetime
import hashlib
import json
import subprocess
import html as html_lib
import re
import shutil
import os
import sys
from pathlib import Path

import seo

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
# Root path the site is served from; 404.html needs absolute links.
# "/" for a custom domain, "/<repo>/" for a GitHub Pages project URL.
SITE_BASE = os.environ.get("SITE_BASE", "/")
MIRROR = ROOT / "mirror" / "www.burdsfamilypractice.com"
# Public URL of the deployed site, used for canonical links, schema, sitemap and llms.txt.
SITE = os.environ.get("SITE_URL", "https://www.burdsfamilypractice.com/").rstrip("/") + "/"

NAV = [
    ("new", "new-patients.html", "New Patients"),
    ("services", "services.html", "Services"),
    ("dpc", "direct-primary-care.html", "Direct Primary Care"),
    ("occ", "occupational-health.html", "Occupational Health"),
    ("about", "about.html", "About"),
    ("resources", "resources.html", "Resources"),
    ("contact", "contact.html", "Contact"),
]

META_RE = re.compile(r"^\s*<!--(.*?)-->\s*", re.S)


def parse_meta(text):
    m = META_RE.match(text)
    if not m:
        raise ValueError("page is missing its metadata comment")
    meta = {}
    # Split only on "|" that starts a new "key:" so titles may contain "|".
    for part in re.split(r"\|(?=\s*(?:title|description|nav|type)\s*:)", m.group(1)):
        key, _, value = part.partition(":")
        meta[key.strip()] = value.strip()
    return meta, text[m.end():]


def nav_html(active, base=""):
    items = []
    for key, href, label in NAV:
        current = ' aria-current="page"' if key == active else ""
        items.append(f'<li><a href="{base}{href}"{current}>{label}</a></li>')
    return "\n          ".join(items)


def rewrite_links(markup, base="../"):
    """Map old Squarespace internal URLs to the new local static paths."""
    replacements = [
        ("../get-in-touch.html", f"{base}contact.html"),
        ("../our-services.html", f"{base}services.html"),
        ("../our-services26.html", f"{base}services.html"),
        ("../primary-care.html", f"{base}services.html"),
        ("../our-story.html", f"{base}about.html"),
        ("../our-team.html", f"{base}about.html"),
        ("../our-favorites.html", f"{base}about.html#favorites"),
        ("../learning-hub.html", f"{base}resources.html#guides"),
        ("../blog.html", f"{base}resources.html#blog"),
        ("https://www.burdsfamilypractice.com/get-in-touch", f"{base}contact.html"),
        ("https://www.burdsfamilypractice.com/our-services26", f"{base}services.html"),
        ("https://www.burdsfamilypractice.com/our-services", f"{base}services.html"),
        ("https://www.burdsfamilypractice.com/primary-care", f"{base}services.html"),
        ("https://www.burdsfamilypractice.com/direct-primary-care", f"{base}direct-primary-care.html"),
        ("https://www.burdsfamilypractice.com/occupational-health", f"{base}occupational-health.html"),
        ("https://www.burdsfamilypractice.com/our-story", f"{base}about.html"),
        ("https://www.burdsfamilypractice.com/our-team", f"{base}about.html"),
        ("https://www.burdsfamilypractice.com/learning-hub", f"{base}resources.html#guides"),
        ("https://www.burdsfamilypractice.com/blog", f"{base}resources.html#blog"),
    ]
    for old, new in replacements:
        markup = markup.replace(old, new)
    return markup


def extract_balanced_div(html_text, open_marker_re):
    """Extract the full <div ...>...</div> element starting at open_marker_re."""
    m = open_marker_re.search(html_text)
    if not m:
        return None
    start = m.start()
    pos = m.end()
    depth = 1
    for tok in re.finditer(r"<(/?)div\b[^>]*>", html_text[pos:], re.I):
        depth += -1 if tok.group(1) else 1
        if depth == 0:
            end = pos + tok.end()
            return html_text[start:end]
    return None


def extract_title_desc(raw, fallback_title):
    t_match = re.search(r"<title>(.*?)</title>", raw, re.S)
    title = html_lib.unescape(t_match.group(1)).strip() if t_match else fallback_title
    title = re.sub(r"\s*[—|–-]\s*Burds Family Practice\s*$", "", title).strip()
    d_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', raw)
    desc = d_match.group(1).strip() if d_match else ""
    return title or fallback_title, desc


def _asset_hash(rel_path):
    """Return a short content hash for cache-busting static CSS/JS links."""
    data = (SRC / rel_path).read_bytes()
    return hashlib.sha256(data).hexdigest()[:10]


def render_page(layout, *, title, description, path, nav_key, base, content,
                css_v="", js_v="", page_type="WebPage", crumbs=None, extra=None):
    # Keep titles near Google's ~60-70 character display limit: add the brand only if it fits.
    brand = " | Burds Family Practice"
    plain_len = len(html_lib.unescape(title))
    full_title = (
        title if "Burds Family Practice" in title or plain_len + len(brand) > 70
        else title + brand
    )
    rendered = (
        layout.replace("{{title}}", html_lib.escape(html_lib.unescape(full_title), quote=False))
        .replace("{{description}}", html_lib.escape(html_lib.unescape(description)))
        .replace("{{site}}", SITE)
        .replace("{{path}}", path)
        .replace("{{robots}}", ROBOTS_NOINDEX if path == "404.html" else ROBOTS_INDEX)
        .replace("{{schema}}", seo.page_schema(
            site=SITE, path=path, title=full_title, description=description,
            content=content, page_type=page_type, crumbs=crumbs, extra=extra))
        .replace("{{base}}", base)
        .replace("{{css_v}}", css_v)
        .replace("{{js_v}}", js_v)
        .replace("{{nav}}", nav_html(nav_key, base=base))
        .replace("{{content}}", content)
    )
    leftover = re.findall(r"\{\{\w+\}\}", rendered)
    if leftover:
        raise ValueError(f"{path}: unreplaced placeholders {leftover}")
    PAGES_INDEX.append({"path": path, "title": title, "description": description,
                        "content": content, "section": nav_key})
    return rendered


ROBOTS_INDEX = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
ROBOTS_NOINDEX = "noindex, follow"
# Every rendered page, used afterwards to write llms.txt / llms-full.txt.
PAGES_INDEX = []


def build_learn_pages(layout):
    learn_dir = MIRROR / "learn"
    if not learn_dir.exists():
        return 0
    out_dir = DIST / "learn"
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for src_file in sorted(learn_dir.glob("*.html")):
        raw = src_file.read_text(encoding="utf-8", errors="replace")
        title, desc = extract_title_desc(raw, src_file.stem.replace("-", " ").title())
        # Drop Squarespace marketing tails ("| Discover ... Today") from guide titles.
        title = title.split(" | ")[0].strip() + " | Burds Family Practice"
        div_marker = re.compile(r'<div\s+class="bfp-learn"[^>]*>', re.I)
        m_div = div_marker.search(raw)
        if not m_div:
            raise ValueError(f"{src_file.name}: missing .bfp-learn container")
        last_style = raw.rfind("<style", 0, m_div.start())
        style_block = raw[last_style:m_div.start()] if last_style != -1 else ""
        learn_div = extract_balanced_div(raw, div_marker)
        if not learn_div:
            raise ValueError(f"{src_file.name}: unbalanced .bfp-learn div")
        learn_div = rewrite_links(learn_div, base="../")
        content = (
            '    <div class="learn-breadcrumb-bar">\n'
            '      <div class="container">\n'
            '        <a class="breadcrumb" href="../resources.html#guides">← Back to Learning Hub &amp; Resources</a>\n'
            '      </div>\n'
            '    </div>\n'
            f"{style_block}\n"
            f"{learn_div}\n"
        )
        html = render_page(
            layout,
            title=title,
            description=desc,
            path=f"learn/{src_file.name}",
            nav_key="resources",
            base="../",
            content=content,
            page_type="Article",
            crumbs=[("Resources", "resources.html"), ("Learning Hub", "resources.html#guides")],
        )
        (out_dir / src_file.name).write_text(html, encoding="utf-8")
        count += 1
    return count


def build_blog_pages(layout):
    blog_dir = MIRROR / "blog"
    if not blog_dir.exists():
        return 0
    out_dir = DIST / "blog"
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for src_file in sorted(blog_dir.glob("*.html")):
        raw = src_file.read_text(encoding="utf-8", errors="replace")
        title, desc = extract_title_desc(raw, src_file.stem.replace("-", " ").title())
        art_match = re.search(r"<article\b[^>]*>(.*?)</article>", raw, re.S)
        if not art_match:
            raise ValueError(f"{src_file.name}: missing <article>")
        art = art_match.group(1)

        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", art, re.S)
        h1_text = h1_match.group(1).strip() if h1_match else title

        dt_match = re.search(r'<time[^>]*datetime="([^"]+)"[^>]*>(.*?)</time>', art, re.S)
        date_iso = dt_match.group(1).strip() if dt_match else ""
        date_label = (
            re.sub(r"<[^>]+>", "", dt_match.group(2)).strip() if dt_match else ""
        )
        if date_iso and date_label and len(date_label) < 8:
            date_label = f"{date_label}, {date_iso[:4]}"

        body_div = extract_balanced_div(
            art, re.compile(r'<div\s+class="sqs-html-content"[^>]*>', re.I)
        )
        if not body_div:
            raise ValueError(f"{src_file.name}: missing .sqs-html-content body")
        # Clean inline pre-wrap styles and rewrite links
        body_div = re.sub(r'\s*style="white-space:\s*pre-wrap;?"', "", body_div)
        body_div = rewrite_links(body_div, base="../")

        date_html = (
            f'<span>Published <time datetime="{date_iso}">{date_label}</time></span>'
            if date_iso
            else ""
        )
        words = len(re.sub(r"<[^>]+>", " ", body_div).split())
        read_min = max(1, -(-words // 220))  # round up
        content = f"""    <section class="article-hero">
      <div class="container article-hero__inner">
        <a class="breadcrumb breadcrumb--light" href="../resources.html#blog">← Resources &amp; Blog</a>
        <span class="eyebrow eyebrow--warm">Community Health Blog</span>
        <h1>{h1_text}</h1>
        <div class="article-meta article-meta--light">
          {date_html}
          <span>{read_min} min read</span>
          <span>By Jennifer Burds, DNP, ARNP</span>
        </div>
      </div>
    </section>

    <section class="article-shell">
      <div class="container">
        <article class="article-wrap">
          <div class="prose">
            {body_div}
          </div>
          <aside class="author-box" aria-label="About the author">
            <span class="author-box__photo"><img src="../assets/img/team/jenny-burds.jpg" alt="Jenny Burds, DNP, ARNP" width="96" height="96" loading="lazy"></span>
            <div>
              <span class="author-box__label">Written &amp; reviewed by</span>
              <strong>Jennifer (Jenny) Burds, DNP, ARNP</strong>
              <p>Owner and family nurse practitioner at Burds Family Practice in Peosta, Iowa, with 30 years in healthcare. This article is general information, not a substitute for a visit.</p>
              <a href="../about.html#team">Meet our providers →</a>
            </div>
          </aside>
        </article>
      </div>
    </section>

    <section class="cta-band">
      <div class="container">
        <div>
          <h2>Questions for our Peosta care team?</h2>
          <p>Same-day sick visits, family checkups, and Direct Primary Care memberships starting at $99/month.</p>
        </div>
        <div class="btn-row">
          <a class="btn btn--warm" href="tel:+15635886659">Call (563) 588-6659</a>
          <a class="btn btn--ghost-light" href="../contact.html">Hours &amp; Directions</a>
        </div>
      </div>
    </section>"""

        html = render_page(
            layout,
            title=title,
            description=desc,
            path=f"blog/{src_file.name}",
            nav_key="resources",
            base="../",
            content=content,
            page_type="BlogPosting",
            crumbs=[("Resources", "resources.html"), ("Blog", "resources.html#blog")],
            extra={"datePublished": date_iso, "headline": re.sub(r"<[^>]+>", "", h1_text)},
        )
        (out_dir / src_file.name).write_text(html, encoding="utf-8")
        count += 1
    return count


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(SRC / "assets", DIST / "assets")
    css_v = _asset_hash("assets/css/styles.css")
    js_v = _asset_hash("assets/js/main.js")
    layout = (
        (SRC / "layout.html")
        .read_text(encoding="utf-8")
        .replace("{{css_v}}", css_v)
        .replace("{{js_v}}", js_v)
    )

    pages = sorted((SRC / "pages").glob("*.html"))
    for page in pages:
        meta, body = parse_meta(page.read_text(encoding="utf-8"))
        html = render_page(
            layout,
            title=meta["title"],
            description=meta.get("description", ""),
            path="" if page.name == "index.html" else page.name,
            nav_key=meta.get("nav", ""),
            base=SITE_BASE if page.name == "404.html" else "",
            content=body,
            css_v=css_v,
            js_v=js_v,
            page_type=meta.get("type", "WebPage"),
            crumbs=[] if page.name in ("index.html", "404.html") else None,
        )
        (DIST / page.name).write_text(html, encoding="utf-8")

    # Standalone QR-code landing page for patient reviews -> dist/review/index.html
    shutil.copytree(SRC / "review", DIST / "review")

    learn_count = build_learn_pages(layout)
    blog_count = build_blog_pages(layout)
    write_sitemap()
    seo.write_llms(DIST, SITE, PAGES_INDEX)
    total = len(pages) + learn_count + blog_count
    print(
        f"Built {total} pages ({len(pages)} core, {learn_count} learn guides, {blog_count} blog posts) into {DIST}"
    )



def _lastmod(rel):
    """Last git commit date of the source behind a built page (falls back to today)."""
    if rel.startswith("learn/") or rel.startswith("blog/"):
        src = MIRROR / rel
    else:
        src = SRC / "pages" / rel
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(src)],
                             cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ""
    return out or datetime.date.today().isoformat()


def write_sitemap():
    """Emit sitemap.xml (every indexable page, with lastmod) and robots.txt."""
    entries = []
    for f in sorted(DIST.rglob("*.html")):
        rel = f.relative_to(DIST).as_posix()
        if rel == "404.html" or rel.startswith("review/"):
            continue
        loc = SITE + ("" if rel == "index.html" else rel)
        prio = "1.0" if rel == "index.html" else ("0.6" if "/" in rel else "0.8")
        entries.append(
            f"  <url><loc>{loc}</loc><lastmod>{_lastmod(rel)}</lastmod>"
            f"<priority>{prio}</priority></url>"
        )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries) + "\n</urlset>\n",
        encoding="utf-8",
    )
    (DIST / "robots.txt").write_text(seo.robots_txt(SITE), encoding="utf-8")


def serve(port=8080):
    import functools
    import http.server

    class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            super().end_headers()

    handler = functools.partial(NoCacheHandler, directory=str(DIST))
    with http.server.ThreadingHTTPServer(("0.0.0.0", port), handler) as httpd:
        print(f"Serving on http://localhost:{port}  (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
