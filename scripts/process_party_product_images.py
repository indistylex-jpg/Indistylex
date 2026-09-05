#!/usr/bin/env python3
"""Batch process Party bear product photos for Indistylex e-commerce.

Creates:
  background/  - product cutout on clean Indistylex-branded backdrop
  humanpic/    - placeholder copies for manual/AI model shots (see README)

Usage:
  .imgvenv/bin/python scripts/process_party_product_images.py
"""
from __future__ import annotations

import io
import os
from pathlib import Path

# Keep rembg model cache inside the project (sandbox-safe).
os.environ.setdefault(
    "XDG_CACHE_HOME",
    str(Path(__file__).resolve().parents[1] / ".cache"),
)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from rembg import remove

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Party bear and festival-20260822T073058Z-1-001" / "Party bear and festival"
OUT_BG = SOURCE.parent / "background"
OUT_HUMAN = SOURCE.parent / "humanpic"

# Indistylex brand palette
COLOR_TOP = (239, 246, 255)      # #EFF6FF
COLOR_BOTTOM = (255, 255, 255)   # #FFFFFF
COLOR_ACCENT = (219, 234, 254)   # #DBEAFE
MAX_EDGE = 1600


def brand_background(width: int, height: int) -> Image.Image:
    bg = Image.new("RGB", (width, height), COLOR_BOTTOM)
    draw = ImageDraw.Draw(bg)
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(COLOR_TOP[0] + (COLOR_BOTTOM[0] - COLOR_TOP[0]) * t)
        g = int(COLOR_TOP[1] + (COLOR_BOTTOM[1] - COLOR_TOP[1]) * t)
        b = int(COLOR_TOP[2] + (COLOR_BOTTOM[2] - COLOR_TOP[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    # subtle top accent band
    draw.rectangle([0, 0, width, int(height * 0.08)], fill=COLOR_ACCENT)
    return bg


def remove_background(img: Image.Image) -> Image.Image:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    out = remove(buf.getvalue())
    return Image.open(io.BytesIO(out)).convert("RGBA")


def composite_product(src: Image.Image) -> Image.Image:
    rgba = remove_background(src)
    rgba = ImageOps.exif_transpose(rgba)

    # Trim transparent margins
    alpha = rgba.split()[-1]
    bbox = alpha.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)

    w, h = rgba.size
    scale = min(MAX_EDGE / w, MAX_EDGE / h, 1.0) * 0.88
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    rgba = rgba.resize((nw, nh), Image.LANCZOS)

    canvas_w = max(nw + 120, 1200)
    canvas_h = max(nh + 160, 1200)
    bg = brand_background(canvas_w, canvas_h)

    shadow = Image.new("RGBA", (nw + 40, nh + 40), (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(shadow)
    sh_draw.rounded_rectangle([20, 20, nw + 20, nh + 20], radius=24, fill=(30, 77, 140, 45))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))

    x = (canvas_w - nw) // 2
    y = (canvas_h - nh) // 2 + 20
    bg_rgba = bg.convert("RGBA")
    bg_rgba.alpha_composite(shadow, (x - 20, y - 10))
    bg_rgba.alpha_composite(rgba, (x, y))
    return bg_rgba.convert("RGB")


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Source folder not found: {SOURCE}")

    OUT_BG.mkdir(parents=True, exist_ok=True)
    OUT_HUMAN.mkdir(parents=True, exist_ok=True)

    files = sorted(
        p for p in SOURCE.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )
    total = len(files)
    print(f"Processing {total} images from {SOURCE.name}")

    done = 0
    for i, path in enumerate(files, 1):
        out_name = path.stem + ".jpg"
        out_path = OUT_BG / out_name
        if out_path.exists() and out_path.stat().st_size > 30_000:
            done += 1
            print(f"  [{i}/{total}] SKIP background/{out_name}")
            continue
        try:
            with Image.open(path) as img:
                img = img.convert("RGB")
                result = composite_product(img)
                result.save(out_path, "JPEG", quality=92, optimize=True)
        except Exception as exc:
            print(f"  [{i}/{total}] FAIL {path.name}: {exc}")
            continue
        done += 1
        print(f"  [{i}/{total}] OK background/{out_name}")

    # humanpic: create README placeholder - model shots need separate AI workflow
    readme = OUT_HUMAN / "README.txt"
    readme.write_text(
        "Model/lifestyle shots (Indian boy/girl wearing each outfit) require AI virtual try-on\n"
        "or a photoshoot. Background-processed product images are in ../background/.\n"
        "Run scripts/generate_lifestyle_batch.py when an image API key is configured.\n",
        encoding="utf-8",
    )
    print(f"\nDone. Background images: {OUT_BG}")
    print(f"Human model folder ready: {OUT_HUMAN}")


if __name__ == "__main__":
    main()
