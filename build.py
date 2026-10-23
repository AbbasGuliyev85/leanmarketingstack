#!/usr/bin/env python3
"""Zero-dependency static site builder. Usage: python3 build.py  -> outputs to dist/"""
import json, re, html, shutil, os, datetime
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = json.load(open(os.path.join(ROOT, "site.json")))
AFF = json.load(open(os.path.join(ROOT, "affiliates.json")))
OUT = os.path.join(ROOT, "dist")
missing = set()

HOME = json.load(open(os.path.join(ROOT, "homepages.json")))
BP = SITE.get("base_path", "").rstrip("/")

def aff_link(slug, text):
    u = AFF.get(slug, "")
    if u:
        return f'<a href="{html.escape(u)}" rel="sponsored nofollow noopener" target="_blank">{text}</a>'
    missing.add(slug)
    return f'<a href="{html.escape(HOME[slug])}" rel="noopener" target="_blank">{text}</a>'

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    def link(m):
        text, href = m.group(1), m.group(2)
        a = re.fullmatch(r"\{\{AFFILIATE:([\w-]+)\}\}", href)
        if a:
            return aff_link(a.group(1), text)
        return f'<a href="{href}">{text}</a>'
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, t)
    # bare placeholders in parentheses -> "(official site)" link
    t = re.sub(r"\{\{AFFILIATE:([\w-]+)\}\}", lambda m: aff_link(m.group(1), "official site"), t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", t)
    return t

def md(src):
    lines, out, i = src.split("\n"), [], 0
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        m = re.match(r"(#{1,4}) (.*)", l)
        if m:
            n = len(m.group(1)); txt = m.group(2)
            sid = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
            out.append(f'<h{n} id="{sid}">{inline(txt)}</h{n}>'); i += 1; continue
        if l.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ")); i += 1
            out.append("<blockquote><p>" + inline(" ".join(buf)) + "</p></blockquote>"); continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            h = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>"
            for r in rows[2:]:
                h += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            out.append(h + "</tbody></table>"); continue
        if re.match(r"(- |\d+\. )", l):
            tag = "ol" if l[0].isdigit() else "ul"; items = []
            while i < len(lines) and re.match(r"(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lines[i])); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"(#{1,4} |>|\||- |\d+\. )", lines[i]):
            buf.append(lines[i]); i += 1
        out.append("<p>" + "<br>".join(inline(b) for b in buf) + "</p>")
    return "\n".join(out)

def parse(path):
    s = open(path).read()
    fm, body = {}, s
    if s.startswith("---"):
        _, head, body = s.split("---", 2)
        for line in head.strip().split("\n"):
            k, v = line.split(":", 1); fm[k.strip()] = v.strip()
    return fm, body

def layout(title, desc, canon, body, article=None):
    t = html.escape(title); d = html.escape(desc)
    ld = ""
    if article:
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "datePublished": article, "dateModified": article, "author": {"@type": "Organization", "name": SITE["author"]}, "mainEntityOfPage": canon}) + "</script>"
    n = html.escape(SITE["name"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="google-site-verification" content="7ZpVK0bY3MuWP3T_WsGl4_Fjy3_ebfGamtP8E8E6pQg"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title><meta name="description" content="{d}"><link rel="canonical" href="{canon}">
<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{t}"><meta property="og:description" content="{d}"><meta property="og:url" content="{canon}"><meta property="og:site_name" content="{n}">
<meta name="twitter:card" content="summary"><meta name="robots" content="index,follow"><link rel="stylesheet" href="/style.css">{ld}</head>
<body><header><div class="wrap"><a class="brand" href="/">{n}</a><nav><a href="/about/">About</a><a href="/disclosure/">Disclosure</a><a href="/privacy/">Privacy</a></nav></div></header>
<main class="wrap">{body}</main>
<footer><div class="wrap"><span>&copy; {datetime.date.today().year} {n}</span><span>We may earn commissions from links. <a href="/disclosure/">Disclosure</a></span></div></footer></body></html>"""

def write(rel, content):
    if rel.endswith(".html"): content = re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{BP}/', content)
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(content)

shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
shutil.copy(os.path.join(ROOT, "static/style.css"), OUT)
base = SITE["url"].rstrip("/"); urls = [(base + "/", None)]; posts = []
for f in sorted(os.listdir(os.path.join(ROOT, "content"))):
    if not f.endswith(".md"): continue
    fm, body = parse(os.path.join(ROOT, "content", f)); slug = f[:-3]
    canon = f"{base}/{slug}/"
    b = f'<article><h1>{inline(fm["title"])}</h1><p class="meta">Updated {fm["date"]}</p>{md(body)}</article>'
    write(f"{slug}/index.html", layout(fm["title"] + " | " + SITE["name"], fm["description"], canon, b, fm["date"]))
    posts.append((slug, fm)); urls.append((canon, fm["date"]))
for f in sorted(os.listdir(os.path.join(ROOT, "pages"))):
    fm, body = parse(os.path.join(ROOT, "pages", f)); slug = f[:-3]; canon = f"{base}/{slug}/"
    write(f"{slug}/index.html", layout(fm["title"] + " | " + SITE["name"], fm["description"], canon, f'<h1>{inline(fm["title"])}</h1>{md(body)}'))
    urls.append((canon, None))
cards = "".join(f'<div class="card"><h2><a href="/{s}/">{html.escape(fm["title"])}</a></h2><p class="meta">{html.escape(fm["description"])}</p></div>' for s, fm in posts)
home = f'<h1>{html.escape(SITE["name"])}</h1><p>{html.escape(SITE["tagline"])}</p><p class="meta">Reader-supported: some links are affiliate links. <a href="/disclosure/">Learn more</a>.</p>{cards}'
write("index.html", layout(SITE["name"] + " | Budget SEO & Email Tool Reviews", SITE["tagline"], base + "/", home))
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>\n" for u, d in urls) + "</urlset>\n"
write("sitemap.xml", sm)
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
write("404.html", layout("Page not found | " + SITE["name"], "Page not found", base + "/404.html", '<h1>Page not found</h1><p><a href="/">Back to home</a></p>'))
print(f"Built {len(posts)} posts, {len(urls)} URLs -> dist/")
if missing: print("WARNING: affiliate links not set yet (linked to vendor homepages, not tagged sponsored):", ", ".join(sorted(missing)))
