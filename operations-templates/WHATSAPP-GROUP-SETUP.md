# Indistylex — WhatsApp Groups (Copy-Paste Setup)

> **Do this on Day 1.** Replace `[Manager Name]` and `[Assistant Name]` with real names.  
> Full text also in Excel → **WhatsApp Group Setup** tab.

---

## Before you start

1. Open `Indistylex-30-Day-Team-Plan.xlsx` → **Team Contacts** tab
2. Fill in Manager name, Assistant name, and all phone numbers
3. Create 3 groups on WhatsApp (phone app)

---

## Group 1: `Indistylex — Team`

**Members:** You + Manager + Assistant  
**Who leads:** Manager posts daily summary

### Group description (paste in group info)

```
Indistylex core team — daily operations
👤 Owner: Satyam Pandey (Bengaluru)
👤 Manager: [Manager Name]
👤 Shop: [Assistant Name] (Allahabad)

📋 Daily updates required
🕕 Assistant EOD: 6:30 PM
🕗 Manager summary: 8:00 PM
📗 Excel + admin sync same day
```

### Pin this as first message (group rules)

```
GROUP RULES — Indistylex Team

1️⃣ Assistant posts EOD update by 6:30 PM
2️⃣ Manager posts daily summary by 8:00 PM
3️⃣ Every delivery = photo in group
4️⃣ Stock issues → tag @Manager
5️⃣ Tech/payment issues → tag @Owner
6️⃣ Sunday = weekly summary from Manager

Templates: Excel → WhatsApp Templates tab
```

---

## Group 2: `Indistylex — Shop Ops`

**Members:** Manager + Assistant only (you optional as silent observer)  
**Who leads:** Manager sends morning tasks

### Group description

```
Fast shop coordination — Manager + Assistant only
Manager: [Manager Name]
Assistant: [Assistant Name] (Allahabad shop)

Use for: delivery tasks, packing, urgent stock, photos
```

### Pin this as first message

```
SHOP OPS RULES

1️⃣ Manager sends task list every morning by 10 AM
2️⃣ Assistant replies ✅ when task read
3️⃣ Photo proof for every delivery
4️⃣ Cash collected → report amount + transfer same day
```

---

## Group 3: `Indistylex — B2B Shops`

**Members:** Manager + shop owners (add one by one)  
**Assistant NOT in this group**

### Group description

```
B2B wholesale shop owners — Indistylex
Order confirmations, payment reminders, new arrivals
Website: indistylex.com
```

### Pin this as welcome message

```
Welcome to Indistylex wholesale!

🏷️ Kids clothing 0-14 years
🚚 Delivery in Prayagraj / nearby
💳 COD & credit available (approved shops)
📦 Min order: [set your minimum]
👤 Contact: [Manager Name] — [Manager Phone]
🌐 Catalog: indistylex.com
```

---

## Day 1 — first messages to send

### In Group 1 (after everyone joined)

**You post:**
```
Welcome team! 👋

This is our official Indistylex operations group.

📗 Excel files shared on Drive: [paste link]
📋 30-day plan: open Indistylex-30-Day-Team-Plan.xlsx

@[Manager Name] — you lead daily updates
@[Assistant Name] — you post EOD from 6:30 PM

Let's start tomorrow. Day 1 task in Excel → 30-Day Plan tab.
```

### In Group 2

**Manager posts:**
```
Shop ops group — for fast daily tasks only.
I'll send your task list here every morning by 10 AM.
Reply ✅ when you've read it.
```

---

## Manager admin access message (send privately to Manager)

```
Hi [Manager Name] — your Indistylex manager access:

🔐 Admin: https://indistylex.com/admin
📧 Email: admin@indistylex.in
🔑 Password: [share from CREDENTIALS.md privately — NOT in group]

Daily:
- Check Orders + Inventory morning & evening
- Record B2B sales in admin → Inventory → Record B2B Sale
- Update Excel same day

Call me only for: server issues, discount >10%, shop credit approval.
```

> ⚠️ Never post admin password in a WhatsApp group.

---

## Update names in Excel permanently

Edit top of `build_30_day_plan.py`:

```python
MANAGER_NAME = 'Rahul'           # real name
MANAGER_PHONE = '+91 98XXXXXXXX'
ASSISTANT_NAME = 'Amit'          # real name
ASSISTANT_PHONE = '+91 97XXXXXXXX'
```

Then run:
```bash
cd operations-templates
.xlsx-venv/bin/python3 build_30_day_plan.py
```

---

*Related: [30-DAY-TEAM-OPERATIONS-GUIDE.md](30-DAY-TEAM-OPERATIONS-GUIDE.md)*
