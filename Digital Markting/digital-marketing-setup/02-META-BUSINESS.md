# 02 — Meta Business Suite Setup

## What This Does
Sets up Facebook Business Page, Business Manager, and Ad Account — the foundation for ALL Meta advertising (Facebook + Instagram ads).

**Time needed**: 45 minutes

---

## Step 1: Create Facebook Business Page

### 1.1 Go to Facebook
1. Log into your **personal** Facebook account
2. Go to: https://www.facebook.com/pages/create
3. Select **"Business or Brand"**

### 1.2 Page Information

| Field | Enter |
|-------|-------|
| Page Name | `Indistylex - Kids Fashion` |
| Category | `Children's Clothing Store` |
| Bio | `Premium kids fashion for 0-14 years. Style meets comfort. 🇮🇳 Free shipping across India.` |

### 1.3 Add Profile Picture
- Upload your **square logo** (400x400px minimum)
- This appears in all comments, messages, and ads

### 1.4 Add Cover Photo
- Size: **820 x 312px** (desktop) / **640 x 360px** (mobile)
- Use a collection showcase or lifestyle image with kids
- Include your tagline: "Style That Speaks, Quality That Lasts"

### 1.5 Complete Page Info
Go to **Settings → Page Info**:

| Field | Value |
|-------|-------|
| Username | `@indistylex` |
| Website | `https://indistylex.com` |
| Phone | Your business number |
| Email | `hello@indistylex.com` |
| Hours | Mon-Sun 10AM-9:30PM |
| Price Range | `₹₹` (moderate) |
| About | See description below |

### About Section (255 characters):
```
India's premium kids clothing brand. Stylish, comfortable & affordable fashion 
for boys & girls (0-14 yrs). Ethnic wear, party wear, casuals & more. 
Free shipping | Easy returns | COD available.
```

---

## Step 2: Set Up Meta Business Manager

> ⚠️ **Business Manager is REQUIRED for running ads.** Don't skip this.

### 2.1 Create Business Manager Account
1. Go to: https://business.facebook.com/create
2. Enter:
   - **Business Name**: `Indistylex`
   - **Your Name**: (your full name)
   - **Business Email**: `hello@indistylex.com`
3. Click **"Submit"**
4. Verify email (check inbox)

### 2.2 Add Your Facebook Page
1. In Business Manager → **Settings** → **Accounts** → **Pages**
2. Click **"Add"** → **"Add a Page"**
3. Enter your page name: `Indistylex - Kids Fashion`
4. Click **"Add Page"**

### 2.3 Add People (Team Access)
1. Go to **Settings** → **People**
2. Add any team members with appropriate roles:
   - **Admin**: Full access (only you initially)
   - **Employee**: Can manage ads but not settings
   - **Analyst**: View-only reports

---

## Step 3: Create Ad Account

### 3.1 Set Up Ad Account
1. In Business Manager → **Settings** → **Accounts** → **Ad Accounts**
2. Click **"Add"** → **"Create a New Ad Account"**
3. Enter:
   - **Ad Account Name**: `Indistylex Ads`
   - **Time Zone**: `(GMT+5:30) India Standard Time`
   - **Currency**: `INR (₹)`
4. Click **"Create"**

### 3.2 Add Payment Method
1. Go to **Ad Account** → **Payment Settings**
2. Add payment method:
   - **Credit/Debit Card** (Visa, Mastercard) — recommended
   - **UPI** (available in India)
   - **Net Banking**
3. Set spending limit (optional but recommended):
   - Daily: ₹1,000 initially
   - Monthly: ₹15,000 initially

> 💡 **TIP**: Start with a low spending limit. Increase as you learn what works.

---

## Step 4: Verify Your Business (Important for Ads)

### Why Verify?
- Unlocks higher ad spend limits
- Required for custom audiences
- Needed for Instagram Shopping
- Builds trust with Meta

### 4.1 Start Verification
1. Go to: **Business Settings** → **Security Center**
2. Click **"Start Verification"**
3. Choose verification method:

### Documents Needed (one of these):
- GST Registration Certificate
- Business PAN Card
- Shop & Establishment Certificate
- Udyam Registration (MSME)
- Business utility bill

### 4.2 Submit & Wait
- Upload clear scan/photo of document
- Verification takes **2-5 business days**
- You'll get email notification when approved

---

## Step 5: Install Meta Pixel on Website

### 5.1 Create Pixel
1. Go to: **Events Manager** (https://business.facebook.com/events_manager)
2. Click **"Connect Data Sources"** → **"Web"**
3. Select **"Meta Pixel"**
4. Name it: `Indistylex Pixel`
5. Enter website: `https://indistylex.com`

### 5.2 Get Pixel Code
After creation, you'll get a Pixel ID (like `316334889540123456`)

### 5.3 Add to Website
The pixel code needs to be added to your website's `<head>` section. 

Add this to your `base.html` template:

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
fbq('init', 'YOUR_PIXEL_ID_HERE');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=YOUR_PIXEL_ID_HERE&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->
```

### 5.4 Add Event Tracking
Add these events to relevant pages:

```javascript
// On product page view
fbq('track', 'ViewContent', {
  content_name: 'Product Name',
  content_category: 'Kids Clothing',
  content_ids: ['SKU123'],
  content_type: 'product',
  value: 499,
  currency: 'INR'
});

// On Add to Cart
fbq('track', 'AddToCart', {
  content_ids: ['SKU123'],
  content_type: 'product',
  value: 499,
  currency: 'INR'
});

// On Purchase (success page)
fbq('track', 'Purchase', {
  content_ids: ['SKU123', 'SKU456'],
  content_type: 'product',
  value: 998,
  currency: 'INR'
});
```

### 5.5 Verify Pixel is Working
1. Install **Meta Pixel Helper** Chrome Extension
2. Visit your website
3. Extension should show green checkmark with events firing

---

## Step 6: Connect Instagram Account

1. In Business Manager → **Settings** → **Accounts** → **Instagram Accounts**
2. Click **"Add"** → **"Connect Your Instagram Account"**
3. Log in with Instagram credentials
4. Authorize connection

> This allows you to run Instagram ads from Business Manager.

---

## Step 7: Set Up Catalog (for Shopping Ads)

### 7.1 Create Catalog
1. Go to: **Commerce Manager** (https://business.facebook.com/commerce)
2. Click **"Create a Catalog"**
3. Select **"E-commerce"**
4. Name: `Indistylex Products`
5. Choose **"Upload Product Info"** (manual) or **"Connect e-commerce platform"**

### 7.2 Add Products Manually
For each product:

| Field | Example |
|-------|---------|
| Title | Boys Cotton T-Shirt - Blue Stripes |
| Description | Soft 100% cotton t-shirt for boys... |
| Website Link | https://indistylex.com/product/boys-tshirt-blue |
| Image Link | https://indistylex.com/static/uploads/product.jpg |
| Price | 499 INR |
| Sale Price | 399 INR (if on sale) |
| Brand | Indistylex |
| Condition | new |
| Availability | in stock |
| Age Group | kids |
| Gender | male / female / unisex |

### 7.3 Product Feed (Automated - Better)
Create a CSV/XML feed URL that auto-updates. We can set this up on your website later.

---

## Step 8: Create Custom Audiences (for Retargeting)

### 8.1 Website Visitors
1. Go to **Audiences** → **Create Audience** → **Custom Audience**
2. Source: **Website**
3. Create these audiences:
   - All visitors (last 30 days)
   - Product viewers (last 14 days)
   - Add to cart but didn't purchase (last 7 days)
   - Purchasers (last 180 days)

### 8.2 Engagement Audiences
- People who engaged with Instagram (last 30 days)
- People who watched 50%+ of videos (last 30 days)
- People who saved posts (last 30 days)

### 8.3 Lookalike Audiences (Create AFTER 100+ purchases)
- 1% Lookalike of Purchasers (best quality)
- 2% Lookalike of Add to Cart
- 3% Lookalike of Website Visitors

---

## ✅ Checklist — You're Done When:

- [ ] Facebook Page created and fully filled
- [ ] Username claimed (@indistylex)
- [ ] Business Manager created
- [ ] Page added to Business Manager
- [ ] Ad Account created (INR currency)
- [ ] Payment method added
- [ ] Business verification submitted
- [ ] Meta Pixel created
- [ ] Pixel installed on website
- [ ] Pixel verified with Pixel Helper extension
- [ ] Instagram account connected
- [ ] Product catalog created
- [ ] At least 10 products in catalog
- [ ] Custom audiences created

---

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "Ad account disabled" | Appeal at https://www.facebook.com/help/contact/531795498479411 |
| Pixel not firing | Check browser console for errors, verify code placement |
| Business verification rejected | Ensure document matches business name exactly |
| Can't create lookalike | Need minimum 100 people in source audience |
| Page restricted from advertising | Check for policy violations, appeal decision |
| "Confirm your identity" | Upload government ID — required for ad accounts in India |
