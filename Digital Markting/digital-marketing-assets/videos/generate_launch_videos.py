#!/usr/bin/env python3
"""Generate Indistylex Coming Soon & Launch Date promo videos."""

from __future__ import annotations

import math
import os
from pathlib import Path

import imageio.v3 as iio
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Brand colors
BLACK = (26, 26, 26)
GOLD = (201, 169, 78)
GOLD_LIGHT = (220, 190, 110)
WHITE = (255, 255, 255)
MUTED = (180, 180, 180)

BASE_DIR = Path(__file__).parent
FONTS_DIR = BASE_DIR / "fonts"
OUTPUT_DIR = BASE_DIR / "output"

FPS = 30
DURATION = 8  # seconds


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONTS_DIR / name
    return ImageFont.truetype(str(path), size)


def ease_out_cubic(t: float) -> float:
    return 1 - pow(1 - t, 3)


def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


def fit_background(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Cover-fit background image to target size."""
    target_w, target_h = size
    src = img.convert("RGB")
    sw, sh = src.size
    scale = max(target_w / sw, target_h / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - target_w) // 2
    top = (nh - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def draw_gold_line(draw: ImageDraw.ImageDraw, x1: int, y: int, x2: int, alpha: int = 255):
    color = (*GOLD[:2], GOLD[2])
    draw.line([(x1, y), (x2, y)], fill=(*GOLD, alpha) if alpha < 255 else GOLD, width=2)


def draw_monogram(img: Image.Image, cx: int, cy: int, size: int, alpha: int = 255) -> Image.Image:
    """Draw iX monogram overlay."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    half = size // 2
    box = [cx - half, cy - half, cx + half, cy + half]
    draw.rounded_rectangle(box, radius=size // 6, fill=(*BLACK, alpha))
    font = load_font("PlayfairDisplay.ttf", int(size * 0.45))
    text = "iX"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - 4), text, font=font, fill=(*GOLD, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    cx: int,
    cy: int,
    fill: tuple,
    letter_spacing: int = 0,
):
    if letter_spacing == 0:
        tw, th = text_size(draw, text, font)
        draw.text((cx - tw // 2, cy - th // 2), text, font=font, fill=fill)
        return

    total_w = 0
    chars = list(text)
    widths = []
    for ch in chars:
        w, _ = text_size(draw, ch, font)
        widths.append(w)
        total_w += w
    total_w += letter_spacing * (len(chars) - 1)
    _, th = text_size(draw, text, font)
    x = cx - total_w // 2
    y = cy - th // 2
    for ch, w in zip(chars, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + letter_spacing


def add_vignette(img: Image.Image, strength: float = 0.35) -> Image.Image:
    w, h = img.size
    arr = np.array(img.convert("RGB"), dtype=np.float32)
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt(((x - cx) / cx) ** 2 + ((y - cy) / cy) ** 2)
    vignette = 1 - np.clip(dist * strength, 0, 0.55)
    arr *= vignette[:, :, np.newaxis]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def add_shimmer_overlay(size: tuple[int, int], progress: float) -> Image.Image:
    """Subtle gold shimmer sweep."""
    w, h = size
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    sweep_x = int(-w * 0.3 + (w * 1.6) * progress)
    for i in range(0, w // 3, 8):
        x = sweep_x + i
        if 0 <= x < w:
            draw.line([(x, 0), (x + h // 4, h)], fill=(*GOLD_LIGHT, 18), width=3)
    return overlay


def render_coming_soon_frame(
    bg: Image.Image,
    size: tuple[int, int],
    frame_idx: int,
    total_frames: int,
) -> Image.Image:
    t = frame_idx / max(total_frames - 1, 1)
    zoom = 1.0 + 0.06 * ease_in_out_sine(t)
    w, h = size

    base = fit_background(bg, (int(w * zoom), int(h * zoom)))
    left = (base.width - w) // 2
    top = (base.height - h) // 2
    frame = base.crop((left, top, left + w, top + h))
    frame = add_vignette(frame, 0.3)
    img = frame.convert("RGBA")

    # Dark overlay for text readability
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([(0, 0), (w, h)], fill=(0, 0, 0, 60))
    img = Image.alpha_composite(img, overlay)

    fade_main = ease_out_cubic(min(1.0, t * 2.5))
    fade_sub = ease_out_cubic(max(0, min(1.0, (t - 0.15) * 2.5)))
    fade_cta = ease_out_cubic(max(0, min(1.0, (t - 0.35) * 2.5)))

    is_vertical = h > w
    mono_y = int(h * (0.22 if is_vertical else 0.28))
    img = draw_monogram(img, w // 2, mono_y, int(w * 0.14), int(255 * fade_main))

    draw = ImageDraw.Draw(img)
    title_font = load_font("PlayfairDisplay.ttf", int(w * 0.09))
    sub_font = load_font("Inter.ttf", int(w * 0.028))
    small_font = load_font("Inter.ttf", int(w * 0.022))

    title_alpha = int(255 * fade_main)
    sub_alpha = int(255 * fade_sub)
    cta_alpha = int(255 * fade_cta)

    title_y = int(h * 0.48)
    draw_centered_text(
        draw, "COMING SOON", title_font, w // 2, title_y,
        (*GOLD, title_alpha), letter_spacing=6,
    )

    line_w = int(w * 0.18 * fade_sub)
    line_y = title_y + int(w * 0.07)
    if line_w > 0:
        draw.line(
            [(w // 2 - line_w // 2, line_y), (w // 2 + line_w // 2, line_y)],
            fill=(*GOLD, sub_alpha), width=2,
        )

    tagline = "Style That Speaks, Quality That Lasts"
    draw_centered_text(
        draw, tagline, sub_font, w // 2, int(h * 0.58),
        (*WHITE, sub_alpha),
    )

    draw_centered_text(
        draw, "INDISTYLEX", load_font("PlayfairDisplay.ttf", int(w * 0.055)),
        w // 2, int(h * 0.68), (*WHITE, sub_alpha), letter_spacing=8,
    )

    draw_centered_text(
        draw, "Premium Kids Fashion  •  indistylex.com", small_font,
        w // 2, int(h * 0.78), (*MUTED, cta_alpha),
    )

    shimmer = add_shimmer_overlay(size, (t * 1.5) % 1.0)
    img = Image.alpha_composite(img, shimmer)

    return img.convert("RGB")


def render_launch_frame(
    bg: Image.Image,
    size: tuple[int, int],
    frame_idx: int,
    total_frames: int,
) -> Image.Image:
    t = frame_idx / max(total_frames - 1, 1)
    zoom = 1.0 + 0.05 * ease_in_out_sine(t)
    w, h = size

    base = fit_background(bg, (int(w * zoom), int(h * zoom)))
    left = (base.width - w) // 2
    top = (base.height - h) // 2
    frame = base.crop((left, top, left + w, top + h))
    frame = add_vignette(frame, 0.28)
    img = frame.convert("RGBA")

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([(0, 0), (w, h)], fill=(0, 0, 0, 50))
    img = Image.alpha_composite(img, overlay)

    fade1 = ease_out_cubic(min(1.0, t * 2.2))
    fade2 = ease_out_cubic(max(0, min(1.0, (t - 0.12) * 2.2)))
    fade3 = ease_out_cubic(max(0, min(1.0, (t - 0.28) * 2.2)))
    fade4 = ease_out_cubic(max(0, min(1.0, (t - 0.42) * 2.2)))

    is_vertical = h > w
    img = draw_monogram(img, w // 2, int(h * 0.16), int(w * 0.11), int(255 * fade1))

    draw = ImageDraw.Draw(img)
    label_font = load_font("Inter.ttf", int(w * 0.026))
    date_font = load_font("PlayfairDisplay.ttf", int(w * 0.11))
    day_font = load_font("PlayfairDisplay.ttf", int(w * 0.055))
    sub_font = load_font("Inter.ttf", int(w * 0.028))
    small_font = load_font("Inter.ttf", int(w * 0.022))

    draw_centered_text(
        draw, "WE'RE LAUNCHING", label_font, w // 2, int(h * 0.34),
        (*GOLD, int(255 * fade1)), letter_spacing=4,
    )

    # Pulsing gold glow behind date
    pulse = 0.85 + 0.15 * math.sin(t * math.pi * 4)
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    glow_r = int(w * 0.22 * pulse * fade2)
    gd.ellipse(
        [w // 2 - glow_r, int(h * 0.44) - glow_r // 2, w // 2 + glow_r, int(h * 0.44) + glow_r // 2],
        fill=(*GOLD, int(30 * fade2)),
    )
    img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img)
    draw_centered_text(
        draw, "July 10", date_font, w // 2, int(h * 0.44),
        (*WHITE, int(255 * fade2)),
    )
    draw_centered_text(
        draw, "2026", day_font, w // 2, int(h * 0.52),
        (*GOLD, int(255 * fade3)),
    )
    draw_centered_text(
        draw, "FRIDAY", label_font, w // 2, int(h * 0.58),
        (*WHITE, int(255 * fade3)), letter_spacing=6,
    )

    line_w = int(w * 0.22 * fade3)
    if line_w > 0:
        draw.line(
            [(w // 2 - line_w // 2, int(h * 0.63)), (w // 2 + line_w // 2, int(h * 0.63))],
            fill=(*GOLD, int(255 * fade3)), width=2,
        )

    draw_centered_text(
        draw, "INDISTYLEX", load_font("PlayfairDisplay.ttf", int(w * 0.06)),
        w // 2, int(h * 0.70), (*WHITE, int(255 * fade3)), letter_spacing=8,
    )
    draw_centered_text(
        draw, "Premium Kids Fashion is Almost Here", sub_font,
        w // 2, int(h * 0.78), (*MUTED, int(255 * fade4)),
    )
    draw_centered_text(
        draw, "indistylex.com", small_font, w // 2, int(h * 0.84),
        (*GOLD, int(255 * fade4)),
    )

    shimmer = add_shimmer_overlay(size, (t * 1.2 + 0.3) % 1.0)
    img = Image.alpha_composite(img, shimmer)

    return img.convert("RGB")


def create_video(
    name: str,
    bg_path: Path,
    size: tuple[int, int],
    render_fn,
    duration: int = DURATION,
):
    bg = Image.open(bg_path)
    total_frames = FPS * duration
    frames = []

    print(f"  Rendering {name} ({size[0]}x{size[1]}, {duration}s)...")
    for i in range(total_frames):
        frames.append(np.array(render_fn(bg, size, i, total_frames)))

    out_path = OUTPUT_DIR / name
    iio.imwrite(
        out_path,
        frames,
        fps=FPS,
        codec="libx264",
        pixelformat="yuv420p",
        output_params=["-crf", "18", "-preset", "medium"],
        extension=".mp4",
    )
    print(f"  ✓ Saved: {out_path} ({out_path.stat().st_size // 1024} KB)")
    return out_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    configs = [
        ("coming-soon-reel.mp4", "coming-soon-bg-vertical.png", (1080, 1920), render_coming_soon_frame),
        ("coming-soon-square.mp4", "coming-soon-bg-square.png", (1080, 1080), render_coming_soon_frame),
        ("coming-soon-landscape.mp4", "coming-soon-bg-square.png", (1920, 1080), render_coming_soon_frame),
        ("launch-date-reel.mp4", "launch-date-bg-vertical.png", (1080, 1920), render_launch_frame),
        ("launch-date-square.mp4", "launch-date-bg-square.png", (1080, 1080), render_launch_frame),
        ("launch-date-landscape.mp4", "launch-date-bg-square.png", (1920, 1080), render_launch_frame),
    ]

    print("Indistylex Launch Video Generator")
    print("=" * 40)
    for name, bg_file, size, fn in configs:
        create_video(name, BASE_DIR / bg_file, size, fn)

    print("\nAll videos generated in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
