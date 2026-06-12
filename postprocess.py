#!/usr/bin/env python3
"""Post-process wget mirror of aviator.co.il for GitHub Pages.

- strips ?ver= query strings from filenames and references
- moves flat PAGE.html -> PAGE/index.html (preserves original site URLs)
- rewrites absolute https://aviator.co.il/... links to relative ones
- collects referenced wp-content URLs that wget missed (srcset etc.)
"""
import os, re, shutil, urllib.parse, pathlib

SITE = pathlib.Path("/home/benyIL123/Desktop/Vibe projects/arturwebsite/site")
DOMAIN = "https://aviator.co.il"

# ---------- 1. strip query strings from filenames ----------
for p in sorted(SITE.rglob("*")):
    if "?" in p.name and p.is_file():
        target = p.with_name(p.name.split("?")[0])
        if target.exists():
            p.unlink()
        else:
            p.rename(target)
print("query-string files cleaned")

# ---------- 2. figure out page set ----------
flat_pages = []  # names without .html, at root
for p in SITE.iterdir():
    if p.suffix == ".html" and p.name != "index.html":
        flat_pages.append(p.stem)
dir_pages = [p.name for p in SITE.iterdir() if p.is_dir()
             and p.name not in ("wp-content", "wp-includes", "comments")]
print("flat pages:", flat_pages)
print("dir pages:", dir_pages)

# move flat -> dir
for name in flat_pages:
    src = SITE / f"{name}.html"
    dst_dir = SITE / name
    dst = dst_dir / "index.html"
    if dst.exists():
        # duplicate (trailing-slash variant already crawled); keep dir version
        src.unlink()
    else:
        dst_dir.mkdir(exist_ok=True)
        src.rename(dst)

all_pages = sorted(set(flat_pages) | set(dir_pages))

# ---------- 3. rewrite every html file ----------
def enc(name: str) -> str:
    return urllib.parse.quote(name)

missing_urls = set()
upload_ref_re = re.compile(r"https://aviator\.co\.il/(wp-content/[^\s\"'<>,)\\]+)")

html_files = sorted(SITE.rglob("*.html"))
for f in html_files:
    depth = len(f.relative_to(SITE).parts) - 1
    rel = "../" * depth          # prefix to reach site root
    home = rel if rel else "./"
    s = f.read_text(encoding="utf-8", errors="replace")

    # collect absolute upload refs before rewriting (to download later)
    for m in upload_ref_re.finditer(s):
        path = urllib.parse.unquote(m.group(1).split("?")[0])
        if not (SITE / path).exists():
            missing_urls.add(m.group(1).split("?")[0])

    # strip wget-encoded query suffixes:  foo.css%3Fver=1.2.css -> foo.css
    s = re.sub(r"%3F[^\"'<>\s\\)]*", "", s)

    # absolute asset urls -> relative
    s = s.replace(f"{DOMAIN}/wp-content/", f"{rel}wp-content/")
    s = s.replace(f"{DOMAIN}/wp-includes/", f"{rel}wp-includes/")

    # absolute page urls (raw + percent-encoded, with/without trailing slash)
    for name in all_pages:
        for variant in {name, enc(name)}:
            s = re.sub(
                re.escape(f"{DOMAIN}/{variant}") + r"/?(?=[\"'<>\s?#])",
                f"{rel}{enc(name)}/", s)
    # bare domain (canonical, og:url, home links, leftover wp-json etc.)
    s = re.sub(re.escape(DOMAIN) + r"(?=/|[\"'<>\s])", "", s)
    s = s.replace('href="/"', f'href="{home}"')

    # wget-converted flat links -> directory links
    for name in all_pages:
        e = re.escape(enc(name))
        s = re.sub(rf"(?:\.\./)*{e}\.html", f"{rel}{enc(name)}/", s)
        s = re.sub(rf"(?:\.\./)*{e}/index\.html", f"{rel}{enc(name)}/", s)
    # home links
    s = re.sub(r"(href|src)=\"(?:\.\./)*index\.html\"", rf'\1="{home}"', s)

    # relative asset refs inside moved pages need ../ prefix
    if depth > 0:
        s = re.sub(r"((?:href|src|content)=[\"'])(wp-(?:content|includes)/)", rf"\1{rel}\2", s)
        s = re.sub(r"(url\([\"']?)(wp-(?:content|includes)/)", rf"\1{rel}\2", s)
        s = re.sub(r"((?:href|src)=[\"'])(feed\.rss|comments/)", rf"\1{rel}\2", s)

    f.write_text(s, encoding="utf-8")

print(f"rewrote {len(html_files)} html files")

# root-relative urls that survived (e.g. /wp-content/...) are fine only on
# custom domains; make them relative too
for f in html_files:
    depth = len(f.relative_to(SITE).parts) - 1
    rel = "../" * depth
    s = f.read_text(encoding="utf-8")
    s = s.replace('"/wp-content/', f'"{rel}wp-content/')
    s = s.replace('"/wp-includes/', f'"{rel}wp-includes/')
    f.write_text(s, encoding="utf-8")

# ---------- 4. css files: any absolute refs? ----------
for f in list(SITE.rglob("*.css")):
    s = f.read_text(encoding="utf-8", errors="replace")
    if DOMAIN in s:
        depth = len(f.relative_to(SITE).parts) - 1
        for m in upload_ref_re.finditer(s):
            path = urllib.parse.unquote(m.group(1).split("?")[0])
            if not (SITE / path).exists():
                missing_urls.add(m.group(1).split("?")[0])
        s = s.replace(f"{DOMAIN}/", "../" * depth)
        f.write_text(s, encoding="utf-8")

# ---------- 5. write missing-asset list ----------
out = pathlib.Path("/tmp/missing_assets.txt")
out.write_text("\n".join(f"{DOMAIN}/{u}" for u in sorted(missing_urls)))
print(f"{len(missing_urls)} missing assets listed in {out}")
