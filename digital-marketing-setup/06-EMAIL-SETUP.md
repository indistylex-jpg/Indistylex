# 06 — Email Marketing Setup (Brevo/Sendinblue)

## What This Does
Sets up automated email marketing: welcome series, abandoned cart recovery, order confirmations, and promotional newsletters.

**Time needed**: 1-2 hours

---

## Why Brevo?
- Free plan: 300 emails/day (9,000/month)
- Built-in automation workflows
- WhatsApp integration
- Good deliverability in India
- Indian payment support

---

## Step 1: Create Brevo Account

1. Go to: https://www.brevo.com
2. Click **"Sign Up Free"**
3. Enter:
   - Email: `hello@indistylex.com`
   - Password: (strong password)
   - Company: `Indistylex`
4. Verify email
5. Complete profile:
   - Company name: Indistylex
   - Website: `https://indistylex.com`
   - Address: Your business address
   - Industry: E-commerce / Retail
   - Team size: 1-10

---

## Step 2: Verify Sending Domain

> ⚠️ **CRITICAL**: Without this, your emails go to SPAM!

### 2.1 Add Your Domain
1. Go to **Settings** → **Senders, Domains & Dedicated IPs**
2. Click **"Domains"** → **"Add a domain"**
3. Enter: `indistylex.com`

### 2.2 Add DNS Records
Brevo will give you DNS records to add. Go to your domain registrar (where you bought indistylex.com):

**Record 1: DKIM (Email Authentication)**
| Type | Host | Value |
|------|------|-------|
| TXT | `mail._domainkey` | (Brevo provides this long string) |

**Record 2: SPF**
| Type | Host | Value |
|------|------|-------|
| TXT | `@` | `v=spf1 include:sendinblue.com ~all` |

**Record 3: DMARC**
| Type | Host | Value |
|------|------|-------|
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:hello@indistylex.com` |

**Record 4: Brevo Verification**
| Type | Host | Value |
|------|------|-------|
| TXT | `@` | (Brevo provides a verification code) |

### 2.3 Verify in Brevo
- After adding DNS records, wait 15-60 minutes
- Click **"Verify"** in Brevo
- All should show green checkmarks ✅

### 2.4 Set Sender
1. Go to **Senders** → **Add a Sender**
2. Name: `Indistylex`
3. Email: `hello@indistylex.com`
4. Mark as default sender

---

## Step 3: Create Contact Lists

### 3.1 Set Up Lists
Go to **Contacts** → **Lists** → Create:

| List Name | Who Goes Here |
|-----------|---------------|
| All Subscribers | Everyone |
| Customers | People who made a purchase |
| Abandoned Cart | Left items in cart |
| VIP Customers | Spent ₹3000+ or 3+ orders |
| New Subscribers | Signed up in last 30 days |
| Inactive | No open in 90 days |

### 3.2 Set Up Contact Attributes
Go to **Contacts** → **Settings** → **Contact attributes**:

| Attribute | Type | Use |
|-----------|------|-----|
| FIRSTNAME | Text | Personalization |
| LASTNAME | Text | Personalization |
| CHILD_AGE | Text | Segmentation |
| LAST_PURCHASE_DATE | Date | RFM |
| TOTAL_SPENT | Number | VIP segmentation |
| CITY | Text | Location targeting |

---

## Step 4: Create Signup Forms

### 4.1 Website Popup Form
1. Go to **Contacts** → **Forms** → **Create Form**
2. Type: **Popup**
3. Design:

**Headline**: `Get 10% Off Your First Order! 🎉`
**Subtext**: `Join 2000+ parents who get exclusive deals, new arrivals & styling tips.`
**Fields**:
- Email (required)
- First Name (optional)
**Button**: `Get My 10% Off`
**Fine print**: `We respect your inbox. Unsubscribe anytime.`

**Popup Settings:**
- Show after: 10 seconds on site
- Show on: All pages except checkout
- Show to: New visitors only
- Don't show again for: 7 days after close
- Mobile: Show as bottom bar (less intrusive)

### 4.2 Footer Signup
Add a simple signup in your website footer:
- Email field + "Subscribe" button
- Text: "Get exclusive deals & new arrivals"

### 4.3 Checkout Signup
Add checkbox at checkout:
- [ ] Send me exclusive offers and new arrivals (checked by default)

---

## Step 5: Set Up Automation Workflows

### Automation 1: Welcome Series (3 emails)

**Trigger**: New contact added to "All Subscribers" list

**Email 1 — Immediately:**
| Field | Content |
|-------|---------|
| Subject | `Welcome to Indistylex! Here's your 10% off 🎉` |
| Content | Welcome message + coupon code (e.g., WELCOME10) + bestsellers |
| CTA | Shop Now with Your Discount |

**Email 2 — After 2 days:**
| Field | Content |
|-------|---------|
| Subject | `Why parents love Indistylex ⭐` |
| Content | Customer reviews + social proof + "What makes us different" |
| CTA | See What Others Are Buying |

**Email 3 — After 5 days:**
| Field | Content |
|-------|---------|
| Subject | `Your 10% off expires soon ⏰` |
| Content | Urgency + reminder of coupon + bestsellers |
| CTA | Use Code WELCOME10 Before It's Gone |

---

### Automation 2: Abandoned Cart Recovery (3 emails)

**Trigger**: Add to cart event but no purchase within 1 hour

**Email 1 — After 1 hour:**
| Field | Content |
|-------|---------|
| Subject | `You left something cute behind! 🛒` |
| Content | Show cart items with images + "Complete your order" |
| CTA | Complete My Order |

**Email 2 — After 24 hours:**
| Field | Content |
|-------|---------|
| Subject | `Still thinking? Here's free shipping 🚚` |
| Content | Cart items + "Free shipping for the next 24 hours" |
| CTA | Get Free Shipping Now |

**Email 3 — After 72 hours:**
| Field | Content |
|-------|---------|
| Subject | `Last chance: 10% extra off your cart 💫` |
| Content | Cart items + 10% discount code + "Items selling fast" |
| CTA | Claim 10% Off - Code: COMEBACK10 |

---

### Automation 3: Post-Purchase Series

**Trigger**: Purchase event

**Email 1 — Immediately (Order Confirmation):**
- Subject: `Order Confirmed! 🎉 #{{order_id}}`
- Content: Order summary + expected delivery + tracking info

**Email 2 — After 5 days (Delivery Check-in):**
- Subject: `Has your order arrived? 📦`
- Content: "Hope [child's name] loves it!" + care instructions + review request

**Email 3 — After 14 days (Cross-sell):**
- Subject: `Complete the look for your little one ✨`
- Content: Related products based on purchase + "Pairs well with..."

**Email 4 — After 30 days (Replenishment):**
- Subject: `Time for new additions? 🆕`
- Content: New arrivals in same category + loyalty offer

---

### Automation 4: Win-Back (Inactive Customers)

**Trigger**: No purchase in 60 days + no email open in 30 days

**Email 1 — Day 0:**
- Subject: `We miss you, {{FIRSTNAME}}! 💕`
- Content: "It's been a while" + what's new + 15% off code

**Email 2 — After 7 days:**
- Subject: `Last chance: 20% off everything 🏷️`
- Content: Higher discount + best new products + urgency

**Email 3 — After 14 days (if still no engagement):**
- Subject: `Should we stop emailing you?`
- Content: "We don't want to bother you" + one-click to stay subscribed or unsubscribe

---

## Step 6: Email Templates

### Design Guidelines:
- **Width**: 600px max
- **Logo**: Top center
- **Colors**: Match brand (black, gold accent, white)
- **Font**: System fonts (Arial, Helvetica) for email compatibility
- **Images**: Compressed, with alt text
- **CTA Button**: Gold (#C9A94E) background, black text, large
- **Footer**: Unsubscribe link, address, social links

### Create These Templates in Brevo:
1. **Welcome Email** — Warm greeting + coupon
2. **Product Showcase** — 3-4 products in grid
3. **Sale Announcement** — Bold, urgent, countdown
4. **New Arrivals** — Fresh collection preview
5. **Cart Recovery** — Cart items + CTA
6. **Order Confirmation** — Clean order summary
7. **Review Request** — Simple star rating CTA

---

## Step 7: Newsletter Schedule

### Weekly Email Calendar:

| Day | Email Type | To Whom |
|-----|-----------|---------|
| Tuesday | New Arrivals / Product Spotlight | All subscribers |
| Thursday | Offer / Sale / Limited stock | All subscribers |
| Saturday | Style Tips / Content | Engaged subscribers only |

### Monthly Campaigns:
- 1st of month: Monthly recap + bestsellers
- Festival prep: 2 weeks before any festival
- Flash sale: Random Wednesday (surprise element)

---

## Step 8: Connect to Your Website

### 8.1 Brevo API Integration
Add to your `.env`:
```
BREVO_API_KEY=xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 8.2 Add Contact on Registration
When user signs up on website, add to Brevo:
```python
import sib_api_v3_sdk

def add_to_brevo(email, first_name, last_name):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.environ.get('BREVO_API_KEY')
    
    api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    contact = sib_api_v3_sdk.CreateContact(
        email=email,
        attributes={"FIRSTNAME": first_name, "LASTNAME": last_name},
        list_ids=[2],  # "All Subscribers" list ID
        update_enabled=True
    )
    api_instance.create_contact(contact)
```

### 8.3 Trigger Abandoned Cart
When user adds to cart but doesn't purchase within 1 hour:
```python
def trigger_abandoned_cart(email, cart_items):
    # Send event to Brevo
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(...)
    # Or use automation trigger via API
```

---

## Step 9: Deliverability Best Practices

### Do This:
- ✅ Always use double opt-in (confirm email)
- ✅ Send consistently (same days/times)
- ✅ Keep list clean (remove bounces)
- ✅ Personalize (use first name)
- ✅ Test subject lines (A/B test)
- ✅ Mobile-responsive design
- ✅ Clear unsubscribe link

### Don't Do This:
- ❌ Buy email lists (kills reputation)
- ❌ Send without permission
- ❌ Use ALL CAPS in subject
- ❌ Too many images, no text
- ❌ Send to inactive users forever
- ❌ Misleading subject lines
- ❌ Hide unsubscribe

---

## ✅ Checklist — You're Done When:

- [ ] Brevo account created
- [ ] Domain verified (DKIM, SPF, DMARC)
- [ ] Sender address configured
- [ ] Contact lists created
- [ ] Custom attributes added
- [ ] Popup form live on website
- [ ] Welcome series automation active (3 emails)
- [ ] Abandoned cart automation active (3 emails)
- [ ] Post-purchase automation active (4 emails)
- [ ] Win-back automation active (3 emails)
- [ ] 7 email templates designed
- [ ] API connected to website
- [ ] First newsletter sent
- [ ] Unsubscribe working properly

---

## Key Metrics

| Metric | Industry Average | Your Target |
|--------|-----------------|-------------|
| Open Rate | 20-25% | 30%+ |
| Click Rate | 2-3% | 5%+ |
| Unsubscribe Rate | <0.5% | <0.3% |
| Cart Recovery Rate | 5-10% | 10-15% |
| Welcome Series Revenue | - | ₹500-1000/subscriber |
