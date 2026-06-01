# 10 — Payment & Shipping Setup

## What This Does
Sets up payment gateway (Razorpay) for online payments and connects shipping partners for order fulfillment.

**Time needed**: 1-2 hours (verification takes 1-3 days)

---

## Part A: Payment Gateway (Razorpay)

### Step 1: Create Razorpay Account

1. Go to: https://razorpay.com
2. Click **"Sign Up"**
3. Enter business email: `hello@indistylex.com`
4. Verify email + phone

### Step 2: Complete KYC

1. Go to **Account & Settings** → **Company Details**
2. Fill:

| Field | Value |
|-------|-------|
| Business Type | Individual / Sole Proprietorship |
| Business Name | Indistylex |
| Business Category | E-commerce |
| Sub-category | Fashion & Lifestyle |
| Website | `https://indistylex.com` |
| GST Number | (if registered) |
| PAN | Your PAN number |

### Step 3: Upload Documents
- PAN Card (individual/business)
- Address proof (Aadhaar / utility bill)
- Bank account proof (cancelled cheque / statement)
- Website screenshot (showing products + prices)

### Step 4: Bank Account Details
| Field | Value |
|-------|-------|
| Account Holder | Your name / business name |
| Account Number | Your business account |
| IFSC Code | Your bank IFSC |
| Account Type | Current (business) / Savings |

### Step 5: Razorpay Verification
- Takes 1-3 business days
- You'll receive approval email
- Test mode available immediately (for development)

### Step 6: Get API Keys
1. Go to **Settings** → **API Keys**
2. Generate **Key ID** and **Key Secret**
3. Add to your `.env` file:
```
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxx
```

### Step 7: Configure Payment Methods

Enable these in Razorpay Dashboard:

| Method | Enable? | Notes |
|--------|---------|-------|
| UPI | ✅ Yes | Most popular in India |
| Credit Card | ✅ Yes | Visa, Mastercard, Amex |
| Debit Card | ✅ Yes | All banks |
| Net Banking | ✅ Yes | All major banks |
| Wallets | ✅ Yes | Paytm, PhonePe, etc. |
| EMI | Optional | For high-value orders |
| Pay Later | Optional | Simpl, LazyPay |

### Step 8: Razorpay Charges

| Method | Razorpay Fee |
|--------|-------------|
| UPI | 2% |
| Credit Card | 2% |
| Debit Card | 2% |
| Net Banking | 2% |
| Wallets | 2% |
| International Cards | 3% |

> All fees + 18% GST on fee amount.
> Settlement: T+2 (money in your account 2 days after payment)

### Step 9: Set Up Payment Page (Quick Start)
If you need a quick payment link:
1. Go to **Payment Links** → **Create**
2. Add product details, amount
3. Share link via WhatsApp/Instagram

---

## Part B: COD Setup

### Cash on Delivery Configuration:
| Setting | Value |
|---------|-------|
| COD Available | Yes |
| COD Charge | ₹50 per order |
| Maximum COD Amount | ₹5,000 |
| COD Prepaid Discount | 10% off for prepaid |
| COD Pin Code Check | Enable (via shipping partner API) |

### Why Limit COD:
- Higher return rate (2-3x more returns)
- RTO (Return to Origin) costs money
- Delayed cash flow
- Strategy: Incentivize prepaid with discounts

---

## Part C: Shipping Setup

### Step 1: Choose Shipping Aggregator

| Aggregator | Best For | Pricing |
|------------|----------|---------|
| **Shiprocket** | Beginners, multi-courier | ₹26/500g (prepaid) |
| **Delhivery** | Pan-India coverage | ₹35-50/500g |
| **iThink Logistics** | Budget option | ₹25/500g |
| **Ecom Express** | E-commerce focused | ₹30/500g |
| **NimbusPost** | Cheapest rates | ₹22/500g |

> **Recommended**: Start with **Shiprocket** — multiple couriers, best rates, easy dashboard.

### Step 2: Shiprocket Setup

1. Go to: https://www.shiprocket.in
2. Click **"Start Free"**
3. Enter business details:
   - Company: Indistylex
   - Email: hello@indistylex.com
   - Phone: Business number
   - GST: (if applicable)

### Step 3: Add Pickup Address
| Field | Value |
|-------|-------|
| Name | Indistylex Warehouse |
| Address | Your full address |
| City | Your city |
| State | Your state |
| Pincode | Your pincode |
| Phone | Pickup contact number |

### Step 4: Configure Shipping Rates

**Strategy 1: Free Shipping (Recommended)**
- All prepaid orders: Free shipping
- COD orders: ₹50 charge
- You absorb shipping cost (₹25-50 per order)
- Build into product pricing

**Strategy 2: Threshold Free Shipping**
- Orders above ₹499: Free shipping
- Below ₹499: ₹49 shipping
- Encourages higher cart value

### Step 5: Set Up Weight & Dimensions
For kids clothing (approximate):

| Product Type | Weight | Dimensions (LxWxH cm) |
|-------------|--------|------------------------|
| T-shirt | 150-200g | 25x20x3 |
| Dress/Frock | 200-300g | 30x25x4 |
| Kurta Set | 300-400g | 30x25x5 |
| Jeans/Pants | 250-350g | 30x20x4 |
| Winter Jacket | 400-600g | 35x30x8 |

> Volumetric weight = (LxWxH)/5000. Charged on higher of actual vs volumetric.

### Step 6: Shipping Workflow

```
1. Order received → Auto-sync to Shiprocket
2. Generate shipping label + AWB (in Shiprocket)
3. Pack order with label
4. Schedule pickup (or drop at courier)
5. Courier picks up → Customer gets tracking SMS
6. Delivery (3-7 days)
7. If COD → Cash collected → Remitted to you (7-10 days)
```

### Step 7: Packaging

| Material | Size | Cost (per unit) |
|----------|------|-----------------|
| Poly mailer | 10x13" | ₹3-5 |
| Branded box | Custom | ₹15-25 |
| Tissue paper | Standard | ₹2-3 |
| Thank you card | 4x6" | ₹3-5 |
| Sticker/seal | 2" round | ₹1-2 |

**Packaging Checklist:**
- [ ] Product folded neatly
- [ ] Wrapped in tissue paper
- [ ] Thank you card included
- [ ] Branded sticker to seal
- [ ] Invoice inside (GST compliant)
- [ ] Return label (optional)
- [ ] Moisture protection (poly bag)

### Step 8: Handle Returns (RTO/NDR)

**NDR (Non-Delivery Report):**
- Courier couldn't deliver
- Call customer immediately to reschedule
- Reduces RTO rate

**RTO (Return to Origin):**
- Customer refused delivery or wrong address
- You pay forward + return shipping
- Track RTO rate — high RTO = problem

**Reduce RTO Tips:**
1. Confirm COD orders via WhatsApp before shipping
2. Send tracking links proactively
3. Call customer before delivery attempt
4. Verify address with pincode check
5. Limit COD to repeat customers / under ₹3000

---

## Part D: Invoice Generation

### GST-Compliant Invoice Must Include:
- Your business name, GSTIN, address
- Customer name and address
- Invoice number (sequential)
- Date
- HSN code for each product
- Quantity, unit price, total
- CGST + SGST (intra-state) or IGST (inter-state)
- Total amount in words

### Invoice Tools:
| Tool | Cost | Features |
|------|------|----------|
| Zoho Invoice | Free (5 clients) | Auto-generate, GST |
| ClearTax | Free | GST compliant |
| Shiprocket | Built-in | Auto-generate per order |
| Your website | Custom | Generate from order data |

---

## ✅ Checklist — You're Done When:

- [ ] Razorpay account created
- [ ] KYC documents submitted
- [ ] Bank account linked
- [ ] API keys generated and added to .env
- [ ] All payment methods enabled (UPI, Cards, NetBanking)
- [ ] Test payment successful
- [ ] COD configured with limits
- [ ] Shiprocket account created
- [ ] Pickup address added
- [ ] Courier partners activated
- [ ] Shipping rates configured
- [ ] Packaging materials ordered
- [ ] Invoice template ready
- [ ] Return process documented
- [ ] First test order placed end-to-end

---

## Monthly Costs Estimate

| Item | Monthly Cost |
|------|-------------|
| Razorpay fees (2% on ₹1L revenue) | ₹2,000 |
| Shipping (100 orders × ₹30) | ₹3,000 |
| Packaging (100 orders × ₹20) | ₹2,000 |
| RTO losses (10% × ₹50) | ₹500 |
| **Total fulfillment** | **₹7,500** |

> Build these costs into your product pricing!
