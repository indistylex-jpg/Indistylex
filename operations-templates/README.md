# Indistylex — Business Tracker (Excel)

> **One file for everything.** Open in Microsoft Excel or LibreOffice Calc.

---

## File

| File | Description |
|------|-------------|
| **`Indistylex-Business-Tracker.xlsx`** | Master workbook — all business tracking in one place |
| **`Indistylex-30-Day-Team-Plan.xlsx`** | 30-day day-by-day plan for Owner + Manager + Assistant (Allahabad shop) |
| **[30-DAY-TEAM-OPERATIONS-GUIDE.md](30-DAY-TEAM-OPERATIONS-GUIDE.md)** | How to use both files + WhatsApp groups + weekly reviews |
| **[WHATSAPP-GROUP-SETUP.md](WHATSAPP-GROUP-SETUP.md)** | Copy-paste WhatsApp group descriptions + Day 1 messages |
| **[CATEGORY-CATALOG-0-18.md](CATEGORY-CATALOG-0-18.md)** | Full category list 0–18Y for Admin UI + Amazon/Flipkart |
| **[COUPON-CODES-GUIDE.md](COUPON-CODES-GUIDE.md)** | Website discount codes — Admin → Coupons, campaigns, examples |
| **[GST-MONTHLY-FILING-GUIDE.md](GST-MONTHLY-FILING-GUIDE.md)** | GST & tax awareness — GSTR-1, GSTR-3B, ITC, CA workflow, monthly checklist |
| **[BUSINESS-BANKING-MONEY-GUIDE.md](BUSINESS-BANKING-MONEY-GUIDE.md)** | Business current account — open, connect Razorpay/Amazon, money handling |
| **[packing-printables/](packing-printables/)** | Print pack: poster, thank-you cards, GST invoice, shipping label guide |

---

## Tabs inside the workbook

| Tab | Purpose | Update |
|-----|---------|--------|
| **Inventory** | SKU, HSN, stock (warehouse + Amazon + Flipkart + B2B) | Daily |
| **Orders** | Every sale — website, Amazon, Flipkart, B2B | Per order |
| **Expenses** | Wholesaler, shipping, ads, packaging, server | When you spend |
| **Weekly KPIs** | Weekly revenue, orders, profit vs targets | Every Monday |
| **B2B Customers** | Wholesale shop contacts and credit tracking | Per B2B order |
| **SKU & HSN Codes** | Full SKU + HSN + GST reference (28 products) | Reference |
| **Monthly P&L** | Profit & loss by channel | 1st of month |
| **Amazon Listing** | Template for new Amazon product listings | Per product |
| **Flipkart Listing** | Template for new Flipkart product listings | Per product |

---

## Pre-built formulas

**Inventory tab:**
- **Available to Sell** (col O) = Warehouse − Amazon − Flipkart − B2B reserved
- **Status** (col T) = Out of Stock / Low Stock / Active

**Weekly KPIs tab:**
- **Total Orders** = sum of all channel orders
- **Total Revenue** = sum of all channel revenue
- **Net Profit** = Revenue − Expenses

---

## Daily routine (5 min)

| When | Tab | Action |
|------|-----|--------|
| Morning | Inventory | Update stock counts |
| Every order | Orders | Add one row (SKU + HSN) |
| Every payment | Expenses | Add one row |
| Monday | Weekly KPIs | Fill week's totals |

---

## SKU format

```
IX-[TYPE]-[NUMBER]-[SIZE]-[COLOR]

IX-FRK-001-2-3Y-PNK  →  Frock, 2-3Y, Pink, HSN 6204
IX-SHT-002-5-6Y-BLU  →  Shirt, 5-6Y, Blue, HSN 6205
```

Full reference: **SKU & HSN Codes** tab, or see [HSN_CODES.md](HSN_CODES.md).

---

## Related docs

| Document | Purpose |
|----------|---------|
| [HSN_CODES.md](HSN_CODES.md) | SKU naming rules + GST guide |
| [../BUSINESS_OPERATIONS_PLAYBOOK.md](../BUSINESS_OPERATIONS_PLAYBOOK.md) | Full business operations guide |

---

*Indistylex Business Tracker — July 12, 2026*
