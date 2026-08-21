# Indistylex — Business Bank Account & Money Handling Guide

> **Purpose:** Step-by-step guide to open a **business current account**, connect all sales channels, and handle money correctly — separate from personal finances.  
> **Business:** Indistylex (proprietorship) · GSTIN `09GVUPP6447P1Z3` · Prayagraj, UP

**Related:** [GST-MONTHLY-FILING-GUIDE.md](GST-MONTHLY-FILING-GUIDE.md) · [BUSINESS_OPERATIONS_PLAYBOOK.md](../BUSINESS_OPERATIONS_PLAYBOOK.md) §11 · [Indistylex-Business-Tracker.xlsx](Indistylex-Business-Tracker.xlsx)

---

## Table of contents

1. [Why you need a separate business account](#1-why-you-need-a-separate-business-account)
2. [Current account vs savings](#2-current-account-vs-savings)
3. [Open a current account — step by step](#3-open-a-current-account--step-by-step)
4. [Connect the account everywhere](#4-connect-the-account-everywhere)
5. [Money flow — all channels](#5-money-flow--all-channels)
6. [Step-by-step: when a customer pays](#6-step-by-step-when-a-customer-pays)
7. [Step-by-step: when you spend money](#7-step-by-step-when-you-spend-money)
8. [Daily, weekly, monthly money routine](#8-daily-weekly-monthly-money-routine)
9. [GST & tax money — don’t spend it](#9-gst--tax-money--dont-spend-it)
10. [Bank reconciliation with Excel](#10-bank-reconciliation-with-excel)
11. [Rules & common mistakes](#11-rules--common-mistakes)
12. [Quick reference card](#12-quick-reference-card)

---

## 1. Why you need a separate business account

| Without business account | With business current account |
|--------------------------|-------------------------------|
| Personal UPI mixed with sales | Clear “Indistylex money” in one place |
| CA cannot reconcile easily | Clean statements for GST & ITR |
| Razorpay / Amazon may reject or delay | KYC matches business name + GSTIN |
| You accidentally spend GST or stock money | Easier to track profit vs tax |
| Looks unprofessional to B2B shops | Issue cheques / NEFT in business name |

**Golden rule:** All **Indistylex income** → business account. All **business expenses** → from same account (or linked business UPI). **No** buying personal groceries from this account.

---

## 2. Current account vs savings

| | **Current account** | **Savings account** |
|---|---------------------|---------------------|
| **Best for** | Business transactions, high volume | Personal savings |
| **Transactions** | Unlimited (or very high) | Limited free withdrawals |
| **Cheque / NEFT** | Yes — B2B shops expect this | Possible but not ideal |
| **Razorpay / marketplaces** | Preferred for settlement | Often accepted for proprietorship start |
| **Minimum balance** | ₹5,000–₹25,000 (bank-dependent) | Lower |
| **Charges** | AMC, per-transaction fees possible | Usually free |

**Recommendation for Indistylex:** Open a **current account** in the name of **Satyam Pandey (Indistylex)** or trade name **Indistylex** with GST proof. If the bank only offers savings initially, upgrade to current when turnover grows — but **keep it separate from your personal savings**.

---

## 3. Open a current account — step by step

### 3.1 Before you visit the bank

| Document | Why |
|----------|-----|
| **PAN** (individual) | KYC — proprietor |
| **Aadhaar** | KYC |
| **GST registration certificate** | Proves business `09GVUPP6447P1Z3` |
| **Address proof** | Shop/warehouse or home (MIG 79, Prayagraj) — rent agreement or utility bill |
| **Passport photos** | 2–3 |
| **Cancelled cheque** (if switching banks) | Optional |
| **Udyam (MSME) certificate** | Optional — helps some banks; free at udyamregistration.gov.in |

### 3.2 At the bank (typical flow)

1. Choose branch (near Prayagraj shop/warehouse for easy cash deposit if needed).
2. Ask for **Current Account — Sole Proprietorship / Individual Business**.
3. Account name examples banks accept:
   - `Satyam Pandey` (proprietor) — simplest  
   - `Satyam Pandey trading as Indistylex`  
   - `Indistylex` (if GST trade name matches)
4. Submit KYC + GST certificate.
5. Initial deposit (often ₹5,000–₹10,000 minimum).
6. Get **account number + IFSC** — needed same day for Razorpay.
7. Enable **net banking + mobile banking**.
8. Request **debit card** (business expenses) and **cheque book** (B2B).
9. Link **business UPI** (many banks: `@ybl`, `@okaxis` on same account).

**Timeline:** Same day to 3–5 working days for full activation.

### 3.3 Banks commonly used by small sellers (pick one nearby)

| Type | Examples | Notes |
|------|----------|-------|
| Public sector | SBI, Bank of Baroda, PNB | Lower charges, slower support |
| Private | HDFC, ICICI, Axis, Kotak | Good net banking, higher min balance |
| Neo / business-focused | Current account via RazorpayX, Open, etc. | Optional later for payouts automation |

No need for multiple accounts at start — **one current account is enough**.

---

## 4. Connect the account everywhere

After account is live, update **the same account number + IFSC** in:

| Platform | Where to add bank details |
|----------|---------------------------|
| **Razorpay** | Dashboard → Account & Settings → Bank Account |
| **Amazon Seller** | Seller Central → Settings → Payment Information |
| **Flipkart Seller** | Seller Hub → Payments → Bank details |
| **Shiprocket / courier** | COD remittance account (if applicable) |
| **Meta Ads** | Billing → Payment method (can use same card/UPI) |
| **Google Ads** | Billing profile |
| **GST portal** | Registration → amend bank details if required |
| **CA / ClearTax / Zoho** | For refund credits and bookkeeping |

**Checklist after opening account:**

```
☐ Razorpay settlement account updated → test ₹1 live payment → verify credit in 2 days
☐ Amazon / Flipkart bank details verified (penny drop)
☐ Save IFSC + account number in CREDENTIALS.md (local, not git)
☐ Never use personal account for new channel onboarding
```

---

## 5. Money flow — all channels

```
                         CUSTOMERS PAY
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   WEBSITE               AMAZON /              B2B SHOPS
   (Razorpay / COD)       FLIPKART              (NEFT / COD)
        │                      │                      │
        │  T+2 settlement      │  7–14 days           │  On delivery
        │  (prepaid)           │  after period        │  or credit terms
        ▼                      ▼                      ▼
        └──────────────────────┼──────────────────────┘
                               │
                               ▼
                  ┌────────────────────────┐
                  │  BUSINESS CURRENT A/C   │
                  │  (Indistylex)           │
                  └───────────┬────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   WHOLESALER            SHIPPING / ADS         GST + CA
   (stock purchase)      (courier, Meta)       (monthly)
        │                     │                     │
        ▼                     ▼                     ▼
   Inventory              Marketing              Compliance
```

### Timing summary

| Source | How money arrives | When in bank (typical) |
|--------|-------------------|-------------------------|
| Website **prepaid** (UPI/card) | Razorpay → your bank | **T+2** (2 working days) |
| Website **COD** | Courier collects → remits to you | **7–14 days** after delivery |
| **Amazon** | Settlement cycle | **7–14 days** (bi-weekly-ish) |
| **Flipkart** | Settlement cycle | **7–14 days** |
| **B2B shop** | NEFT / UPI / cash deposit | Same day or **7–15 day credit** |

**Important:** Money in bank ≠ profit. Fees and GST are deducted or owed separately.

---

## 6. Step-by-step: when a customer pays

### A. Website — prepaid (Razorpay)

```
1. Customer pays ₹523 on indistylex.com (₹499 + GST example)
2. Razorpay deducts ~2% + GST on fee → net ~₹512 lands in Razorpay balance
3. Razorpay auto-settles to business current account (T+2)
4. YOU DO:
   a. Order appears in Admin → Orders
   b. Pack & ship order
   c. Log row in Excel → Orders tab (date, amount, channel = Website)
   d. When bank credit appears → match Razorpay settlement ID in dashboard
```

### B. Website — COD

```
1. Customer pays courier in cash on delivery
2. Courier remits to your bank (or Shiprocket wallet → bank) weekly
3. YOU DO:
   a. Mark order shipped in admin
   b. Log in Orders tab as COD
   c. When bank deposit from courier arrives → mark “COD received” in tracker
   d. Watch RTO — refused COD = you pay return shipping, no cash in
```

### C. Amazon / Flipkart

```
1. Customer pays Amazon/Flipkart (not you directly)
2. Marketplace deducts commission, shipping, TCS, etc.
3. Net amount settles to business bank on schedule
4. YOU DO:
   a. Download settlement report from seller portal
   b. Log net revenue in Orders / channel sheet
   c. Match bank credit line-by-line (reference number in statement)
   d. Send report copy to CA for GST (see GST guide)
```

### D. B2B wholesale shop

```
1. Issue GST invoice to shop (with their GSTIN)
2. Shop pays via NEFT/UPI/cheque to business account
3. YOU DO:
   a. Log in B2B Customers + Orders tabs
   b. Save payment date + UTR number
   c. Give shop delivery / transport receipt
   d. CA includes in GSTR-1 B2B table
```

---

## 7. Step-by-step: when you spend money

| Expense | Pay from | Record in |
|---------|----------|-----------|
| **Wholesaler stock** | Business account (NEFT/UPI) | Expenses tab + save **GST invoice** |
| **Courier / Shiprocket** | Business account / wallet top-up | Expenses tab |
| **Packaging** (polybags, tissue) | Business account | Expenses tab |
| **Razorpay fees** | Auto-deducted before settlement | Razorpay report |
| **Amazon / Flipkart fees** | Auto-deducted from settlement | Marketplace report |
| **Meta / Google ads** | Business debit card or UPI | Expenses tab |
| **Server hosting** | Business card/UPI | Expenses tab |
| **CA / ClearTax** | Business account | Expenses tab |
| **GST payment** | Business account (challan) | Note + GST guide folder |
| **Salary / helper** (future) | Business account | Expenses tab |

### Wholesaler purchase flow (most important expense)

```
1. Decide SKUs to reorder (Inventory tab — low stock)
2. Pay wholesaler from BUSINESS account only
3. Get GST invoice in YOUR GSTIN (09GVUPP6447P1Z3)
4. Stock arrives → update Inventory tab
5. Send purchase invoice PDF to CA (for ITC in GSTR-3B)
```

**Never pay wholesaler from personal GPay** — you lose clean ITC trail and CA reconciliation breaks.

---

## 8. Daily, weekly, monthly money routine

### Daily (5 minutes)

| Task | Action |
|------|--------|
| Check admin orders | New paid orders to pack |
| Glance at bank app | Unexpected debits? Razorpay credit? |
| COD shipped | Note which orders are in transit |

### Weekly — Monday (20 minutes)

| Task | Action |
|------|--------|
| Razorpay settlements | Dashboard → Download last week’s settlements |
| Bank statement | Export / screenshot credits vs Orders tab |
| Amazon / Flipkart | Download payment report if live |
| Update **Weekly KPIs** tab | Revenue by channel |
| Pay pending courier wallet | If balance low |

### Monthly — by 5th (see GST guide)

| Task | Action |
|------|--------|
| Full bank statement | PDF for the month |
| Reconcile every credit | Website + B2B + marketplace = bank in |
| Reconcile every debit | Expenses tab = bank out |
| Send pack to CA | Sales + purchases + bank summary |
| **Monthly P&L tab** | Revenue − expenses = rough profit |
| GST payment | CA confirms 3B amount → pay challan |

---

## 9. GST & tax money — don’t spend it

GST collected from customers is **government money**, not revenue.

**Simple discipline (optional but recommended):**

```
Example month:
  Sales GST collected (output)     ₹8,000
  Purchase GST credit (ITC)        ₹5,000
  Net GST payable (CA confirms)    ₹3,000

→ When ₹50,000 settles in bank from Razorpay, mentally ₹3,000 is not yours to spend on ads.
```

**Methods:**

| Method | How |
|--------|-----|
| **Mental bucket** | Note expected GST from CA after 3B |
| **Spreadsheet** | Column in P&L: “GST liability set-aside” |
| **Separate savings pocket** | Some banks allow sub-accounts — transfer net GST after CA tells you |

Income tax is separate — paid quarterly (advance tax) or at year-end via CA. See [GST-MONTHLY-FILING-GUIDE.md](GST-MONTHLY-FILING-GUIDE.md) §16.

---

## 10. Bank reconciliation with Excel

Use **`Indistylex-Business-Tracker.xlsx`**:

| Tab | Money use |
|-----|-----------|
| **Orders** | Every sale — date, channel, amount, payment mode |
| **Expenses** | Every business payment out |
| **Weekly KPIs** | Total in vs target |
| **Monthly P&L** | Profit picture |

### Reconciliation steps (monthly)

```
1. Download bank statement (1st → last day of month)
2. Sum all CREDITS → should match Orders (± Razorpay timing lag)
3. Sum all DEBITS → should match Expenses tab
4. List UNMATCHED items:
   - Credit with no order → find UTR in Razorpay / Amazon
   - Debit with no expense row → add to Expenses or mark personal (avoid)
5. Save statement PDF: Finance/2026-07/bank-statement.pdf
```

**Timing difference is normal:** July 31 sale may settle in bank on August 2 — CA handles period cut-off.

---

## 11. Rules & common mistakes

### Do

- One **dedicated** current account for Indistylex  
- Pay wholesalers only with GST invoice to your GSTIN  
- Log every order and expense in Excel  
- Match Razorpay settlement IDs to bank credits  
- Keep 6 months of statements (GST + income tax)  

### Don’t

- Mix personal Swiggy, rent, family transfers in business account  
- Spend full bank balance without reserving GST  
- Accept B2B payment to personal UPI without recording  
- Skip logging COD until “someday”  
- Open 5 accounts — one is enough until scale demands more  

### If you already mixed money

1. Open business current account **now**.  
2. Route all **new** sales there.  
3. Tell CA which past transactions were business vs personal — they may adjust opening books.  
4. Going forward: **100% clean**.

---

## 12. Quick reference card

```
┌──────────────────────────────────────────────────────────────┐
│  INDISTYLEX MONEY — AT A GLANCE                               │
├──────────────────────────────────────────────────────────────┤
│  ACCOUNT: Current account (NOT personal savings)              │
│  NAME: Satyam Pandey / Indistylex + GSTIN on file             │
├──────────────────────────────────────────────────────────────┤
│  MONEY IN                          TIMING                     │
│  Website prepaid (Razorpay)          T+2 to bank                │
│  Website COD                         7–14 days via courier      │
│  Amazon / Flipkart                   7–14 days settlement       │
│  B2B shops                           NEFT / credit terms        │
├──────────────────────────────────────────────────────────────┤
│  MONEY OUT                                                    │
│  Stock → wholesaler (GST bill)     Ads → business debit       │
│  Courier, packaging                GST → monthly challan      │
├──────────────────────────────────────────────────────────────┤
│  EVERY SALE → Orders tab          EVERY PAYMENT → Expenses tab│
│  EVERY MONTH → bank reconcile + send CA data by 5th           │
└──────────────────────────────────────────────────────────────┘
```

---

## Document index

| File | Purpose |
|------|---------|
| **This file** | Business bank account + money handling |
| [GST-MONTHLY-FILING-GUIDE.md](GST-MONTHLY-FILING-GUIDE.md) | GST returns, ITC, CA workflow |
| [HSN_CODES.md](HSN_CODES.md) | Invoices & product tax codes |
| [Indistylex-Business-Tracker.xlsx](Indistylex-Business-Tracker.xlsx) | Orders, expenses, P&L |
| [../Indistylex/digital-marketing-setup/10-PAYMENT-SHIPPING.md](../Indistylex/digital-marketing-setup/10-PAYMENT-SHIPPING.md) | Razorpay + COD setup |

---

*Indistylex Banking & Money Guide — August 2026*
