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
import hashlib
import html as html_lib
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
MIRROR = ROOT / "mirror" / "www.burdsfamilypractice.com"

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
    for part in m.group(1).split("|"):
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


def render_page(layout, *, title, description, path, nav_key, base, content, css_v="", js_v=""):
    full_title = (
        title if "Burds Family Practice" in title else f"{title} | Burds Family Practice"
    )
    rendered = (
        layout.replace("{{title}}", full_title)
        .replace("{{description}}", description)
        .replace("{{path}}", path)
        .replace("{{base}}", base)
        .replace("{{css_v}}", css_v)
        .replace("{{js_v}}", js_v)
        .replace("{{nav}}", nav_html(nav_key, base=base))
        .replace("{{content}}", content)
    )
    leftover = re.findall(r"\{\{\w+\}\}", rendered)
    if leftover:
        raise ValueError(f"{path}: unreplaced placeholders {leftover}")
    return rendered


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
        content = f"""    <section class="article-shell">
      <div class="container">
        <article class="article-wrap">
          <a class="breadcrumb" href="../resources.html#blog">← Back to Resources &amp; Blog</a>
          <header class="article-head">
            <span class="eyebrow">Community Health Blog</span>
            <h1>{h1_text}</h1>
            <div class="article-meta">
              {date_html}
              <span>Written by Jennifer Burds, DNP, ARNP · Peosta, IA</span>
            </div>
          </header>
          <div class="prose">
            {body_div}
          </div>
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
            base="/" if page.name == "404.html" else "",
            content=body,
            css_v=css_v,
            js_v=js_v,
        )
        (DIST / page.name).write_text(html, encoding="utf-8")

    # Standalone QR-code landing page for patient reviews -> dist/review/index.html
    shutil.copytree(SRC / "review", DIST / "review")

    learn_count = build_learn_pages(layout)
    blog_count = build_blog_pages(layout)
    write_sitemap()
    total = len(pages) + learn_count + blog_count
    print(
        f"Built {total} pages ({len(pages)} core, {learn_count} learn guides, {blog_count} blog posts) into {DIST}"
    )


SITE = "https://www.burdsfamilypractice.com/"


def write_sitemap():
    """Emit sitemap.xml (every built page except 404) and robots.txt."""
    urls = []
    for f in sorted(DIST.rglob("*.html")):
        rel = f.relative_to(DIST).as_posix()
        if rel == "404.html" or rel.startswith("review/"):
            continue
        urls.append(SITE + ("" if rel == "index.html" else rel))
    body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n",
        encoding="utf-8",
    )
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8"
    )


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
