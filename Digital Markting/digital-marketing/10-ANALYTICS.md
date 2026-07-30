# 10 — Analytics & Tracking Setup

## Essential Tools to Set Up

| Tool                    | Purpose                      | Priority | Cost    |
|-------------------------|------------------------------|----------|---------|
| Google Analytics 4      | Website traffic & behavior   | HIGH     | Free    |
| Google Search Console   | SEO & search performance     | HIGH     | Free    |
| Meta Pixel              | Facebook/Instagram ad tracking| HIGH    | Free    |
| Google Tag Manager      | Manage all tracking codes    | HIGH     | Free    |
| Hotjar (or Microsoft Clarity)| Heatmaps & recordings  | MEDIUM   | Free    |

---

## Step 1: Google Analytics 4 (GA4)

### Setup:
1. Go to https://analytics.google.com
2. Create account: "Indistylex"
3. Create property: "Indistylex Website"
4. Get Measurement ID: `G-XXXXXXXXXX`

### Add to website (`base.html` in `<head>`):
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### E-commerce Events to Track:
```javascript
// View product
gtag('event', 'view_item', {
  currency: 'INR',
  value: 999,
  items: [{item_id: 'SKU001', item_name: 'Product Name', price: 999}]
});

// Add to cart
gtag('event', 'add_to_cart', {
  currency: 'INR',
  value: 999,
  items: [{item_id: 'SKU001', item_name: 'Product Name', price: 999, quantity: 1}]
});

// Begin checkout
gtag('event', 'begin_checkout', {
  currency: 'INR',
  value: 1998,
  items: [/* cart items */]
});

// Purchase
gtag('event', 'purchase', {
  transaction_id: 'ORDER-12345',
  currency: 'INR',
  value: 1998,
  shipping: 0,
  items: [/* order items */]
});
```

---

## Step 2: Google Search Console

### Setup:
1. Go to https://search.google.com/search-console
2. Add property → URL prefix: `https://indistylex.com`
3. Verify via HTML tag or DNS
4. Submit sitemap: `https://indistylex.com/sitemap.xml`

### Monthly Checks:
- Top performing pages & queries
- Click-through rates (improve titles if CTR < 3%)
- Coverage errors (fix 404s, redirect issues)
- Mobile usability issues
- Core Web Vitals

---

## Step 3: Meta Pixel

(See `05-META-ADS.md` for full setup code)

### Verify Setup:
1. Install "Meta Pixel Helper" Chrome extension
2. Visit your site — should show PageView event firing
3. Test events: add to cart, checkout, purchase

---

## Step 4: Microsoft Clarity (Free Heatmaps)

### Setup:
1. Go to https://clarity.microsoft.com
2. Sign up, create project
3. Add tracking code to `base.html`:
```html
<script type="text/javascript">
(function(c,l,a,r,i,t,y){
c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "YOUR_PROJECT_ID");
</script>
```

### What to look for:
- Where users click (dead clicks = confusing UX)
- How far they scroll (move CTA above fold if needed)
- Session recordings of confused users
- Rage clicks (frustrated users)

---

## Key Performance Indicators (KPIs)

### Weekly Dashboard:

| Metric                  | How to Find                      | Target      |
|-------------------------|----------------------------------|-------------|
| Website Sessions        | GA4 → Reports → Acquisition     | Growing 10%/week |
| Conversion Rate         | GA4 → E-commerce → Purchase rate| 1.5-3%      |
| Revenue                 | GA4 → E-commerce → Revenue      | Growing     |
| Avg Order Value         | Revenue / Orders                 | ₹1,200+     |
| Bounce Rate             | GA4 → Engagement → Bounce rate  | < 60%       |
| Cart Abandonment        | Checkouts started / Purchases    | < 70%       |
| Top Traffic Source      | GA4 → Acquisition → Channels    | —           |

### Monthly Dashboard:

| Metric                  | Target (Month 3)   |
|-------------------------|--------------------|
| Total Revenue           | ₹75,000            |
| Total Orders            | 60                 |
| New Customers           | 50                 |
| Return Customers        | 10                 |
| Email Subscribers       | 500                |
| Instagram Followers     | 2,000              |
| Google Organic Traffic  | 1,000 sessions     |
| Paid Ads ROAS           | 3x+                |
| Customer Acq. Cost      | < ₹350             |

---

## UTM Tracking (Track Campaign Performance)

### Format:
```
https://indistylex.com/shop?utm_source=SOURCE&utm_medium=MEDIUM&utm_campaign=CAMPAIGN
```

### Use These UTMs:

| Channel          | utm_source  | utm_medium    | utm_campaign          |
|------------------|-------------|---------------|------------------------|
| Instagram Bio    | instagram   | social        | bio_link              |
| Instagram Stories| instagram   | story         | new_arrivals_june     |
| Facebook Ad      | facebook    | paid_social   | summer_sale_cold      |
| Google Search Ad | google      | cpc           | brand_keywords        |
| Email Newsletter | email       | newsletter    | june_newsletter       |
| WhatsApp         | whatsapp    | messaging     | flash_sale            |
| Influencer       | influencer  | social        | priya_collab_june     |

### UTM Builder:
Use https://ga-dev-tools.google/ga4/campaign-url-builder/

---

## Reporting Template (Monthly)

```
📊 INDISTYLEX — Monthly Marketing Report
Month: [Month Year]

REVENUE:
• Total Revenue: ₹___
• Orders: ___
• AOV: ₹___
• Conversion Rate: ___%

TRAFFIC:
• Total Sessions: ___
• Organic: ___ (___%)
• Paid: ___ (___%)
• Social: ___ (___%)
• Direct: ___ (___%)
• Email: ___ (___%)

PAID ADS:
• Meta Ads Spend: ₹___ → Revenue: ₹___ (ROAS: ___x)
• Google Ads Spend: ₹___ → Revenue: ₹___ (ROAS: ___x)
• Total CAC: ₹___

SOCIAL MEDIA:
• Instagram Followers: ___ (+___)
• Engagement Rate: ___%
• Top Post: [description] — ___ likes, ___ comments

EMAIL:
• Subscribers: ___ (+___)
• Open Rate: ___%
• Revenue from Email: ₹___
• Cart Recovery: ___emails → ₹___ recovered

TOP WINS THIS MONTH:
1.
2.
3.

FOCUS FOR NEXT MONTH:
1.
2.
3.
```

---

## Tools Stack Summary

| Category        | Tool              | Cost/month | Link                    |
|-----------------|-------------------|-----------|--------------------------|
| Analytics       | Google Analytics 4 | Free      | analytics.google.com    |
| SEO             | Google Search Console| Free    | search.google.com/search-console |
| Heatmaps        | Microsoft Clarity  | Free      | clarity.microsoft.com   |
| Email           | Brevo             | Free-₹1,500| brevo.com             |
| Social Schedule | Buffer / Later     | Free      | buffer.com             |
| Design          | Canva             | Free-₹500 | canva.com              |
| Link in Bio     | Linktree          | Free      | linktr.ee              |
| URL Shortener   | Bitly             | Free      | bitly.com              |
| Competitor Intel| SimilarWeb        | Free      | similarweb.com         |
