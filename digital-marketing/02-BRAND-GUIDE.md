# 02 — Brand Guide

> **Source of truth:** Website (`app/static/css/style.css`, `app/static/images/logo.svg`) · Flutter app (`indistylex_app/lib/app/theme/app_theme.dart`) · Physical shop labels (`docs/shop-setup/SHOP-SETUP-GUIDE.md` §3.2)  
> **Last updated:** August 2026 — replaces old black/gold identity

---

## Brand identity

| Element | Value |
|---------|--------|
| **Name** | Indistylex |
| **Category line** | KIDS FASHION (under logo, letter-spaced) |
| **Tagline** | Style That Speaks, Quality That Lasts |
| **Logo** | Kids tee icon on **blue gradient tile** + wordmark **INDISTYLEX** + blue underline bar |
| **Logo files** | `app/static/images/logo.svg`, `logo-white.svg`, `logo-icon.svg`, `favicon.svg` |
| **Domain** | indistylex.com |
| **Email** | indistylex@gmail.com |
| **Instagram** | [@indistylex_clothing](https://www.instagram.com/indistylex_clothing) |
| **WhatsApp** | +91 63941 42176 |

### Logo usage

| Context | File / treatment |
|---------|------------------|
| Website navbar & footer | `logo.svg` (full wordmark) |
| Dark / photo backgrounds | `logo-white.svg` |
| App icon, favicon, social avatar | `logo-icon.svg` or `favicon-192x192.png` |
| **Don’t** | Old gold “iX” square, black/gold-only lockups, stretch or recolor the gradient |

---

## Brand colors

Aligned with **indistylex.com** — trustworthy blue, clean white, soft sky backgrounds. **Not** black/gold.

### Core palette

| Name | Hex | CSS variable | Usage |
|------|-----|--------------|--------|
| **Primary blue** | `#1E4D8C` | `--primary` | Headings, body text, nav links, brand wordmark |
| **Accent blue** | `#2563EB` | `--accent` | Buttons, CTAs, logo underline, links on hover |
| **Accent hover** | `#1D4ED8` | `--accent-hover` | Button hover states |
| **Sky light** | `#DBEAFE` | — | Promo ticker bar, logo tee detail |
| **Soft blue bg** | `#EFF6FF` | `--accent-soft` | Section tints, admin sidebar bg |
| **Card blue tint** | `#EEF4FC` | `--card-bg` | Product cards, feature blocks |
| **Page background** | `#F8FAFC` | `--light-bg` | Alternate sections, app scaffold |
| **White** | `#FFFFFF` | `--white` | Header, cards, hang tags |
| **Border** | `#E2E8F0` | `--border` | Dividers, inputs |
| **Muted text** | `#64748B` | `--text-muted` | Subtitles, “KIDS FASHION”, captions |

### Secondary / functional

| Name | Hex | Usage |
|------|-----|--------|
| **Warm accent** | `#E85D04` | Optional urgency (limited promos) |
| **Sale / error** | `#E53935` | Sale badges, form errors |
| **Success** | `#43A047` | Order success, stock “Active” |
| **Gradient** | `#1E4D8C` → `#2563EB` → `#3B82F6` | Logo icon tile, hero buttons, shop flex |

### Gradients (website & app)

```css
/* Primary CTA / logo mark */
linear-gradient(145deg, #1E4D8C 0%, #2563EB 100%);

/* Logo icon (SVG) */
linear-gradient: #1E4D8C → #2563EB → #3B82F6
```

### Color rules

| Do ✅ | Don’t ❌ |
|-------|----------|
| White or `#F8FAFC` backgrounds | Full black `#1a1a1a` page backgrounds |
| Blue CTAs (`#2563EB`) | Gold `#C9A94E` as primary accent |
| Deep blue text on white | Gold text on busy photos (old style) |
| Soft blue ticker `#DBEAFE` | Heavy dark luxury aesthetic |

---

## Typography

| Role | Font | Weight | Notes |
|------|------|--------|-------|
| **Headings & body** | **Inter** | 600–800 headings, 400–500 body | Single family sitewide — clean, modern |
| **Logo wordmark** | Inter | 800, letter-spacing ~1.2px | ALL CAPS: INDISTYLEX |
| **Category line** | Inter | 700, letter-spacing ~2.4px | KIDS FASHION — muted `#64748B` |

**Google Fonts load:** Inter (primary). Playfair Display may load in templates but **live UI uses Inter** — use Inter in Canva, ads, and shop print.

### Type scale (web)

| Element | Size | Weight |
|---------|------|--------|
| Hero title | 2–2.5rem | 700–800 |
| Section heading | 1.5–1.75rem | 700 |
| Product title | 0.95–1rem | 600 |
| Body | 0.875–1rem | 400 |
| Promo ticker | 0.72rem | 600 |

---

## Physical shop & labelling

Same colors online and in-store. Full setup: **`docs/shop-setup/SHOP-SETUP-GUIDE.md`**

### Shop visual identity

| Item | Spec |
|------|------|
| **Entrance flex / board** | Logo + “Indistylex · Kids Wear” — primary blue on white, or white logo on `#1E4D8C` |
| **Counter / walls** | White + light grey `#F8FAFC`; accent strips in `#2563EB` |
| **Hang tags** | White or cream card; **INDISTYLEX** in `#1E4D8C`; blue bar or thin `#2563EB` rule |
| **Barcode stickers** | White label; text black/`#1E4D8C`; optional small blue logo |
| **Woven care labels** | Navy `#1E4D8C` + white thread |
| **Carry bags** | White kraft or white LDPE; logo primary blue one-side print |
| **Staff suggestion** | Plain tops; optional blue lanyard — no conflicting brands |

### Hang tag layout (print)

```
┌─────────────────────────┐
│      INDISTYLEX         │  ← #1E4D8C, Inter bold
│   ─────────────         │  ← #2563EB bar
│   Kids Fashion          │  ← #64748B small caps
│                         │
│   Floral Cotton Frock   │
│   Size: 3–4Y · Pink     │
│   MRP: ₹899 (Incl. GST) │
│   SKU: IX-FRK-001-3-4Y-PNK
│   [barcode]             │
│   indistylex.com        │
└─────────────────────────┘
```

Mockup reference: `docs/shop-setup/images/indistylex-label-mockup.png`

---

## UI patterns (website & app)

| Pattern | Treatment |
|---------|-----------|
| **Header** | White bar, blue logo, search + nav |
| **Promo ticker** | `#DBEAFE` background, `#1E4D8C` text, scrolling offers |
| **Primary button** | `#2563EB` fill, white text, pill radius |
| **Secondary button** | White fill, `#1E4D8C` border/text |
| **Product cards** | White/`#EEF4FC`, soft shadow, blue price |
| **Sale badge** | Red or warm orange — small, corner |
| **Footer** | Dark blue `#1E4D8C` or deep section with `logo-white.svg` |

---

## Brand voice

### Tone: Warm, confident, trustworthy — premium but approachable (parents + kids)

| Do ✅ | Don’t ❌ |
|-------|----------|
| “Crafted for your little one” | “Buy cheap clothes here” |
| “Premium comfort meets style” | “Best quality guaranteed!!!” |
| “Soft cotton for active kids” | “Your kid will look amazing” |
| “Easy 7-day returns” | “ORDER NOW!!! LIMITED STOCK!!!” |

### Writing guidelines

- Short sentences — parents are busy.
- Pair **comfort + style**; mention **age band** (2–3Y, 5–6Y).
- Use “your little one” / “your child”.
- ALL CAPS only for small badges (SALE, NEW).
- Always **indistylex.com** and **@indistylex_clothing** — not `.in` domain.

---

## Brand hashtags

### Primary (most posts)

```
#Indistylex #indistylex_clothing #KidsFashionIndia
```

### Secondary (rotate)

```
#KidsOfInstagram #MomApproved #LittleFashionista
#IndianKidsFashion #ToddlerStyle #BabyFashion
#KidsWear #ChildrensFashion #EthnicKidsWear
#KidsPartyWear #CuteKidsClothes #PrayagrajKids
```

### Campaign

```
#IndistylexSale #FestiveWithIndistylex
#SummerWithIndistylex #IndistylexNewArrivals
```

---

## Photography & social creative

### Product

- **Background:** White `#FFFFFF` or very soft blue `#F8FAFC` / `#EFF6FF`
- **Lighting:** Natural, soft; show fabric texture
- **On-model:** Indian kids, diverse, age-appropriate styling
- **Props:** Minimal — toys, books, soft neutrals (avoid loud gold props)

### Lifestyle

- Parks, home, festivals — relatable Indian settings
- Clothing colors should pop against soft backgrounds, not dark moody gold filters

### Social / ads / Reels

- **Text overlays:** White or `#1E4D8C` on semi-transparent blue `#1E4D8C` at 80% — or white text on photo with blue CTA pill
- **CTA button graphic:** `#2563EB` rounded pill, white “Shop now”
- **Avoid:** Gold typography, black luxury frames, old iX gold square logo

### Export sizes

| Asset | Size |
|-------|------|
| Instagram post | 1080×1080 |
| Story / Reel cover | 1080×1920 |
| Shop flex (entrance) | Printer spec — logo SVG at 300 DPI |
| WhatsApp catalog | Square product on white bg |

Marketing PNGs: `digital-marketing-assets/` (regenerate if old gold assets appear)

---

## Content pillars (rotate)

1. **Product showcase (40%)** — New arrivals, size guides, styling tips  
2. **Parenting relatability (25%)** — Memes, mom/dad moments, festival prep  
3. **Behind the scenes (20%)** — Packing orders, shop counter, quality checks  
4. **UGC & reviews (15%)** — Customer photos, unboxing, @indistylex_clothing tags  

---

## Quick copy-paste for designers

```
Primary:    #1E4D8C
Accent:     #2563EB
Background: #F8FAFC
Ticker:     #DBEAFE
Text muted: #64748B
Font:       Inter (Google Fonts)
Instagram:  @indistylex_clothing
Website:    indistylex.com
```

---

## Related docs

| Document | Purpose |
|----------|---------|
| [01-STRATEGY.md](01-STRATEGY.md) | Marketing strategy |
| [../docs/shop-setup/SHOP-SETUP-GUIDE.md](../docs/shop-setup/SHOP-SETUP-GUIDE.md) | Physical shop + labels |
| [../../operations-templates/packing-printables/](../../operations-templates/packing-printables/) | Thank-you card, invoice print colors |
| `app/static/css/style.css` | Live website tokens |
| `scripts/sync_brand_from_website.sh` (Flutter) | Sync app assets from site |

---

*Indistylex Brand Guide — aligned with live website & shop plan, August 2026*
