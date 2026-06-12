#!/usr/bin/env python3
"""Generate the AVIATOR static site from extracted content (site_content.json).

Replaces the Elementor mirror pages with lean hand-built HTML:
same URLs, same content, same images — ~3% of the page weight.
"""
import json, pathlib, re, urllib.parse, html as H

DOCS = pathlib.Path("/home/benyIL123/Desktop/Vibe projects/arturwebsite/docs")
DATA = json.load(open("site_content.json", encoding="utf-8"))

PHONE = "+972523735775"
PHONE_FMT = "052-373-5775"
EMAIL = "a0523735775a@gmail.com"
WA_MSG = urllib.parse.quote("היי, אשמח לקבל פרטים על אטרקציית תא הטייס לאירוע")
WA = f"https://wa.me/972523735775?text={WA_MSG}"
GA = "G-37H1B7Q2ZL"
FB = "https://www.facebook.com/aviator.co.il"
IG = "https://www.instagram.com/aviatorcoil"
YT = "https://www.youtube.com/channel/UCDRFjVaSXts1MnPsCzmMnHA"

# slug -> display name (also nav labels)
PAGES = {
    "כניסה-לאולם-בתא": "כניסה לאולם בתא טייס",
    "אירועים-פרטיים": "אירועים פרטיים",
    "אירועים-עסקיים": "אירועים עסקיים",
    "בר-בת-מצווה": "בר/בת מצווה",
    "קייטנות": "קייטנות",
    "הפנינג": "הפנינג",
    "פרסום": "פרסום נייד וקבוע",
    "סדנה-מטוסי-גבס": "סדנת מטוסי גבס",
    "חץ-וקשת": "חץ וקשת",
    "בובות-ענק": "בובות ענק",
    "בובות-חתונה": "בובות חתונה",
    "משקפי-ראייה-הפוכה": "משקפי ראייה הפוכה",
    "גלריה": "גלריה",
    "סרטונים": "סרטונים",
    "אודותינו": "אודותינו",
    "צור-קשר": "צור קשר",
    "vcard2": "כרטיס ביקור",
}
SERVICES = ["כניסה-לאולם-בתא", "אירועים-פרטיים", "אירועים-עסקיים", "בר-בת-מצווה",
            "קייטנות", "הפנינג", "פרסום", "סדנה-מטוסי-גבס", "חץ-וקשת",
            "בובות-ענק", "בובות-חתונה", "משקפי-ראייה-הפוכה"]
TOP_NAV = ["כניסה-לאולם-בתא", "גלריה", "סרטונים", "אודותינו", "צור-קשר"]

def enc(slug): return urllib.parse.quote(slug)

def u(src):
    """attr-safe url; keep existing percent-escapes"""
    return H.escape(urllib.parse.quote(src, safe="/%:?=&"), quote=True)

def yt_id(url):
    m = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([\w-]{6,})', url)
    return m.group(1) if m else None

def variant(src, maxw):
    """smaller -WxH variant of an upload if available (for grid thumbs)"""
    dec = urllib.parse.unquote(src)
    p = DOCS / dec
    stem = re.sub(r'-\d+x\d+(?=\.\w+$)', '', dec)
    base = pathlib.Path(stem)
    cands = []
    if (DOCS / stem).exists():
        cands.append((10**6, stem))  # full size fallback
    for f in (DOCS / base.parent).glob(base.stem + "-*x*" + base.suffix):
        m = re.match(re.escape(base.stem) + r'-(\d+)x(\d+)$', f.stem)
        if m:
            w = int(m.group(1))
            rel = str(f.relative_to(DOCS))
            cands.append((w if w <= maxw else w + 10**5, rel))
    if not cands:
        return src
    cands.sort()
    # prefer largest width <= maxw
    best = None
    for w, rel in cands:
        if w <= maxw:
            best = (w, rel)
    return urllib.parse.quote(best[1]) if best else src

def full(src):
    dec = urllib.parse.unquote(src)
    stem = re.sub(r'-\d+x\d+(?=\.\w+$)', '', dec)
    return urllib.parse.quote(stem) if (DOCS / stem).exists() else src

ICONS = {
    "wa": '<svg viewBox="0 0 32 32" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M16 3C9.4 3 4 8.4 4 15c0 2.1.6 4.2 1.6 6L4 29l8.2-1.5c1.2.5 2.5.7 3.8.7 6.6 0 12-5.4 12-12S22.6 3 16 3zm6.1 16.9c-.3.8-1.5 1.5-2.1 1.6-.6.1-1.2.2-3.6-.8-3-1.2-5-4.3-5.1-4.5-.1-.2-1.2-1.6-1.2-3.1s.8-2.2 1-2.5c.3-.3.6-.4.8-.4h.6c.2 0 .4 0 .7.5.3.6.9 2.1.9 2.3.1.2.1.4 0 .6-.1.2-.2.4-.4.6l-.6.7c-.2.2-.4.4-.2.8.2.4 1 1.7 2.2 2.7 1.5 1.3 2.8 1.7 3.2 1.9.4.2.6.2.9-.1.2-.3 1-1.2 1.3-1.6.3-.4.5-.3.9-.2.4.1 2.3 1.1 2.7 1.3.4.2.7.3.8.5.1.2.1.9-.2 1.7z"/></svg>',
    "tel": '<svg viewBox="0 0 24 24" width="19" height="19" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.6.1.3 0 .7-.2 1l-2.3 2.2z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" width="19" height="19" fill="currentColor" aria-hidden="true"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M13.5 9H16l.5-3h-3V4.5c0-.9.3-1.5 1.6-1.5H17V.2C16.7.2 15.6 0 14.4 0 11.9 0 10.2 1.5 10.2 4.3V6H7.5v3h2.7v9h3.3V9z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M12 2.2c3.2 0 3.6 0 4.9.1 3.3.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.9.1-3.2 0-3.6 0-4.8-.1-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 4 4 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zm0 3.6a6.2 6.2 0 100 12.4 6.2 6.2 0 000-12.4zm0 10.2a4 4 0 110-8 4 4 0 010 8zm6.4-10.5a1.4 1.4 0 11-2.9 0 1.4 1.4 0 012.9 0z"/></svg>',
    "yt": '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M23.5 7.2s-.2-1.7-1-2.4c-.9-1-1.9-1-2.4-1C16.8 3.5 12 3.5 12 3.5s-4.8 0-8.1.3c-.5.1-1.5.1-2.4 1-.7.7-1 2.4-1 2.4S.3 9.1.3 11.1v1.8c0 1.9.2 3.9.2 3.9s.2 1.7 1 2.4c.9 1 2.1.9 2.6 1 1.9.2 7.9.3 7.9.3s4.8 0 8.1-.3c.5-.1 1.5-.1 2.4-1 .7-.7 1-2.4 1-2.4s.2-1.9.2-3.9v-1.8c0-1.9-.2-3.9-.2-3.9zM9.8 15.1V8.3l6.4 3.4-6.4 3.4z"/></svg>',
    "site": '<svg viewBox="0 0 24 24" width="19" height="19" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm7 6h-3a15 15 0 00-1.3-3.6A8 8 0 0119 8zM12 4c.8 1.2 1.5 2.5 1.9 4h-3.8c.4-1.5 1.1-2.8 1.9-4zM4.3 14a8.2 8.2 0 010-4h3.4a16 16 0 000 4H4.3zm.7 2h3a15 15 0 001.3 3.6A8 8 0 015 16zm3-8H5a8 8 0 014.3-3.6A15 15 0 008 8zm4 12c-.8-1.2-1.5-2.5-1.9-4h3.8c-.4 1.5-1.1 2.8-1.9 4zm2.3-6H9.7a14 14 0 010-4h4.6a14 14 0 010 4zm.4 5.6A15 15 0 0016 16h3a8 8 0 01-4.3 3.6zM16.3 14a16 16 0 000-4h3.4a8.2 8.2 0 010 4h-3.4z"/></svg>',
    "pic": '<svg viewBox="0 0 24 24" width="19" height="19" fill="currentColor" aria-hidden="true"><path d="M21 19V5a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2zM8.5 13.5l2.5 3 3.5-4.5 4.5 6H5l3.5-4.5z"/></svg>',
    "star": '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.6 7-6.2-3.7-6.2 3.7 1.6-7L2 9.2l7.1-.6L12 2z"/></svg>',
    "truck": '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M20 8h-3V4H3a2 2 0 00-2 2v11h2a3 3 0 006 0h6a3 3 0 006 0h2v-5l-3-4zM7.5 18.5A1.5 1.5 0 116 17a1.5 1.5 0 011.5 1.5zm12 0A1.5 1.5 0 1118 17a1.5 1.5 0 011.5 1.5zM17 12V9.5h2.5l1.9 2.5H17z"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M12 1L3 5v6c0 5.6 3.8 10.7 9 12 5.2-1.3 9-6.4 9-12V5l-9-4zm-2 16l-4-4 1.4-1.4L10 14.2l6.6-6.6L18 9l-8 8z"/></svg>',
}

# short labels for the mobile quick-nav tiles
GRID_LABELS = {
    "כניסה-לאולם-בתא": "כניסה לאולם",
    "אירועים-פרטיים": "אירועים פרטיים",
    "אירועים-עסקיים": "אירועים עסקיים",
    "בר-בת-מצווה": "בר/בת מצווה",
    "קייטנות": "קייטנות",
    "הפנינג": "הפנינג",
    "פרסום": "פרסום",
    "סדנה-מטוסי-גבס": "סדנת מטוסי גבס",
    "חץ-וקשת": "חץ וקשת",
    "בובות-ענק": "בובות ענק",
    "בובות-חתונה": "בובות חתונה",
    "משקפי-ראייה-הפוכה": "משקפי ראייה הפוכה",
    "גלריה": "גלריה",
    "סרטונים": "סרטונים",
    "אודותינו": "אודותינו",
}

def page_grid(rel, active=None):
    """compact tile grid linking to every page — shown on mobile only"""
    home = rel if rel else "./"
    tiles = f'<a href="{home}"{" class=on" if active == "HOME" else ""}>ראשי</a>'
    order = ["כניסה-לאולם-בתא", "אירועים-פרטיים", "אירועים-עסקיים", "בר-בת-מצווה",
             "קייטנות", "הפנינג", "פרסום", "סדנה-מטוסי-גבס", "חץ-וקשת",
             "בובות-ענק", "בובות-חתונה", "משקפי-ראייה-הפוכה", "גלריה", "אודותינו"]
    for s in order:
        cls = ' class="on"' if s == active else ""
        tiles += f'<a href="{rel}{enc(s)}/"{cls}>{GRID_LABELS[s]}</a>'
    cls = ' on' if active == "צור-קשר" else ""
    tiles += f'<a href="{rel}{enc("צור-קשר")}/" class="pg-contact{cls}">צור קשר</a>'
    return f'<nav class="pgrid" aria-label="ניווט מהיר">{tiles}</nav>'

def header(rel, active=None):
    home = rel if rel else "./"
    more = "".join(
        f'<a href="{rel}{enc(s)}/">{PAGES[s]}</a>'
        for s in SERVICES if s != "כניסה-לאולם-בתא")
    nav_links = ""
    for s in TOP_NAV:
        cls = ' class="on"' if s == active else ""
        label = "כניסה לאולם — חדש!" if s == "כניסה-לאולם-בתא" else PAGES[s]
        nav_links += f'<a href="{rel}{enc(s)}/"{cls}>{label}</a>'
    return f'''<header class="hdr"><div class="wrap hdr-in">
<a class="brand" href="{home}"><img class="brand-img" src="{rel}assets/logo.png" alt="AVIATOR — אטרקציה והדמיית טיסה בתא טייס אמיתי"></a>
<nav class="nav" id="nav">
<a href="{home}"{' class="on"' if active == "HOME" else ""}>ראשי</a>
<details class="nav-more"><summary>אטרקציות</summary><div class="nav-more-menu">{more}</div></details>
{nav_links}
<a class="btn btn-sm hdr-cta" href="tel:{PHONE}">{ICONS["tel"]}{PHONE_FMT}</a>
</nav>
<button class="nav-burger" aria-label="תפריט" aria-expanded="false"><span></span><span></span><span></span></button>
</div></header>'''

def footer(rel):
    home = rel if rel else "./"
    links = "".join(f'<li><a href="{rel}{enc(s)}/">{PAGES[s]}</a></li>' for s in SERVICES[:6])
    links2 = "".join(f'<li><a href="{rel}{enc(s)}/">{PAGES[s]}</a></li>'
                     for s in ["גלריה", "סרטונים", "אודותינו", "צור-קשר", "vcard2"])
    return f'''<footer class="ftr"><div class="wrap ftr-in">
<div>
<a class="ftr-logo" href="{home}"><img src="{rel}assets/logo.png" alt="AVIATOR" width="170" loading="lazy"></a>
<p>סימולטור טיסה בתא טייס אמיתי של מטוס סילוני — אטרקציה ניידת לאירועים פרטיים ועסקיים, בר/בת מצווה, קייטנות, הפנינגים ופרסום, בכל רחבי הארץ.</p>
<div class="ftr-soc">
<a href="{FB}" target="_blank" rel="noopener" aria-label="פייסבוק">{ICONS["fb"]}</a>
<a href="{IG}" target="_blank" rel="noopener" aria-label="אינסטגרם">{ICONS["ig"]}</a>
<a href="{YT}" target="_blank" rel="noopener" aria-label="יוטיוב">{ICONS["yt"]}</a>
</div>
</div>
<div><h4>אטרקציות</h4><ul>{links}</ul></div>
<div><h4>מידע ויצירת קשר</h4><ul>{links2}
<li><a href="tel:{PHONE}">{PHONE_FMT}</a></li>
<li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
</div>
<div class="ftr-bar">© AVIATOR — כל הזכויות שמורות</div></footer>
<a class="float-wa" href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp">{ICONS["wa"].replace('width="20" height="20"', 'width="30" height="30"')}</a>'''

def shell(rel, title, desc, body, active=None, og_img=None):
    og = f'\n<meta property="og:image" content="{u(og_img)}">' if og_img else ""
    return f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{H.escape(title)}</title>
<meta name="description" content="{H.escape(desc, quote=True)}">
<meta property="og:title" content="{H.escape(title, quote=True)}">
<meta property="og:description" content="{H.escape(desc, quote=True)}">
<meta property="og:type" content="website">{og}
<link rel="icon" type="image/png" href="{rel}assets/favicon.png">
<link rel="preload" href="{rel}assets/fonts/heebo-hebrew.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/site.css">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA}');</script>
</head>
<body>
{header(rel, active)}
{page_grid(rel, active)}
{body}
{footer(rel)}
<script src="{rel}assets/site.js" defer></script>
</body>
</html>'''

def cta_band():
    return f'''<section class="wrap"><div class="cta-band" data-rv>
<h2>רוצים אטרקציה שאף אחד לא ישכח?</h2>
<p>ספרו לנו על האירוע שלכם ונחזור אליכם עם כל הפרטים — אנחנו מגיעים לכל מקום בארץ.</p>
<div class="hero-cta">
<a class="btn btn-wa" href="{WA}" target="_blank" rel="noopener">{ICONS["wa"]}שלחו הודעת וואטסאפ</a>
<a class="btn" href="tel:{PHONE}">{ICONS["tel"]}התקשרו: {PHONE_FMT}</a>
</div></div></section>'''

def img_grid(srcs, rel, cls="g-imgs"):
    cells = []
    for s in srcs:
        thumb = variant(s, 768)
        cells.append(f'<a href="{rel}{u(full(s))}"><img loading="lazy" src="{rel}{u(thumb)}" alt=""></a>')
    return f'<div class="grid {cls}">{"".join(cells)}</div>'

def vid_embed(url):
    vid = yt_id(url)
    if not vid: return ""
    return (f'<div class="yt" data-id="{vid}">'
            f'<img loading="lazy" src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="סרטון">'
            f'<button class="play" aria-label="נגן סרטון"></button></div>')

def vids_block(urls, style=""):
    """one video -> large centered frame; several -> grid"""
    sty = f' style="{style}"' if style else ""
    if len(urls) == 1:
        return f'<div class="vid-solo"{sty}>{vid_embed(urls[0])}</div>'
    return f'<div class="grid g-vids"{sty}>{"".join(vid_embed(v) for v in urls)}</div>'

LIST_TRIGGER = re.compile(r':\s*$')

def tidy(t):
    """clean up punctuation spacing in the legacy copy"""
    t = re.sub(r'\s+([,.!?;:])', r'\1', t)                      # no space before punctuation
    t = re.sub(r'([,;])(?=[֐-׿A-Za-z])', r'\1 ', t)   # space after comma
    t = re.sub(r'(?<=[֐-׿])([!?.])(?=[֐-׿])', r'\1 ', t)
    t = t.replace('\\', '/')
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r' ?\n ?', '\n', t)
    return t.strip()

def render_prose(items, rel, page_title):
    """flat item list -> structured article html"""
    out = []
    imgbuf = []
    vidbuf = []
    lead_used = False
    in_list = False
    last_kind = None

    def flush():
        nonlocal imgbuf, vidbuf, in_list, last_kind
        if imgbuf or vidbuf:
            last_kind = None
        if in_list:
            out.append('</ul>')
            in_list = False
        if imgbuf:
            if len(imgbuf) == 1:
                s = imgbuf[0]
                out.append(f'<figure class="solo"><a href="{rel}{u(full(s))}">'
                           f'<img loading="lazy" src="{rel}{u(variant(s, 1024))}" alt=""></a></figure>')
            else:
                out.append(img_grid(imgbuf, rel))
            imgbuf = []
        if vidbuf:
            out.append(vids_block(vidbuf))
            vidbuf = []

    for it in items:
        t = it["t"]
        if t in ("button", "html"):
            continue
        if t == "image":
            if in_list: out.append('</ul>'); in_list = False
            if vidbuf: flush()
            imgbuf.append(it["src"])
            continue
        if t == "gallery":
            flush()
            out.append(img_grid(it["srcs"], rel))
            continue
        if t == "video":
            if in_list: out.append('</ul>'); in_list = False
            if imgbuf: flush()
            vidbuf.append(it["url"])
            continue
        if t == "text":
            flush()
            for p in it["paras"]:
                out.append(f'<p>{H.escape(tidy(p))}</p>')
            continue
        if t == "heading":
            txt = tidy(it["text"])
            if not txt or txt == page_title:
                continue
            txt_esc = H.escape(txt).replace("\n", "<br>")
            if in_list:
                if len(txt) <= 110:
                    out.append(f'<li>{txt_esc}</li>')
                    continue
                out.append('</ul>'); in_list = False
            flush()
            if LIST_TRIGGER.search(txt):
                out.append(f'<h2>{H.escape(txt.rstrip(":").strip())}</h2><ul class="checks">')
                in_list = True
                last_kind = "h2"
            elif txt.rstrip("!").endswith("?") and len(txt) <= 120:
                # questions make natural section anchors
                out.append(f'<h2>{txt_esc}</h2>')
                last_kind = "h2"
            elif not lead_used and len(txt) > 40:
                out.append(f'<p class="lead">{txt_esc}</p>')
                lead_used = True
                last_kind = "lead"
            elif len(txt) <= 70 and (txt.endswith("!") or len(txt) <= 45) and last_kind != "em":
                out.append(f'<p class="em">{txt_esc}</p>')
                last_kind = "em"
            else:
                out.append(f'<p>{txt_esc}</p>')
                last_kind = "p"
    flush()
    return "\n".join(out)

def page_hero(title, rel):
    home = rel if rel else "./"
    return (f'<section class="page-hero"><div class="wrap"><h1>{H.escape(title)}</h1>'
            f'<div class="crumb"><a href="{home}">ראשי</a> ‹ {H.escape(title)}</div></div></section>')

# ---------------- service / generic pages ----------------
def build_generic(slug):
    d = DATA[slug]
    rel = "../"
    title = d["title"] or f"{PAGES[slug]} - AVIATOR"
    desc = d["desc"] or f"{PAGES[slug]} — אטרקציית תא טייס אמיתי לאירועים מבית AVIATOR."
    body = (page_hero(PAGES[slug], rel)
            + f'<main class="wrap"><article class="prose">{render_prose(d["items"], rel, PAGES[slug])}</article></main>'
            + cta_band())
    return shell(rel, title, desc, body, active=slug)

# ---------------- home ----------------
def build_home():
    d = DATA["HOME"]
    rel = ""
    # cards: img -> h1 -> text -> btn groups
    cards = []
    cur = {}
    for it in d["items"]:
        if it["t"] == "image":
            if cur.get("img"): cur = {}
            cur = {"img": it["src"], "link": it.get("link")}
        elif it["t"] == "heading" and it["tag"] == "h1" and cur.get("img"):
            cur["title"] = it["text"]
        elif it["t"] == "text" and cur.get("title"):
            cur["blurb"] = " ".join(it["paras"])
            cards.append(cur)
            cur = {}

    # every attraction in the nav gets a card; add the ones the old
    # homepage didn't feature, built from their own page content
    TITLE_ALIAS = {  # legacy homepage card titles -> page slug
        "פרסום נייד/קבוע": "פרסום",
        "סדנה מטוסי גבס": "סדנה-מטוסי-גבס",
        "כניסה לאולם בתא טייס אמיתי": "כניסה-לאולם-בתא",
    }
    NEW_BLURBS = {
        "אירועים-פרטיים": "חתונה, בר/בת מצווה או יום הולדת — תא טייס אמיתי שהופך כל אירוע פרטי לחוויה שמדברים עליה.",
        "אירועים-עסקיים": "ימי כיף, אירועי חברה ותערוכות — אטרקציה ממותגת שמושכת קהל, מגבשת את הצוות ונחרטת בזיכרון.",
        "חץ-וקשת": "עמדת חץ וקשת מקצועית ובטוחה — תחרות מדויקת, ספורטיבית ומלהיבה לילדים ולמבוגרים.",
        "בובות-ענק": "בובות ענק בגובה 2.6 מטר שמסתובבות באירוע, מצטלמות עם האורחים ועושות שמח לכל גיל.",
        "בובות-חתונה": "בובות ענק של חתן וכלה שמוסיפות לחתונה רגע WOW — צילומים, ריקודים והפתעה שכל האורחים יזכרו.",
        "משקפי-ראייה-הפוכה": "אתגר משקפי הראייה ההפוכה — משימות שיווי משקל, מיקוד וצחוק גדול לכל המשפחה.",
    }
    covered = set()
    for c in cards:
        t = re.sub(r'\s+', ' ', c.get("title", "")).strip()
        if t in TITLE_ALIAS:
            covered.add(TITLE_ALIAS[t])
        for slug, name in PAGES.items():
            if t == name:
                covered.add(slug)
    for slug in SERVICES:
        if slug in covered:
            continue
        d2 = DATA.get(slug)
        if not d2:
            continue
        img = next((it["src"] for it in d2["items"] if it["t"] == "image"), None) \
            or next((it["srcs"][0] for it in d2["items"] if it["t"] == "gallery" and it["srcs"]), None)
        blurb = NEW_BLURBS.get(slug) or (d2.get("desc") or "").strip()
        if len(blurb) < 30:
            blurb = next((it["text"].replace("\n", " ") for it in d2["items"]
                          if it["t"] == "heading" and len(it["text"]) > 40), "") \
                or next((" ".join(it["paras"])[:220] for it in d2["items"] if it["t"] == "text"), "")
        if img:
            cards.append({"img": img, "link": enc(slug) + "/",
                          "title": PAGES[slug], "blurb": blurb})

    card_html = ""
    for c in cards:
        link = c.get("link")
        if link:
            link = urllib.parse.quote(urllib.parse.unquote(link), safe="/%-._~")
        else:
            link = enc("צור-קשר") + "/"
        card_html += (f'<a class="card" data-rv href="{link}">'
                      f'<img loading="lazy" src="{u(variant(c["img"], 768))}" alt="{H.escape(c["title"], quote=True)}">'
                      f'<div class="card-b"><h3>{H.escape(c["title"])}</h3>'
                      f'<p>{H.escape(c.get("blurb", ""))}</p>'
                      f'<span class="more">לפרטים</span></div></a>')

    hero_img = "wp-content/uploads/2024/02/aviator.co_.il-160-1024x768.jpg"
    spot_img = "wp-content/uploads/2024/02/aviator.co_.il-184-1024x768.jpg"
    logos = "".join(
        f'<div class="client" data-rv>'
        f'<img class="ph" loading="lazy" src="{u(variant(c["photo"], 768))}" alt="אוויאטור אצל הלקוח">'
        f'<div class="lg"><img loading="lazy" src="{u(variant(c["logo"], 420))}" alt="לוגו לקוח"></div>'
        f'</div>'
        for c in DATA.get("CLIENTS", []))

    slides = [
        ("wp-content/uploads/2024/02/aviator.co_.il-160.jpg", "ימי כיף וגיבוש לחברות ולצוותים"),
        ("wp-content/uploads/2024/02/aviator.co_.il-185.jpg", "בר/בת מצווה עם טעם של טיסה"),
        ("wp-content/uploads/2024/02/aviator.co_.il-89.jpg", "קייטנות וחוויית טיס לילדים"),
        ("wp-content/uploads/2024/02/aviator.co_.il-14.jpg", "כניסה לאולם בתא טייס אמיתי — קבלת פנים שלא שוכחים"),
        ("wp-content/uploads/2024/02/aviator.co_.il-93.jpg", "הפנינגים ואירועים בכל רחבי הארץ"),
    ]
    slide_html = "".join(
        f'<div class="hs{" on" if n == 0 else ""}" data-cap="{H.escape(capt, quote=True)}">'
        f'<img src="{u(variant(img, 1024))}" alt="{H.escape(capt, quote=True)}"'
        + (' fetchpriority="high">' if n == 0 else ' loading="lazy">')
        + '</div>'
        for n, (img, capt) in enumerate(slides))
    dot_html = "".join(
        f'<button{" class=on" if n == 0 else ""} aria-label="תמונה {n+1}"></button>'
        for n in range(len(slides)))
    def first_img(slug):
        d2 = DATA.get(slug, {})
        return next((it["src"] for it in d2.get("items", []) if it["t"] == "image"), None) \
            or next((it["srcs"][0] for it in d2.get("items", []) if it["t"] == "gallery" and it["srcs"]), None)

    ARROWS = ('<button class="car-prev" aria-label="הקודם"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M9 6l6 6-6 6"/></svg></button>'
              '<button class="car-next" aria-label="הבא"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 6l-6 6 6 6"/></svg></button>')

    # rotating spotlight band
    spots = [
        {"kick": "חדש אצלנו", "title": "כזה עוד לא ראיתם: כניסה מיוחדת לאולם בתא טייס אמיתי!",
         "text": "החתן, הכלה או חתן הבר-מצווה נכנסים לאולם בתוך תא טייס אמיתי — כניסה מרשימה שאף אורח לא ישכח.",
         "btn": "לפרטים על הכניסה לאולם", "slug": "כניסה-לאולם-בתא", "img": spot_img},
        {"kick": "שמח באירוע", "title": "בובות ענק בגובה 2.6 מטר שעושות שמח לכולם",
         "text": "הבובות מסתובבות בין האורחים, רוקדות ומצטלמות — אטרקציה צבעונית ומלהיבה לילדים ולמבוגרים.",
         "btn": "לפרטים על בובות ענק", "slug": "בובות-ענק", "img": first_img("בובות-ענק")},
        {"kick": "אתגר לכל המשפחה", "title": "משקפי ראייה הפוכה — פתאום כל העולם מתהפך!",
         "text": "משימות שיווי משקל ומיקוד עם משקפי היפוך — צחוק גדול, אתגר אמיתי וחוויה בלתי נשכחת לכל הגילאים.",
         "btn": "לפרטים על משקפי ראייה הפוכה", "slug": "משקפי-ראייה-הפוכה", "img": first_img("משקפי-ראייה-הפוכה")},
        {"kick": "לחברות ולארגונים", "title": "ימי כיף ואירועי חברה שממריאים לגבהים",
         "text": "תא טייס אמיתי, עמדות סימולציה ותחרויות מטוסי נייר — גיבוש שהעובדים לא מפסיקים לדבר עליו.",
         "btn": "לפרטים על אירועים עסקיים", "slug": "אירועים-עסקיים", "img": first_img("אירועים-עסקיים")},
        {"kick": "לקיץ ולחופשים", "title": "קייטנות עם טעם של טיסה אמיתית",
         "text": "חוויית טיס לילדים: סימולטור בתא טייס אמיתי, בניית מטוסי נייר ותעודת טייס לכל משתתף.",
         "btn": "לפרטים על קייטנות", "slug": "קייטנות", "img": first_img("קייטנות")},
    ]
    ss_html = "".join(
        f'<div class="ss{" on" if n == 0 else ""}" '
        f'data-kick="{H.escape(sp["kick"], quote=True)}" data-title="{H.escape(sp["title"], quote=True)}" '
        f'data-text="{H.escape(sp["text"], quote=True)}" data-btn="{H.escape(sp["btn"], quote=True)}" '
        f'data-href="{enc(sp["slug"])}/">'
        f'<img loading="lazy" src="{u(variant(sp["img"], 1024))}" alt="{H.escape(sp["title"], quote=True)}"></div>'
        for n, sp in enumerate(spots))
    spot_dots = "".join(
        f'<button{" class=on" if n == 0 else ""} aria-label="אטרקציה {n+1}"></button>'
        for n in range(len(spots)))
    spot_html = f'''<section class="sec spot"><div class="wrap spot-in">
<div class="spot-txt" data-rv><div class="spot-body">
<span class="kicker">{spots[0]["kick"]}</span>
<h2>{spots[0]["title"]}</h2>
<p>{spots[0]["text"]}</p>
<a class="btn" href="{enc(spots[0]["slug"])}/">{spots[0]["btn"]}</a>
</div></div>
<div class="spot-car" data-rv>
{ss_html}
{ARROWS}
<div class="spot-dots">{spot_dots}</div>
</div>
</div></section>'''

    plane = ('<span class="hero-plane" aria-hidden="true">'
             '<svg width="58" height="58" viewBox="0 0 24 24" fill="currentColor" style="transform:rotate(76deg)">'
             '<path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg></span>')
    FP_D = "M1160 70 C 860 -10, 340 130, 40 30"
    PLANE_D = "M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"
    flightpath = (f'<div class="flightpath" aria-hidden="true">'
                  f'<svg viewBox="0 0 1200 110" preserveAspectRatio="none">'
                  f'<path class="fp-track" d="{FP_D}"/>'
                  f'<path class="fp-trail" d="{FP_D}"/>'
                  f'<g class="fpg" transform="translate(1160 70) rotate(-75)">'
                  f'<circle r="22" fill="#fff" stroke="#e3e9f1"/>'
                  f'<path d="{PLANE_D}" transform="translate(-17.5 -17.5) scale(1.45)" fill="#0d2a4d"/>'
                  f'</g></svg></div>')

    body = f'''
<section class="hero">{plane}<div class="wrap hero-in">
<div>
<h1>אטרקציה שאי אפשר לשכוח:<br><em>סימולטור טיסה בתא טייס אמיתי</em></h1>
<p class="hero-sub">תא טייס של מטוס סילוני שטס בשמי ישראל — נייד, אמיתי עד הכפתור האחרון, ומגיע לכל מקום בארץ. לאירועים פרטיים ועסקיים, בר/בת מצווה, קייטנות, הפנינגים ופרסום.</p>
<div class="hero-cta">
<a class="btn btn-wa" href="{WA}" target="_blank" rel="noopener">{ICONS["wa"]}דברו איתנו בוואטסאפ</a>
<a class="btn btn-ghost" href="#services">לכל האטרקציות</a>
</div>
<div class="hero-strip">
<div>{ICONS["truck"]}ניידים בכל הארץ</div>
<div>{ICONS["shield"]}תא טייס אמיתי</div>
<div>{ICONS["star"]}מאות אירועים מרוצים</div>
</div>
</div>
<div class="hero-img">
<div class="hero-car">
{slide_html}
{ARROWS}
<div class="hero-cap">{H.escape(slides[0][1])}</div>
<div class="hero-dots">{dot_html}</div>
</div>
</div>
</div></section>

{flightpath}

{spot_html}

<section class="sec" id="services"><div class="wrap">
<div class="sec-head" data-rv>
<span class="kicker">מה אנחנו מציעים</span>
<h2>האטרקציות שלנו</h2>
<p>סימולטור טיסה בתא טייס אמיתי ועוד שלל פעילויות לכל סוגי האירועים — לילדים ולמבוגרים.</p>
</div>
<div class="cards">{card_html}</div>
</div></section>

<section class="sec sec-alt"><div class="wrap">
<div class="sec-head" data-rv>
<span class="kicker">סומכים עלינו</span>
<h2>לקוחות שלנו</h2>
<p>חברות מובילות, משרדי ממשלה ומאות לקוחות פרטיים כבר חוו את אוויאטור.</p>
</div>
<div class="clients">{logos}</div>
<p style="text-align:center;margin:30px 0 0;font-weight:700;color:var(--navy);font-size:18px" data-rv>נשמח לראות אתכם בין לקוחותינו!</p>
</div></section>

{cta_band()}

<div class="skypath" aria-hidden="true"><svg preserveAspectRatio="none">
<path class="sp-track" d=""/>
<path class="sp-trail" d=""/>
</svg></div>
<div class="skyplane" aria-hidden="true"><svg width="44" height="44" viewBox="0 0 44 44">
<circle cx="22" cy="22" r="21" fill="#fff" stroke="#e3e9f1"/>
<path d="{PLANE_D}" transform="translate(7 7) scale(1.25)" fill="#0d2a4d"/>
</svg></div>'''
    return shell(rel, DATA["HOME"]["title"], DATA["HOME"]["desc"], body, active="HOME")

# ---------------- gallery ----------------
def build_gallery():
    d = DATA["גלריה"]
    rel = "../"
    # videos placed at the head of the item list open the page
    items = list(d["items"])
    top_vids = []
    while items and items[0]["t"] == "video":
        top_vids.append(items.pop(0)["url"])
    top_html = ""
    if top_vids:
        top_html = vids_block(top_vids, "margin-top:38px")
    seen, imgs, vids = set(), [], []
    for it in items:
        if it["t"] == "gallery":
            for s in it["srcs"]:
                k = full(s)
                if k not in seen:
                    seen.add(k); imgs.append(s)
        elif it["t"] == "image":
            k = full(it["src"])
            if k not in seen:
                seen.add(k); imgs.append(it["src"])
        elif it["t"] == "video":
            vids.append(it["url"])
    vhtml = ""
    if vids:
        vhtml = (f'<div class="sec-head" style="margin-top:54px"><h2>סרטונים מהאירועים</h2></div>'
                 + vids_block(vids))
    body = (page_hero("גלריה", rel)
            + f'<main class="wrap">{top_html}<div style="margin-top:38px">{img_grid(imgs, rel)}</div>{vhtml}</main>'
            + cta_band())
    return shell(rel, d["title"], d["desc"], body, active="גלריה")

# ---------------- videos ----------------
def build_videos():
    d = DATA["סרטונים"]
    rel = "../"
    vids = [it["url"] for it in d["items"] if it["t"] == "video"]
    body = (page_hero("סרטונים", rel)
            + f'<main class="wrap">{vids_block(vids, "margin-top:38px")}</main>'
            + cta_band())
    return shell(rel, d["title"], d["desc"], body, active="סרטונים")

# ---------------- contact ----------------
def build_contact():
    d = DATA["צור-קשר"]
    rel = "../"
    cards = f'''<div class="contact-cards">
<a class="ccard" href="{WA}" target="_blank" rel="noopener"><div class="ic" style="background:var(--wa)">{ICONS["wa"]}</div><h3>וואטסאפ</h3><p>{PHONE_FMT}</p></a>
<a class="ccard" href="tel:{PHONE}"><div class="ic" style="background:var(--navy)">{ICONS["tel"]}</div><h3>טלפון</h3><p>{PHONE_FMT}</p></a>
<a class="ccard" href="mailto:{EMAIL}"><div class="ic" style="background:var(--red)">{ICONS["mail"]}</div><h3>אימייל</h3><p style="font-size:13.5px">{EMAIL}</p></a>
</div>'''
    body = (page_hero("צור קשר", rel)
            + f'''<main class="wrap"><div class="sec-head" style="margin-top:44px">
<h2>נשמח לשמוע על האירוע שלכם</h2>
<p>פעילים בכל רחבי הארץ, מענה מהיר בוואטסאפ ובטלפון. תרגישו חופשי לשאול — ואנו נשמח לעזור.</p>
</div>{cards}</main>''')
    return shell(rel, d["title"], d["desc"], body, active="צור-קשר")

# ---------------- vcard ----------------
def build_vcard():
    d = DATA["vcard2"]
    rel = "../"
    photo = next((it["src"] for it in d["items"] if it["t"] == "image" and not it.get("link")), None)
    photo_html = f'<img src="{rel}{u(variant(photo, 768))}" alt="AVIATOR" style="border-radius:18px;box-shadow:var(--shadow-lg)">' if photo else ""
    links = [
        (WA, "wa", "var(--wa)", "וואטסאפ"),
        (f"tel:{PHONE}", "tel", "var(--navy)", f"טלפון: {PHONE_FMT}"),
        (f"mailto:{EMAIL}", "mail", "var(--red)", "אימייל"),
        (f"{rel}{enc('גלריה')}/", "pic", "var(--blue)", "גלריה"),
        (rel, "site", "var(--navy)", "האתר שלנו"),
        (FB, "fb", "#1877f2", "פייסבוק"),
        (IG, "ig", "#d62976", "אינסטגרם"),
        (YT, "yt", "#ff0000", "יוטיוב"),
    ]
    lh = "".join(
        f'<a href="{href}"{" target=_blank rel=noopener" if href.startswith("http") else ""}>'
        f'<span class="ic" style="background:{color}">{ICONS[ic]}</span>{label}</a>'
        for href, ic, color, label in links)
    body = f'''<main class="vcard-page">{photo_html}
<h1 style="margin:22px 0 2px"><img src="{rel}assets/logo.png" alt="AVIATOR — אטרקציה והדמיית טיסה בתא טייס אמיתי" width="230" style="margin:0 auto"></h1>
<div class="vcard-links">{lh}</div></main>'''
    return shell(rel, d["title"], d["desc"], body)

# ---------------- wedding puppets ----------------
def build_wedding():
    d = DATA["בובות-חתונה"]
    rel = "../"
    vids = [it["url"] for it in d["items"] if it["t"] == "video"]
    imgs = [it["src"] for it in d["items"] if it["t"] == "image"]

    def checks(items):
        return ('<ul class="checks">'
                + "".join(f'<li>{H.escape(t)}</li>' for t in items) + '</ul>')

    prose = f'''<article class="prose">
<p class="lead">🎉 בובות ענק לאירוע שלכם! 🎉 רוצים להוסיף לטקס שלכם ייחודיות ולהעניק לאורחים חוויה בלתי נשכחת? הבובות שלנו — דמויות ענק של חתן וכלה — הן הבחירה המושלמת.</p>
{vids_block(vids)}
{checks(["📸 תמונות, רגשות, מחיאות כפיים והתלהבות — מובטחים",
         "✈️ בובות הענק שלנו = אפקט WOW!",
         "תנו לאורחים לזכור את האירוע שלכם לנצח"])}
<h2>💍 מתנה ורגע שלא שוכחים</h2>
{checks(["מתנה מיוחדת לזוג הצעיר או לאורחים — מושלם גם להצעות נישואין! 💓",
         "סמל של אושר ואהבה שיישאר כמזכרת לשנים רבות",
         "אפשרות למיתוג שמות חתן וכלה אמיתיים — בכובע של החתן, בכיס ובבטן של הכלה יש שטח למיתוג"])}
{img_grid(imgs, rel)}
<h2>✨ למה לבחור בנו?</h2>
{checks(["איכות גבוהה ותשומת לב לכל פרט",
         "גישה אישית — הבובות רוקדות ומשמחות את האורחים, מלוות בקבלת הפנים, מצטלמות עם האורחים ועושות את הערב שלכם בלתי נשכח ושמח! 💓🇮🇱"])}
<p class="em">📸 תדמיינו כמה מרגש זה ייראה כשהבובות יעמדו ליד העוגה או בצילומי החתונה!</p>
<p class="lead" style="text-align:center">🎁 הזמינו עכשיו והפכו את החתונה שלכם לבלתי נשכחת!</p>
<div style="text-align:center;margin:8px 0 4px">
<a class="btn btn-wa" href="{WA}" target="_blank" rel="noopener">{ICONS["wa"]}לפרטים והזמנות בוואטסאפ</a>
<a class="btn" href="tel:{PHONE}" style="margin-inline-start:10px">{ICONS["tel"]}052-373-5775</a>
</div></article>'''
    body = page_hero("בובות חתונה", rel) + f'<main class="wrap">{prose}</main>' + cta_band()
    return shell(rel, d["title"], d["desc"], body, active="בובות-חתונה")

# ---------------- write everything ----------------
written = []
(DOCS / "index.html").write_text(build_home(), encoding="utf-8")
written.append("HOME")
for slug in PAGES:
    p = DOCS / slug / "index.html"
    if slug == "גלריה": html_out = build_gallery()
    elif slug == "סרטונים": html_out = build_videos()
    elif slug == "צור-קשר": html_out = build_contact()
    elif slug == "vcard2": html_out = build_vcard()
    elif slug == "בובות-חתונה": html_out = build_wedding()
    else: html_out = build_generic(slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html_out, encoding="utf-8")
    written.append(slug)

# duplicate page -> redirect to canonical
dup = DOCS / "בר-בת-מצווה-2" / "index.html"
dup.write_text(f'''<!DOCTYPE html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=../{enc("בר-בת-מצווה")}/">
<link rel="canonical" href="../{enc("בר-בת-מצווה")}/">
<title>בר/בת מצווה - AVIATOR</title></head>
<body><p><a href="../{enc("בר-בת-מצווה")}/">להמשך לעמוד בר/בת מצווה</a></p></body></html>''', encoding="utf-8")
written.append("בר-בת-מצווה-2 (redirect)")

print(f"generated {len(written)} pages:", ", ".join(written))
