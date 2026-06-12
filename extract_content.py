#!/usr/bin/env python3
"""Extract unique page content from the Elementor static mirror into JSON."""
import pathlib, re, hashlib, collections, json, html

DOCS = pathlib.Path("/home/benyIL123/Desktop/Vibe projects/arturwebsite/docs")
PAGES = sorted(DOCS.glob("*/index.html")) + [DOCS / "index.html"]

def top_sections(s):
    out = []
    for m in re.finditer(r'<(section|div)[^>]*class="[^"]*elementor-top-section[^"]*"[^>]*>', s):
        start = m.start(); tag = m.group(1)
        depth = 0; i = m.end()
        pat = re.compile(rf'<{tag}\b|</{tag}>')
        while True:
            n = pat.search(s, i)
            if not n: break
            if n.group(0).startswith(f'<{tag}'):
                depth += 1
            else:
                if depth == 0:
                    out.append((start, n.end())); break
                depth -= 1
            i = n.end()
    res = []; last = -1
    for a, b in out:
        if a >= last:
            res.append((a, b)); last = b
    return res

def sig(chunk):
    widgets = re.findall(r'data-widget_type="([^".]+)', chunk)
    texts = re.sub(r'<[^>]+>', ' ', chunk)
    texts = re.sub(r'\s+', ' ', texts).strip()[:300]
    media = ','.join(re.findall(r'data-breeze="([^"]+)"', chunk)[:20]
                     + re.findall(r'[?&]v=([\w-]{6,})', chunk)[:20])
    return hashlib.md5((','.join(widgets) + '|' + texts + '|' + media).encode()).hexdigest()[:10]

# pass 1: shared-section signatures
sec_count = collections.Counter()
cache = {}
for f in PAGES:
    s = f.read_text(encoding="utf-8")
    cache[f] = s
    for h in {sig(s[a:b]) for a, b in top_sections(s)}:
        sec_count[h] += 1
SHARED = {h for h, c in sec_count.items() if c >= 12}

WIDGET_RE = re.compile(
    r'<div class="elementor-element[^"]*elementor-widget[^"]*"[^>]*'
    r'data-widget_type="([^".]+)\.default"[^>]*>', )

def widget_spans(chunk):
    """document-order (type, inner-html) for widgets in a section chunk"""
    out = []
    for m in WIDGET_RE.finditer(chunk):
        depth = 0; i = m.end()
        pat = re.compile(r'<div\b|</div>')
        while True:
            n = pat.search(chunk, i)
            if not n: break
            if n.group(0).startswith('<div'):
                depth += 1
            else:
                if depth == 0:
                    out.append((m.group(1), m.group(0), chunk[m.end():n.start()])); break
                depth -= 1
            i = n.end()
    return out

def clean_text(x):
    x = re.sub(r'<br\s*/?>', '\n', x)
    x = re.sub(r'<[^>]+>', '', x)
    return html.unescape(x).replace('‏', '').strip()

def best_img(tag):
    """full-resolution src from an <img>: strip -WxH suffix if that file exists"""
    m = re.search(r'data-breeze="([^"]+)"', tag) or re.search(r'src="(?!data:)([^"]+)"', tag)
    if not m: return None
    src = html.unescape(m.group(1))
    src = re.sub(r'^(\.\./)+', '', src)
    full = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', src)
    if full != src and (DOCS / re.sub(r'%[0-9A-Fa-f]{2}', lambda mm: bytes.fromhex(mm.group(0)[1:]).decode('latin1'), full)).exists():
        return full
    return src

def extract_items(chunk):
    items = []
    for wtype, opentag, inner in widget_spans(chunk):
        if wtype == 'heading':
            m = re.search(r'<(h\d|p|div|span)[^>]*class="[^"]*elementor-heading-title[^"]*"[^>]*>(.*?)</\1>', inner, re.S)
            if m:
                t = clean_text(m.group(2))
                if t: items.append({"t": "heading", "tag": m.group(1), "text": t})
        elif wtype == 'text-editor':
            paras = [clean_text(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', inner, re.S)]
            paras = [p for p in paras if p]
            if paras: items.append({"t": "text", "paras": paras})
        elif wtype == 'image':
            img = re.search(r'<img[^>]+>', inner)
            if not img: continue
            src = best_img(img.group(0))
            alt = re.search(r'alt="([^"]*)"', img.group(0))
            link = re.search(r'<a[^>]+href="([^"]+)"', inner)
            items.append({"t": "image", "src": src,
                          "alt": html.unescape(alt.group(1)) if alt else "",
                          "link": html.unescape(link.group(1)) if link else None})
        elif wtype in ('image-gallery', 'image-carousel'):
            srcs = []
            for img in re.findall(r'<img[^>]+>', inner):
                s2 = best_img(img)
                if s2 and s2 not in srcs: srcs.append(s2)
            if srcs: items.append({"t": "gallery", "srcs": srcs})
        elif wtype == 'video':
            m = re.search(r'data-settings="([^"]*)"', opentag) or re.search(r'data-settings="([^"]*)"', inner)
            url = None
            if m:
                try:
                    url = json.loads(html.unescape(m.group(1))).get("youtube_url")
                except Exception: pass
            if url: items.append({"t": "video", "url": url})
        elif wtype == 'button':
            txt = re.search(r'<span class="elementor-button-text">(.*?)</span>', inner, re.S)
            href = re.search(r'href="([^"]*)"', inner)
            if txt:
                items.append({"t": "button", "text": clean_text(txt.group(1)),
                              "href": html.unescape(href.group(1)) if href else ""})
        elif wtype == 'html':
            t = clean_text(inner)
            items.append({"t": "html", "raw": inner.strip()[:500], "text": t[:200]})
    return items

# chrome assets = images inside shared sections (nav tiles, client logos, banners)
CHROME_SRCS = set()
for f in PAGES:
    sc = cache[f]
    for a, b in top_sections(sc):
        if sig(sc[a:b]) in SHARED:
            for it in extract_items(sc[a:b]):
                if it["t"] == "image" and it.get("src"): CHROME_SRCS.add(it["src"])
                elif it["t"] == "gallery": CHROME_SRCS.update(it["srcs"])
print(f"{len(CHROME_SRCS)} chrome asset urls collected")

def not_chrome(it):
    if it["t"] == "image":
        return it.get("src") not in CHROME_SRCS
    if it["t"] == "gallery":
        it["srcs"] = [x for x in it["srcs"] if x not in CHROME_SRCS]
        return bool(it["srcs"])
    return True

result = {}
for f in PAGES:
    s = cache[f]
    name = f.parent.name if f.parent.name != str(DOCS.name) and f.parent != DOCS else "HOME"
    if f == DOCS / "index.html": name = "HOME"
    page_items = []
    for a, b in top_sections(s):
        if sig(s[a:b]) in SHARED: continue
        page_items.extend(it for it in extract_items(s[a:b]) if not_chrome(it))
    # page meta
    title = re.search(r'<title>([^<]*)</title>', s)
    desc = re.search(r'<meta name="description" content="([^"]*)"', s)
    result[name] = {
        "title": html.unescape(title.group(1)) if title else "",
        "desc": html.unescape(desc.group(1)) if desc else "",
        "items": page_items,
    }

out = pathlib.Path("/tmp/site_content.json")
out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
for name, d in result.items():
    types = collections.Counter(i["t"] for i in d["items"])
    print(f"{name}: {dict(types)}")
print("written", out)
