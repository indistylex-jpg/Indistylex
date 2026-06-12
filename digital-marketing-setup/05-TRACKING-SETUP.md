# 05 — Website Tracking Setup (GA4, Pixel, Clarity, GTM)

## What This Does
Installs all analytics and tracking tools so you know exactly: who visits your site, what they do, what they buy, and which ads work.

**Time needed**: 1 hour

---

## Tool Overview

| Tool | Purpose | Cost |
|------|---------|------|
| Google Tag Manager (GTM) | Container for ALL tracking codes | Free |
| Google Analytics 4 (GA4) | Traffic, behavior, conversions | Free |
| Meta Pixel | Facebook/Instagram ad tracking | Free |
| Microsoft Clarity | Heatmaps, session recordings | Free |
| Google Search Console | SEO monitoring | Free |

---

## Step 1: Google Tag Manager (Install FIRST)

> GTM is a container that holds all your other tracking codes. Install this ONCE, then add everything else through GTM.

### 1.1 Create GTM Account
1. Go to: https://tagmanager.google.com
2. Click **"Create Account"**
3. Enter:
   - Account name: `Indistylex`
   - Country: India
   - Container name: `indistylex.com`
   - Target platform: **Web**
4. Accept Terms

### 1.2 Install GTM on Website

You'll get two code snippets. Add them to your `base.html`:

**Snippet 1 — Add to `<head>` (as high as possible):**
```html
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-XXXXXXX');</script>
<!-- End Google Tag Manager -->
```

**Snippet 2 — Add immediately after `<body>`:**
```html
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
```

> Replace `GTM-XXXXXXX` with your actual GTM ID.

### 1.3 Verify Installation
1. Install **Tag Assistant** Chrome extension
2. Visit your website
3. Should show "Tag Manager found" with green status

---

## Step 2: Google Analytics 4 (GA4)

### 2.1 Create GA4 Property
1. Go to: https://analytics.google.com
2. Click **"Start Measuring"** (or Admin → Create Property)
3. Enter:
   - Property name: `Indistylex`
   - Time zone: India (GMT+5:30)
   - Currency: INR
4. Business details:
   - Industry: Shopping
   - Size: Small
5. Choose: **Web** platform
6. Enter:
   - Website URL: `https://indistylex.com`
   - Stream name: `Indistylex Web`

### 2.2 Get Measurement ID
- You'll get a **Measurement ID** like `G-XXXXXXXXXX`
- Save this — you'll add it to GTM

### 2.3 Add GA4 to GTM
1. In GTM → **Tags** → **New**
2. Tag type: **Google Analytics: GA4 Configuration**
3. Measurement ID: `G-XXXXXXXXXX`
4. Trigger: **All Pages**
5. Save → **Submit** (publish)

### 2.4 Set Up E-commerce Tracking

Add this **dataLayer** code to your website pages:

**Product Page (view_item):**
```html
<script>
dataLayer.push({
  event: 'view_item',
  ecommerce: {
    currency: 'INR',
    value: {{ product.price }},
    items: [{
      item_id: '{{ product.id }}',
      item_name: '{{ product.name }}',
      item_category: '{{ product.category }}',
      price: {{ product.price }},
      quantity: 1
    }]
  }
});
</script>
```

**Add to Cart (add_to_cart):**
```javascript
dataLayer.push({
  event: 'add_to_cart',
  ecommerce: {
    currency: 'INR',
    value: productPrice,
    items: [{
      item_id: productId,
      item_name: productName,
      price: productPrice,
      quantity: 1
    }]
  }
});
```

**Purchase (on success page):**
```html
<script>
dataLayer.push({
  event: 'purchase',
  ecommerce: {
    transaction_id: '{{ order.id }}',
    value: {{ order.total }},
    currency: 'INR',
    shipping: {{ order.shipping_cost }},
    items: [
      {% for item in order.items %}
      {
        item_id: '{{ item.product_id }}',
        item_name: '{{ item.name }}',
        price: {{ item.price }},
        quantity: {{ item.quantity }}
      }{% if not loop.last %},{% endif %}
      {% endfor %}
    ]
  }
});
</script>
```

### 2.5 GA4 Configuration Checklist
In GA4 Admin → Data Streams → your stream:

- [x] Enhanced Measurement: ON (tracks scrolls, outbound clicks, site search)
- [x] Cross-domain measurement: Not needed (single domain)
- [x] Data retention: Set to **14 months**
- [x] Google Signals: **Enable** (for demographics)
- [x] Link Google Ads account
- [x] Link Search Console

---

## Step 3: Meta Pixel (via GTM)

### 3.1 Get Your Pixel ID
- From Meta Business Manager → Events Manager → Your Pixel
- Copy the Pixel ID (numbers only, like `123456789012345`)

### 3.2 Add Meta Pixel via GTM

**Method: Custom HTML Tag**

1. In GTM → **Tags** → **New**
2. Tag type: **Custom HTML**
3. Paste this code:

```html
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', 'YOUR_PIXEL_ID');
fbq('track', 'PageView');
</script>
```

4. Trigger: **All Pages**
5. Name: `Meta Pixel - Base`
6. Save

### 3.3 Add Meta Pixel Events via GTM

**ViewContent (Product Pages):**
1. New Tag → Custom HTML
2. Code:
```html
<script>
fbq('track', 'ViewContent', {
  content_type: 'product',
  content_ids: [{{DL - Product ID}}],
  value: {{DL - Product Price}},
  currency: 'INR'
});
</script>
```
3. Trigger: Custom Event → `view_item`

**AddToCart:**
```html
<script>
fbq('track', 'AddToCart', {
  content_type: 'product',
  content_ids: [{{DL - Product ID}}],
  value: {{DL - Product Price}},
  currency: 'INR'
});
</script>
```
Trigger: Custom Event → `add_to_cart`

**Purchase:**
```html
<script>
fbq('track', 'Purchase', {
  value: {{DL - Order Value}},
  currency: 'INR',
  content_type: 'product'
});
</script>
```
Trigger: Custom Event → `purchase`

### 3.4 Verify Meta Pixel
1. Install **Meta Pixel Helper** Chrome extension
2. Visit your site — should show events firing
3. Check Events Manager → Test Events tab

---

## Step 4: Microsoft Clarity

### 4.1 Create Clarity Account
1. Go to: https://clarity.microsoft.com
2. Sign up with Microsoft/Google account
3. Create project:
   - Name: `Indistylex`
   - URL: `https://indistylex.com`
   - Category: `E-commerce`

### 4.2 Install via GTM
1. Get your Clarity project ID (like `abc123xyz`)
2. In GTM → New Tag → Custom HTML:
```html
<script type="text/javascript">
(function(c,l,a,r,i,t,y){
c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "YOUR_CLARITY_ID");
</script>
```
3. Trigger: All Pages
4. Save & Publish

### 4.3 What Clarity Shows You (Free!)
- **Heatmaps**: Where people click/scroll on each page
- **Session Recordings**: Watch real user sessions
- **Dead Clicks**: Places people click but nothing happens
- **Rage Clicks**: Frustrated clicking (UX problems!)
- **Scroll Depth**: How far people scroll

### 4.4 Weekly Clarity Review
Every Monday, check:
1. Product pages → Are people clicking "Add to Cart"?
2. Checkout page → Where do people drop off?
3. Mobile vs Desktop → Different behaviors?
4. Any rage clicks? → Fix those elements

---

## Step 5: Google Search Console

### 5.1 Add Property
1. Go to: https://search.google.com/search-console
2. Click **"Add Property"**
3. Choose **"URL prefix"**: `https://indistylex.com`
4. Verify with same method as Merchant Center (HTML tag or DNS)

### 5.2 Submit Sitemap
1. Go to **Sitemaps** → Enter: `sitemap.xml`
2. Click **"Submit"**

### 5.3 Weekly SEO Checks
- **Performance**: Which queries bring traffic? CTR?
- **Coverage**: Any pages with errors?
- **Mobile Usability**: Any mobile issues?
- **Core Web Vitals**: Page speed OK?

---

## Step 6: UTM Tracking (for all links you share)

### UTM Parameters Template:
Always add UTM parameters to links you share:

```
https://indistylex.com/?utm_source=SOURCE&utm_medium=MEDIUM&utm_campaign=CAMPAIGN
```

### Standard UTMs for Each Channel:

| Channel | UTM Source | UTM Medium | UTM Campaign |
|---------|-----------|------------|--------------|
| Instagram Bio | instagram | social | bio_link |
| Instagram Story | instagram | story | [campaign_name] |
| Facebook Post | facebook | social | organic_post |
| Facebook Ad | facebook | cpc | [ad_set_name] |
| WhatsApp | whatsapp | messaging | [campaign_name] |
| Email Newsletter | brevo | email | weekly_newsletter |
| Google Ads | google | cpc | (auto-tagged) |
| Influencer | influencer | referral | [influencer_name] |

### UTM Builder:
Use: https://ga-dev-tools.google/ga4/campaign-url-builder/

---

## Step 7: Publish GTM Container

After adding ALL tags:
1. In GTM → Click **"Submit"** (top right)
2. Version name: `Initial Setup - GA4 + Pixel + Clarity`
3. Click **"Publish"**

### Verify Everything Works:
1. Use GTM **Preview Mode** (click "Preview" in GTM)
2. Enter your website URL
3. Check all tags fire correctly:
   - ✅ GA4 Config fires on all pages
   - ✅ Meta Pixel fires on all pages
   - ✅ Clarity fires on all pages
   - ✅ ViewContent fires on product pages
   - ✅ AddToCart fires when button clicked
   - ✅ Purchase fires on success page

---

## ✅ Checklist — You're Done When:

- [ ] GTM account created and installed
- [ ] GA4 property created
- [ ] GA4 added via GTM
- [ ] E-commerce dataLayer events added to website
- [ ] GA4 data retention set to 14 months
- [ ] Google Signals enabled
- [ ] Meta Pixel created and added via GTM
- [ ] Pixel events (ViewContent, AddToCart, Purchase) configured
- [ ] Pixel verified with Pixel Helper
- [ ] Clarity installed
- [ ] Google Search Console verified
- [ ] Sitemap submitted
- [ ] GA4 linked to Google Ads
- [ ] GA4 linked to Search Console
- [ ] GTM container published
- [ ] All tags verified in Preview Mode
- [ ] UTM tracking convention documented

---

## Dashboard to Check Daily

| Tool | Check | URL |
|------|-------|-----|
| GA4 | Real-time visitors, top pages | analytics.google.com |
| Meta Events Manager | Pixel events, match quality | business.facebook.com/events_manager |
| Clarity | Session recordings, heatmaps | clarity.microsoft.com |
| Search Console | Indexing, search queries | search.google.com/search-console |
