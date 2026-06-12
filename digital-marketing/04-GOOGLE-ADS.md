# 04 — Google Ads Setup

## Account Setup

### Step 1: Create Google Ads Account
1. Go to https://ads.google.com
2. Sign in with your business Google account (indistylex@gmail.com)
3. Choose "Expert Mode" (bottom of page) — NOT Smart Campaign
4. Set billing country: India, Currency: INR
5. Add payment method (credit/debit card or UPI)

### Step 2: Link Accounts
- Link Google Analytics 4 (for conversion tracking)
- Link Google Merchant Center (for Shopping ads)
- Link Google Search Console

### Step 3: Set Up Conversion Tracking
Track these actions:
- **Purchase** (primary) — fire on `/checkout/success` page
- **Add to Cart** (secondary)
- **Begin Checkout** (secondary)

---

## Campaign 1: Google Shopping Ads (HIGHEST PRIORITY)

### Why: Shoppers see your product image + price directly in search results.

### Setup Google Merchant Center:
1. Go to https://merchants.google.com
2. Verify & claim website: indistylex.com
3. Create product feed (you'll need to build a feed URL)

### Product Feed Requirements:
| Field          | Example Value                                    |
|----------------|--------------------------------------------------|
| id             | SKU-001                                          |
| title          | Kids Cotton Kurta Pajama Set - Blue (2-3 Years)  |
| description    | Comfortable cotton kurta pajama for boys...       |
| link           | https://indistylex.com/product/kids-kurta-blue   |
| image_link     | https://indistylex.com/static/uploads/...        |
| price          | 1299.00 INR                                      |
| sale_price     | 999.00 INR                                       |
| availability   | in_stock                                         |
| brand          | Indistylex                                       |
| condition      | new                                              |
| age_group      | toddler / kids                                   |
| gender         | male / female / unisex                           |
| google_product_category | Apparel & Accessories > Clothing > Kids |

### Shopping Campaign Settings:
- **Budget**: ₹500/day (start)
- **Bidding**: Maximize clicks (first 2 weeks), then Target ROAS
- **Target ROAS**: 400% (₹4 revenue per ₹1 spent)
- **Negative keywords**: free, used, second hand, wholesale, bulk

---

## Campaign 2: Search Ads (Brand + High-Intent)

### Ad Group 1: Brand Keywords
**Keywords**: indistylex, indistylex.com, indistylex clothing
**Budget**: ₹100/day
**Why**: Protect brand name, cheap clicks (₹1-3/click)

### Ad Group 2: High-Intent Kids Clothing
**Keywords**:
```
kids clothes online
buy kids clothes online india
baby clothes online shopping
toddler dresses online india
boys ethnic wear online
girls party dress buy online
newborn clothes online india
kids kurta pajama online
```

**Match Type**: Phrase match for all

**Ad Copy Template**:
```
Headline 1: Kids Clothes Online | Indistylex
Headline 2: Premium Quality from ₹499
Headline 3: Free Shipping Above ₹999
Description 1: Shop trendy & comfortable kids' clothing. Newborn to 12 years. 
               100% cotton, skin-friendly fabrics. Easy 7-day returns.
Description 2: New arrivals every week. Ethnic, casual & party wear. 
               India's fastest-growing kids' fashion brand. Order now!
```

**Budget**: ₹300/day
**Bidding**: Manual CPC (₹8-15/click max)
**Target CPA**: ₹250-350

### Ad Group 3: Occasion-Based
**Keywords**:
```
kids birthday dress
children wedding outfit
baby first birthday dress
kids diwali clothes
toddler party wear
```

---

## Campaign 3: Remarketing (Display)

### Target: People who visited site but didn't buy

**Audience Segments**:
1. Visited product page but no add-to-cart (show that product)
2. Added to cart but didn't checkout (show discount offer)
3. Past buyers — 30+ days ago (show new arrivals)

**Ad Sizes** (create these):
- 300x250 (Medium Rectangle)
- 728x90 (Leaderboard)
- 160x600 (Wide Skyscraper)
- 300x600 (Half Page)
- 320x50 (Mobile Banner)

**Budget**: ₹200/day
**Bidding**: Target CPA ₹150

---

## Negative Keywords (Add to ALL campaigns)

```
free
wholesale
bulk
manufacturer
supplier
used
second hand
sewing pattern
DIY
how to make
jobs
careers
salary
```

---

## Budget Allocation (₹10,000/month total)

| Campaign           | Daily   | Monthly | Priority |
|--------------------|---------|---------|----------|
| Shopping Ads       | ₹200    | ₹6,000  | HIGH     |
| Search (Intent)    | ₹100    | ₹3,000  | MEDIUM   |
| Remarketing        | ₹35     | ₹1,000  | LOW      |

---

## Optimization Schedule

| Task                              | Frequency |
|-----------------------------------|-----------|
| Check search terms, add negatives | Daily     |
| Adjust bids on keywords           | 3x/week   |
| Test new ad copy variations       | Weekly    |
| Review conversion data            | Weekly    |
| Pause underperforming keywords    | Weekly    |
| Add new keywords from Search Console | Bi-weekly |
