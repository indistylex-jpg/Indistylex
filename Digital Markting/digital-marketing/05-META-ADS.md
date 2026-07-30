# 05 — Meta Ads (Facebook + Instagram)

## Account Setup

### Step 1: Facebook Business Manager
1. Go to https://business.facebook.com
2. Create Business Account: "Indistylex"
3. Add Facebook Page + Instagram Business account
4. Add payment method

### Step 2: Meta Pixel Setup
Add this to your website's `<head>` (in `base.html`):
```html
<!-- Meta Pixel Code -->
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

### Step 3: Track Events
Fire these on respective pages:
```javascript
// Product viewed
fbq('track', 'ViewContent', {content_name: 'Product Name', value: 999, currency: 'INR'});

// Add to cart
fbq('track', 'AddToCart', {content_name: 'Product Name', value: 999, currency: 'INR'});

// Begin checkout
fbq('track', 'InitiateCheckout', {value: 1999, currency: 'INR'});

// Purchase complete
fbq('track', 'Purchase', {value: 1999, currency: 'INR'});
```

---

## Campaign Structure

### Campaign 1: COLD — Awareness + Traffic (Top of Funnel)

**Objective**: Traffic / Engagement
**Budget**: ₹300/day
**Duration**: Always-on

**Audience (Create these)**:
- Women, 25-40, India (Metro + Tier 1 cities)
- Interests: Parenting, Kids Fashion, Firstcry, Hopscotch, Baby clothing
- Lookalike: 1% of website visitors (once pixel has data)

**Ad Format**: Carousel (show 4-5 products) OR Video Reel

**Ad Set 1 — Moms (Interest-based)**:
```
Targeting:
- Age: 25-38
- Gender: Female
- Location: Delhi, Mumbai, Bangalore, Hyderabad, Pune, Chennai, Kolkata
- Interests: Parenting, Motherhood, Baby products, Kids fashion
- Exclude: Existing customers
```

**Ad Set 2 — Gifting Audience**:
```
Targeting:
- Age: 22-45
- Gender: All
- Life Events: Close friends of parents with toddlers, 
               Close friends of parents with preschoolers
- Interests: Gift shopping, Online shopping
```

---

### Campaign 2: WARM — Retargeting (Middle Funnel)

**Objective**: Conversions (Purchase)
**Budget**: ₹200/day

**Ad Set 1 — Website Visitors (no purchase, last 14 days)**:
```
Custom Audience: Website visitors (14 days) - Exclude purchasers
Ad: Dynamic Product Ads (show exact products they viewed)
Copy: "Still thinking about it? Your little one deserves this! 💛"
```

**Ad Set 2 — Cart Abandoners (last 7 days)**:
```
Custom Audience: AddToCart (7 days) - Exclude purchasers
Ad: Carousel of abandoned products + free shipping reminder
Copy: "You left something cute in your cart! Free shipping on orders above ₹999 🛒"
Offer: Additional 10% off code: COMEBACK10
```

**Ad Set 3 — Engaged but not visited (IG/FB engagement, 30 days)**:
```
Custom Audience: People who engaged with page (30 days) - Exclude visitors
Ad: Best-selling products carousel
Copy: "Our most-loved styles — now at special prices!"
```

---

### Campaign 3: HOT — Retention (Bottom Funnel)

**Objective**: Conversions
**Budget**: ₹100/day

**Audience**: Past buyers (30-90 days ago)
**Ad**: New arrivals OR complementary products
**Copy**: "New in! Fresh styles just dropped for your growing kiddo 🌟"

---

## Ready-to-Use Ad Copies

### Ad Copy 1 — General (Carousel)
```
Primary Text:
Premium kids' clothing that's comfortable AND stylish? Yes, it exists! 👶✨

✅ Skin-friendly cotton fabrics
✅ Newborn to 12 years
✅ Free shipping above ₹999
✅ Easy 7-day returns

Shop now → indistylex.com

Headline: Trendy Kids Clothes | From ₹499
Description: Premium quality. Fast delivery. Happy kids.
CTA: Shop Now
```

### Ad Copy 2 — Ethnic Wear
```
Primary Text:
Festival season is here! Dress your little prince/princess in the most adorable ethnic wear 🪔👑

Kurta sets, lehengas, sherwani sets — all crafted in breathable fabrics your child will actually want to wear!

Starting ₹799 | Free shipping above ₹999

Headline: Kids Ethnic Wear | Festive Collection
CTA: Shop Now
```

### Ad Copy 3 — Social Proof
```
Primary Text:
Join 1000+ happy parents who trust Indistylex for their kids' wardrobe! 💛

⭐⭐⭐⭐⭐ "The quality is amazing for this price. My daughter loves her new dress!" — Priya, Delhi

New arrivals every week. Sizes 0-12 years.

Headline: India's Fastest-Growing Kids' Fashion Brand
CTA: Shop Now
```

### Ad Copy 4 — Urgency/Sale
```
Primary Text:
🚨 FLAT 30% OFF — This weekend only!

Premium kids' clothing at prices you won't believe. 
Cotton tees from ₹349 | Dresses from ₹599 | Ethnic sets from ₹699

⏰ Sale ends Sunday midnight. Don't miss out!
Use code: WEEKEND30

Headline: 30% Off Everything | Limited Time
CTA: Shop Now
```

---

## Creative Guidelines

### Image Ads:
- Show real kids wearing clothes (NOT flat-lays for main ads)
- Bright, natural lighting
- Show price clearly on image
- Add "Free Shipping ₹999+" badge
- Use brand gold (#C9A94E) for text accents

### Video/Reel Ads (15-30 seconds):
1. Hook (0-3s): Cute kid moment OR question ("Looking for...")
2. Product showcase (3-15s): Multiple outfits, transitions
3. Offer + CTA (15-30s): Price, free shipping, "Shop now"
4. Music: Upbeat, happy (no copyright issues)

### Carousel Ads:
- Card 1: Hero shot (best-selling product)
- Card 2-4: Product variations / outfit ideas
- Card 5: Offer summary + CTA

---

## Budget Split (₹15,000/month)

| Campaign       | Daily  | Monthly  | % of Budget |
|----------------|--------|----------|-------------|
| Cold (Awareness)| ₹300  | ₹9,000   | 60%         |
| Warm (Retarget) | ₹130  | ₹4,000   | 27%         |
| Hot (Retention)  | ₹65  | ₹2,000   | 13%         |

---

## Optimization Rules

| Rule                                           | Action                    |
|------------------------------------------------|---------------------------|
| Ad spending > ₹500, 0 purchases               | Pause ad set              |
| CPC > ₹15 (cold audience)                     | Refresh creative          |
| ROAS < 2x after 7 days                        | Reduce budget 50%         |
| ROAS > 5x for 3+ days                         | Increase budget 20%       |
| Frequency > 3 (retargeting)                   | Refresh creative          |
| CTR < 1% (cold)                               | Test new headline/image   |
