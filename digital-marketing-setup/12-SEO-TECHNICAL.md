# 12 — SEO Technical Setup

## What This Does
Implements technical SEO on your website: sitemap, robots.txt, schema markup, page speed, and on-page optimization so Google ranks your pages higher.

**Time needed**: 1-2 hours

---

## Step 1: robots.txt

### Create/Update robots.txt
File: `app/static/robots.txt` (serve at root URL)

```txt
# robots.txt for indistylex.com
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /cart/
Disallow: /checkout/
Disallow: /user/orders
Disallow: /user/profile
Disallow: /static/uploads/temp/

# Sitemap
Sitemap: https://indistylex.com/sitemap.xml
```

### Serve at Root URL
Add route in Flask (if not already):
```python
@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')
```

---

## Step 2: XML Sitemap

### Create Dynamic Sitemap
Add a route that generates sitemap from your products:

```python
from flask import make_response
from datetime import datetime

@app.route('/sitemap.xml')
def sitemap():
    pages = []
    
    # Static pages
    static_pages = [
        ('https://indistylex.com/', '1.0', 'daily'),
        ('https://indistylex.com/shop', '0.9', 'daily'),
        ('https://indistylex.com/about', '0.5', 'monthly'),
        ('https://indistylex.com/contact', '0.5', 'monthly'),
        ('https://indistylex.com/faq', '0.5', 'monthly'),
        ('https://indistylex.com/size-guide', '0.6', 'monthly'),
    ]
    
    # Category pages
    categories = Category.query.all()
    for cat in categories:
        pages.append((f'https://indistylex.com/shop/{cat.slug}', '0.8', 'daily'))
    
    # Product pages
    products = Product.query.filter_by(is_active=True).all()
    for product in products:
        pages.append((f'https://indistylex.com/product/{product.slug}', '0.7', 'weekly'))
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url, priority, freq in static_pages + pages:
        xml += f'  <url>\n'
        xml += f'    <loc>{url}</loc>\n'
        xml += f'    <changefreq>{freq}</changefreq>\n'
        xml += f'    <priority>{priority}</priority>\n'
        xml += f'  </url>\n'
    
    xml += '</urlset>'
    
    response = make_response(xml)
    response.headers['Content-Type'] = 'application/xml'
    return response
```

### Submit to Google Search Console:
1. Go to Search Console → **Sitemaps**
2. Enter: `sitemap.xml`
3. Click **"Submit"**

---

## Step 3: Meta Tags (On-Page SEO)

### 3.1 Base Template Meta Tags
Add to `base.html` `<head>`:

```html
<!-- Primary Meta Tags -->
<title>{% block title %}Indistylex - Premium Kids Clothing Online{% endblock %}</title>
<meta name="description" content="{% block meta_description %}Shop premium kids clothing for boys & girls aged 0-14. Stylish, comfortable & affordable fashion. Free shipping across India. COD available.{% endblock %}">
<meta name="keywords" content="{% block meta_keywords %}kids clothing, children's fashion, boys clothes, girls dresses, kids wear online, Indian kids fashion{% endblock %}">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="{% block og_type %}website{% endblock %}">
<meta property="og:url" content="{{ request.url }}">
<meta property="og:title" content="{% block og_title %}Indistylex - Premium Kids Clothing{% endblock %}">
<meta property="og:description" content="{% block og_description %}Premium kids clothing for 0-14 years. Free shipping pan India.{% endblock %}">
<meta property="og:image" content="{% block og_image %}https://indistylex.com/static/images/og-default.jpg{% endblock %}">
<meta property="og:site_name" content="Indistylex">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{% block twitter_title %}Indistylex - Premium Kids Clothing{% endblock %}">
<meta name="twitter:description" content="{% block twitter_description %}Premium kids clothing for 0-14 years.{% endblock %}">
<meta name="twitter:image" content="{% block twitter_image %}https://indistylex.com/static/images/og-default.jpg{% endblock %}">

<!-- Canonical URL -->
<link rel="canonical" href="{{ request.url }}">
```

### 3.2 Product Page Meta Tags
In product detail template:
```html
{% block title %}{{ product.name }} | Buy Online - Indistylex{% endblock %}
{% block meta_description %}Buy {{ product.name }} for ₹{{ product.price }}. {{ product.short_description }}. Free shipping, COD available. Shop at Indistylex.{% endblock %}
{% block og_type %}product{% endblock %}
{% block og_image %}https://indistylex.com{{ product.image_url }}{% endblock %}
```

### 3.3 Category Page Meta Tags
```html
{% block title %}{{ category.name }} - Kids Clothing Online | Indistylex{% endblock %}
{% block meta_description %}Shop {{ category.name }} for kids at Indistylex. Premium quality, comfortable fabrics. Ages 0-14. Free shipping across India.{% endblock %}
```

---

## Step 4: Schema Markup (Structured Data)

### 4.1 Organization Schema (Homepage)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Indistylex",
  "url": "https://indistylex.com",
  "logo": "https://indistylex.com/static/images/logo.png",
  "description": "Premium kids clothing brand in India",
  "sameAs": [
    "https://www.instagram.com/indistylex",
    "https://www.facebook.com/indistylex"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+91-XXXXXXXXXX",
    "contactType": "customer service",
    "availableLanguage": ["English", "Hindi"]
  }
}
</script>
```

### 4.2 Product Schema (Product Pages)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{ product.name }}",
  "image": "https://indistylex.com{{ product.image_url }}",
  "description": "{{ product.description }}",
  "brand": {
    "@type": "Brand",
    "name": "Indistylex"
  },
  "offers": {
    "@type": "Offer",
    "url": "{{ request.url }}",
    "priceCurrency": "INR",
    "price": "{{ product.price }}",
    "availability": "https://schema.org/{% if product.stock > 0 %}InStock{% else %}OutOfStock{% endif %}",
    "seller": {
      "@type": "Organization",
      "name": "Indistylex"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{{ product.avg_rating }}",
    "reviewCount": "{{ product.review_count }}"
  }
}
</script>
```

### 4.3 BreadcrumbList Schema
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://indistylex.com"},
    {"@type": "ListItem", "position": 2, "name": "{{ category.name }}", "item": "https://indistylex.com/shop/{{ category.slug }}"},
    {"@type": "ListItem", "position": 3, "name": "{{ product.name }}"}
  ]
}
</script>
```

### 4.4 Local Business Schema (If physical store)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ClothingStore",
  "name": "Indistylex",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Your Address",
    "addressLocality": "Your City",
    "addressRegion": "Your State",
    "postalCode": "Your Pincode",
    "addressCountry": "IN"
  },
  "openingHours": "Mo-Su 10:00-21:30",
  "telephone": "+91-XXXXXXXXXX",
  "url": "https://indistylex.com",
  "priceRange": "₹₹"
}
</script>
```

---

## Step 5: Page Speed Optimization

### 5.1 Image Optimization
```python
# In your image processing pipeline:
from PIL import Image

def optimize_image(image_path, max_width=800, quality=80):
    img = Image.open(image_path)
    
    # Resize if too large
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    # Convert to WebP (smaller file size)
    webp_path = image_path.rsplit('.', 1)[0] + '.webp'
    img.save(webp_path, 'WebP', quality=quality)
    
    return webp_path
```

### 5.2 Lazy Loading Images
```html
<!-- Add loading="lazy" to all images below the fold -->
<img src="{{ product.image_url }}" alt="{{ product.name }}" loading="lazy" width="300" height="300">
```

### 5.3 Minify CSS/JS
Add to your build process or use Flask extensions:
```python
# requirements.txt
Flask-Assets==2.0
cssmin==0.2.0
jsmin==3.0.1
```

### 5.4 Enable Gzip/Brotli (Apache)
In Apache config:
```apache
# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json
    AddOutputFilterByType DEFLATE image/svg+xml application/xml
</IfModule>
```

### 5.5 Browser Caching
```apache
# Cache static assets
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/webp "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

### 5.6 Test Page Speed
- **Google PageSpeed**: https://pagespeed.web.dev
- **GTmetrix**: https://gtmetrix.com
- Target: 90+ mobile score

---

## Step 6: URL Structure

### SEO-Friendly URLs:
| Bad ❌ | Good ✅ |
|--------|---------|
| `/product/123` | `/product/boys-cotton-tshirt-blue-stripes` |
| `/category/5` | `/shop/boys-clothing` |
| `/search?q=kurta` | `/shop?q=kurta` (keep for search) |

### URL Rules:
- Lowercase only
- Hyphens (not underscores)
- Include target keyword
- Keep under 60 characters
- No stop words (and, the, of) unless natural

---

## Step 7: Internal Linking

### Key Internal Links to Add:
1. **Homepage** → links to all category pages
2. **Category pages** → links to product pages
3. **Product pages** → links to related products
4. **Blog posts** → links to relevant product/category
5. **Footer** → links to all important pages
6. **Breadcrumbs** → structured navigation on every page

### Footer Links (SEO + UX):
```
Shop              Help                Company
├── Boys          ├── Size Guide      ├── About Us
├── Girls         ├── Shipping        ├── Contact
├── Ethnic Wear   ├── Returns         ├── Privacy Policy
├── Party Wear    ├── FAQ             ├── Terms
├── New Arrivals  ├── Track Order     ├── Blog
└── Sale          └── Contact Us      └── Careers
```

---

## Step 8: Mobile SEO

### Mobile Checklist:
- [ ] Responsive design (works on all screen sizes)
- [ ] Touch targets minimum 44x44px
- [ ] No horizontal scroll
- [ ] Fast loading (<3 seconds on 3G)
- [ ] Easy to read text (16px minimum)
- [ ] Click-to-call phone numbers
- [ ] Thumb-friendly navigation
- [ ] No intrusive popups on mobile

### Test Mobile:
1. Google Mobile-Friendly Test: https://search.google.com/test/mobile-friendly
2. Chrome DevTools → Toggle device toolbar

---

## Step 9: Content SEO (Blog Setup)

### Blog Categories for Kids Clothing:
1. **Style Guides** — "How to style your toddler for Diwali"
2. **Parenting Tips** — "Choosing comfortable fabrics for sensitive skin"
3. **Seasonal** — "Back to school essentials checklist 2025"
4. **Product Care** — "How to wash and maintain kids' clothes"

### Target Keywords (Blog Post Ideas):

| Keyword | Volume | Difficulty | Blog Title |
|---------|--------|------------|------------|
| kids fashion india | 2,400 | Medium | "Top Kids Fashion Trends in India 2025" |
| best fabric for kids | 1,600 | Low | "Best Fabrics for Children: A Parent's Guide" |
| diwali dress for kids | 3,200 | High | "20 Diwali Outfit Ideas for Kids" |
| kids clothing size guide | 900 | Low | "Complete Size Guide: How to Find the Perfect Fit" |
| birthday dress for girls | 2,100 | Medium | "15 Beautiful Birthday Dresses for Girls" |

---

## ✅ Checklist — You're Done When:

- [ ] robots.txt live at /robots.txt
- [ ] XML sitemap live at /sitemap.xml
- [ ] Sitemap submitted to Google Search Console
- [ ] Meta title + description on ALL pages
- [ ] Open Graph tags on all pages
- [ ] Canonical URLs set
- [ ] Product schema on product pages
- [ ] Organization schema on homepage
- [ ] BreadcrumbList schema implemented
- [ ] Images optimized (WebP, lazy loading)
- [ ] Gzip compression enabled
- [ ] Browser caching configured
- [ ] PageSpeed score 90+ (mobile)
- [ ] Mobile-friendly test passing
- [ ] Internal linking structure done
- [ ] URL structure is SEO-friendly
- [ ] H1 tag on every page (only one)
- [ ] Alt text on all images
- [ ] 404 page created and helpful

---

## SEO Monitoring (Monthly)

| Check | Tool | Target |
|-------|------|--------|
| Organic traffic | GA4 | Growing month-over-month |
| Keyword rankings | Google Search Console | Top 10 for brand terms |
| Indexed pages | Search Console → Coverage | All product pages indexed |
| Core Web Vitals | Search Console → Experience | All "Good" |
| Backlinks | Free: Google Alerts / Ahrefs free | Growing |
| Errors | Search Console → Coverage | 0 errors |
