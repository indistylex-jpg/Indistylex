"""
Indistylex Brand Asset Generator v2
Generates logo, icons, covers, banners for website + all social platforms.
Brand: Primary #1E4D8C | Accent #2563EB | Light #DBEAFE | BG #EFF6FF
Run: python generate_assets.py
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

PRIMARY = (30, 77, 140)
PRIMARY_DARK = (15, 45, 90)
ACCENT = (37, 99, 235)
ACCENT_BRIGHT = (59, 130, 246)
ACCENT_LIGHT = (219, 234, 254)
WHITE = (255, 255, 255)
SLATE = (100, 116, 139)
LIGHT_BG = (239, 246, 255)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_BRAND_DIR = os.path.join(
    os.path.dirname(OUTPUT_DIR), '..', 'Indistylex', 'app', 'static', 'images', 'brand'
)
SITE_BRAND_DIR = os.path.normpath(SITE_BRAND_DIR)

TAGLINE = 'Premium Kids Fashion'
WEBSITE = 'indistylex.com'
FEATURES = ['Ages 0–18 Years', 'Free Shipping ₹999+', 'Easy Returns & COD']


def get_font(size, bold=False):
    paths = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return int(a * (1 - t) + b * t)


def gradient_image(w, h, c1, c2, c3=None, direction='diag'):
    img = Image.new('RGB', (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            if direction == 'diag':
                t = (x / max(w - 1, 1) + y / max(h - 1, 1)) / 2
            elif direction == 'h':
                t = x / max(w - 1, 1)
            else:
                t = y / max(h - 1, 1)
            if c3 and t > 0.5:
                t2 = (t - 0.5) * 2
                r = lerp(c2[0], c3[0], t2)
                g = lerp(c2[1], c3[1], t2)
                b = lerp(c2[2], c3[2], t2)
            else:
                t2 = t * 2 if c3 else t
                r = lerp(c1[0], c2[0], min(t2, 1))
                g = lerp(c1[1], c2[1], min(t2, 1))
                b = lerp(c1[2], c2[2], min(t2, 1))
            px[x, y] = (r, g, b)
    return img


def draw_soft_circles(draw, w, h):
    """Decorative background blobs."""
    blobs = [
        (w * 0.85, h * 0.15, 120, ACCENT_BRIGHT, 25),
        (w * 0.1, h * 0.75, 90, ACCENT, 18),
        (w * 0.7, h * 0.8, 70, ACCENT_LIGHT, 12),
    ]
    for cx, cy, r, color, alpha in blobs:
        for i in range(r, 0, -2):
            a = int(alpha * (i / r))
            c = tuple(lerp(color[j], PRIMARY[j], 0.3) for j in range(3))
            draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=c + (a,) if False else c)


def draw_shirt_icon(draw, cx, cy, size):
    """Minimal kids tee silhouette for the brand mark."""
    s = size * 0.36
    body = [
        (cx - s * 0.55, cy - s * 0.15),
        (cx - s * 0.95, cy - s * 0.75),
        (cx - s * 0.35, cy - s * 1.05),
        (cx, cy - s * 0.55),
        (cx + s * 0.35, cy - s * 1.05),
        (cx + s * 0.95, cy - s * 0.75),
        (cx + s * 0.55, cy - s * 0.15),
        (cx + s * 0.55, cy + s * 1.05),
        (cx - s * 0.55, cy + s * 1.05),
    ]
    draw.polygon(body, fill=WHITE)
    draw.line(
        [(cx - s * 0.28, cy - s * 0.35), (cx, cy - s * 0.05), (cx + s * 0.28, cy - s * 0.35)],
        fill=ACCENT_LIGHT,
        width=max(2, int(size * 0.04)),
    )


def draw_logo_mark(draw, x, y, size, with_shadow=False):
    """Gradient rounded-square kids tee mark."""
    r = size // 4
    if with_shadow:
        draw.rounded_rectangle(
            [x + 3, y + 4, x + size + 3, y + size + 4],
            radius=r, fill=(15, 45, 90)
        )
    steps = 8
    for i in range(steps):
        t = i / (steps - 1)
        c = (lerp(PRIMARY[0], ACCENT_BRIGHT[0], t),
             lerp(PRIMARY[1], ACCENT_BRIGHT[1], t),
             lerp(PRIMARY[2], ACCENT_BRIGHT[2], t))
        inset = i * 2
        if inset < size // 2:
            draw.rounded_rectangle(
                [x + inset // 2, y + inset // 2,
                 x + size - inset // 2, y + size - inset // 2],
                radius=max(r - inset // 4, 4), fill=c
            )
    draw.rounded_rectangle([x, y, x + size, y + size], radius=r, outline=ACCENT_LIGHT, width=max(1, size // 40))
    draw_shirt_icon(draw, x + size // 2, y + size // 2 + size // 16, size)


def draw_brand_row(draw, x, y, mark_size, wordmark_size, light=False):
    """Icon + Indistylex wordmark."""
    draw_logo_mark(draw, x, y, mark_size, with_shadow=not light)
    wx = x + mark_size + mark_size // 4
    color = WHITE if light else PRIMARY
    sub_color = ACCENT_LIGHT if light else ACCENT
    tag_color = ACCENT_LIGHT if light else SLATE

    font = get_font(wordmark_size, bold=True)
    draw.text((wx, y + mark_size // 8), 'INDISTYLEX', fill=color, font=font)
    bbox = draw.textbbox((wx, y), 'INDISTYLEX', font=font)
    draw.rounded_rectangle([wx, bbox[3] + 2, wx + wordmark_size * 2.2, bbox[3] + 6], radius=2, fill=sub_color)
    font_tag = get_font(max(12, wordmark_size // 3))
    draw.text((wx, bbox[3] + 10), TAGLINE.upper(), fill=tag_color, font=font_tag)


def brand_background(w, h, style='cover'):
    img = gradient_image(w, h, PRIMARY_DARK, PRIMARY, ACCENT, 'diag')
    draw = ImageDraw.Draw(img)
    # Subtle grid
    for i in range(0, w + h, 70):
        draw.line([(i, 0), (i - h, h)], fill=(255, 255, 255), width=1)
    # Top/bottom accent bars
    draw.rectangle([0, 0, w, 5], fill=ACCENT)
    draw.rectangle([0, h - 5, w, h], fill=ACCENT_BRIGHT)
    if style == 'cover':
        draw.ellipse([w - 200, -60, w + 60, 200], fill=(37, 99, 235))
        draw.ellipse([-80, h - 180, 180, h + 40], fill=(30, 77, 140))
    return img, draw


def save(name, img, also_site=True):
    path = os.path.join(OUTPUT_DIR, name)
    if img.mode == 'RGBA':
        img.save(path, 'PNG', optimize=True)
    else:
        img.save(path, 'PNG', quality=95, optimize=True)
    print(f'  ✓ {path}')
    if also_site and os.path.isdir(os.path.dirname(SITE_BRAND_DIR)):
        os.makedirs(SITE_BRAND_DIR, exist_ok=True)
        site_path = os.path.join(SITE_BRAND_DIR, name)
        img.save(site_path, 'PNG', quality=95 if img.mode != 'RGBA' else None, optimize=True)
    return path


# ── LOGOS & ICONS ──────────────────────────────────────────────────

def generate_profile_logo():
    """720×720 — Google Business, Meta page profile."""
    size = 720
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)
    # Soft bg circle
    draw.ellipse([40, 40, size - 40, size - 40], fill=LIGHT_BG)
    draw.ellipse([60, 60, size - 60, size - 60], outline=ACCENT_LIGHT, width=3)
    draw_logo_mark(draw, (size - 260) // 2, 160, 260)
    font = get_font(64, bold=True)
    text = 'Indistylex'
    bbox = draw.textbbox((0, 0), text, font=font)
    tx = (size - (bbox[2] - bbox[0])) // 2
    draw.text((tx, 450), text, fill=PRIMARY, font=font)
    draw.line([(size // 2 - 90, 530), (size // 2 + 90, 530)], fill=ACCENT, width=4)
    font_t = get_font(24)
    tag = TAGLINE
    bbox = draw.textbbox((0, 0), tag, font=font_t)
    draw.text(((size - (bbox[2] - bbox[0])) // 2, 548), tag, fill=SLATE, font=font_t)
    font_u = get_font(22, bold=True)
    draw.text(((size - 180) // 2, 600), WEBSITE, fill=ACCENT, font=font_u)
    save('logo-720x720-profile.png', img)


def generate_logo_transparent():
    """500×500 transparent — overlays, WhatsApp stickers."""
    size = 500
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_logo_mark(draw, 175, 80, 150)
    font = get_font(46, bold=True)
    text = 'Indistylex'
    bbox = draw.textbbox((0, 0), text, font=font)
    tx = (size - (bbox[2] - bbox[0])) // 2
    draw.text((tx, 260), text, fill=PRIMARY + (255,), font=font)
    draw.line([(size // 2 - 55, 320), (size // 2 + 55, 320)], fill=ACCENT + (255,), width=3)
    font_t = get_font(18)
    tag = TAGLINE
    bbox = draw.textbbox((0, 0), tag, font=font_t)
    draw.text(((size - (bbox[2] - bbox[0])) // 2, 335), tag, fill=SLATE + (255,), font=font_t)
    save('logo-transparent-500x500.png', img)


def generate_logo_horizontal():
    """800×200 — email signatures, invoices."""
    w, h = 800, 200
    img = Image.new('RGB', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, w, h], radius=0, fill=LIGHT_BG)
    draw_brand_row(draw, 30, 40, 100, 52, light=False)
    save('logo-horizontal-800x200.png', img)


def generate_favicon_png(size, name):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = max(2, size // 16)
    mark = size - pad * 2
    draw_logo_mark(draw, pad, pad, mark)
    save(name, img)


def generate_apple_touch_icon():
    size = 180
    img = Image.new('RGB', (size, size), LIGHT_BG)
    draw = ImageDraw.Draw(img)
    draw_logo_mark(draw, 30, 30, 120)
    save('apple-touch-icon-180x180.png', img)


def generate_site_manifest():
    manifest = """{
  "name": "Indistylex",
  "short_name": "Indistylex",
  "description": "Premium kids fashion — ages 0–18",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#EFF6FF",
  "theme_color": "#1E4D8C",
  "icons": [
    {
      "src": "/static/images/brand/favicon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/images/brand/apple-touch-icon-180x180.png",
      "sizes": "180x180",
      "type": "image/png"
    }
  ]
}
"""
    path = os.path.join(SITE_BRAND_DIR, 'site.webmanifest')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(manifest)
    print(f'  ✓ {path}')


# ── SOCIAL COVERS ──────────────────────────────────────────────────

def generate_facebook_cover():
    w, h = 820, 312
    img, draw = brand_background(w, h)
    draw_brand_row(draw, 40, 60, 70, 32, light=True)
    font = get_font(20)
    draw.text((40, 175), '  |  '.join(FEATURES[:3]), fill=ACCENT_LIGHT, font=font)
    font_u = get_font(22, bold=True)
    draw.text((40, 240), WEBSITE, fill=WHITE, font=font_u)
    # Right badge
    bx = w - 150
    draw.rounded_rectangle([bx, 70, w - 40, h - 70], radius=12, outline=ACCENT_LIGHT, width=2)
    font_ix = get_font(52, bold=True)
    draw.text((bx + 35, 110), 'iX', fill=WHITE, font=font_ix)
    save('facebook-cover-820x312.png', img)


def generate_google_cover():
    w, h = 1080, 608
    img, draw = brand_background(w, h)
    draw_brand_row(draw, 60, 50, 90, 40, light=True)
    font = get_font(44, bold=True)
    draw.text((60, 200), TAGLINE, fill=WHITE, font=font)
    draw.line([(60, 265), (340, 265)], fill=ACCENT_LIGHT, width=3)
    font_s = get_font(26)
    draw.text((60, 285), 'Style That Speaks · Quality That Lasts', fill=ACCENT_LIGHT, font=font_s)
    for i, feat in enumerate(FEATURES):
        draw.text((80, 360 + i * 42), f'✦  {feat}', fill=WHITE, font=get_font(22))
    draw.text((60, 530), WEBSITE, fill=ACCENT_LIGHT, font=get_font(30, bold=True))
    save('google-cover-1080x608.png', img)


def generate_linkedin_cover():
    w, h = 1584, 396
    img, draw = brand_background(w, h)
    draw_brand_row(draw, 80, 80, 80, 36, light=True)
    font = get_font(36, bold=True)
    draw.text((80, 220), f'{TAGLINE}  ·  Boys & Girls 0–18', fill=WHITE, font=font)
    draw.text((80, 290), WEBSITE, fill=ACCENT_LIGHT, font=get_font(24, bold=True))
    save('linkedin-cover-1584x396.png', img)


def generate_twitter_header():
    w, h = 1500, 500
    img, draw = brand_background(w, h)
    draw_brand_row(draw, 80, 120, 100, 44, light=True)
    font = get_font(32)
    draw.text((80, 320), '  ·  '.join(FEATURES), fill=ACCENT_LIGHT, font=font)
    save('twitter-header-1500x500.png', img)


def generate_youtube_banner():
    w, h = 2560, 1440
    img, draw = brand_background(w, h)
    sx, sy = (w - 1546) // 2, (h - 423) // 2
    draw.rectangle([0, sy - 3, w, sy], fill=ACCENT)
    draw.rectangle([0, sy + 423, w, sy + 426], fill=ACCENT_BRIGHT)
    draw_brand_row(draw, sx + 60, sy + 70, 110, 48, light=True)
    font = get_font(26)
    draw.text((sx + 60, sy + 280), f'{TAGLINE}  |  {WEBSITE}', fill=ACCENT_LIGHT, font=font)
    for i, feat in enumerate(FEATURES):
        fx, fy = sx + 1100, sy + 100 + i * 55
        draw.rounded_rectangle([fx, fy, fx + 260, fy + 42], radius=21, outline=ACCENT_LIGHT, width=2)
        draw.text((fx + 18, fy + 8), feat, fill=WHITE, font=get_font(20))
    save('youtube-banner-2560x1440.png', img)


def generate_instagram_profile():
    size = 400
    img = gradient_image(size, size, PRIMARY, ACCENT, ACCENT_BRIGHT, 'diag')
    draw = ImageDraw.Draw(img)
    draw.ellipse([20, 20, size - 20, size - 20], outline=WHITE, width=4)
    draw.ellipse([35, 35, size - 35, size - 35], outline=ACCENT_LIGHT, width=2)
    draw_logo_mark(draw, 100, 90, 200)
    save('instagram-profile-400x400.png', img)


def generate_whatsapp_profile():
    size = 640
    img = gradient_image(size, size, PRIMARY_DARK, PRIMARY, ACCENT, 'diag')
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([15, 15, size - 15, size - 15], radius=24, outline=ACCENT_LIGHT, width=3)
    draw_logo_mark(draw, (size - 220) // 2, 120, 220)
    font = get_font(46, bold=True)
    text = 'Indistylex'
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text(((size - (bbox[2] - bbox[0])) // 2, 370), text, fill=WHITE, font=font)
    draw.line([(size // 2 - 70, 435), (size // 2 + 70, 435)], fill=ACCENT_LIGHT, width=2)
    font_t = get_font(20)
    tag = TAGLINE
    bbox = draw.textbbox((0, 0), tag, font=font_t)
    draw.text(((size - (bbox[2] - bbox[0])) // 2, 455), tag, fill=ACCENT_LIGHT, font=font_t)
    save('whatsapp-profile-640x640.png', img)


def generate_pinterest_pin():
    w, h = 1000, 1500
    img, draw = brand_background(w, h, 'cover')
    draw_brand_row(draw, 60, 60, 80, 36, light=True)
    draw.rounded_rectangle([60, 280, w - 60, 900], radius=16, fill=(24, 58, 108), outline=ACCENT_LIGHT, width=2)
    font = get_font(28)
    draw.text((120, 560), '[ Product Photo Here ]', fill=SLATE, font=font)
    draw.text((60, 960), 'NEW ARRIVAL', fill=ACCENT_LIGHT, font=get_font(40, bold=True))
    draw.text((60, 1030), 'Starting ₹499', fill=WHITE, font=get_font(52, bold=True))
    draw.text((60, 1120), f'Shop at {WEBSITE}', fill=ACCENT_LIGHT, font=get_font(24))
    save('pinterest-pin-1000x1500.png', img)


# ── WEBSITE & ADS ──────────────────────────────────────────────────

def generate_website_banner():
    """1920×600 homepage / hero marketing banner."""
    w, h = 1920, 600
    img, draw = brand_background(w, h)
    draw_brand_row(draw, 100, 120, 120, 56, light=True)
    font = get_font(56, bold=True)
    draw.text((100, 300), TAGLINE, fill=WHITE, font=font)
    font_s = get_font(28)
    draw.text((100, 380), 'Boys & Girls · Newborn to Teens · Pan-India Delivery', fill=ACCENT_LIGHT, font=font_s)
    draw.rounded_rectangle([100, 460, 340, 530], radius=8, fill=ACCENT)
    draw.text((145, 478), 'SHOP NOW', fill=WHITE, font=get_font(26, bold=True))
    draw.text((360, 490), WEBSITE, fill=WHITE, font=get_font(24, bold=True))
    save('website-banner-1920x600.png', img)


def generate_og_share():
    """1200×630 Open Graph / WhatsApp link preview."""
    w, h = 1200, 630
    img, draw = brand_background(w, h)
    draw_brand_row(draw, 80, 160, 110, 50, light=True)
    font = get_font(48, bold=True)
    draw.text((80, 340), TAGLINE, fill=WHITE, font=font)
    draw.text((80, 420), 'Free Shipping · Easy Returns · COD Available', fill=ACCENT_LIGHT, font=get_font(26))
    draw.text((80, 530), WEBSITE, fill=WHITE, font=get_font(32, bold=True))
    save('og-share-1200x630.png', img)


def generate_email_header():
    w, h = 600, 200
    img, draw = brand_background(w, h)
    draw_brand_row(draw, 24, 40, 70, 28, light=True)
    save('email-header-600x200.png', img)


def generate_instagram_story():
    w, h = 1080, 1920
    img, draw = brand_background(w, h)
    draw_brand_row(draw, 40, 50, 65, 26, light=True)
    draw.rounded_rectangle([50, 350, w - 50, 1150], radius=16, fill=(20, 50, 95), outline=ACCENT_LIGHT, width=2)
    draw.text((200, 720), '[ Product Image ]', fill=SLATE, font=get_font(32))
    draw.text((50, 1250), 'NEW ARRIVAL', fill=ACCENT_LIGHT, font=get_font(40, bold=True))
    draw.text((50, 1320), 'Starting ₹499', fill=WHITE, font=get_font(56, bold=True))
    draw.text((50, 1410), f'Shop · {WEBSITE}', fill=ACCENT_LIGHT, font=get_font(26))
    save('instagram-story-1080x1920.png', img)


def generate_ad_square():
    size = 1080
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, size, 110], fill=PRIMARY)
    draw.rectangle([0, 107, size, 110], fill=ACCENT)
    draw_logo_mark(draw, 28, 18, 74)
    draw.text((120, 42), 'Indistylex', fill=WHITE, font=get_font(30, bold=True))
    draw.rounded_rectangle([50, 140, size - 50, 760], radius=12, fill=LIGHT_BG, outline=ACCENT_LIGHT, width=1)
    draw.text((280, 430), '[ Product Image Here ]', fill=SLATE, font=get_font(28))
    draw.text((60, 810), 'Product Name', fill=PRIMARY, font=get_font(34, bold=True))
    draw.text((60, 870), '₹499', fill=PRIMARY, font=get_font(42, bold=True))
    draw.text((190, 878), '₹999', fill=SLATE, font=get_font(28))
    draw.line([(190, 895), (280, 895)], fill=SLATE, width=2)
    draw.rounded_rectangle([60, 960, 300, 1020], radius=8, fill=ACCENT)
    draw.text((95, 975), 'SHOP NOW', fill=WHITE, font=get_font(22, bold=True))
    draw.rounded_rectangle([size - 200, 810, size - 60, 860], radius=6, fill=PRIMARY)
    draw.text((size - 178, 822), '50% OFF', fill=WHITE, font=get_font(20, bold=True))
    save('ad-square-1080x1080.png', img)


def generate_sale_banner():
    w, h = 1200, 628
    img, draw = brand_background(w, h)
    draw.text((60, 70), 'MEGA SALE', fill=ACCENT_LIGHT, font=get_font(52, bold=True))
    draw.text((60, 150), '50% OFF', fill=WHITE, font=get_font(96, bold=True))
    draw.line([(60, 280), (360, 280)], fill=ACCENT_LIGHT, width=3)
    draw.text((60, 300), 'On All Kids Fashion', fill=WHITE, font=get_font(30))
    draw.text((60, 345), 'Boys & Girls · Ages 0–18', fill=ACCENT_LIGHT, font=get_font(24))
    draw.rounded_rectangle([60, 420, 310, 490], radius=8, outline=WHITE, width=2)
    draw.text((105, 440), 'SHOP NOW', fill=WHITE, font=get_font(24, bold=True))
    draw.text((60, h - 60), WEBSITE, fill=ACCENT_LIGHT, font=get_font(22, bold=True))
    draw.rounded_rectangle([w - 300, 80, w - 60, h - 80], radius=12, outline=ACCENT_LIGHT, width=2)
    draw_logo_mark(draw, w - 250, 180, 140)
    save('sale-banner-1200x628.png', img)


def generate_readme():
    lines = [
        '# Indistylex Brand Assets',
        '',
        'Generated by `generate_assets.py`. Brand colors: `#1E4D8C` · `#2563EB` · `#DBEAFE`',
        '',
        '## Logos & Icons',
        '| File | Size | Use for |',
        '|------|------|---------|',
        '| logo-720x720-profile.png | 720×720 | Google Business, Facebook page photo |',
        '| logo-transparent-500x500.png | 500×500 | Overlays, presentations |',
        '| logo-horizontal-800x200.png | 800×200 | Email signature, invoices |',
        '| favicon-192x192.png | 192×192 | PWA, Android |',
        '| favicon-32x32.png | 32×32 | Browser tab |',
        '| apple-touch-icon-180x180.png | 180×180 | iPhone home screen |',
        '',
        '## Social Covers',
        '| File | Platform |',
        '|------|----------|',
        '| facebook-cover-820x312.png | Facebook page cover |',
        '| google-cover-1080x608.png | Google Business cover |',
        '| instagram-profile-400x400.png | Instagram profile photo |',
        '| whatsapp-profile-640x640.png | WhatsApp Business profile |',
        '| youtube-banner-2560x1440.png | YouTube channel art |',
        '| linkedin-cover-1584x396.png | LinkedIn company page |',
        '| twitter-header-1500x500.png | X (Twitter) header |',
        '| pinterest-pin-1000x1500.png | Pinterest pin template |',
        '',
        '## Website & Ads',
        '| File | Use for |',
        '|------|---------|',
        '| website-banner-1920x600.png | Homepage hero, ads |',
        '| og-share-1200x630.png | WhatsApp/FB link preview |',
        '| email-header-600x200.png | Email newsletters |',
        '| instagram-story-1080x1920.png | Instagram/Facebook stories |',
        '| ad-square-1080x1080.png | Meta/Instagram feed ads |',
        '| sale-banner-1200x628.png | Facebook/Google display ads |',
        '',
        'Website SVG logos: `Indistylex/app/static/images/logo.svg`, `favicon.svg`, `logo-white.svg`',
    ]
    path = os.path.join(OUTPUT_DIR, 'ASSETS-README.md')
    with open(path, 'w') as f:
        f.write('\n'.join(lines))
    print(f'  ✓ {path}')


if __name__ == '__main__':
    print('=' * 56)
    print('  INDISTYLEX Brand Asset Generator v2')
    print('=' * 56)
    print(f'\nOutput: {OUTPUT_DIR}')
    print(f'Site copy: {SITE_BRAND_DIR}\n')

    print('Logos & Icons:')
    generate_profile_logo()
    generate_logo_transparent()
    generate_logo_horizontal()
    generate_favicon_png(192, 'favicon-192x192.png')
    generate_favicon_png(32, 'favicon-32x32.png')
    generate_favicon_png(16, 'favicon-16x16.png')
    generate_apple_touch_icon()
    generate_site_manifest()

    print('\nSocial Covers:')
    generate_facebook_cover()
    generate_google_cover()
    generate_linkedin_cover()
    generate_twitter_header()
    generate_youtube_banner()
    generate_instagram_profile()
    generate_whatsapp_profile()
    generate_pinterest_pin()

    print('\nWebsite & Ads:')
    generate_website_banner()
    generate_og_share()
    generate_email_header()
    generate_instagram_story()
    generate_ad_square()
    generate_sale_banner()

    print('\nDocumentation:')
    generate_readme()

    print('\n' + '=' * 56)
    print('  ALL 20 ASSETS GENERATED ✓')
    print('=' * 56)
