# Indistylex — GST & Monthly Filing Guide (India)

> **Purpose:** End-to-end awareness guide — how GST works, what GSTR-1 / GSTR-3B mean, and what **you** must track so your **CA** can file via **ClearTax / Zoho Books** without errors.  
> **This is not tax advice.** Rates, due dates, and rules change — your CA is the final authority.

| Your business | Value |
|---------------|-------|
| **Trade name** | Indistylex |
| **GSTIN** | 09GVUPP6447P1Z3 |
| **State** | Uttar Pradesh (code `09` in GSTIN) |
| **Structure** | Proprietorship |
| **Activity** | Retail — kids' clothing (website, Amazon, Flipkart, B2B shops) |

**Related:** [HSN_CODES.md](HSN_CODES.md) · [BUSINESS_OPERATIONS_PLAYBOOK.md](../BUSINESS_OPERATIONS_PLAYBOOK.md) §10–11

---

## Table of contents

1. [GST in plain language](#1-gst-in-plain-language)
2. [Key terms you must know](#2-key-terms-you-must-know)
3. [How GST applies to Indistylex products](#3-how-gst-applies-to-indistylex-products)
4. [CGST, SGST, IGST — which one?](#4-cgst-sgst-igst--which-one)
5. [Tax invoices — your daily compliance](#5-tax-invoices--your-daily-compliance)
6. [Input Tax Credit (ITC) — GST you get back](#6-input-tax-credit-itc--gst-you-get-back)
7. [Sales by channel — what goes in returns](#7-sales-by-channel--what-goes-in-returns)
8. [Monthly returns — the full picture](#8-monthly-returns--the-full-picture)
9. [GSTR-1 step by step (sales return)](#9-gstr-1-step-by-step-sales-return)
10. [GSTR-3B step by step (summary + payment)](#10-gstr-3b-step-by-step-summary--payment)
11. [Other returns & forms (awareness)](#11-other-returns--forms-awareness)
12. [Working with CA + ClearTax / Zoho](#12-working-with-ca--cleartax--zoho)
13. [Monthly calendar & checklist](#13-monthly-calendar--checklist)
14. [Penalties & common mistakes](#14-penalties--common-mistakes)
15. [Records to keep (6 years)](#15-records-to-keep-6-years)
16. [GST vs Income Tax — don’t mix them](#16-gst-vs-income-tax--dont-mix-them)
17. [Quick reference card](#17-quick-reference-card)

---

## 1. GST in plain language

**GST (Goods and Services Tax)** is India’s indirect tax on supply of goods/services. As a seller you:

1. **Collect** GST from customers on sales (output tax).
2. **Pay** GST on purchases from wholesalers (input tax — often recoverable as **ITC**).
3. **Remit** the **net** amount to government every month (usually via GSTR-3B).

```
You charge customer     ₹499 + 5% GST = ₹523.95  (example)
You bought stock        ₹300 + 5% GST = ₹315       (wholesaler invoice)

Net GST to government ≈ GST collected on sales − GST paid on purchases (ITC)
                        (simplified — CA reconciles exactly)
```

**GST is not your income.** It is tax held on behalf of the government. Keep it mentally (and ideally in a separate bank slice) separate from profit.

---

## 2. Key terms you must know

| Term | Meaning | Indistylex example |
|------|---------|-------------------|
| **GSTIN** | 15-character tax ID | `09GVUPP6447P1Z3` |
| **HSN** | Product category code for tax | `6204` (frock), `6205` (shirt) |
| **SKU** | Your internal product code | `IX-FRK-001-2-3Y-PNK` |
| **Taxable value** | Price **before** GST (or value on which GST is calculated) | ₹499 item @ 5% → taxable ₹499, GST ₹24.95 |
| **Output tax** | GST you **collect** on sales | From website / B2B invoices |
| **Input tax / ITC** | GST you **paid** on purchases — credit against output | Wholesaler GST invoice |
| **B2B** | Sale to business with GSTIN | Shop in Lucknow with GSTIN |
| **B2C** | Sale to consumer (no GSTIN) | Website customer, Amazon retail buyer |
| **GSTR-1** | Return reporting **outward supplies** (your sales) | Filed monthly |
| **GSTR-3B** | Summary return + **tax payment** | Filed monthly |
| **GSTR-2B** | Auto-generated **purchase** statement (for ITC) | Download from portal — CA matches |
| **Place of supply** | State where tax applies | UP customer → CGST+SGST; Maharashtra → IGST |
| **TCS** | Tax collected at source (marketplaces) | Amazon/Flipkart may deduct ~1% — shows in 2B |

---

## 3. How GST applies to Indistylex products

Kids’ garments — rate depends on **selling price per piece** (not MRP on tag alone — use your actual selling price):

| Selling price (per piece) | Typical HSN | GST rate |
|---------------------------|-------------|----------|
| **≤ ₹1,000** | 6109, 6110, 6111, 6112, 6203, 6204, 6205, 6209 | **5%** |
| **> ₹1,000** | 6203, 6204 (premium / ethnic) | **12%** |

Full SKU → HSN map: **[HSN_CODES.md](HSN_CODES.md)** and Excel **SKU & HSN Codes** tab.

**Rule of thumb:** Most Indistylex items at ₹299–₹999 → **5% GST**. Premium ethnic > ₹1000 → **12%**.

---

## 4. CGST, SGST, IGST — which one?

Your GSTIN starts with **09** = Uttar Pradesh.

| Customer location | Tax split | Example (5% on ₹1000) |
|-------------------|-----------|------------------------|
| **Same state (UP)** | CGST 2.5% + SGST 2.5% | ₹25 + ₹25 = ₹50 |
| **Other state** | IGST 5% | ₹50 |

- **Website order to Prayagraj** → CGST + SGST  
- **Website order to Mumbai** → IGST  
- **Amazon/Flipkart** → Marketplace reports state-wise; CA maps in GSTR-1  

Always put **correct state + pincode** on invoices and orders — wrong state = wrong tax type in returns.

---

## 5. Tax invoices — your daily compliance

Every B2B and D2C sale should have a **GST tax invoice** (website order confirmation / printed slip in package).

### Mandatory fields (minimum)

- Supplier name, address, GSTIN  
- Invoice number & date  
- Customer name, address (and **GSTIN** if B2B)  
- HSN, description, qty, taxable value, GST rate, CGST/SGST or IGST, total  
- Place of supply (for inter-state)

**Template:** `operations-templates/packing-printables/invoice-gst-a4.html`

### B2B vs B2C

| | B2B (shop) | B2C (website / retail) |
|---|------------|-------------------------|
| Customer GSTIN | Required on invoice | Not required |
| Invoice copy | Give to shop; you retain duplicate | Put in package + email PDF if possible |
| GSTR-1 table | **B2B** — invoice-wise with buyer GSTIN | **B2C** — consolidated by state + rate |

---

## 6. Input Tax Credit (ITC) — GST you get back

When you buy stock from a **registered** wholesaler with a valid GST invoice, the GST on that purchase is usually **Input Tax Credit** — it reduces what you pay the government.

```
Output GST (on sales)     ₹10,000
Minus ITC (on purchases)  ₹ 6,000
─────────────────────────────────
Net payable (GSTR-3B)     ₹ 4,000
```

### You CAN usually claim ITC when

- Wholesaler gave **valid GST invoice** with your GSTIN  
- Goods are for **business** (kids’ stock for resale)  
- Invoice appears in **GSTR-2B** (matched on portal)  
- You **paid** supplier (for high-value cases CA may check)

### You CANNOT claim ITC on (common)

- Personal expenses  
- Purchases without GST invoice  
- Blocked categories (some items — CA confirms)  
- ITC on **Composition** suppliers (if any)

**Your job:** Save every wholesaler GST invoice (PDF/physical). Send to CA monthly. Log in Excel **Expenses** tab.

---

## 7. Sales by channel — what goes in returns

| Channel | Invoice issued by | What CA needs from you |
|---------|-------------------|-------------------------|
| **Website** (Razorpay/COD) | You (Indistylex) | Order export / admin reports — date, amount, state, HSN, tax |
| **B2B shops** | You | GST invoice copies + payment date |
| **Amazon** | You (seller) — Amazon reports for reconciliation | Amazon **MTR** / tax reports, settlement CSV |
| **Flipkart** | Same | Flipkart seller tax / payment reports |
| **Credit notes / returns** | You issue credit note | Return date, original invoice ref |

### Marketplace TCS (Tax Collected at Source)

Amazon / Flipkart may deduct **TCS** (~1% on taxable value) and deposit with GST department. This appears in **GSTR-2B**. Your CA adjusts so you don’t double-pay. **You still file GSTR-1 and GSTR-3B** — TCS is not a substitute for your return.

---

## 8. Monthly returns — the full picture

```
                    ┌─────────────────────────────────────┐
                    │         YOUR RECORDS (daily)         │
                    │  Invoices, orders, purchase bills    │
                    └─────────────────┬───────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
        ┌───────────┐           ┌───────────┐           ┌───────────┐
        │  GSTR-1   │           │ GSTR-2B   │           │  Bank /   │
        │  (sales)  │           │(purchases)│           │ Razorpay  │
        └─────┬─────┘           └─────┬─────┘           └─────┬─────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      ▼
                              ┌───────────────┐
                              │   GSTR-3B     │
                              │ summary + PAY │
                              └───────────────┘
                                      │
                                      ▼
                              GST portal payment
                              (Challan / net banking)
```

| Return | What it is | Typical due date* | Who files |
|--------|------------|-------------------|-----------|
| **GSTR-1** | Details of **all sales** (B2B invoice-wise, B2C summary) | **11th** of next month | CA via ClearTax/Zoho |
| **GSTR-3B** | Monthly **summary** + ITC claim + **tax payment** | **20th** of next month | CA via ClearTax/Zoho |
| **GSTR-2B** | Auto-drafted purchase register | Available ~14th | CA downloads — you don’t “file” it |

\*Due dates are often extended by government notifications — CA tracks actual dates.

### Quarterly filing (QRMP) — are you on this?

Businesses with turnover up to **₹5 crore** may opt **QRMP** (Quarterly Return Monthly Payment):

- GSTR-1 **quarterly**, GSTR-3B **monthly** (pay tax every month still)

**Confirm with your CA** which scheme your GSTIN is registered under. This guide assumes **monthly GSTR-1 + GSTR-3B** unless CA says otherwise.

---

## 9. GSTR-1 step by step (sales return)

**Purpose:** Tell the government what you **sold** this month.

### Sections that matter for Indistylex

| Table | What goes here |
|-------|----------------|
| **4A – B2B** | Invoices to shops **with GSTIN** (one row per invoice) |
| **5 – B2C** | Website / retail sales **without GSTIN** — often **state-wise + rate-wise** totals |
| **7 – B2C others** | Large B2C invoices if applicable (CA decides) |
| **9B – Credit / debit notes** | Returns, cancellations, price corrections |
| **12 – HSN summary** | Total qty/value/tax **by HSN code** (mandatory) |
| **13 – Documents issued** | Invoice number series (from – to) |

### Example (simplified)

**July 2026 sales:**

- B2B: 3 invoices to shops in UP → Table 4A (each with buyer GSTIN)  
- Website: 120 orders across UP, MH, DL → Table 5 (state totals @ 5%)  
- Amazon: CA imports from Amazon tax report  
- HSN: 6204 — 80 pcs, taxable ₹39,920, tax ₹1,996  

**Your role:** Provide clean data by **5th of next month** — not file the return yourself unless CA asks.

---

## 10. GSTR-3B step by step (summary + payment)

**Purpose:** Pay net GST for the month.

### Main tables (simplified)

| Table | Meaning |
|-------|---------|
| **3.1 – Outward taxable supplies** | Total sales tax liability (from GSTR-1 logic) |
| **4 – ITC available** | Credit from purchases (matched with GSTR-2B) |
| **6.1 – Net tax payable** | Output tax − ITC = **pay this** (if positive) |

### Payment flow

1. CA files GSTR-3B on gst.gov.in (or via ClearTax/Zoho).  
2. System generates **challan** if tax due > 0.  
3. Pay via net banking / UPI on GST portal.  
4. Save payment receipt.

**Cash ledger / ITC ledger** on portal show balance — CA reconciles.

If **ITC > output tax** (common early stage when buying lots of stock):

- Pay **zero** this month  
- **ITC carries forward** to next month (does not expire immediately — CA tracks)

---

## 11. Other returns & forms (awareness)

| Item | When it matters |
|------|-----------------|
| **E-way bill** | Moving goods **> ₹50,000** between locations — courier may handle; B2B bulk delivery you may need |
| **GSTR-9 / 9C** | **Annual** return (+ audit if turnover > ₹5 crore) — CA files after March year-end |
| **LUT / exports** | Only if exporting outside India |
| **Composition scheme** | **Not suitable** for inter-state e-commerce / marketplaces |
| **RCM (Reverse charge)** | Rare for your model — CA flags if wholesaler is unregistered |

---

## 12. Working with CA + ClearTax / Zoho

### Recommended split of work

| You (Indistylex owner) | CA + ClearTax/Zoho |
|------------------------|---------------------|
| Issue GST invoices on every sale | File GSTR-1, GSTR-3B |
| Collect & scan wholesaler purchase invoices | Match GSTR-2B vs purchases |
| Export website / Amazon / Flipkart reports | HSN summary, state-wise B2C |
| Log orders in **Business Tracker** Excel | Reconcile mismatches |
| Pay CA fee; approve return before filing | Sign off & submit on portal |
| Pay GST challan (or CA pays from your authorization) | Calculate exact liability |

### Data pack to send CA every month (by **5th**)

Use email / WhatsApp folder: `GST/2026-07/` (year-month)

```
☐ Website orders export (July 1–31)
    - Order ID, date, customer state, taxable value, GST rate, HSN
☐ B2B invoice PDFs + Excel list (invoice no, date, buyer GSTIN, amounts)
☐ Wholesaler purchase invoices (all GST bills for stock bought in July)
☐ Amazon Seller Central → Tax / MTR report (July)
☐ Flipkart seller tax report (if live)
☐ Credit notes / refunds issued in July
☐ Razorpay settlement summary (optional — for bank reconcile)
☐ Notes: any special cases (cancelled orders, wrong state, etc.)
```

### ClearTax / Zoho Books (typical flow)

1. **Invoices entered** (manual or import from Excel).  
2. Software calculates GSTR-1 JSON.  
3. CA reviews → uploads to GST portal.  
4. GSTR-2B imported → ITC matched.  
5. GSTR-3B auto-populated partly from GSTR-1 → CA adjusts → file & pay.

**Give CA GST portal login** (or use CA’s DSC / emsigner) — never share Aadhaar OTP casually; use official authorization.

---

## 13. Monthly calendar & checklist

### For month **M** (e.g. July sales → file in **August**)

| Date | Task | Owner |
|------|------|-------|
| **Daily** | GST invoice on every B2B sale; website orders recorded | You |
| **Daily** | Save wholesaler GST purchase bills | You |
| **1st–4th** | Close July books in Excel (Orders + Expenses tabs) | You |
| **By 5th** | Send **data pack** to CA | You |
| **By 10th** | CA shares draft GSTR-1 for your review | CA |
| **By 11th** | **GSTR-1 filed** | CA |
| **~14th** | GSTR-2B available — CA matches purchases | CA |
| **By 18th** | CA shares GSTR-3B + tax amount due | CA |
| **By 20th** | **GSTR-3B filed + GST paid** | CA / You pay challan |
| **After filing** | Save acknowledgment PDFs in `GST/2026-07/filed/` | You |

### Set phone reminders

- **5th** — Send data to CA  
- **18th** — Confirm 3B amount & pay  
- **25th** — Verify payment reflected in cash ledger  

---

## 14. Penalties & common mistakes

### Late filing (indicative — verify current rules)

| Issue | Risk |
|-------|------|
| Late GSTR-1 / GSTR-3B | Late fee (per day, capped) + interest on late tax |
| Non-filing | E-way bill blocked, GSTIN suspended, marketplace issues |
| Wrong ITC claim | Demand + interest + penalty — CA must match 2B |

### Mistakes Indistylex should avoid

| Mistake | Fix |
|---------|-----|
| No HSN on invoice | Use [HSN_CODES.md](HSN_CODES.md) |
| Wrong GST rate (5% vs 12%) | Rate = **your selling price**, not wholesaler’s |
| Missing B2B buyer GSTIN | Ask shop before first order |
| Website orders not shared with CA | Monthly export from admin |
| Personal purchases mixed with stock | Separate business bank + records |
| Ignoring Amazon reports | Download MTR every month |
| Not keeping purchase bills | No ITC → you pay more GST |

---

## 15. Records to keep (6 years)

GST law requires records for **at least 6 years** (72 months from due date of annual return).

| Record | Format |
|--------|--------|
| Sales invoices (all channels) | PDF + backup |
| Purchase invoices (wholesalers) | PDF + physical |
| Credit / debit notes | PDF |
| GSTR-1, 3B acknowledgments | PDF from portal |
| GST payment challans | PDF |
| Amazon / Flipkart tax reports | CSV/PDF monthly |
| Excel Business Tracker | XLSX monthly snapshot |

**Folder structure:**

```
Indistylex-GST-Records/
├── 2026-07/
│   ├── sales-website.csv
│   ├── sales-b2b-invoices/
│   ├── purchases/
│   ├── amazon-mtr-july.pdf
│   ├── filed-gstr1-ack.pdf
│   └── filed-gstr3b-ack.pdf
└── ...
```

---

## 16. GST vs Income Tax — don’t mix them

| | **GST** | **Income Tax** |
|---|---------|----------------|
| **What** | Indirect tax on **sales** | Direct tax on **profit** |
| **Frequency** | Monthly (GSTR-1, 3B) | Annual ITR (+ advance tax quarterly if high profit) |
| **Registered under** | GSTIN | PAN (same proprietor) |
| **Based on** | Turnover / tax invoices | Revenue − expenses |
| **Filed via** | gst.gov.in | incometax.gov.in |
| **Who files** | CA (ClearTax/Zoho) | CA — usually **ITR-3** or **ITR-4** for proprietorship |

**GST turnover ≠ taxable income.** Example: ₹20 lakh sales in a year doesn’t mean ₹20 lakh profit — subtract cost of goods, shipping, ads, etc.

### Proprietorship income tax (awareness only)

- Business profit added to your **personal** income.  
- **Presumptive taxation (44AD):** Some small businesses declare 6%–8% of turnover as profit — **only if CA confirms eligibility** (digital receipts may qualify for 6%).  
- **Advance tax:** If tax liability > ₹10,000/year, pay quarterly instalments (15 Jun, 15 Sep, 15 Dec, 15 Mar).  
- **Due date:** ITR usually **31 July** (non-audit) — CA handles.

**One CA can handle both GST and ITR** — share same Excel tracker.

---

## 17. Quick reference card

```
┌─────────────────────────────────────────────────────────────┐
│  INDISTYLEX GST MONTHLY — AT A GLANCE                        │
├─────────────────────────────────────────────────────────────┤
│  GSTIN: 09GVUPP6447P1Z3  │  State: UP  │  Most items: 5% GST │
├─────────────────────────────────────────────────────────────┤
│  YOU DO:                         CA DOES:                    │
│  • GST invoice every sale        • GSTR-1 by ~11th           │
│  • Save purchase bills           • GSTR-3B by ~20th          │
│  • Send data pack by 5th         • ITC match (GSTR-2B)       │
│  • Log in Excel tracker          • ClearTax / Zoho filing    │
├─────────────────────────────────────────────────────────────┤
│  GSTR-1 = WHAT YOU SOLD          GSTR-3B = PAY NET TAX       │
│  HSN summary mandatory           Output tax − ITC = payable  │
├─────────────────────────────────────────────────────────────┤
│  UP customer → CGST+SGST         Other state → IGST          │
│  B2B → need buyer GSTIN          B2C → state-wise totals   │
└─────────────────────────────────────────────────────────────┘
```

---

## Document index

| File | Purpose |
|------|---------|
| **This file** | GST awareness + monthly filing end-to-end |
| [HSN_CODES.md](HSN_CODES.md) | SKU, HSN, rates per product |
| [COUPON-CODES-GUIDE.md](COUPON-CODES-GUIDE.md) | Discounts (taxable value may reduce) |
| [packing-printables/invoice-gst-a4.html](packing-printables/invoice-gst-a4.html) | Printable GST invoice |
| [Indistylex-Business-Tracker.xlsx](Indistylex-Business-Tracker.xlsx) | Orders, expenses, SKU/HSN |
| [BUSINESS-BANKING-MONEY-GUIDE.md](BUSINESS-BANKING-MONEY-GUIDE.md) | Business bank account & money flow |
| [../BUSINESS_OPERATIONS_PLAYBOOK.md](../BUSINESS_OPERATIONS_PLAYBOOK.md) | Full business ops |

---

*Indistylex GST Guide — August 2026. Verify rates and due dates with your CA before each filing.*
