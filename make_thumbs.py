#!/usr/bin/env python3
"""Generate small grid thumbnails (~560px WebP q70) for every image that appears
in a photo grid. Grids display cells at ~150-280px; without this they were
shipping the full 768-1920px source (6x the pixels needed). The lightbox still
loads the full image on click, so quality is unaffected.

Thumb path for source <dir>/<name>[-WxH].<ext>  ->  <dir>/<name>-thumb.webp
Run before generate_site.py. Idempotent: skips thumbs already present and newer
than their source.
"""
import json
import pathlib
import re
import urllib.parse

from PIL import Image, ImageOps

DOCS = pathlib.Path(__file__).resolve().parent / "docs"
DATA = json.load(open(pathlib.Path(__file__).resolve().parent / "site_content.json", encoding="utf-8"))

THUMB_W = 560      # max width; covers a ~280px cell at 2x DPR
QUALITY = 70


def collect_grid_sources():
    """every image that renders inside a grid (prose images + galleries)"""
    srcs = set()
    for page in DATA.values():
        if not isinstance(page, dict):
            continue
        for it in page.get("items", []):
            if it.get("t") == "image" and it.get("src"):
                srcs.add(it["src"])
            elif it.get("t") == "gallery":
                for s in it.get("srcs", []):
                    srcs.add(s)
    return srcs


def full_path(src):
    """resolve to the largest on-disk file for this image (strip -WxH variant)"""
    dec = urllib.parse.unquote(src)
    stem = re.sub(r'-\d+x\d+(?=\.\w+$)', '', dec)
    if (DOCS / stem).exists():
        return stem
    return dec if (DOCS / dec).exists() else None


def thumb_rel(src):
    dec = urllib.parse.unquote(src)
    stem = re.sub(r'-\d+x\d+(?=\.\w+$)', '', dec)
    return re.sub(r'\.\w+$', '-thumb.webp', stem)


def main():
    made = skipped = missing = 0
    saved_before = saved_after = 0
    for src in sorted(collect_grid_sources()):
        full = full_path(src)
        if not full:
            missing += 1
            continue
        srcp = DOCS / full
        outp = DOCS / thumb_rel(src)
        if outp.exists() and outp.stat().st_mtime >= srcp.stat().st_mtime:
            skipped += 1
            continue
        try:
            im = Image.open(srcp)
            im = ImageOps.exif_transpose(im)
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGB")
            if im.width > THUMB_W:
                h = round(im.height * THUMB_W / im.width)
                im = im.resize((THUMB_W, h), Image.LANCZOS)
            if im.mode == "RGBA":
                im = im.convert("RGB")
            outp.parent.mkdir(parents=True, exist_ok=True)
            im.save(outp, "WEBP", quality=QUALITY, method=6)
            saved_before += srcp.stat().st_size
            saved_after += outp.stat().st_size
            made += 1
        except Exception as e:
            print(f"  ! {full}: {e}")
            missing += 1
    print(f"thumbs: {made} made, {skipped} up-to-date, {missing} skipped/missing")
    if made:
        print(f"  grid payload for new thumbs: {saved_before/1048576:.1f} MB "
              f"-> {saved_after/1048576:.1f} MB")


if __name__ == "__main__":
    main()
