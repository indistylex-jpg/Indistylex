# Silkensway Clothing — Production Deployment Checklist

> **Single dedicated server (Ubuntu 22.04/24.04 recommended) with a domain name.**
> This document covers every step from server setup to go-live.

---

## Table of Contents

1. [Server Requirements](#1-server-requirements)
2. [Domain & DNS Setup](#2-domain--dns-setup)
3. [Server Initial Setup](#3-server-initial-setup)
4. [Install Dependencies](#4-install-dependencies)
5. [Clone & Configure the App](#5-clone--configure-the-app)
6. [Environment Variables (.env)](#6-environment-variables-env)
7. [Database Setup (MySQL)](#7-database-setup-mysql)
8. [Redis Setup](#8-redis-setup)
9. [Run the Application with Gunicorn](#9-run-the-application-with-gunicorn)
10. [Nginx Reverse Proxy + SSL](#10-nginx-reverse-proxy--ssl)
11. [Celery Worker (Background Tasks)](#11-celery-worker-background-tasks)
12. [Firewall Configuration](#12-firewall-configuration)
13. [OAuth Setup (Google & Facebook)](#13-oauth-setup-google--facebook)
14. [Razorpay Production Keys](#14-razorpay-production-keys)
15. [Email Configuration](#15-email-configuration)
16. [File Uploads & Permissions](#16-file-uploads--permissions)
17. [Security Hardening Checklist](#17-security-hardening-checklist)
18. [Backup Strategy](#18-backup-strategy)
19. [Monitoring & Logging](#19-monitoring--logging)
20. [Final Go-Live Checks](#20-final-go-live-checks)
21. [Quick Reference Commands](#21-quick-reference-commands)

---

## 1. Server Requirements

| Resource       | Minimum            | Recommended          |
|----------------|--------------------|----------------------|
| **OS**         | Ubuntu 22.04 LTS   | Ubuntu 24.04 LTS    |
| **CPU**        | 2 vCPU             | 4 vCPU               |
| **RAM**        | 2 GB               | 4 GB                 |
| **Disk**       | 20 GB SSD          | 40 GB SSD            |
| **Bandwidth**  | 1 TB/month         | 2 TB/month           |

Providers: DigitalOcean, Hetzner, Linode, AWS Lightsail, Hostinger VPS, etc.

---

## 2. Domain & DNS Setup

1. **Buy a domain** (e.g., `silkensway.com`) from Namecheap, GoDaddy, Google Domains, etc.
2. **Point DNS** to your server's IP address:

   ```
   Type   Name   Value              TTL
   A      @      YOUR_SERVER_IP     300
   A      www    YOUR_SERVER_IP     300
   ```

3. Wait for DNS propagation (5 min – 48 hours, usually under 30 min).
4. Verify: `ping silkensway.com` should resolve to your server IP.

---

## 3. Server Initial Setup

SSH into your server and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Create a deploy user (don't run the app as root)
sudo adduser silkensway
sudo usermod -aG sudo silkensway

# Switch to deploy user
su - silkensway

# Set timezone
sudo timedatectl set-timezone Asia/Kolkata

# Enable automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 4. Install Dependencies

```bash
# Python 3.11+
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Build tools (for Pillow, mysqlclient, bcrypt)
sudo apt install build-essential libffi-dev libjpeg-dev zlib1g-dev \
    libmysqlclient-dev pkg-config -y

# Nginx
sudo apt install nginx -y

# MySQL 8.0
sudo apt install mysql-server -y

# Redis
sudo apt install redis-server -y

# Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y

# Git
sudo apt install git -y

# Supervisor (process manager)
sudo apt install supervisor -y
```

---

## 5. Clone & Configure the App

```bash
# Go to deploy directory
cd /home/silkensway
git clone https://github.com/YOUR_USERNAME/Silkensway_Clothing_final_flask.git app
cd app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Also install mysqlclient for MySQL (PyMySQL is already in requirements)
pip install gunicorn
```

---

## 6. Environment Variables (.env)

Create `/home/silkensway/app/.env` with **production values**:

```env
# ═══════════════════════════════════════════════════════
# FLASK
# ═══════════════════════════════════════════════════════
FLASK_APP=run.py
FLASK_ENV=production

# CRITICAL: Generate a strong random key. Run:
#   python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=<PASTE_64_CHAR_HEX_HERE>

# ═══════════════════════════════════════════════════════
# DATABASE (MySQL)
# ═══════════════════════════════════════════════════════
DATABASE_URL=mysql+pymysql://silkensway_user:<DB_PASSWORD>@localhost:3306/silkensway_db

# ═══════════════════════════════════════════════════════
# REDIS
# ═══════════════════════════════════════════════════════
REDIS_URL=redis://localhost:6379/0

# ═══════════════════════════════════════════════════════
# EMAIL (Gmail App Password or SMTP provider)
# ═══════════════════════════════════════════════════════
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-real-email@gmail.com
MAIL_PASSWORD=<GMAIL_APP_PASSWORD>
MAIL_DEFAULT_SENDER=noreply@silkensway.com

# ═══════════════════════════════════════════════════════
# RAZORPAY (Live Keys — NOT Test Keys)
# ═══════════════════════════════════════════════════════
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=<LIVE_SECRET>
RAZORPAY_WEBHOOK_SECRET=<WEBHOOK_SECRET>

# ═══════════════════════════════════════════════════════
# OAUTH (Google & Facebook)
# ═══════════════════════════════════════════════════════
GOOGLE_CLIENT_ID=<GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<GOOGLE_CLIENT_SECRET>
FACEBOOK_APP_ID=<FACEBOOK_APP_ID>
FACEBOOK_APP_SECRET=<FACEBOOK_APP_SECRET>

# ═══════════════════════════════════════════════════════
# FILE UPLOADS
# ═══════════════════════════════════════════════════════
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=5242880

# ═══════════════════════════════════════════════════════
# ADMIN (first-time seed only — change password after login)
# ═══════════════════════════════════════════════════════
ADMIN_EMAIL=admin@silkensway.com
ADMIN_PASSWORD=<STRONG_ADMIN_PASSWORD>
```

**Lock down the file:**

```bash
chmod 600 /home/silkensway/app/.env
```

---

## 7. Database Setup (MySQL)

```bash
# Secure MySQL installation
sudo mysql_secure_installation
# → Set root password, remove anonymous users, disallow remote root, remove test DB

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE silkensway_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'silkensway_user'@'localhost' IDENTIFIED BY '<STRONG_DB_PASSWORD>';
GRANT ALL PRIVILEGES ON silkensway_db.* TO 'silkensway_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

```bash
# Initialize tables and seed data
cd /home/silkensway/app
source venv/bin/activate
python seed_products.py
```

---

## 8. Redis Setup

```bash
# Redis should already be running after install. Verify:
sudo systemctl status redis

# Secure Redis (bind to localhost only — default on Ubuntu)
sudo nano /etc/redis/redis.conf
# Ensure these lines:
#   bind 127.0.0.1 ::1
#   requirepass <OPTIONAL_REDIS_PASSWORD>

sudo systemctl restart redis
```

If you set a Redis password, update `.env`:
```
REDIS_URL=redis://:<REDIS_PASSWORD>@localhost:6379/0
```

---

## 9. Run the Application with Gunicorn

**Test manually first:**

```bash
cd /home/silkensway/app
source venv/bin/activate
gunicorn -c gunicorn.conf.py run:app
# Visit http://YOUR_SERVER_IP:8000 — should show the site
# Press Ctrl+C to stop
```

**Create Supervisor config for auto-restart:**

```bash
sudo nano /etc/supervisor/conf.d/silkensway.conf
```

```ini
[program:silkensway]
directory=/home/silkensway/app
command=/home/silkensway/app/venv/bin/gunicorn -c gunicorn.conf.py run:app
user=silkensway
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/silkensway/error.log
stdout_logfile=/var/log/silkensway/access.log
environment=PATH="/home/silkensway/app/venv/bin"
```

```bash
sudo mkdir -p /var/log/silkensway
sudo chown silkensway:silkensway /var/log/silkensway
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start silkensway

# Check status
sudo supervisorctl status silkensway
```

---

## 10. Nginx Reverse Proxy + SSL

**Create Nginx config:**

```bash
sudo nano /etc/nginx/sites-available/silkensway
```

```nginx
server {
    listen 80;
    server_name silkensway.com www.silkensway.com;

    # Redirect HTTP → HTTPS (Certbot will add this automatically)
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name silkensway.com www.silkensway.com;

    # SSL certs (Certbot fills these in)
    # ssl_certificate     /etc/letsencrypt/live/silkensway.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/silkensway.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Max upload size (match Flask MAX_CONTENT_LENGTH)
    client_max_body_size 5M;

    # Static files — served directly by Nginx (fast)
    location /static/ {
        alias /home/silkensway/app/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/silkensway /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

**Get free SSL certificate (Let's Encrypt):**

```bash
sudo certbot --nginx -d silkensway.com -d www.silkensway.com
# Follow prompts — enter email, agree to terms
# Certbot auto-configures Nginx SSL

# Auto-renew (cron already added by certbot, verify):
sudo certbot renew --dry-run
```

---

## 11. Celery Worker (Background Tasks)

Only needed if you use async email sending or background tasks.

```bash
sudo nano /etc/supervisor/conf.d/silkensway-celery.conf
```

```ini
[program:silkensway-celery]
directory=/home/silkensway/app
command=/home/silkensway/app/venv/bin/celery -A run.celery worker --loglevel=info --concurrency=2
user=silkensway
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/silkensway/celery-error.log
stdout_logfile=/var/log/silkensway/celery.log
environment=PATH="/home/silkensway/app/venv/bin"
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start silkensway-celery
```

---

## 12. Firewall Configuration

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'    # ports 80 + 443
sudo ufw deny 3306              # MySQL — localhost only
sudo ufw deny 6379              # Redis — localhost only
sudo ufw deny 8000              # Gunicorn — only Nginx needs it
sudo ufw enable
sudo ufw status
```

**Expected output:**
```
To        Action  From
--        ------  ----
OpenSSH   ALLOW   Anywhere
Nginx Full ALLOW  Anywhere
3306      DENY    Anywhere
6379      DENY    Anywhere
8000      DENY    Anywhere
```

---

## 13. OAuth Setup (Google & Facebook)

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use existing)
3. Navigate to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth Client ID**
5. Application type: **Web application**
6. Authorized redirect URIs:
   ```
   https://silkensway.com/oauth/google/callback
   ```
7. Copy **Client ID** and **Client Secret** → paste into `.env`

### Facebook OAuth

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app (type: **Consumer**)
3. Add **Facebook Login** product
4. Settings → Valid OAuth Redirect URIs:
   ```
   https://silkensway.com/oauth/facebook/callback
   ```
5. Go to **Settings → Basic** — copy **App ID** and **App Secret** → paste into `.env`
6. **IMPORTANT:** Switch app from Development to **Live** mode before launch

---

## 14. Razorpay Production Keys

1. Log in to [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Complete **KYC verification** (PAN, bank account, business details)
3. Once approved, go to **Settings → API Keys**
4. Generate **Live** keys (not Test)
5. Update `.env`:
   ```
   RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxx
   RAZORPAY_KEY_SECRET=<LIVE_SECRET>
   ```
6. Set up **Webhook**:
   - URL: `https://silkensway.com/checkout/webhook`
   - Events: `payment.captured`, `payment.failed`
   - Copy webhook secret → `RAZORPAY_WEBHOOK_SECRET` in `.env`

---

## 15. Email Configuration

### Option A: Gmail App Password (small scale)

1. Enable 2FA on your Gmail account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Use in `.env`:
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=<16_CHAR_APP_PASSWORD>
   ```
5. **Limit:** ~500 emails/day

### Option B: Transactional Email Service (recommended for production)

Use services like **Brevo (Sendinblue)**, **Mailgun**, **Amazon SES**, or **Postmark**:

| Service     | Free Tier        | Setup             |
|-------------|------------------|-------------------|
| Brevo       | 300 emails/day   | SMTP or API       |
| Mailgun     | 100 emails/day*  | SMTP              |
| Amazon SES  | 62,000/month**   | SMTP              |

*first 3 months, **if sending from EC2

Update `.env` with the provider's SMTP credentials.

---

## 16. File Uploads & Permissions

```bash
# Ensure upload directory exists and has correct ownership
mkdir -p /home/silkensway/app/app/static/uploads
chown -R silkensway:silkensway /home/silkensway/app/app/static/uploads
chmod 755 /home/silkensway/app/app/static/uploads
```

For a production site with many images, consider moving uploads to **cloud storage** (AWS S3, Cloudflare R2) later.

---

## 17. Security Hardening Checklist

| # | Task | Status |
|---|------|--------|
| 1 | `SECRET_KEY` is a random 64-char hex (not the default) | ☐ |
| 2 | `DEBUG = False` in production (`FLASK_ENV=production`) | ☐ |
| 3 | `ADMIN_PASSWORD` is strong (16+ chars, mixed) | ☐ |
| 4 | `.env` file permissions are `600` (owner-only read) | ☐ |
| 5 | MySQL root has a strong password | ☐ |
| 6 | MySQL user has only the needed database privileges | ☐ |
| 7 | Redis is bound to `127.0.0.1` (not exposed) | ☐ |
| 8 | Firewall blocks ports 3306, 6379, 8000 from outside | ☐ |
| 9 | SSL certificate is active (HTTPS only) | ☐ |
| 10 | `SESSION_COOKIE_SECURE = True` (set by ProductionConfig) | ☐ |
| 11 | CSP, HSTS, X-Frame-Options headers are active | ☐ |
| 12 | SSH uses key-based auth (disable password auth) | ☐ |
| 13 | Fail2ban installed for SSH brute-force protection | ☐ |
| 14 | No test/debug routes exposed | ☐ |
| 15 | Razorpay webhook secret is set | ☐ |

**SSH key-based auth (highly recommended):**

```bash
# On your LOCAL machine:
ssh-keygen -t ed25519 -C "your-email@example.com"
ssh-copy-id silkensway@YOUR_SERVER_IP

# On the server, disable password login:
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

**Install Fail2ban:**

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 18. Backup Strategy

### Database Backup (daily cron)

```bash
sudo nano /home/silkensway/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/silkensway/backups"
DATE=$(date +%Y-%m-%d_%H%M)
mkdir -p $BACKUP_DIR

# MySQL dump
mysqldump -u silkensway_user -p'<DB_PASSWORD>' silkensway_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Upload directory
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" /home/silkensway/app/app/static/uploads

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod 700 /home/silkensway/backup.sh

# Run daily at 2 AM
crontab -e
# Add:
0 2 * * * /home/silkensway/backup.sh >> /var/log/silkensway/backup.log 2>&1
```

**Offsite backups:** Copy backups to an external location (S3, Google Drive via rclone, another server) weekly.

---

## 19. Monitoring & Logging

### Log Rotation

```bash
sudo nano /etc/logrotate.d/silkensway
```

```
/var/log/silkensway/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 silkensway silkensway
}
```

### Basic Uptime Monitoring (free)

- [UptimeRobot](https://uptimerobot.com/) — free up to 50 monitors
- [Better Stack](https://betterstack.com/) — free tier
- Add HTTPS check for `https://silkensway.com` with 5-minute interval
- Set up email/SMS alerts for downtime

### Server Monitoring

```bash
# Quick resource check
htop          # CPU/RAM usage
df -h         # Disk usage
free -h       # Memory

# View app logs
tail -f /var/log/silkensway/access.log
tail -f /var/log/silkensway/error.log

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 20. Final Go-Live Checks

Run through this list **after** everything is set up:

| # | Check | How to Verify | ☐ |
|---|-------|---------------|---|
| 1 | Site loads over HTTPS | `https://silkensway.com` | ☐ |
| 2 | HTTP redirects to HTTPS | `http://silkensway.com` → `https://` | ☐ |
| 3 | www redirects properly | `www.silkensway.com` → `silkensway.com` | ☐ |
| 4 | Homepage loads products | Browse homepage | ☐ |
| 5 | Product images display | Check shop listing | ☐ |
| 6 | Registration works | Create a test account | ☐ |
| 7 | Login/logout works | Test login flow | ☐ |
| 8 | Google OAuth works | Click "Continue with Google" | ☐ |
| 9 | Facebook OAuth works | Click "Continue with Facebook" | ☐ |
| 10 | Add to cart works | Add a product, check cart | ☐ |
| 11 | Checkout + payment works | Complete a test order with Razorpay | ☐ |
| 12 | Order confirmation email arrives | Check inbox after order | ☐ |
| 13 | Admin panel accessible | `https://silkensway.com/admin` | ☐ |
| 14 | Age filter works in shop | Filter by age group | ☐ |
| 15 | Gender filter works in shop | Filter by gender | ☐ |
| 16 | Password reset email works | Test forgot password flow | ☐ |
| 17 | SSL certificate grade | [SSL Labs Test](https://www.ssllabs.com/ssltest/) — aim for A+ | ☐ |
| 18 | Security headers OK | [SecurityHeaders.com](https://securityheaders.com/) | ☐ |
| 19 | Error pages work | Visit `/nonexistent-page` → 404 page | ☐ |
| 20 | Backups are running | Check `/home/silkensway/backups/` | ☐ |

---

## 21. Quick Reference Commands

```bash
# ─── App Management ────────────────────────
sudo supervisorctl status                    # Check all processes
sudo supervisorctl restart silkensway        # Restart app
sudo supervisorctl restart silkensway-celery # Restart celery

# ─── Deploy Updates ────────────────────────
cd /home/silkensway/app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt              # If dependencies changed
sudo supervisorctl restart silkensway
sudo supervisorctl restart silkensway-celery

# ─── Nginx ─────────────────────────────────
sudo nginx -t                                # Test config
sudo systemctl restart nginx                 # Restart

# ─── SSL ───────────────────────────────────
sudo certbot renew --dry-run                 # Test renewal
sudo certbot renew                           # Force renew

# ─── Logs ──────────────────────────────────
tail -f /var/log/silkensway/error.log        # App errors
tail -f /var/log/silkensway/access.log       # App access
tail -f /var/log/nginx/error.log             # Nginx errors

# ─── Database ──────────────────────────────
mysql -u silkensway_user -p silkensway_db    # Connect to DB
/home/silkensway/backup.sh                   # Manual backup

# ─── Generate Secret Key ──────────────────
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Architecture Diagram

```
    Internet
       │
       ▼
  ┌─────────┐
  │  Domain  │  silkensway.com (DNS A record → Server IP)
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │  Nginx   │  :80 (→ redirect) / :443 (SSL termination)
  │          │  Serves /static/ directly
  └────┬─────┘
       │ proxy_pass
       ▼
  ┌───────────┐
  │ Gunicorn  │  127.0.0.1:8000  (workers × 2 + 1)
  │  (Flask)  │  Silkensway application
  └──┬────┬───┘
     │    │
     ▼    ▼
  ┌─────┐ ┌───────┐
  │MySQL│ │ Redis  │  localhost:3306 / localhost:6379
  └─────┘ └───┬───┘
              │
              ▼
         ┌────────┐
         │ Celery │  Background tasks (emails, etc.)
         └────────┘
```

---

**You're ready to go live. Work through each section in order, check items off, and your Silkensway store will be production-ready!**
