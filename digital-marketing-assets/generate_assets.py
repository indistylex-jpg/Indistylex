"""
Digital Marketing Asset Generator for Indistylex
Generates all social media images: logos, covers, banners, and profile pictures.
Brand Colors: Primary #1A1A1A (Black), Accent #C8A962 (Gold), White #FFFFFF
Design: Ultra-clean luxury — black, white, gold, minimal
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Brand Colors (matching website)
PRIMARY = (26, 26, 26)        # #1A1A1A Black
SECONDARY = (107, 114, 128)   # #6B7280 Muted gray
ACCENT = (200, 169, 98)       # #C8A962 Gold
WHITE = (255, 255, 255)
DARK = (26, 26, 26)           # #1A1A1A Black
LIGHT_BG = (249, 249, 249)    # #F9F9F9 Off-white

# Output directory
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_font(size, bold=False):
    """Try to get a good font, fall back to default."""
    font_paths = [
        "C:/Windows/Fonts/georgiabd.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def create_gradient(width, height, color1, color2, direction='horizontal'):
    """Create a gradient image."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            if direction == 'horizontal':
                ratio = x / width
            elif direction == 'vertical':
                ratio = y / height
            else:  # diagonal
                ratio = (x + y) / (width + height)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pixels[x, y] = (r, g, b)
    return img


def draw_logo_mark(draw, x, y, size):
    """Draw the iX logo mark — black square with gold iX."""
    # Rounded rectangle background
    rect_size = size
    draw.rounded_rectangle(
        [x, y, x + rect_size, y + rect_size],
        radius=size // 5,
        fill=PRIMARY
    )
    # "iX" text in gold
    font_size = int(size * 0.55)
    font = get_font(font_size, bold=True)
    text = "iX"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x + (rect_size - tw) // 2
    ty = y + (rect_size - th) // 2 - size // 10
    draw.text((tx, ty), text, fill=ACCENT, font=font)
    # Gold underline
    line_y = y + rect_size - size // 6
    line_margin = size // 5
    draw.line([(x + line_margin, line_y), (x + rect_size - line_margin, line_y)], fill=ACCENT, width=max(2, size // 40))


def draw_wordmark(draw, x, y, font_size, color=PRIMARY):
    """Draw 'Indistylex' text."""
    font = get_font(font_size, bold=True)
    draw.text((x, y), "Indistylex", fill=color, font=font)


# ============================================================
# 1. LOGO - Square Profile Picture (720x720)
# ============================================================
def generate_profile_logo():
    """720x720 square logo for Google Business, Meta profile."""
    size = 720
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    # Draw large logo mark centered
    mark_size = 240
    mark_x = (size - mark_size) // 2
    mark_y = size // 4 - 20

    draw_logo_mark(draw, mark_x, mark_y, mark_size)

    # Wordmark below
    font = get_font(72, bold=True)
    text = "Indistylex"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = (size - tw) // 2
    ty = mark_y + mark_size + 50
    draw.text((tx, ty), text, fill=PRIMARY, font=font)

    # Gold accent line under wordmark
    line_w = 80
    line_y = ty + 85
    draw.line([(size // 2 - line_w, line_y), (size // 2 + line_w, line_y)], fill=ACCENT, width=3)

    # Tagline
    font_tag = get_font(26)
    tagline = "Premium Kids Fashion"
    bbox = draw.textbbox((0, 0), tagline, font=font_tag)
    tw = bbox[2] - bbox[0]
    tx = (size - tw) // 2
    ty2 = line_y + 25
    draw.text((tx, ty2), tagline, fill=SECONDARY, font=font_tag)

    path = os.path.join(OUTPUT_DIR, "logo-720x720-profile.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")
    return img


# ============================================================
# 2. GOOGLE BUSINESS COVER (1080x608)
# ============================================================
def generate_google_cover():
    """1080x608 cover for Google Business Profile."""
    width, height = 1080, 608
    img = Image.new('RGB', (width, height), PRIMARY)
    draw = ImageDraw.Draw(img)

    # Subtle diagonal gold lines as texture
    for i in range(0, width + height, 80):
        draw.line([(i, 0), (i - height, height)], fill=(40, 40, 40), width=1)

    # Gold accent bar at top
    draw.rectangle([0, 0, width, 4], fill=ACCENT)

    # Logo mark top-left
    draw_logo_mark(draw, 60, 50, 80)

    # Main headline
    font_main = get_font(52, bold=True)
    draw.text((60, 190), "Premium Kids Fashion", fill=WHITE, font=font_main)

    # Gold accent line
    draw.line([(60, 260), (300, 260)], fill=ACCENT, width=3)

    # Sub headline
    font_sub = get_font(30)
    draw.text((60, 280), "Style That Speaks, Quality That Lasts", fill=ACCENT, font=font_sub)

    # Features
    font_feat = get_font(22)
    features = ["Ages 0-14 Years", "Free Shipping Pan-India", "Easy Returns & COD"]
    for i, feat in enumerate(features):
        fy = 350 + i * 40
        draw.text((80, fy), f"\u2022  {feat}", fill=WHITE, font=font_feat)

    # Website in gold
    font_url = get_font(28, bold=True)
    draw.text((60, 520), "indistylex.com", fill=ACCENT, font=font_url)

    # Gold accent bar at bottom
    draw.rectangle([0, height - 4, width, height], fill=ACCENT)

    path = os.path.join(OUTPUT_DIR, "google-cover-1080x608.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")


# ============================================================
# 3. FACEBOOK COVER (820x312)
# ============================================================
def generate_facebook_cover():
    """820x312 cover for Facebook page."""
    width, height = 820, 312
    img = Image.new('RGB', (width, height), PRIMARY)
    draw = ImageDraw.Draw(img)

    # Gold top line
    draw.rectangle([0, 0, width, 3], fill=ACCENT)

    # Main text
    font_main = get_font(38, bold=True)
    draw.text((40, 50), "Premium Kids Fashion", fill=WHITE, font=font_main)

    # Gold line
    draw.line([(40, 105), (250, 105)], fill=ACCENT, width=2)

    # Tagline
    font_tag = get_font(22)
    draw.text((40, 120), "Style That Speaks, Quality That Lasts", fill=ACCENT, font=font_tag)

    # Features row
    font_feat = get_font(16)
    draw.text((40, 180), "Boys & Girls (0-14 yrs)  |  Free Shipping  |  COD Available", fill=WHITE, font=font_feat)

    # Website
    font_url = get_font(20, bold=True)
    draw.text((40, 255), "indistylex.com", fill=ACCENT, font=font_url)

    # Right side — elegant gold frame
    frame_x = width - 180
    draw.rounded_rectangle([frame_x, 40, width - 40, height - 40], radius=8, outline=ACCENT, width=2)
    font_ix = get_font(48, bold=True)
    draw.text((frame_x + 38, 100), "iX", fill=ACCENT, font=font_ix)
    font_sm = get_font(14)
    draw.text((frame_x + 25, 180), "Since 2024", fill=SECONDARY, font=font_sm)

    # Gold bottom line
    draw.rectangle([0, height - 3, width, height], fill=ACCENT)

    path = os.path.join(OUTPUT_DIR, "facebook-cover-820x312.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")


# ============================================================
# 4. INSTAGRAM PROFILE (400x400)
# ============================================================
def generate_instagram_profile():
    """400x400 square for Instagram profile."""
    size = 400
    img = Image.new('RGB', (size, size), PRIMARY)
    draw = ImageDraw.Draw(img)

    # Gold border circle
    margin = 15
    draw.ellipse([margin, margin, size - margin, size - margin], outline=ACCENT, width=3)

    # iX logo in center
    font = get_font(100, bold=True)
    text = "iX"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2
    ty = (size - th) // 2 - 20
    draw.text((tx, ty), text, fill=ACCENT, font=font)

    # Gold underline
    draw.line([(size // 2 - 40, ty + th + 5), (size // 2 + 40, ty + th + 5)], fill=ACCENT, width=2)

    path = os.path.join(OUTPUT_DIR, "instagram-profile-400x400.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")


# ============================================================
# 5. INSTAGRAM STORY TEMPLATE (1080x1920)
# ============================================================
def generate_instagram_story():
    """1080x1920 story template."""
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height), PRIMARY)
    draw = ImageDraw.Draw(img)

    # Subtle texture lines
    for i in range(0, width + height, 60):
        draw.line([(i, 0), (i - height, height)], fill=(35, 35, 35), width=1)

    # Gold top border
    draw.rectangle([0, 0, width, 4], fill=ACCENT)

    # Top logo
    draw_logo_mark(draw, 40, 60, 70)
    font_brand = get_font(28, bold=True)
    draw.text((130, 78), "Indistylex", fill=WHITE, font=font_brand)

    # Center content area (placeholder box)
    box_y = 400
    box_h = 800
    draw.rounded_rectangle(
        [60, box_y, width - 60, box_y + box_h],
        radius=12,
        fill=(35, 35, 35),
        outline=ACCENT,
        width=2
    )

    # "YOUR PRODUCT HERE" placeholder
    font_ph = get_font(32)
    text = "[ Product Image Here ]"
    bbox = draw.textbbox((0, 0), text, font=font_ph)
    tw = bbox[2] - bbox[0]
    tx = (width - tw) // 2
    ty = box_y + box_h // 2 - 20
    draw.text((tx, ty), text, fill=SECONDARY, font=font_ph)

    # Bottom CTA
    cta_y = 1400
    font_cta = get_font(36, bold=True)
    draw.text((60, cta_y), "NEW ARRIVAL", fill=ACCENT, font=font_cta)

    font_price = get_font(48, bold=True)
    draw.text((60, cta_y + 60), "Starting \u20b9499", fill=WHITE, font=font_price)

    font_swipe = get_font(24)
    draw.text((60, cta_y + 130), "Swipe Up to Shop", fill=SECONDARY, font=font_swipe)

    # Gold line separator
    draw.line([(60, cta_y - 20), (width - 60, cta_y - 20)], fill=ACCENT, width=1)

    # Bottom website
    font_url = get_font(20)
    draw.text((60, height - 80), "indistylex.com", fill=ACCENT, font=font_url)

    # Gold bottom border
    draw.rectangle([0, height - 4, width, height], fill=ACCENT)

    path = os.path.join(OUTPUT_DIR, "instagram-story-1080x1920.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")


# ============================================================
# 6. WHATSAPP BUSINESS PROFILE (640x640)
# ============================================================
def generate_whatsapp_profile():
    """640x640 for WhatsApp Business profile."""
    size = 640
    img = Image.new('RGB', (size, size), PRIMARY)
    draw = ImageDraw.Draw(img)

    # Gold border
    draw.rounded_rectangle([10, 10, size - 10, size - 10], radius=20, outline=ACCENT, width=3)

    # Logo mark centered
    mark_size = 180
    mark_x = (size - mark_size) // 2
    mark_y = size // 3 - 50
    draw_logo_mark(draw, mark_x, mark_y, mark_size)

    # Brand name
    font = get_font(48, bold=True)
    text = "Indistylex"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = (size - tw) // 2
    ty = mark_y + mark_size + 40
    draw.text((tx, ty), text, fill=WHITE, font=font)

    # Gold line
    draw.line([(size // 2 - 60, ty + 60), (size // 2 + 60, ty + 60)], fill=ACCENT, width=2)

    # Tagline
    font_tag = get_font(20)
    tagline = "Premium Kids Fashion"
    bbox = draw.textbbox((0, 0), tagline, font=font_tag)
    tw = bbox[2] - bbox[0]
    tx = (size - tw) // 2
    draw.text((tx, ty + 75), tagline, fill=ACCENT, font=font_tag)

    path = os.path.join(OUTPUT_DIR, "whatsapp-profile-640x640.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")


# ============================================================
# 7. YOUTUBE BANNER (2560x1440)
# ============================================================
def generate_youtube_banner():
    """2560x1440 YouTube channel art (safe area: 1546x423 center)."""
    width, height = 2560, 1440
    img = Image.new('RGB', (width, height), PRIMARY)
    draw = ImageDraw.Draw(img)

    # Subtle texture
    for i in range(0, width + height, 100):
        draw.line([(i, 0), (i - height, height)], fill=(35, 35, 35), width=1)

    # Safe area guide (center 1546x423)
    safe_x = (width - 1546) // 2
    safe_y = (height - 423) // 2

    # Gold accent lines
    draw.rectangle([0, safe_y - 2, width, safe_y], fill=ACCENT)
    draw.rectangle([0, safe_y + 423, width, safe_y + 425], fill=ACCENT)

    # Logo mark
    draw_logo_mark(draw, safe_x + 50, safe_y + 80, 100)

    # Brand name
    font_brand = get_font(68, bold=True)
    draw.text((safe_x + 180, safe_y + 100), "Indistylex", fill=WHITE, font=font_brand)

    # Gold underline
    draw.line([(safe_x + 180, safe_y + 180), (safe_x + 450, safe_y + 180)], fill=ACCENT, width=3)

    # Tagline
    font_tag = get_font(28)
    draw.text((safe_x + 180, safe_y + 195), "Premium Kids Fashion | Ages 0-14", fill=ACCENT, font=font_tag)

    # Right side features
    font_feat = get_font(22)
    features = ["Free Shipping", "Easy Returns", "COD Available"]
    for i, feat in enumerate(features):
        fx = safe_x + 1100
        fy = safe_y + 120 + i * 50
        draw.rounded_rectangle([fx, fy, fx + 220, fy + 38], radius=19, outline=ACCENT, width=2)
        draw.text((fx + 20, fy + 7), feat, fill=ACCENT, font=font_feat)

    path = os.path.join(OUTPUT_DIR, "youtube-banner-2560x1440.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")


# ============================================================
# 8. EMAIL HEADER (600x200)
# ============================================================
def generate_email_header():
    """600x200 email newsletter header."""
    width, height = 600, 200
    img = Image.new('RGB', (width, height), PRIMARY)
    draw = ImageDraw.Draw(img)

    # Gold top line
    draw.rectangle([0, 0, width, 3], fill=ACCENT)

    # Logo mark
    draw_logo_mark(draw, 30, 50, 90)

    # Brand
    font_brand = get_font(36, bold=True)
    draw.text((140, 60), "Indistylex", fill=WHITE, font=font_brand)

    # Tagline
    font_tag = get_font(16)
    draw.text((140, 105), "Premium Kids Fashion | indistylex.com", fill=ACCENT, font=font_tag)

    # Gold bottom line
    draw.rectangle([0, height - 3, width, height], fill=ACCENT)

    path = os.path.join(OUTPUT_DIR, "email-header-600x200.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")


# ============================================================
# 9. FAVICON (192x192 for web)
# ============================================================
def generate_favicon():
    """192x192 PNG favicon."""
    size = 192
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded square
    draw.rounded_rectangle([8, 8, size - 8, size - 8], radius=30, fill=PRIMARY)

    # iX
    font = get_font(80, bold=True)
    text = "iX"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2
    ty = (size - th) // 2 - 10
    draw.text((tx, ty), text, fill=ACCENT, font=font)

    path = os.path.join(OUTPUT_DIR, "favicon-192x192.png")
    img.save(path, "PNG")
    print(f"✓ Created: {path}")


# ============================================================
# 10. AD CREATIVE TEMPLATE - SQUARE (1080x1080)
# ============================================================
def generate_ad_square():
    """1080x1080 square ad template for Meta/Instagram feed ads."""
    size = 1080
    img = Image.new('RGB', (size, size), WHITE)
    draw = ImageDraw.Draw(img)

    # Top bar black with gold accents
    bar_height = 100
    draw.rectangle([0, 0, size, bar_height], fill=PRIMARY)
    draw.rectangle([0, bar_height - 3, size, bar_height], fill=ACCENT)

    # Logo on top bar
    draw_logo_mark(draw, 30, 15, 70)
    font_brand = get_font(28, bold=True)
    draw.text((120, 38), "Indistylex", fill=WHITE, font=font_brand)

    # Product placeholder area
    product_y = 130
    product_h = 600
    draw.rounded_rectangle(
        [60, product_y, size - 60, product_y + product_h],
        radius=8,
        fill=LIGHT_BG,
        outline=(200, 200, 200),
        width=1
    )
    font_ph = get_font(28)
    text = "[ Product Image Here ]"
    bbox = draw.textbbox((0, 0), text, font=font_ph)
    tw = bbox[2] - bbox[0]
    draw.text(((size - tw) // 2, product_y + product_h // 2 - 14), text, fill=SECONDARY, font=font_ph)

    # Bottom section
    bottom_y = 770
    font_name = get_font(32, bold=True)
    draw.text((60, bottom_y), "Product Name Here", fill=PRIMARY, font=font_name)

    font_price = get_font(38, bold=True)
    draw.text((60, bottom_y + 50), "\u20b9499", fill=PRIMARY, font=font_price)

    font_old = get_font(26)
    draw.text((190, bottom_y + 56), "\u20b9999", fill=SECONDARY, font=font_old)
    # Strikethrough
    bbox_old = draw.textbbox((190, bottom_y + 56), "\u20b9999", font=font_old)
    draw.line([(190, bottom_y + 72), (bbox_old[2], bottom_y + 72)], fill=SECONDARY, width=2)

    # CTA Button — black with gold text
    btn_y = bottom_y + 120
    draw.rounded_rectangle([60, btn_y, 320, btn_y + 55], radius=4, fill=PRIMARY)
    font_btn = get_font(20, bold=True)
    draw.text((100, btn_y + 15), "SHOP NOW", fill=ACCENT, font=font_btn)

    # Offer badge in gold
    draw.rounded_rectangle([size - 200, bottom_y, size - 60, bottom_y + 40], radius=4, fill=ACCENT)
    font_badge = get_font(18, bold=True)
    draw.text((size - 185, bottom_y + 9), "50% OFF", fill=PRIMARY, font=font_badge)

    # Bottom gold line
    draw.rectangle([0, size - 4, size, size], fill=ACCENT)

    path = os.path.join(OUTPUT_DIR, "ad-square-1080x1080.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")


# ============================================================
# 11. SALE BANNER (1200x628) - Facebook/Google Ads
# ============================================================
def generate_sale_banner():
    """1200x628 landscape ad for Facebook feed / Google Display."""
    width, height = 1200, 628
    img = Image.new('RGB', (width, height), PRIMARY)
    draw = ImageDraw.Draw(img)

    # Subtle diagonal texture
    for i in range(0, width + height, 80):
        draw.line([(i, 0), (i - height, height)], fill=(35, 35, 35), width=1)

    # Gold top/bottom borders
    draw.rectangle([0, 0, width, 4], fill=ACCENT)
    draw.rectangle([0, height - 4, width, height], fill=ACCENT)

    # Left side content
    font_sale = get_font(60, bold=True)
    draw.text((60, 80), "MEGA SALE", fill=ACCENT, font=font_sale)

    font_off = get_font(100, bold=True)
    draw.text((60, 160), "50% OFF", fill=WHITE, font=font_off)

    # Gold separator line
    draw.line([(60, 290), (350, 290)], fill=ACCENT, width=2)

    font_sub = get_font(28)
    draw.text((60, 310), "On All Kids Fashion", fill=WHITE, font=font_sub)
    draw.text((60, 350), "Boys & Girls | Ages 0-14", fill=SECONDARY, font=font_sub)

    # CTA — gold outline button
    cta_y = 430
    draw.rounded_rectangle([60, cta_y, 320, cta_y + 60], radius=4, outline=ACCENT, width=2)
    font_cta = get_font(24, bold=True)
    draw.text((105, cta_y + 16), "SHOP NOW", fill=ACCENT, font=font_cta)

    # Website
    font_url = get_font(20)
    draw.text((60, height - 55), "indistylex.com", fill=ACCENT, font=font_url)

    # Right side — elegant gold frame
    frame_x = width - 320
    draw.rounded_rectangle([frame_x, 80, width - 60, height - 80], radius=8, outline=ACCENT, width=2)
    font_ix = get_font(80, bold=True)
    draw.text((frame_x + 70, 220), "iX", fill=ACCENT, font=font_ix)
    font_est = get_font(18)
    draw.text((frame_x + 60, 330), "Premium Fashion", fill=SECONDARY, font=font_est)

    # Offer validity
    font_valid = get_font(18)
    draw.text((width - 260, height - 55), "Limited Time Offer", fill=SECONDARY, font=font_valid)

    path = os.path.join(OUTPUT_DIR, "sale-banner-1200x628.png")
    img.save(path, "PNG", quality=95)
    print(f"✓ Created: {path}")


# ============================================================
# 12. LOGO TRANSPARENT (500x500 with transparency)
# ============================================================
def generate_logo_transparent():
    """500x500 logo with transparent background."""
    size = 500
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Logo mark
    mark_size = 150
    mark_x = (size - mark_size) // 2
    mark_y = 80
    draw.rounded_rectangle(
        [mark_x, mark_y, mark_x + mark_size, mark_y + mark_size],
        radius=mark_size // 5,
        fill=PRIMARY + (255,)
    )
    font_ix = get_font(int(mark_size * 0.55), bold=True)
    text = "iX"
    bbox = draw.textbbox((0, 0), text, font=font_ix)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = mark_x + (mark_size - tw) // 2
    ty = mark_y + (mark_size - th) // 2 - mark_size // 10
    draw.text((tx, ty), text, fill=ACCENT + (255,), font=font_ix)
    # Gold underline in mark
    line_y = mark_y + mark_size - mark_size // 6
    draw.line([(mark_x + mark_size // 5, line_y), (mark_x + mark_size - mark_size // 5, line_y)], fill=ACCENT + (255,), width=2)

    # Wordmark
    font_brand = get_font(48, bold=True)
    text = "Indistylex"
    bbox = draw.textbbox((0, 0), text, font=font_brand)
    tw = bbox[2] - bbox[0]
    tx = (size - tw) // 2
    ty = mark_y + mark_size + 35
    draw.text((tx, ty), text, fill=PRIMARY + (255,), font=font_brand)

    # Gold accent line
    draw.line([(size // 2 - 50, ty + 58), (size // 2 + 50, ty + 58)], fill=ACCENT + (255,), width=2)

    # Tagline
    font_tag = get_font(18)
    tagline = "Premium Kids Fashion"
    bbox = draw.textbbox((0, 0), tagline, font=font_tag)
    tw = bbox[2] - bbox[0]
    tx = (size - tw) // 2
    draw.text((tx, ty + 70), tagline, fill=SECONDARY + (255,), font=font_tag)

    path = os.path.join(OUTPUT_DIR, "logo-transparent-500x500.png")
    img.save(path, "PNG")
    print(f"✓ Created: {path}")


# ============================================================
# RUN ALL
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  INDISTYLEX - Digital Marketing Asset Generator")
    print("=" * 50)
    print()

    generate_profile_logo()
    generate_google_cover()
    generate_facebook_cover()
    generate_instagram_profile()
    generate_instagram_story()
    generate_whatsapp_profile()
    generate_youtube_banner()
    generate_email_header()
    generate_favicon()
    generate_ad_square()
    generate_sale_banner()
    generate_logo_transparent()

    print()
    print("=" * 50)
    print("  ALL ASSETS GENERATED SUCCESSFULLY! ✓")
    print("=" * 50)
    print()
    print("Files saved to:", OUTPUT_DIR)
