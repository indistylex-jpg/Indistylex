# 07 — Email Marketing

## Platform Recommendation

**Use Brevo (formerly Sendinblue)** — Free plan: 300 emails/day, automation included.
- Alternative: Mailchimp (free up to 500 contacts)
- Alternative: MailerLite (free up to 1,000 subscribers)

> Your Flask app already sends transactional emails via Gmail SMTP.
> Use a dedicated email marketing platform for bulk/automated campaigns.

---

## Email Collection Strategy

### Pop-up (Add to website):
- **Trigger**: After 10 seconds OR on exit intent
- **Offer**: "Get 10% off your first order! Join 5000+ happy parents."
- **Fields**: Email only (reduce friction)
- **Discount Code**: WELCOME10

### Footer Form:
- Already exists — ensure it connects to your email platform

### Post-Purchase:
- Auto-subscribe buyers (with consent checkbox at checkout)

### Social Media:
- "Sign up for early access to sales" in bio link

---

## Automated Email Flows (Set Once, Runs Forever)

### Flow 1: Welcome Series (New Subscriber)

**Trigger**: New email signup

| Email | Delay    | Subject                                    | Content                          |
|-------|----------|--------------------------------------------|----------------------------------|
| 1     | Immediate| Welcome to Indistylex! Here's 10% off 💛   | Brand intro + discount code      |
| 2     | Day 2    | Meet our bestsellers                       | Top 5 products + social proof    |
| 3     | Day 5    | Why parents love Indistylex                | Reviews + trust badges           |
| 4     | Day 7    | Your 10% off expires tomorrow! ⏰          | Urgency + CTA                    |

---

### Flow 2: Abandoned Cart (HIGHEST ROI)

**Trigger**: Added to cart but no purchase in 1 hour

| Email | Delay       | Subject                                 | Content                         |
|-------|-------------|-----------------------------------------|---------------------------------|
| 1     | 1 hour      | You left something cute behind! 🛒      | Cart items + "Complete order"   |
| 2     | 24 hours    | Still thinking? Here's 5% off           | Cart items + code SAVE5         |
| 3     | 48 hours    | Last chance! Your cart is expiring       | Urgency + free shipping remind  |

**Expected Recovery Rate**: 10-15% of abandoned carts

---

### Flow 3: Post-Purchase

**Trigger**: Order completed

| Email | Delay    | Subject                                    | Content                          |
|-------|----------|--------------------------------------------|----------------------------------|
| 1     | Day 0    | Order confirmed! 🎉 (#ORDER_NUMBER)       | Order summary + tracking info    |
| 2     | Day 3    | Your order is on its way! 🚚              | Shipping update + delivery date  |
| 3     | Day 7    | How's the fit? We'd love your feedback ⭐ | Review request + product link    |
| 4     | Day 14   | Complete the look! 👀                     | Cross-sell related products      |
| 5     | Day 30   | We miss you! Here's 10% off your next order| Win-back + discount code        |

---

### Flow 4: Browse Abandonment

**Trigger**: Viewed product 2+ times but no add-to-cart

| Email | Delay    | Subject                                    |
|-------|----------|--------------------------------------------|
| 1     | 4 hours  | "That [Product Name] looks great on kids!" |
| 2     | 2 days   | "Back in stock alert" (even if it was in stock)|

---

### Flow 5: Win-Back (Inactive Customers)

**Trigger**: No purchase in 60 days

| Email | Delay    | Subject                                    |
|-------|----------|--------------------------------------------|
| 1     | Day 60   | We miss you! See what's new 💛             |
| 2     | Day 75   | Exclusive: 15% off just for you            |
| 3     | Day 90   | Last chance: Your VIP discount expires     |

---

## Campaign Emails (Manual, 2-4 per month)

### Types:
1. **New Arrival** — "Just dropped: [Collection Name]"
2. **Sale Announcement** — "🚨 FLAT 30% OFF starts NOW"
3. **Festival Special** — "Diwali dress-up for your little star 🪔"
4. **Newsletter** — Parenting tip + new products + offer

### Best Send Times (India):
- **Tuesday/Thursday**: 10:00 AM or 8:00 PM
- **Saturday**: 11:00 AM (weekend shopping mood)
- **Avoid**: Monday morning, Friday evening

---

## Email Templates

### Welcome Email:
```
Subject: Welcome to Indistylex! Here's 10% off 💛

Hi {first_name}!

Welcome to the Indistylex family! We're so happy you're here. 🎉

As a thank you, here's 10% OFF your first order:

    Code: WELCOME10

What makes us special:
✅ Premium quality fabrics (soft cotton, skin-friendly)
✅ Trendy designs for ages 0-12
✅ Free shipping on orders above ₹999
✅ Easy 7-day returns

[SHOP NOW →]

See you soon!
Team Indistylex 💛
```

### Abandoned Cart Email:
```
Subject: You left something cute behind! 🛒

Hi {first_name},

Your cart is waiting! These adorable pieces won't last long:

[Product Image] [Product Name] — ₹{price}

Complete your order now and get FREE SHIPPING on orders above ₹999.

[COMPLETE MY ORDER →]

Need help? Reply to this email or WhatsApp us at +91-6394142176

💛 Team Indistylex
```

### Review Request:
```
Subject: How's the fit? ⭐ We'd love your feedback

Hi {first_name}!

We hope your little one is loving their new [product_name]! 🥰

Would you mind leaving a quick review? It takes just 30 seconds 
and helps other parents make the right choice.

[LEAVE A REVIEW →]

As a thank you, you'll get 5% off your next order!

💛 Team Indistylex
```

---

## Key Email Metrics

| Metric          | Target     |
|-----------------|------------|
| Open Rate       | 25-35%     |
| Click Rate      | 3-5%       |
| Unsubscribe     | < 0.5%     |
| Cart Recovery   | 10-15%     |
| Revenue/Email   | ₹5-15      |

---

## Segmentation Strategy

| Segment              | Criteria                           | Send Them                    |
|----------------------|------------------------------------|------------------------------|
| New subscribers      | Signed up < 7 days                 | Welcome series               |
| Active buyers        | Purchased in last 30 days          | New arrivals, cross-sells    |
| High spenders        | AOV > ₹1,500                       | Premium/exclusive collections|
| Boys parents         | Bought boys' items                 | Boys new arrivals            |
| Girls parents        | Bought girls' items                | Girls new arrivals           |
| Newborn parents      | Bought newborn items               | Age-appropriate upgrades     |
| Lapsed              | No purchase 60+ days               | Win-back discounts           |
