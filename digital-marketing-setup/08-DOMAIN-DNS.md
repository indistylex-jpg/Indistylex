# 08 — Domain & DNS Setup

## What This Does
Verifies your domain ownership across all platforms, sets up proper DNS records for email deliverability, and connects your domain to all marketing tools.

**Time needed**: 30-45 minutes

---

## Your Domain Info

| Field | Value |
|-------|-------|
| Domain | `indistylex.com` |
| Registrar | (where you bought the domain) |
| Nameservers | (your hosting/DNS provider) |
| SSL | Let's Encrypt (already configured) |
| Server IP | `138.201.50.228` |

---

## Step 1: Access DNS Management

1. Login to your domain registrar
2. Find **DNS Management** / **DNS Records** / **Zone Editor**
3. You should see existing records (A, CNAME, etc.)

### Current Records (should already exist):
| Type | Host | Value | Purpose |
|------|------|-------|---------|
| A | `@` | `138.201.50.228` | Points domain to server |
| A | `www` | `138.201.50.228` | www subdomain |
| CNAME | `www` | `indistylex.com` | Alternate www setup |

---

## Step 2: Email DNS Records

### 2.1 SPF Record (Who can send email as you)
| Type | Host | Value |
|------|------|-------|
| TXT | `@` | `v=spf1 ip4:138.201.50.228 include:sendinblue.com include:_spf.google.com ~all` |

> This allows: Your server, Brevo, and Google to send emails on your behalf.

### 2.2 DKIM Record (Email signature verification)
Your email provider will give you the exact DKIM value.

**For Brevo:**
| Type | Host | Value |
|------|------|-------|
| TXT | `mail._domainkey` | (Long string from Brevo dashboard) |

### 2.3 DMARC Record (Email policy)
| Type | Host | Value |
|------|------|-------|
| TXT | `_dmarc` | `v=DMARC1; p=quarantine; rua=mailto:hello@indistylex.com; pct=100` |

### 2.4 MX Records (If using custom email like hello@indistylex.com)

**If using Google Workspace:**
| Type | Host | Priority | Value |
|------|------|----------|-------|
| MX | `@` | 1 | `ASPMX.L.GOOGLE.COM` |
| MX | `@` | 5 | `ALT1.ASPMX.L.GOOGLE.COM` |
| MX | `@` | 5 | `ALT2.ASPMX.L.GOOGLE.COM` |
| MX | `@` | 10 | `ALT3.ASPMX.L.GOOGLE.COM` |
| MX | `@` | 10 | `ALT4.ASPMX.L.GOOGLE.COM` |

**If using Zoho Mail (Free for 1 user):**
| Type | Host | Priority | Value |
|------|------|----------|-------|
| MX | `@` | 10 | `mx.zoho.in` |
| MX | `@` | 20 | `mx2.zoho.in` |
| MX | `@` | 50 | `mx3.zoho.in` |

---

## Step 3: Domain Verification Records

### Google Search Console Verification:
| Type | Host | Value |
|------|------|-------|
| TXT | `@` | `google-site-verification=XXXXXXXXXX` |

### Meta/Facebook Domain Verification:
| Type | Host | Value |
|------|------|-------|
| TXT | `@` | `facebook-domain-verification=XXXXXXXXXX` |

### Google Merchant Center (if using DNS method):
| Type | Host | Value |
|------|------|-------|
| TXT | `@` | (Google provides specific verification string) |

---

## Step 4: Subdomain Setup (Optional)

You might want these subdomains:

| Subdomain | Purpose | Record Type | Value |
|-----------|---------|-------------|-------|
| `shop.indistylex.com` | Alternate shop URL | CNAME | `indistylex.com` |
| `track.indistylex.com` | Order tracking | CNAME | `indistylex.com` |
| `mail.indistylex.com` | Email sending | A | `138.201.50.228` |
| `links.indistylex.com` | Link tracking (Brevo) | CNAME | (Brevo provides) |

---

## Step 5: Verify All Connections

### Verification Checklist:

| Platform | How to Verify | Expected Result |
|----------|--------------|-----------------|
| Google Search Console | Settings → Verification | ✅ Verified |
| Facebook Business | Business Settings → Brand Safety → Domains | ✅ Verified |
| Google Merchant Center | Settings → Business Info | ✅ Claimed |
| Brevo | Settings → Senders & Domains | ✅ All green |
| Email (SPF) | https://mxtoolbox.com/spf.aspx | ✅ Pass |
| Email (DKIM) | https://mxtoolbox.com/dkim.aspx | ✅ Pass |
| Email (DMARC) | https://mxtoolbox.com/dmarc.aspx | ✅ Pass |
| SSL | https://www.ssllabs.com/ssltest/ | A or A+ grade |

---

## Step 6: Email Testing

### Test Your Email Deliverability:
1. Go to: https://www.mail-tester.com
2. Send an email from `hello@indistylex.com` to the provided address
3. Check your score (aim for 9/10 or 10/10)

### Common Issues:
| Score Deduction | Fix |
|----------------|-----|
| Missing SPF | Add SPF TXT record |
| Missing DKIM | Add DKIM record from email provider |
| No DMARC | Add DMARC TXT record |
| Blacklisted IP | Check at mxtoolbox.com/blacklists |
| Missing reverse DNS | Contact hosting provider |

---

## Step 7: SSL Certificate Check

Your site already has Let's Encrypt SSL. Verify:

1. Visit `https://indistylex.com`
2. Click padlock icon → "Connection is secure"
3. Check expiry date (Let's Encrypt = 90 days, auto-renews)

### Auto-Renewal (should already be set):
```bash
# On your server, this should exist:
sudo certbot renew --dry-run
```

---

## ✅ Checklist — You're Done When:

- [ ] A record pointing to server IP
- [ ] SPF record added (includes all senders)
- [ ] DKIM record added
- [ ] DMARC record added
- [ ] MX records configured (for custom email)
- [ ] Google Search Console domain verified
- [ ] Facebook domain verified
- [ ] Google Merchant Center domain claimed
- [ ] Brevo domain verified (all green)
- [ ] Email deliverability score 9+/10
- [ ] SSL working (no mixed content)
- [ ] DNS propagation complete (check at whatsmydns.net)

---

## Useful DNS Tools

| Tool | URL | Purpose |
|------|-----|---------|
| MXToolbox | mxtoolbox.com | Check all DNS records |
| WhatsmyDNS | whatsmydns.net | Check DNS propagation globally |
| Mail Tester | mail-tester.com | Test email deliverability |
| SSL Labs | ssllabs.com/ssltest | Test SSL configuration |
| DNS Checker | dnschecker.org | Verify record values |
| Google DNS | dns.google | Quick DNS lookup |

---

## DNS Propagation Note

After making DNS changes:
- **TXT records**: 15 min - 4 hours
- **A/CNAME records**: 15 min - 48 hours
- **MX records**: 1 - 24 hours

> Be patient. If verification fails, wait 1-2 hours and try again.
