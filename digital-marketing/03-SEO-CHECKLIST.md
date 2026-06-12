# 03 — SEO Checklist

## Priority Keywords (Target These First)

### High Intent (Buy Keywords):
| Keyword                          | Monthly Searches | Difficulty |
|----------------------------------|-----------------|------------|
| kids clothes online india        | 12,000          | Medium     |
| baby clothes online              | 18,000          | High       |
| toddler dress online             | 3,600           | Low        |
| boys ethnic wear                 | 8,100           | Medium     |
| girls party dress online         | 6,600           | Medium     |
| newborn baby clothes online      | 5,400           | Medium     |
| kids kurta pajama                | 4,400           | Low        |
| baby girl frock online           | 3,200           | Low        |

### Long-tail (Easy wins):
| Keyword                                    | Monthly Searches |
|--------------------------------------------|-----------------|
| cute baby clothes for 1 year old boy       | 1,200           |
| kids ethnic wear for wedding               | 900             |
| toddler girl birthday dress india          | 800             |
| comfortable kids clothes online india      | 600             |
| kids summer clothes cotton india           | 500             |

---

## On-Page SEO (Already Partially Done)

### ✅ Completed:
- [x] Meta titles on all pages
- [x] Meta descriptions
- [x] Structured data (ClothingStore, WebSite)
- [x] Clean URL slugs (product/category)
- [x] Alt text on product images
- [x] Mobile responsive
- [x] HTTPS (SSL)
- [x] Fast loading (Gzip, caching)

### 🔲 To Do:
- [ ] Add breadcrumb structured data (`BreadcrumbList`)
- [ ] Add `Product` structured data on product pages (price, availability, reviews)
- [ ] Create XML sitemap (`/sitemap.xml`)
- [ ] Submit sitemap to Google Search Console
- [ ] Add `robots.txt` with sitemap reference
- [ ] Create a blog section for content marketing
- [ ] Optimize images with WebP format
- [ ] Add canonical URLs to prevent duplicate content
- [ ] Internal linking between related products

---

## Technical SEO Setup

### Step 1: Google Search Console
1. Go to https://search.google.com/search-console
2. Add property: `https://indistylex.com`
3. Verify via DNS TXT record or HTML file upload
4. Submit sitemap once created

### Step 2: robots.txt (add to app root)
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /cart/
Disallow: /checkout/
Disallow: /account/
Disallow: /auth/

Sitemap: https://indistylex.com/sitemap.xml
```

### Step 3: XML Sitemap
Create dynamic sitemap including:
- Homepage
- All category pages
- All active product pages
- Static pages (about, contact, FAQ, size-guide)

### Step 4: Product Schema (add to product detail pages)
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "image": "https://indistylex.com/static/uploads/...",
  "description": "...",
  "brand": { "@type": "Brand", "name": "Indistylex" },
  "offers": {
    "@type": "Offer",
    "price": "999",
    "priceCurrency": "INR",
    "availability": "https://schema.org/InStock",
    "url": "https://indistylex.com/product/..."
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "12"
  }
}
```

---

## Content Marketing / Blog Ideas

Write 1-2 blog posts per week targeting long-tail keywords:

1. "Best Outfits for Your Toddler's First Birthday Party"
2. "How to Choose the Right Size for Kids' Clothes Online"
3. "10 Trendy Ethnic Wear Ideas for Kids This Diwali"
4. "Summer Wardrobe Essentials for Kids (2026)"
5. "Cotton vs Polyester: Which Fabric is Best for Kids?"
6. "What to Dress Your Newborn in During Monsoon Season"
7. "Boys Party Wear: Complete Guide for Indian Weddings"
8. "How to Style Matching Sibling Outfits"

---

## Local SEO

### Google My Business:
1. Create listing at https://business.google.com
2. Category: "Children's Clothing Store"
3. Add photos, business hours, website link
4. Get reviews from customers (aim for 50+ in 3 months)

### NAP Consistency (Name, Address, Phone):
```
Indistylex
MIG 79, Dhoomanganj, Preetam Nagar
Prayagraj, Uttar Pradesh 211011
+91-6394142176
```
Use this EXACT format everywhere (website footer, GMB, social profiles, directories).

---

## Monthly SEO Tasks

| Task                                    | Frequency |
|-----------------------------------------|-----------|
| Check Search Console for errors         | Weekly    |
| Monitor keyword rankings                | Weekly    |
| Publish 1-2 blog posts                  | Weekly    |
| Build 2-3 backlinks                     | Monthly   |
| Update product descriptions             | Monthly   |
| Check page speed (PageSpeed Insights)   | Monthly   |
| Review & respond to Google reviews      | Daily     |
