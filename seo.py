"""Search-engine and AI-assistant metadata for the Burds Family Practice build.

- page_schema(): one JSON-LD @graph per page (clinic, providers, website,
  breadcrumbs, FAQPage from <div class="faq"> blocks, Article/BlogPosting).
- robots_txt(): crawl rules that explicitly welcome search and AI crawlers.
- write_llms(): llms.txt (site map for LLMs) and llms-full.txt (full text).
"""
import html as html_lib
import json
import re

PHONE = "+1-563-588-6659"
MAPS_URL = (
    "https://www.google.com/maps/place/Burds+Family+Practice/@42.4460877,-90.8486134,17z/"
    "data=!3m1!4b1!4m6!3m5!1s0x87e336ea39157471:0x22a81eacb796ab28!8m2!3d42.4460877!4d-90.8486134"
    "!16s%2Fg%2F11twq3td_p?entry=ttu"
)
FACEBOOK = "https://www.facebook.com/profile.php?id=100089369972632"
TEBRA = "https://www.tebra.com/care/practice/burds-family-practice-477010"
DPC_PASSPORT = "https://dpcpassport.com/providers/burds-family-practice--lvormskxciih/jennifer-burds-1"

# Towns we draw patients from (kept in sync with areas-we-serve.html).
AREA_TOWNS = [
    "Peosta", "Dubuque", "Asbury", "Epworth", "Farley", "Dyersville",
    "Cascade", "Bernard", "Centralia", "Graf", "Holy Cross", "Sherrill",
]

SERVICES = [
    ("Same-day sick visits", "MedicalProcedure"),
    ("Annual wellness exams and physicals", "MedicalProcedure"),
    ("Well-child checks and pediatric care", "MedicalProcedure"),
    ("School, sports and camp physicals", "MedicalProcedure"),
    ("Chronic disease management (diabetes, high blood pressure, thyroid)", "MedicalTherapy"),
    ("Immunizations and vaccines", "MedicalProcedure"),
    ("In-office lab draws", "DiagnosticProcedure"),
    ("Joint injections", "TherapeuticProcedure"),
    ("Women's health care", "MedicalProcedure"),
    ("Psychiatric evaluations and medication management (ages 12+)", "MedicalTherapy"),
    ("Perinatal mental health care", "MedicalTherapy"),
    ("DOT / CDL physicals (FMCSA National Registry certified examiner)", "MedicalProcedure"),
    ("Pre-employment physicals", "MedicalProcedure"),
    ("12-panel drug screening", "DiagnosticProcedure"),
    ("Work injury care and return-to-work clearances", "MedicalProcedure"),
    ("Direct Primary Care membership", "MedicalProcedure"),
    ("Infrared sauna wellness sessions", "MedicalTherapy"),
]


def _id(site, frag):
    return f"{site}#{frag}"


def site_graph(site):
    """Entities shared by every page: the clinic, its providers and the website."""
    clinic = _id(site, "clinic")
    providers = [
        {
            "@type": "Person",
            "@id": _id(site, "jenny-burds"),
            "name": "Jennifer (Jenny) Burds",
            "honorificSuffix": "DNP, ARNP",
            "jobTitle": "Owner, Family Nurse Practitioner and FMCSA Certified Medical Examiner",
            "identifier": {"@type": "PropertyValue", "propertyID": "NPI", "value": "1639433030"},
            "alumniOf": {"@type": "CollegeOrUniversity", "name": "Clarke University"},
            "worksFor": {"@id": clinic},
            "image": f"{site}assets/img/team/jenny-burds.jpg",
            "url": f"{site}about.html#team",
        },
        {
            "@type": "Person",
            "@id": _id(site, "channah-chase"),
            "name": "Channah Chase",
            "honorificSuffix": "DNP, FNP-BC",
            "jobTitle": "Family Nurse Practitioner",
            "alumniOf": {"@type": "CollegeOrUniversity", "name": "Clarke University"},
            "worksFor": {"@id": clinic},
            "image": f"{site}assets/img/team/channah-chase.jpg",
            "url": f"{site}about.html#team",
        },
        {
            "@type": "Person",
            "@id": _id(site, "jenna-hefel"),
            "name": "Jenna Hefel",
            "honorificSuffix": "DNP, PMHNP-BC",
            "jobTitle": "Psychiatric Mental Health Nurse Practitioner",
            "worksFor": {"@id": clinic},
            "image": f"{site}assets/img/team/jenna-hefel.jpg",
            "url": f"{site}about.html#team",
        },
    ]
    dpc_offers = [
        ("Direct Primary Care membership: adult", 99),
        ("Direct Primary Care membership: spouse or partner", 79),
        ("Direct Primary Care membership: child (newborn to 18)", 49),
    ]
    clinic_node = {
        "@type": ["MedicalClinic", "MedicalBusiness", "LocalBusiness"],
        "@id": clinic,
        "name": "Burds Family Practice",
        "alternateName": ["Burds Family Practice, PLLC", "Burds Family Practice Peosta"],
        "legalName": "Burds Family Practice, PLLC",
        "description": (
            "Independent, locally owned family medicine clinic in Peosta, Iowa, serving "
            "western Dubuque County. Primary care for newborns through seniors, same-day sick "
            "visits, Direct Primary Care memberships from $99/month, DOT and occupational health "
            "physicals, and psychiatric care for ages 12 and up."
        ),
        "slogan": "Community rooted in Peosta, Iowa. Personalized healthcare since 2023.",
        "identifier": {"@type": "PropertyValue", "propertyID": "NPI", "value": "1194432864"},
        "foundingDate": "2022-09-16",
        "founder": {"@id": _id(site, "jenny-burds")},
        "employee": [{"@id": p["@id"]} for p in providers],
        "url": site,
        "logo": f"{site}assets/img/fb-logo.jpg",
        "image": [
            f"{site}assets/img/fb-banner.png",
            f"{site}assets/img/storefront.jpg",
            f"{site}assets/img/lobby.jpg",
        ],
        "telephone": PHONE,
        "email": "bfpstaff@burdsfamilypractice.com",
        "priceRange": "$$",
        "currenciesAccepted": "USD",
        "paymentAccepted": "Cash, Credit Card, Health Insurance, HSA, FSA",
        "isAcceptingNewPatients": True,
        "medicalSpecialty": ["PrimaryCare", "Pediatric", "Psychiatric"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "8411 Peosta Commercial Ct, Suite 8",
            "addressLocality": "Peosta",
            "addressRegion": "IA",
            "postalCode": "52068",
            "addressCountry": "US",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": 42.4460877, "longitude": -90.8486134},
        "hasMap": MAPS_URL,
        "areaServed": [{"@type": "City", "name": f"{t}, Iowa"} for t in AREA_TOWNS]
        + [{"@type": "AdministrativeArea", "name": "Dubuque County, Iowa"}],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday"],
             "opens": "08:00", "closes": "17:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Thursday", "opens": "08:00", "closes": "18:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Friday", "opens": "08:00", "closes": "12:00"},
        ],
        "availableService": [{"@type": t, "name": n} for n, t in SERVICES],
        "makesOffer": [
            {
                "@type": "Offer",
                "name": name,
                "price": price,
                "priceCurrency": "USD",
                "priceSpecification": {
                    "@type": "UnitPriceSpecification", "price": price, "priceCurrency": "USD",
                    "unitText": "MONTH", "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitCode": "MON"},
                },
                "url": f"{site}direct-primary-care.html",
            }
            for name, price in dpc_offers
        ],
        "knowsAbout": [
            "Family medicine", "Primary care", "Direct Primary Care", "Pediatrics",
            "DOT physicals", "CDL medical exams", "Occupational health", "Drug screening",
            "Mental health", "Perinatal mental health", "Chronic disease management",
            "Preventive care", "Medical aesthetics",
        ],
        "aggregateRating": {
            "@type": "AggregateRating", "ratingValue": "5.0", "bestRating": "5", "reviewCount": "103",
        },
        "review": [
            {
                "@type": "Review",
                "author": {"@type": "Person", "name": a},
                "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                "reviewBody": b,
            }
            for a, b in [
                ("Melissa R.", "Jenny is very kind and compassionate. She deeply cares for her patients and takes time to address your concerns without feeling rushed. The environment is warm and inviting and all staff make you feel welcome. 5 star care."),
                ("Casey Thein", "I highly recommend this family practice! My nurse practitioner is knowledgeable, compassionate, and truly takes the time to listen. I never feel rushed during my appointments, and she always explains things clearly so I understand my options and feel confident in my care."),
                ("Nisha Lewis", "My 1st Burds Family Practice experience was great! Jennifer took great care of me! She was attentive & also gave me tips & advice to help with my supplements. I am a new patient & I'm happy they were recommended to me."),
            ]
        ],
        "subOrganization": {
            "@type": "MedicalBusiness",
            "name": "SkinRx by Burds",
            "url": "https://www.burdsskinrx.com/",
        },
        "sameAs": [MAPS_URL, FACEBOOK, TEBRA, DPC_PASSPORT, "https://www.burdsskinrx.com/"],
    }
    website = {
        "@type": "WebSite",
        "@id": _id(site, "website"),
        "url": site,
        "name": "Burds Family Practice",
        "inLanguage": "en-US",
        "publisher": {"@id": clinic},
    }
    return [clinic_node, website, *providers]


def _text(fragment):
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html_lib.unescape(fragment)).strip()


FAQ_RE = re.compile(r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>", re.S)


def faq_items(content):
    """Q&A pairs from every <details><summary> inside a .faq block."""
    items = []
    for block in re.finditer(r'<div class="faq"[^>]*>(.*?)\n\s*</div>\s*\n', content, re.S):
        for q, a in FAQ_RE.findall(block.group(1)):
            items.append((_text(q), _text(a)))
    return items


def page_schema(*, site, path, title, description, content, page_type="WebPage",
                crumbs=None, extra=None):
    url = site + path
    clean_title = _text(title)
    graph = site_graph(site)

    page = {
        "@type": "MedicalWebPage" if page_type == "WebPage" else "WebPage",
        "@id": url + "#webpage",
        "url": url,
        "name": clean_title,
        "description": _text(description),
        "isPartOf": {"@id": _id(site, "website")},
        "about": {"@id": _id(site, "clinic")},
        "inLanguage": "en-US",
        "primaryImageOfPage": f"{site}assets/img/fb-banner.png",
    }
    if path == "":
        page["mainEntity"] = {"@id": _id(site, "clinic")}
    graph.append(page)

    if path not in ("", "404.html"):
        crumbs = crumbs or []
        trail = [("Home", "")] + list(crumbs) + [(clean_title.split(" | ")[0], path)]
        graph.append({
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": i, "name": n, "item": site + p}
                for i, (n, p) in enumerate(trail, 1)
            ],
        })
        page["breadcrumb"] = {"@id": url + "#breadcrumb"}

    faqs = faq_items(content)
    if faqs:
        graph.append({
            "@type": "FAQPage",
            "@id": url + "#faq",
            "url": url,
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faqs
            ],
        })

    if page_type in ("Article", "BlogPosting"):
        art = {
            "@type": page_type,
            "@id": url + "#article",
            "mainEntityOfPage": {"@id": url + "#webpage"},
            "headline": (extra or {}).get("headline") or clean_title.split(" | ")[0],
            "description": _text(description),
            "image": f"{site}assets/img/fb-banner.png",
            "author": {"@id": _id(site, "jenny-burds")},
            "publisher": {"@id": _id(site, "clinic")},
            "inLanguage": "en-US",
            "reviewedBy": {"@id": _id(site, "jenny-burds")},
        }
        if extra and extra.get("datePublished"):
            art["datePublished"] = extra["datePublished"]
            art["dateModified"] = extra["datePublished"]
        graph.append(art)

    data = json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=1)
    data = data.replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{data}\n  </script>'


# Search engines plus the crawlers behind ChatGPT, Claude, Perplexity, Gemini,
# Copilot, Apple Intelligence, Meta AI and others. All are explicitly allowed.
AI_AND_SEARCH_BOTS = [
    "Googlebot", "Google-Extended", "Bingbot", "DuckDuckBot", "Applebot", "Applebot-Extended",
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
    "anthropic-ai", "PerplexityBot", "Perplexity-User", "CCBot", "Meta-ExternalAgent",
    "Amazonbot", "YouBot", "cohere-ai", "MistralAI-User", "DuckAssistBot",
]


def robots_txt(site):
    lines = ["# Burds Family Practice: search engines and AI assistants are welcome.", ""]
    for bot in AI_AND_SEARCH_BOTS:
        lines += [f"User-agent: {bot}", "Allow: /", "Disallow: /review/", ""]
    lines += ["User-agent: *", "Allow: /", "Disallow: /review/", "",
              f"Sitemap: {site}sitemap.xml", f"# LLM guide: {site}llms.txt", ""]
    return "\n".join(lines)


def html_to_markdown(fragment):
    """Rough HTML -> Markdown for llms-full.txt (headings, lists, links, paragraphs)."""
    s = re.sub(r"<(script|style|svg|form|button)\b.*?</\1>", "", fragment, flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    for n in range(1, 5):
        s = re.sub(rf"<h{n}[^>]*>(.*?)</h{n}>",
                   lambda m, n=n: "\n\n" + "#" * (n + 1) + " " + _text(m.group(1)) + "\n\n",
                   s, flags=re.S | re.I)
    s = re.sub(r"<summary[^>]*>(.*?)</summary>", lambda m: "\n\n**Q: " + _text(m.group(1)) + "**\n", s, flags=re.S)
    s = re.sub(r"<li[^>]*>", "\n- ", s, flags=re.I)
    s = re.sub(r"<tr[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"</t[hd]>", " ", s, flags=re.I)
    s = re.sub(r"<(p|div|section|article|blockquote|br|ul|ol|table|figure|header|footer)\b[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html_lib.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n[ \t]+", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


FACTS = """\
- Name: Burds Family Practice (Burds Family Practice, PLLC), an independent, locally owned family medicine clinic. Not part of a hospital system.
- Address: 8411 Peosta Commercial Ct, Suite 8, Peosta, IA 52068 (just off U.S. Highway 20 between Dubuque and Dyersville, western Dubuque County, Iowa)
- Phone: (563) 588-6659 · Email: bfpstaff@burdsfamilypractice.com
- Hours: Monday–Wednesday 8 AM–5 PM, Thursday 8 AM–6 PM, Friday 8 AM–12 PM, closed Saturday and Sunday
- Accepting new patients of all ages, newborns through seniors. Same-day sick visits available by phone.
- Insurance: most major insurance plans accepted. Direct Primary Care (DPC) membership also available: $99/month adult, $79/month spouse or partner, $49/month child, $276/month family of four; unlimited visits, $0 copays, same- or next-day access, direct phone and text access to your provider.
- Providers: Jennifer (Jenny) Burds, DNP, ARNP (owner, family nurse practitioner, FMCSA National Registry certified medical examiner for DOT/CDL physicals); Channah Chase, DNP, FNP-BC (family nurse practitioner); Jenna Hefel, DNP, PMHNP-BC (psychiatric nurse practitioner, ages 12+, certified in perinatal mental health).
- Services: primary care, wellness exams, sick visits, pediatrics and well-child checks, school and sports physicals, chronic disease management, immunizations, in-office labs, joint injections, mental health care, DOT/CDL physicals, pre-employment physicals, 12-panel drug screening, work injury care, infrared sauna, and medical aesthetics through sister medspa SkinRx by Burds (burdsskinrx.com).
- Serves: Peosta, Dubuque, Asbury, Epworth, Farley, Dyersville, Cascade, Bernard, Centralia, Graf, Holy Cross, Sherrill and the rest of Dubuque County, Iowa.
- Ratings: 5.0 stars on Google (100+ reviews), Facebook and Tebra.
- Founded 2022 (PLLC formed September 16, 2022), clinic opened 2023. Organization NPI 1194432864.
- Patient portal: https://portal.kareo.com/pp-webapp/app/new/login
- In an emergency, call 911.
"""


def write_llms(dist, site, pages):
    def link(p):
        return f"{site}{p['path']}"

    def section(name, pred):
        rows = [p for p in pages if pred(p)]
        out = [f"## {name}", ""]
        for p in rows:
            desc = _text(p["description"])
            out.append(f"- [{_text(p['title'])}]({link(p)})" + (f": {desc}" if desc else ""))
        return out + [""]

    core = lambda p: "/" not in p["path"] and p["path"] != "404.html"
    learn = lambda p: p["path"].startswith("learn/")
    blog = lambda p: p["path"].startswith("blog/")

    head = [
        "# Burds Family Practice",
        "",
        "> Independent family medicine clinic in Peosta, Iowa, serving Dubuque and western "
        "Dubuque County. Primary care for all ages, same-day sick visits, Direct Primary Care "
        "from $99/month, DOT/CDL and occupational health physicals, and mental health care for "
        "ages 12 and up. Accepting new patients: call (563) 588-6659.",
        "",
        "## Key facts",
        "",
        FACTS,
    ]
    body = section("Main pages", core) + section("Learning Hub guides", learn) + section("Health blog", blog)
    body += ["## Optional", "", f"- [Full text of every page]({site}llms-full.txt)", ""]
    (dist / "llms.txt").write_text("\n".join(head + body), encoding="utf-8")

    full = head[:]
    for p in [x for x in pages if core(x)] + [x for x in pages if learn(x)] + [x for x in pages if blog(x)]:
        full += ["", "---", "", f"# {_text(p['title'])}", "", f"URL: {link(p)}", "",
                 html_to_markdown(p["content"]), ""]
    (dist / "llms-full.txt").write_text("\n".join(full), encoding="utf-8")
