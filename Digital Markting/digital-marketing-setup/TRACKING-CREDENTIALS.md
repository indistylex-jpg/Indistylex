# Indistylex — Tracking & Analytics Credentials

> **Central reference for all marketing tracking IDs, install locations, and verification steps.**  
> **Website:** https://indistylex.com  
> **Last updated:** June 14, 2026

---

## Quick Reference

| Tool | ID / Value | Status | Installed in |
|------|------------|--------|--------------|
| **Google Analytics 4** | `G-QXW7GBCQNJ` | ✅ Live on site | `app/templates/base.html` |
| **Google Tag Manager** | `GTM-KH75QZKH` | ✅ Installed | `app/templates/base.html` |
| Meta Pixel | _Add when created_ | ⏳ Pending | GTM or `base.html` |
| Microsoft Clarity | _Add when created_ | ⏳ Pending | GTM or `base.html` |
| Google Search Console | _Add property URL_ | ⏳ Pending | DNS / HTML file |
| Domain | `indistylex.com` | ✅ Live | Server `138.201.50.228` |

---

## 1. Google Analytics 4 (GA4)

### Data stream details (Indistylex — production)

| Field | Value |
|-------|-------|
| **Stream name** | Indistylex |
| **Stream URL** | `https://www.indistylex.com` |
| **Stream ID** | `15071450143` |
| **Measurement ID** | `G-QXW7GBCQNJ` |
| **Enhanced measurement** | ✅ Enabled (page views, scrolls, outbound clicks, site search, video, file downloads) |
| **Connected site tags** | 0 |
| **Email redaction** | Active |
| **URL query parameter keys** | Inactive |

### GA4 admin links

| Page | Path in GA4 |
|------|-------------|
| Data stream settings | Admin → Data collection and modification → **Data streams** → Indistylex |
| Realtime report | Reports → **Realtime** |
| Tag instructions | Admin → Data streams → Indistylex → **View tag instructions** |
| Enhanced measurement | Data stream → **Enhanced measurement** → Modify events |

### Measurement ID
```
G-QXW7GBCQNJ
```

### Install method
**Manual gtag.js** (recommended by Google) — installed on all customer-facing pages.

### Code location
File: `app/templates/base.html` — immediately after `<head>`:

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QXW7GBCQNJ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-QXW7GBCQNJ');
</script>
```

### Dashboard URLs
| Page | URL |
|------|-----|
| GA4 Home | https://analytics.google.com |
| Realtime report | https://analytics.google.com → Reports → Realtime |
| Admin / Data streams | https://analytics.google.com → Admin → Data Streams |

### How to verify it's working
1. Visit **https://www.indistylex.com** in your browser (matches stream URL)
2. Disable ad blockers / use Incognito mode
3. Open GA4 → **Reports → Realtime**
4. You should see **1 active user** within 30 seconds
5. Stream status "No data received" in Admin may take **10–30 minutes** to change after first visit

### Troubleshooting "No data received"

| Check | How |
|-------|-----|
| Tag in page source | View source on www.indistylex.com → search `G-QXW7GBCQNJ` |
| Ad blocker | Disable uBlock/Brave shields and reload |
| Correct URL | Stream is `www.indistylex.com` — test that exact URL |
| CSP not blocking | Server `app/__init__.py` must allow `googletagmanager.com` and `google-analytics.com` |
| Deployed code | Server must be on latest `main` branch (`git log -1` shows GA4 commit) |
| Wait time | GA4 stream status updates slowly — Realtime report is faster |

**Verified live (June 14, 2026):** Tag `G-QXW7GBCQNJ` present in HTML and CSP allows Google domains on www.indistylex.com.

### Enhanced measurement (enabled)
Automatically tracks: page views, scrolls (90%), outbound clicks, site search, video engagement, file downloads.

To modify: GA4 → Admin → Data streams → Indistylex → Enhanced measurement → **Modify events**

### Measurement Protocol API secrets
Status: ⏳ Not created yet.  
Use only if sending server-side events later (e.g. purchase webhooks).  
Create at: Data stream → **Measurement Protocol API secrets** → Create.

### Ecommerce events (to add later)
Add these `gtag` calls when ready for purchase tracking:

```javascript
// Product page view
gtag('event', 'view_item', {
  currency: 'INR',
  value: 899.00,
  items: [{ item_id: 'SKU123', item_name: 'Product Name', price: 899.00 }]
});

// Add to cart
gtag('event', 'add_to_cart', {
  currency: 'INR',
  value: 899.00,
  items: [{ item_id: 'SKU123', item_name: 'Product Name', price: 899.00 }]
});

// Purchase (checkout success page)
gtag('event', 'purchase', {
  transaction_id: 'ORD-12345',
  value: 1798.00,
  currency: 'INR',
  items: [{ item_id: 'SKU123', item_name: 'Product Name', price: 899.00, quantity: 2 }]
});
```

---

## 2. Google Tag Manager (GTM)

### Container ID
```
GTM-KH75QZKH
```

### Install location
File: `app/templates/base.html` — in `<head>` and `<body>` (noscript fallback)

### Dashboard URL
https://tagmanager.google.com

### ⚠️ Important — Avoid double counting
GA4 is installed **directly via gtag** (`G-QXW7GBCQNJ`).  
**Do NOT** also add a GA4 Configuration tag with the same ID inside GTM — that would count every pageview twice.

**Use GTM for:**
- Meta Pixel
- Microsoft Clarity
- Other third-party tags

**Use direct gtag for:**
- GA4 (`G-QXW7GBCQNJ`) — already installed

---

## 3. Content Security Policy (CSP)

Analytics domains were added to `app/__init__.py` so gtag and GTM can load:

```
script-src: ... https://www.googletagmanager.com https://www.google-analytics.com
connect-src: ... https://www.googletagmanager.com https://www.google-analytics.com
              https://analytics.google.com https://region1.google-analytics.com
```

**Redeploy required** after any CSP or template change.

---

## 4. Pages with tracking

| Template | Tracking | Notes |
|----------|----------|-------|
| `app/templates/base.html` | ✅ GA4 + GTM | All storefront pages (shop, cart, checkout, etc.) |
| `app/templates/admin/base_admin.html` | ❌ No tracking | Admin excluded intentionally — avoids skewing data |

---

## 5. Meta Pixel (Facebook / Instagram)

### Status: ⏳ Not yet installed

When you create it in Meta Events Manager, add the ID here:

```
Meta Pixel ID: ___________________
```

### Setup guide
`digital-marketing-setup/02-META-BUSINESS.md` (Step 5)  
`digital-marketing-setup/05-TRACKING-SETUP.md` (Step 3)

### Recommended install
Add via **GTM** (not duplicate in `base.html` if using GTM).

---

## 6. Microsoft Clarity

### Status: ⏳ Not yet installed

When created at https://clarity.microsoft.com, add ID here:

```
Clarity Project ID: ___________________
```

### Setup guide
`digital-marketing-setup/05-TRACKING-SETUP.md` (Step 4)

---

## 7. Google Search Console

### Status: ⏳ Pending verification

| Field | Value |
|-------|-------|
| Property URL | `https://indistylex.com` |
| Sitemap URL | `https://indistylex.com/sitemap.xml` |

### Setup guide
`digital-marketing-setup/12-SEO-TECHNICAL.md`

### After verification
1. Submit sitemap: `https://indistylex.com/sitemap.xml`
2. Link GA4 property: GA4 Admin → Product links → Search Console

---

## 8. Deployment checklist (after code changes)

Run on production server after pushing tracking updates:

```bash
ssh root@138.201.50.228
cd /var/www/indistylex
git pull   # or your deploy method
chown -R www-data:www-data /var/www/indistylex
systemctl restart indistylex
```

Then verify:
- [ ] Visit https://indistylex.com
- [ ] GA4 Realtime shows your visit
- [ ] Browser console has no CSP errors for googletagmanager.com
- [ ] GTM Preview mode shows container loading (optional)

---

## 9. Business & launch info

| Field | Value |
|-------|-------|
| Brand | Indistylex |
| Domain | indistylex.com |
| Launch date | July 10, 2026 (Friday) |
| Tagline | Style That Speaks, Quality That Lasts |
| GSTIN | 09GVUPP6447P1Z3 |
| Phone | +91 63941 42176 |
| Support email | support@indistylex.com (update from .in) |

---

## 10. Related documentation

| Topic | File |
|-------|------|
| Full tracking setup guide | `digital-marketing-setup/05-TRACKING-SETUP.md` |
| Analytics KPIs & reporting | `digital-marketing/10-ANALYTICS.md` |
| SEO & Search Console | `digital-marketing-setup/12-SEO-TECHNICAL.md` |
| Meta Pixel & ads | `digital-marketing-setup/02-META-BUSINESS.md` |
| 30-day go-live plan | `30-DAY-GO-LIVE-PLAN.md` |
| Launch promo videos | `digital-marketing-assets/videos/README.md` |

---

## 11. Account access log

Record who has access to each platform (fill in as you set up):

| Platform | Account email | Role | Date set up |
|----------|---------------|------|-------------|
| Google Analytics 4 | | Owner | June 2026 |
| Google Tag Manager | | Admin | |
| Google Search Console | | Owner | |
| Meta Business Manager | | Admin | |
| Brevo (email) | | Admin | |
| Razorpay | | Admin | |

> **Secrets (tokens, passwords):** store in `CREDENTIALS.md` at project root — **local only, gitignored, never push to GitHub.**

---

*Keep this file updated whenever you add a new tracking ID, pixel, or marketing tool.*
