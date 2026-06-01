# 04 — Google Ads & Merchant Center Setup

## What This Does
Sets up Google Ads for Search/Shopping campaigns + Google Merchant Center for product listings. When parents search "buy kids clothes online", YOUR products show up.

**Time needed**: 1-2 hours

---

## Part A: Google Merchant Center

### Step 1: Create Merchant Center Account

1. Go to: https://merchants.google.com
2. Sign in with your business Google account
3. Click **"Get Started"**
4. Enter:
   - **Business name**: `Indistylex`
   - **Country**: India
   - **Time zone**: IST
5. Agree to Terms of Service

### Step 2: Verify & Claim Website

1. Go to **Settings** → **Business Information** → **Website**
2. Enter: `https://indistylex.com`
3. Verification method — choose ONE:

**Method 1: HTML Tag (Easiest)**
Add this to your `base.html` `<head>`:
```html
<meta name="google-site-verification" content="YOUR_VERIFICATION_CODE" />
```

**Method 2: HTML File**
Download the verification file and place it at your website root.

4. Click **"Verify"** then **"Claim"**

### Step 3: Set Up Shipping

1. Go to **Settings** → **Shipping and Returns**
2. Click **"Add shipping service"**

**Free Shipping Setup:**
| Field | Value |
|-------|-------|
| Service name | Free Standard Shipping |
| Country | India |
| Currency | INR |
| Delivery time | 3-7 business days |
| Shipping cost | Free (₹0) |
| Minimum order | ₹499 (if applicable) |

**COD Setup (if offering):**
| Field | Value |
|-------|-------|
| Service name | Cash on Delivery |
| Delivery time | 3-7 business days |
| Shipping cost | ₹50 |

### Step 4: Set Up Return Policy

1. Go to **Settings** → **Shipping and Returns** → **Return policies**
2. Add policy:
   - Return window: **7 days**
   - Return method: Pickup / Drop-off
   - Restocking fee: None
   - Condition: Unused with tags

### Step 5: Add Products (Product Feed)

#### Option 1: Manual Upload (Small Catalog <50 products)
1. Go to **Products** → **All Products** → **Add Products**
2. Click **"Add products one at a time"**
3. Fill for each product:

| Field | Example | Required |
|-------|---------|----------|
| id | `SKU-BOYS-TSHIRT-001` | ✅ |
| title | `Boys Cotton T-Shirt Blue Stripes - 4-5 Years` | ✅ |
| description | `Soft 100% cotton t-shirt for boys. Comfortable...` | ✅ |
| link | `https://indistylex.com/product/boys-tshirt-blue` | ✅ |
| image_link | `https://indistylex.com/static/uploads/product1.jpg` | ✅ |
| price | `499 INR` | ✅ |
| sale_price | `399 INR` | Optional |
| availability | `in_stock` | ✅ |
| brand | `Indistylex` | ✅ |
| condition | `new` | ✅ |
| age_group | `kids` | ✅ |
| gender | `male` / `female` / `unisex` | ✅ |
| color | `Blue` | ✅ |
| size | `4-5 Years` | ✅ |
| item_group_id | `BOYS-TSHIRT-BLUE` | For variants |
| google_product_category | `Apparel & Accessories > Clothing > Baby & Toddler Clothing` | ✅ |

#### Option 2: Google Sheets Feed (Medium Catalog)
1. Create Google Sheet with all columns above
2. In Merchant Center → **Products** → **Feeds** → **Add feed**
3. Select **"Google Sheets"**
4. Link your spreadsheet
5. Set fetch schedule: Daily

#### Option 3: Website Crawl (Automated)
1. In Merchant Center → **Products** → **Feeds** → **Add feed**
2. Select **"Website crawl"**
3. Google will find products with structured data (schema.org)
4. Requires proper Product schema on your website pages

### Step 6: Fix Disapprovals
After uploading, check **Diagnostics** tab:

| Common Issue | Fix |
|--------------|-----|
| Missing GTIN | Add `identifier_exists: false` for custom products |
| Image too small | Use 800x800px minimum |
| Price mismatch | Ensure feed price = website price |
| Missing shipping | Complete shipping settings |
| Policy violation | Remove prohibited claims |

---

## Part B: Google Ads Account

### Step 7: Create Google Ads Account

1. Go to: https://ads.google.com
2. Click **"Start now"**
3. Select **"Switch to Expert Mode"** (bottom of page) ← IMPORTANT!
4. Click **"Create an account without a campaign"**
5. Confirm:
   - Country: India
   - Currency: INR
   - Time zone: IST
6. Click **"Submit"**

> ⚠️ ALWAYS use Expert Mode. Smart campaigns waste money with no control.

### Step 8: Set Up Conversion Tracking

1. Go to **Tools & Settings** → **Measurement** → **Conversions**
2. Click **"+ New conversion action"** → **"Website"**
3. Enter: `https://indistylex.com`
4. Set up these conversions:

**Purchase (Most Important):**
| Setting | Value |
|---------|-------|
| Name | Purchase |
| Category | Purchase |
| Value | Use different values for each conversion |
| Count | Every conversion |

**Add to Cart:**
| Setting | Value |
|---------|-------|
| Name | Add to Cart |
| Category | Add to cart |
| Value | ₹0 (or average cart value) |
| Count | Every conversion |

5. Install the **Google Ads tag** on your website (or use Google Tag Manager)

### Step 9: Link Merchant Center to Google Ads

1. In Merchant Center → **Settings** → **Linked accounts**
2. Click **"Link account"** → Google Ads
3. Enter your Google Ads customer ID
4. Approve in Google Ads

### Step 10: Set Up Your First Campaign

---

## Campaign 1: Google Shopping (Start Here)

### Create Shopping Campaign:
1. Click **"+ New Campaign"**
2. Goal: **Sales**
3. Campaign type: **Shopping**
4. Select Merchant Center account
5. Country: India

### Settings:
| Setting | Value |
|---------|-------|
| Campaign name | `Shopping - All Products` |
| Bidding | Maximize clicks (start) → switch to Target ROAS later |
| Daily budget | ₹300-500/day |
| Networks | Google Search + Search Partners |
| Devices | All (mobile priority) |
| Location | All India |

### Product Groups:
- Start with **All Products** in one group
- After 2 weeks, segment by:
  - Category (Boys / Girls / Ethnic / Party)
  - Price range
  - Best sellers vs others

---

## Campaign 2: Brand Search

### Create Search Campaign:
1. **"+ New Campaign"** → **Sales** → **Search**
2. Settings:

| Setting | Value |
|---------|-------|
| Campaign name | `Search - Brand Keywords` |
| Bidding | Maximize clicks |
| Daily budget | ₹100-200/day |
| Location | India |
| Language | English + Hindi |

### Keywords (Exact + Phrase Match):
```
[indistylex]
"indistylex"
[indistylex kids]
"indistylex clothing"
[indistylex.com]
```

### Ad Copy:
**Headline 1**: Indistylex - Kids Fashion
**Headline 2**: Premium Quality, Affordable Prices  
**Headline 3**: Free Shipping Pan India
**Description 1**: Shop stylish & comfortable kids clothing for boys & girls aged 0-14. Ethnic wear, party wear, casuals & more. COD available.
**Description 2**: ✨ New Arrivals Every Week. Easy 7-day Returns. Trusted by 1000+ Parents. Shop Now!
**Final URL**: https://indistylex.com

---

## Campaign 3: Category Search (Week 3+)

### Keywords (Broad Match Modified → Phrase Match):
```
"kids clothing online india"
"buy children's clothes"
"boys party wear online"
"girls ethnic dress"
"kids kurta pajama online"
"baby girl frock online"
"toddler clothes india"
```

### Negative Keywords (ADD THESE — saves money):
```
-free
-wholesale
-bulk
-used
-second hand
-adult
-men
-women
-DIY
-sewing pattern
-job
-career
```

### Ad Copy Template:
**Headline 1**: {Keyword Related} - Indistylex
**Headline 2**: Soft Fabrics, Stylish Designs
**Headline 3**: ₹299 Onwards | Free Ship
**Description**: Premium kids clothing online. Comfortable cotton fabrics, trendy designs for ages 0-14. Free shipping + COD. Shop new arrivals now!

---

## Step 11: Set Up Remarketing

### Create Remarketing List:
1. **Tools** → **Audience Manager** → **+ Audience**
2. Create:
   - All visitors (30 days)
   - Product viewers who didn't buy (14 days)
   - Cart abandoners (7 days)
   - Past buyers (180 days)

### Create Display Remarketing Campaign:
- Type: Display
- Audience: Cart abandoners
- Budget: ₹100-200/day
- Ads: Show the exact products they viewed

---

## Budget Allocation (Starting)

| Campaign | Daily Budget | Monthly |
|----------|-------------|---------|
| Shopping - All Products | ₹400 | ₹12,000 |
| Search - Brand | ₹100 | ₹3,000 |
| Search - Category | ₹300 | ₹9,000 |
| Display - Remarketing | ₹150 | ₹4,500 |
| **Total** | **₹950** | **₹28,500** |

> Start with Shopping + Brand only (₹500/day). Add others after 2 weeks.

---

## Step 12: Optimization Checklist (Weekly)

| Task | When |
|------|------|
| Check search terms, add negatives | Mon & Thu |
| Pause underperforming keywords | Weekly |
| Adjust bids on top performers | Weekly |
| Review product disapprovals | Weekly |
| Check conversion tracking is working | Weekly |
| Update product feed | When inventory changes |
| A/B test ad copy | Bi-weekly |
| Review device performance | Monthly |
| Review location performance | Monthly |

---

## ✅ Checklist — You're Done When:

- [ ] Merchant Center account created
- [ ] Website verified and claimed
- [ ] Shipping configured
- [ ] Return policy added
- [ ] Product feed uploaded (10+ products minimum)
- [ ] All product disapprovals fixed
- [ ] Google Ads account created (Expert Mode)
- [ ] Conversion tracking installed
- [ ] Merchant Center linked to Ads
- [ ] Shopping campaign live
- [ ] Brand Search campaign live
- [ ] Negative keywords added
- [ ] Remarketing audiences created
- [ ] Daily budget set with spending limit

---

## Key Metrics to Track

| Metric | Target (Month 1) | Good (Month 3+) |
|--------|-------------------|------------------|
| ROAS (Return on Ad Spend) | 2x | 4-6x |
| CPC (Cost per Click) | ₹3-8 | ₹2-5 |
| CTR (Click-through Rate) | 2-3% | 4-6% |
| Conversion Rate | 1-2% | 3-5% |
| Cost per Acquisition | ₹200-400 | ₹100-200 |
