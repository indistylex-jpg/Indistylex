# Indistylex — SKU & HSN Codes for Products

> **GSTIN:** 09GVUPP6447P1Z3  
> **Business:** Kids' clothing (0–12 years)  
> **Full list:** `Indistylex-Business-Tracker.xlsx` → **SKU & HSN Codes** tab  
> **Last updated:** July 12, 2026

---

## SKU Naming Convention

Every product variant gets a **unique SKU**:

```
IX - [TYPE] - [NUMBER] - [SIZE] - [COLOR]

Examples:
IX-FRK-001-2-3Y-PNK   →  Frock #1, 2-3 Years, Pink
IX-SHT-002-5-6Y-BLU   →  Shirt #2, 5-6 Years, Blue
IX-ETH-004-4-5Y-RED   →  Ethnic #4, 4-5 Years, Red
IX-SWD-003-0-6M-WHT   →  Swaddle #3, 0-6 Months, White
```

### SKU Type Codes

| Code | Product type |
|------|-------------|
| FRK | Frock / Dress |
| SHT | Shirt |
| JNS | Jeans |
| POL | Polo / T-shirt |
| HDI | Hoodie / Sweatshirt |
| TRK | Track suit |
| JGR | Jogger set |
| KRT | Kurta pajama |
| ETH | Ethnic (lehenga, sherwani, anarkali) |
| DNG | Dungaree |
| PJM | Pajama / Nightwear |
| RMP | Romper |
| BDY | Bodysuit |
| SWD | Swaddle / Blanket |
| SKT | Skirt |
| ACC | Accessories |

---

## Quick Reference — SKU + HSN + GST

| SKU Example | Product | HSN | GST (≤₹1000) | GST (>₹1000) |
|-------------|---------|-----|---------------|--------------|
| IX-FRK-001-2-3Y-PNK | Cotton Frock | **6204** | 5% | 12% |
| IX-SHT-002-5-6Y-BLU | Boys Shirt | **6205** | 5% | 12% |
| IX-POL-001-5-6Y-BLU | Polo T-Shirt | **6109** | 5% | 12% |
| IX-JNS-001-7-8Y-BLU | Denim Jeans | **6203** | 5% | 12% |
| IX-HDI-001-9-10Y-GRY | Hoodie | **6110** | 5% | 12% |
| IX-TRK-001-8-9Y-STR | Track Suit | **6112** | 5% | 12% |
| IX-ETH-004-4-5Y-RED | Lehenga Set | **6204** | 5% | 12% |
| IX-ETH-005-10-11Y-CRM | Sherwani Set | **6203** | 12% | 12% |
| IX-RMP-001-0-6M-WHT | Romper | **6111** | 5% | 12% |
| IX-SWD-003-0-6M-WHT | Swaddle Blanket | **6302** | 5% | 12% |

> Full list of 28+ products: open **SKU & HSN Codes** tab in `Indistylex-Business-Tracker.xlsx`

---

## GST Rule

```
Selling price per piece ≤ ₹1,000  →  5% GST
Selling price per piece >  ₹1,000  →  12% GST
```

---

## Where to Use SKU + HSN

| Platform / Document | SKU | HSN |
|---------------------|-----|-----|
| **Inventory tab** | Column A | Column F |
| **Orders tab** | Per order line | Per order line |
| **GST Invoice** | Item code | Mandatory column |
| **Amazon listing** | Seller SKU | Tax → HSN |
| **Flipkart listing** | Your SKU | Tax Details → HSN |
| **GSTR-1 filing** | — | HSN summary mandatory |

---

## Invoice Example

```
Indistylex (GSTIN: 09GVUPP6447P1Z3)
Invoice #INV-2026-0042

SKU                    Item                          HSN    Qty  Rate    GST%   Amount
IX-FRK-001-2-3Y-PNK   Cotton Frock Butterfly Garden  6204    1   ₹499    5%    ₹499.00
IX-SHT-002-5-6Y-BLU   Boys Cotton Half Shirt         6205    2   ₹399    5%    ₹798.00
                                              Subtotal:              ₹1,297.00
                                              GST (5%):              ₹64.85
                                              Total:                 ₹1,361.85
```

---

## Related

| File | Purpose |
|------|---------|
| `Indistylex-Business-Tracker.xlsx` | Master Excel — all tabs |
| `README.md` | How to use the workbook |
| `../BUSINESS_OPERATIONS_PLAYBOOK.md` §10.3 | GST quick reference |
| `GST-MONTHLY-FILING-GUIDE.md` | Full monthly filing guide (GSTR-1, GSTR-3B) |

---

*Verify HSN codes with your CA before GST filing.*
