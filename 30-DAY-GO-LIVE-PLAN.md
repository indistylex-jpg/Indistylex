# Indistylex — 30-Day Go-Live Plan

> **Start date:** June 13, 2026  
> **Launch date:** July 10, 2026 (Friday)  
> **Domain:** [indistylex.com](https://indistylex.com)  
> **Production server:** `138.201.50.228` (HTTPS live)  
> **Last audited:** June 13, 2026 — live site + DNS + code reviewed

This plan combines **technical production readiness**, **business setup**, and **digital marketing launch** into one day-by-day roadmap. Items marked ✅ were verified on the live site or in code. Items marked 🔶 need your confirmation (set up in external dashboards, not verifiable from code). Items marked ❌ are confirmed gaps.

---

## Production Environment (Updated)

| Item | Value | Status |
|------|-------|--------|
| Domain | `indistylex.com` | ✅ Live |
| Server IP | `138.201.50.228` | ✅ DNS resolves |
| HTTPS / SSL | Let's Encrypt + HSTS | ✅ Verified |
| App server | Gunicorn | ✅ Running |
| Security headers | CSP, X-Frame-Options, etc. | ✅ Active |
| Sitemap | `https://indistylex.com/sitemap.xml` | ✅ Working |
| Robots.txt | `https://indistylex.com/robots.txt` | ✅ Working |
| Products on site | Shop page live with catalog | ✅ Verified |
| Old server | `78.46.145.88` (Hetzner) | ⚠️ Deprecated — update `DEPLOYMENT.md` |

> **Note:** Website templates still use `support@indistylex.in` in many places. Standardize to `@indistylex.com` emails across site, emails, and JSON-LD.

---

## Digital Platform Audit

Checked against `digital-marketing-setup/` guides and live site on June 13, 2026.

### ✅ DONE — Verified on Live Site / DNS

| Platform | Guide | Evidence |
|----------|-------|----------|
| Domain `indistylex.com` | `08-DOMAIN-DNS.md` | A record → `138.201.50.228` |
| HTTPS / SSL | `08-DOMAIN-DNS.md` | HSTS header, padlock secure |
| Website deployed | `DEPLOYMENT.md` | Homepage, shop, products loading |
| Product catalog live | — | Shop page active with products |
| SEO sitemap | `12-SEO-TECHNICAL.md` | `/sitemap.xml` returns valid XML |
| SEO robots.txt | `12-SEO-TECHNICAL.md` | Blocks admin/auth, lists sitemap |
| Google Tag Manager | `05-TRACKING-SETUP.md` | `GTM-KH75QZKH` in page source |
| Facebook Page | `02-META-BUSINESS.md` | `facebook.com/indistylex` exists |
| Instagram profile | `03-INSTAGRAM-BUSINESS.md` | `instagram.com/indistylex` exists |
| Legal pages live | `09-LEGAL-COMPLIANCE.md` | Privacy, terms, FAQ, contact pages |
| GST in schema | `09-LEGAL-COMPLIANCE.md` | `09GVUPP6447P1Z3` in JSON-LD |
| Business address in schema | — | Prayagraj address in `base.html` |
| GTM container created | `05-TRACKING-SETUP.md` | Container ID active in code |

### 🔶 LIKELY DONE — You Set Up via Docs (Confirm in Your Dashboards)

These cannot be verified without login access. **Please confirm each in your accounts:**

| Platform | Guide | How to confirm |
|----------|-------|----------------|
| Google Analytics 4 | `05-TRACKING-SETUP.md` | GA4 → Reports → Realtime shows visitors |
| Meta Pixel | `02-META-BUSINESS.md` | Events Manager → Test Events on site visit |
| Meta Business Manager | `02-META-BUSINESS.md` | business.facebook.com → Business Settings |
| Google Search Console | `12-SEO-TECHNICAL.md` | search.google.com/search-console → property verified |
| Google Business Profile | `01-GOOGLE-BUSINESS.md` | business.google.com → profile verified |
| Brevo (email marketing) | `06-EMAIL-SETUP.md` | app.brevo.com → Senders & Domains all green |
| WhatsApp Business | `07-WHATSAPP-SETUP.md` | WhatsApp Business app → profile complete |
| Razorpay (live keys) | `10-PAYMENT-SHIPPING.md` | dashboard.razorpay.com → Live mode active |
| Google Ads account | `04-GOOGLE-ADS-SETUP.md` | ads.google.com → account created |
| Google Merchant Center | `04-GOOGLE-ADS-SETUP.md` | merchants.google.com → domain claimed |
| Microsoft Clarity | `05-TRACKING-SETUP.md` | clarity.microsoft.com → project receiving data |
| Canva / content tools | `11-SOCIAL-TOOLS.md` | Your Canva/Later accounts |
| Shiprocket / shipping | `10-PAYMENT-SHIPPING.md` | shiprocket.in → pickup address added |

### ❌ NOT DONE — Confirmed Gaps (Fix Before Full Launch)

| Item | Guide | Evidence | Priority |
|------|-------|----------|----------|
| Email DNS (SPF/DKIM/DMARC) | `08-DOMAIN-DNS.md` | No TXT/MX records on domain | 🔴 Critical |
| GTM blocked by CSP | `05-TRACKING-SETUP.md` | Live CSP missing `googletagmanager.com` in `script-src` — GA4/Pixel may not fire | 🔴 Critical |
| Footer social links | `03-INSTAGRAM-BUSINESS.md` | Live site: `href="#"` for Facebook/Instagram | 🟠 High |
| WhatsApp button on website | `07-WHATSAPP-SETUP.md` | No `wa.me` link found on live site | 🟠 High |
| Newsletter → Brevo API | `06-EMAIL-SETUP.md` | Code: toast only, no backend | 🟠 High |
| Contact form → email | — | Code: logs only, no email sent | 🟠 High |
| Email addresses inconsistent | `08-DOMAIN-DNS.md` | Site shows `support@indistylex.in`, docs use `.com` | 🟠 High |
| `sameAs` social in JSON-LD | `12-SEO-TECHNICAL.md` | Empty array in schema — add IG/FB URLs | 🟡 Medium |
| Missing OG image | `12-SEO-TECHNICAL.md` | `og-default.jpg` referenced but missing | 🟡 Medium |
| Microsoft Clarity in HTML | `05-TRACKING-SETUP.md` | Not detected in page source | 🟡 Medium |
| Pinterest / Twitter links | `11-SOCIAL-TOOLS.md` | Footer links are `#` | 🟡 Medium |
| Ecommerce dataLayer events | `05-TRACKING-SETUP.md` | Purchase/AddToCart events not in templates | 🟡 Medium |
| Abandoned cart emails | `07-EMAIL-MARKETING.md` | Not wired in app | 🟢 Low |
| CI/CD pipeline | — | No GitHub Actions | 🟢 Low |

### ⚠️ Critical Fix — GTM / Analytics May Be Broken

Your live site Content-Security-Policy allows scripts only from `'self'`, `cdn.jsdelivr.net`, and `checkout.razorpay.com`. **Google Tag Manager, GA4, Meta Pixel, and Clarity all load from external domains and are likely blocked.**

**Fix in `app/__init__.py` — add to `script-src`:**
```
https://www.googletagmanager.com https://connect.facebook.net https://www.clarity.ms
```

Also add to `connect-src`:
```
https://www.google-analytics.com https://analytics.google.com https://www.facebook.com
```

Redeploy after this fix, then verify with Meta Pixel Helper and GA4 Realtime.

---

## Current Status Summary

### ✅ DONE — Website Development

| Area | Status |
|------|--------|
| Storefront, shop, filters, search, product pages | ✅ Done |
| Cart, checkout (COD + Razorpay code) | ✅ Done |
| User accounts, wishlist, orders, reviews, coupons | ✅ Done |
| Admin dashboard (full CRUD) | ✅ Done |
| Static pages, chatbot, mobile API | ✅ Done |
| SEO basics (meta, JSON-LD, sitemap, robots) | ✅ Done |
| Automated tests (~169 pytest) | ✅ Done |
| Deployed on production server with HTTPS | ✅ Done |
| Products live on site | ✅ Done |

### ✅ DONE — Documentation

| Area | Location |
|------|----------|
| Digital marketing playbook (10 guides) | `digital-marketing/` |
| Platform setup guides (12 guides) | `digital-marketing-setup/` |
| Brand guide, 90-day checklist, ad templates | `digital-marketing/` |
| Deployment guides | `DEPLOYMENT.md`, `PRODUCTION_CHECKLIST.md` |

### ❌ REMAINING — Before Full Public Launch

| Item | Priority |
|------|----------|
| Fix CSP so GTM/GA4/Pixel actually work | 🔴 Critical |
| Email DNS (SPF, DKIM, DMARC) for `@indistylex.com` | 🔴 Critical |
| SMTP configured for order emails | 🔴 Critical |
| Confirm Razorpay live keys on server | 🔴 Critical |
| Wire contact form + newsletter to email/Brevo | 🟠 High |
| Add social + WhatsApp links to website | 🟠 High |
| Standardize all emails to `@indistylex.com` | 🟠 High |
| End-to-end order test (COD + Razorpay + emails) | 🟠 High |
| Submit sitemap in Search Console | 🟡 Medium |
| Launch first ad campaigns | 🟡 Medium |

---

## 30-Day Plan — Adjusted for Current Progress

> **Week 1 infrastructure (domain, SSL, deploy) is largely complete.** The plan below starts from where you are today.

### WEEK 1 (Days 1–7): Fix Gaps & Wire Integrations
**Goal:** Make tracking, email, and lead capture actually work on the live site.

#### Day 1 — Audit & Confirm Platforms ✅
- [x] Domain `indistylex.com` live on `138.201.50.228`
- [x] HTTPS working
- [x] Products on site
- [x] Facebook + Instagram profiles exist
- [ ] **You confirm:** GA4, Meta Pixel, Search Console, Brevo, Razorpay live, WhatsApp — check dashboards listed in audit above
- [ ] Complete `todo.md` questionnaire (phone, budget, photo status)
- [ ] Document which platforms are ✅ in your accounts vs still pending

#### Day 2 — Fix Tracking (CSP + GTM)
- [ ] Fix CSP in `app/__init__.py` to allow GTM, GA4, Meta Pixel, Clarity domains
- [ ] Verify GTM container `GTM-KH75QZKH` has these tags published:
  - GA4 Configuration
  - Meta Pixel base + events
  - Clarity (optional)
- [ ] Add ecommerce `dataLayer` events: `view_item`, `add_to_cart`, `begin_checkout`, `purchase`
- [ ] Deploy to server, restart service
- [ ] Test: GA4 Realtime, Meta Pixel Helper, GTM Preview mode
- [ ] Guide: `digital-marketing-setup/05-TRACKING-SETUP.md`

#### Day 3 — Email DNS & SMTP
- [ ] Add SPF, DKIM, DMARC records for `indistylex.com`
  - Guide: `digital-marketing-setup/08-DOMAIN-DNS.md`
- [ ] Verify Brevo domain (all green in Senders & Domains)
- [ ] Configure server `.env` SMTP for transactional emails (orders, password reset)
- [ ] Set up `hello@indistylex.com`, `support@indistylex.com`, `noreply@indistylex.com`
- [ ] Test: order confirmation email, password reset email
- [ ] Test deliverability at mail-tester.com (target 9+/10)

#### Day 4 — Wire Website Integrations
- [ ] **Contact form:** send email via `email_service` (currently logs only)
- [ ] **Newsletter:** connect footer form to Brevo API
- [ ] **Footer social links:** update to real URLs:
  - `https://www.facebook.com/indistylex`
  - `https://www.instagram.com/indistylex`
- [ ] **WhatsApp floating button:** add `wa.me/91XXXXXXXXXX` (your business number)
- [ ] **JSON-LD `sameAs`:** add Instagram + Facebook URLs
- [ ] Replace all `support@indistylex.in` → `support@indistylex.com` in templates
- [ ] Add missing `og-default.jpg` and product placeholder image
- [ ] Deploy and test all changes on live site

#### Day 5 — Payments & Orders End-to-End
- [ ] Confirm Razorpay **live** keys in server `.env`
- [ ] Update Razorpay dashboard callback URL: `https://indistylex.com/checkout/...`
- [ ] Test COD order: browse → cart → checkout → admin → status email
- [ ] Test Razorpay order: ₹1 test payment → refund
- [ ] Verify purchase event fires in GA4 + Meta Pixel on success page
- [ ] Set up daily DB backup cron on server
- [ ] Guide: `digital-marketing-setup/10-PAYMENT-SHIPPING.md`

#### Day 6 — Search Console & Google Business
- [ ] Verify domain in Google Search Console (if not done)
- [ ] Submit sitemap: `https://indistylex.com/sitemap.xml`
- [ ] Request indexing for homepage and top product pages
- [ ] Confirm Google Business Profile is verified and 100% complete
- [ ] Add website link `https://indistylex.com` to GBP, Instagram, Facebook
- [ ] Run through `digital-marketing/03-SEO-CHECKLIST.md`
- [ ] Run PageSpeed Insights — target 70+ mobile score

#### Day 7 — Week 1 Review
- [ ] Tracking works: GA4 realtime + Pixel Helper green
- [ ] Emails deliver: order confirm, password reset, contact form
- [ ] Newsletter saves to Brevo
- [ ] Social + WhatsApp links work from website
- [ ] Full mobile test on real phone
- [ ] Fix any bugs found

---

### WEEK 2 (Days 8–14): Marketing Activation & Content
**Goal:** Activate email flows, social content, and platform connections.

#### Day 8 — Brevo Email Automations
- [ ] Welcome series (3 emails) active in Brevo
- [ ] Post-purchase review request email (7 days after delivery)
- [ ] Launch announcement email template ready
- [ ] Guide: `digital-marketing-setup/06-EMAIL-SETUP.md`, `digital-marketing/07-EMAIL-MARKETING.md`

#### Day 9 — WhatsApp Business Complete
- [ ] Profile 100% complete (photo, description, hours, catalog)
- [ ] 8+ quick replies saved
- [ ] Click-to-chat link in Instagram bio + Facebook page
- [ ] Guide: `digital-marketing-setup/07-WHATSAPP-SETUP.md`

#### Day 10 — Social Profiles Polish
- [ ] Instagram bio optimized with link to `indistylex.com`
- [ ] Facebook page fully filled (about, cover, CTA button → Shop Now)
- [ ] Connect Instagram ↔ Facebook ↔ Website in Meta Business Suite
- [ ] Pinterest business account + 10 pins (optional)
- [ ] Guide: `digital-marketing-setup/03-INSTAGRAM-BUSINESS.md`

#### Day 11 — Content Creation
- [ ] Create 5 Canva post templates (brand colors from `02-BRAND-GUIDE.md`)
- [ ] Run `digital-marketing-assets/generate_assets.py` for ad banners
- [ ] Prepare 14 Instagram posts (2 weeks of content)
- [ ] Prepare 3 Reels (product showcase, styling, unboxing)
- [ ] Guide: `digital-marketing/06-SOCIAL-MEDIA.md`

#### Day 12 — Publish & Engage
- [ ] Publish first 3 Instagram posts
- [ ] Publish first Facebook post
- [ ] Post daily Stories (product highlights, behind-the-scenes)
- [ ] Join 3–5 Facebook parenting groups (build presence, don't spam)
- [ ] Engage with 10 accounts in kids' fashion niche daily

#### Day 13 — Google Ads & Merchant Prep
- [ ] Google Ads account ready with billing
- [ ] Google Merchant Center: domain claimed, product feed uploaded
- [ ] Link Merchant Center → Google Ads
- [ ] **Do NOT launch ads yet** — wait for Merchant approval (3–7 days)
- [ ] Guide: `digital-marketing-setup/04-GOOGLE-ADS-SETUP.md`

#### Day 14 — Week 2 Review
- [ ] GA4 shows 7+ days of traffic data
- [ ] Search Console shows pages indexed
- [ ] Instagram + Facebook consistent (logo, bio, website link)
- [ ] Brevo welcome email triggers on newsletter signup
- [ ] Email list: aim for 30+ subscribers (friends, family, social)

---

### WEEK 3 (Days 15–21): Pre-Launch Hardening & Outreach
**Goal:** Security pass, ad account setup, influencer outreach, dry-run.

#### Day 15 — Meta Ads Account Ready
- [ ] Business Manager verified
- [ ] Ad account with payment method (INR)
- [ ] Meta Pixel collecting data 7+ days (needed for custom audiences)
- [ ] 3 ad creatives prepared from `digital-marketing/templates/`
- [ ] Guide: `digital-marketing/05-META-ADS.md`

#### Day 16 — Security & Server Hardening
- [ ] Rotate `SECRET_KEY` on production
- [ ] Change `ADMIN_PASSWORD` from default
- [ ] Remove test credentials from `.env.example`
- [ ] Enable UFW firewall (ports 22, 80, 443 only)
- [ ] Set up fail2ban for SSH
- [ ] Set up UptimeRobot monitoring (ping every 5 min)
- [ ] Verify Redis running: `redis-cli ping`

#### Day 17 — Shipping & Operations
- [ ] Confirm shipping partner (Shiprocket / Delhivery / DTDC)
- [ ] Packaging materials ready (tissue, thank-you card, invoice)
- [ ] Document order fulfillment SOP
- [ ] Test admin order flow: receive → pack → ship → update status → email
- [ ] Guide: `digital-marketing-setup/10-PAYMENT-SHIPPING.md`

#### Day 18 — Influencer Outreach
- [ ] Identify 10 micro-influencers (5K–50K, parenting/kids niche)
- [ ] Send first 5 outreach DMs
- [ ] Create influencer coupon codes in admin
- [ ] Guide: `digital-marketing/09-INFLUENCER.md`

#### Day 19 — Abandoned Cart & Email List
- [ ] Brevo abandoned cart flow (24h + 72h) — minimum: manual reminder via WhatsApp
- [ ] Build email list to 50+ subscribers
- [ ] Send pre-launch teaser email to list

#### Day 20 — Dry-Run Rehearsal
- [ ] Complete full launch day simulation:
  1. Customer places order (COD + Razorpay)
  2. Admin processes order
  3. Status update email sent
  4. GA4 + Pixel record purchase
  5. WhatsApp thank-you sent
- [ ] Fix all P0/P1 bugs

#### Day 21 — Week 3 Review
- [ ] All critical gaps from audit section closed
- [ ] Ad accounts ready but not yet spending
- [ ] 50+ email subscribers
- [ ] Launch day checklist prepared (Day 30)

---

### WEEK 4 (Days 22–28): Launch Week 🚀
**Goal:** Soft launch → public launch → first ad campaigns.

#### Day 22 — Soft Launch
- [ ] Message 20–30 friends/family with site link + 10% coupon
- [ ] Instagram Story: "We're live!"
- [ ] Monitor server: `journalctl -u indistylex -f`
- [ ] Target: 3–5 real orders

#### Day 23 — Fix Soft Launch Issues
- [ ] Review all orders end-to-end (packaging, shipping, emails)
- [ ] Fix UX issues reported
- [ ] Respond to all messages within 2 hours

#### Day 24 — Launch Meta Ads
- [ ] First campaign: ₹300/day, Conversions (Purchase)
- [ ] Audience: Parents 25–40, India, kids clothing interests
- [ ] Creative: best-performing organic post
- [ ] Guide: `digital-marketing/05-META-ADS.md`

#### Day 25 — Launch Google Ads
- [ ] Brand keywords: ₹100/day ("indistylex", "indistylex kids clothes")
- [ ] 5–10 category keywords
- [ ] Enable Shopping Ads if Merchant Center approved
- [ ] Guide: `digital-marketing/04-GOOGLE-ADS.md`

#### Day 26 — Public Launch Day 🚀
- [ ] Launch post on Instagram feed + Facebook
- [ ] Launch Reel
- [ ] Launch email to full Brevo list
- [ ] WhatsApp broadcast to contacts
- [ ] Google Business post: "Now live!"
- [ ] Monitor ads, site, orders every 2 hours

#### Day 27 — Post-Launch Engagement
- [ ] Reply to every comment, DM, review
- [ ] Share customer unboxing on Stories (with permission)
- [ ] Pause ads with CPC > ₹15 and no conversions
- [ ] Scale winning ads (+20% budget)

#### Day 28 — Week 4 Metrics Review

| Metric | Target |
|--------|--------|
| Orders | 10+ |
| Website sessions | 500+ |
| Instagram followers | 200+ |
| Email subscribers | 50+ |
| Ad spend | ₹2,800 (₹400/day × 7) |
| Conversion rate | 1–3% |

- [ ] Review GA4 funnel: sessions → product views → cart → purchase
- [ ] Plan Month 2 from `digital-marketing/FIRST-90-DAYS.md`

---

### DAYS 29–30: Stabilize & Sign-Off

#### Day 29 — Operations & Monitoring
- [ ] Weekly backup restore test
- [ ] Error alerting (Sentry or log-based)
- [ ] Monthly analytics template from `digital-marketing/10-ANALYTICS.md`

#### Day 30 — Official Go-Live Sign-Off

**Infrastructure**
- [x] HTTPS on indistylex.com
- [ ] Server auto-restarts on reboot
- [ ] Daily DB backups
- [ ] Redis running
- [ ] Firewall configured
- [ ] Uptime monitoring active

**Payments & Email**
- [ ] Razorpay live payments tested
- [ ] COD flow tested
- [ ] Order emails sending
- [ ] Contact form emails sending
- [ ] Email DNS (SPF/DKIM/DMARC) verified

**Website Quality**
- [x] Products with photos live
- [ ] All pages error-free
- [ ] Mobile responsive verified
- [ ] Emails standardized to `@indistylex.com`
- [ ] Social + WhatsApp links on site

**Marketing**
- [ ] GA4 + Meta Pixel tracking purchases (CSP fixed)
- [ ] Search Console verified + sitemap submitted
- [ ] Instagram + Facebook active with website link
- [ ] WhatsApp Business ready
- [ ] At least 1 ad campaign running

**Security**
- [ ] Strong SECRET_KEY and admin password
- [ ] No secrets in git
- [ ] HTTPS enforced

- [ ] 🎉 **Indistylex officially live on production**

---

## Post-Launch — Month 2

Continue with `digital-marketing/FIRST-90-DAYS.md` Month 2:

| Week | Focus |
|------|-------|
| Week 5 | Scale winning Meta ads, Google Shopping |
| Week 6 | 2 SEO blog posts, 2 influencer collabs |
| Week 7 | Retargeting campaign, A/B test creatives |
| Week 8 | Monthly analytics report, festival campaign plan |

---

## Daily Routine (30–45 min)

| Time | Task | Minutes |
|------|------|---------|
| Morning | Check orders, reply DMs/comments | 10 |
| Morning | Post 1 Instagram Story | 10 |
| Midday | Engage with 10 niche accounts | 10 |
| Evening | Check ad performance (from Day 24) | 10 |
| Evening | Reply to messages & reviews | 5 |

---

## Budget Summary (Month 1)

| Item | Cost | Status |
|------|------|--------|
| Domain indistylex.com | ~₹800/year | ✅ Owned |
| Server `138.201.50.228` | ~₹1,500/month | ✅ Running |
| SSL (Let's Encrypt) | Free | ✅ Active |
| Razorpay | 2% per transaction | Confirm live |
| Meta Ads | ₹9,000 (from Day 24) | Pending |
| Google Ads | ₹3,000 (from Day 25) | Pending |
| Brevo email | Free (300/day) | Confirm setup |
| Canva | Free tier | — |
| **Total Month 1** | **~₹14,000–19,000** | excl. inventory |

---

## Priority Order (Do These First)

1. **Fix CSP** — GTM/GA4/Pixel likely blocked right now
2. **Email DNS** — SPF/DKIM/DMARC for `@indistylex.com`
3. **SMTP on server** — order confirmation emails
4. **Confirm Razorpay live keys** — online payments
5. **Wire contact + newsletter** — stop losing leads
6. **Add social + WhatsApp links** — connect website to your profiles
7. **Standardize emails to `.com`** — professional consistency
8. **Search Console + sitemap** — start Google indexing
9. **End-to-end order test** — COD + Razorpay + emails + tracking
10. **Launch Meta ad ₹300/day** — start traffic (Week 4)

---

## Quick Reference

| Need | File |
|------|------|
| Deploy to server | `DEPLOYMENT.md` (update IP to `138.201.50.228`) |
| DNS & email setup | `digital-marketing-setup/08-DOMAIN-DNS.md` |
| Tracking fix | `digital-marketing-setup/05-TRACKING-SETUP.md` |
| Platform setup index | `digital-marketing-setup/README.md` |
| 90-day marketing | `digital-marketing/FIRST-90-DAYS.md` |
| Business info needed | `todo.md` |

---

*Last updated: June 13, 2026 — Live site audited at https://indistylex.com*
