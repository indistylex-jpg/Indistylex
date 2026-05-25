# Indistylex â€” Production Deployment Guide

> Step-by-step guide for deploying the application to a fresh server or updating an existing deployment.

---

## Prerequisites

| Requirement       | Minimum            | Current Setup               |
|-------------------|--------------------|------------------------------|
| **OS**            | Ubuntu 22.04+ LTS  | Ubuntu 24.04 LTS             |
| **Python**        | 3.11+              | 3.12                         |
| **RAM**           | 2 GB               | 8 GB                         |
| **Disk**          | 20 GB SSD          | Available                    |
| **Domain**        | Optional           | Using IP: 78.46.145.88       |

---

## Quick Deploy (Existing Server)

```bash
ssh root@78.46.145.88
cd /var/www/indistylex
git fetch origin kids && git reset --hard origin/kids
chown -R www-data:www-data /var/www/indistylex
systemctl restart indistylex
systemctl status indistylex          # Verify running
```

---

## Fresh Server Setup

### 1. Install System Dependencies

```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx git sqlite3 redis-server
```

### 2. Clone Repository

```bash
mkdir -p /var/www
cd /var/www
git clone -b kids https://github.com/shivam74826/indistylex_Clothing_final_flask.git indistylex
cd indistylex
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create .env File

```bash
cat > /var/www/indistylex/.env << 'EOF'
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=sqlite:////var/www/indistylex/instance/indistylex.db

# Email (configure for order confirmations)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Payment (configure for online payments)
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=your_secret

# Admin
ADMIN_EMAIL=admin@indistylex.in
ADMIN_PASSWORD=IndistyAdmin2026!

# Misc
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=RedisCache
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=5242880
EOF

chmod 600 /var/www/indistylex/.env
```

### 5. Initialize Database

```bash
cd /var/www/indistylex
source venv/bin/activate
mkdir -p instance

# Create tables (happens automatically on first run)
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.extensions import db; db.create_all(); print('Tables created')"

# Seed products
python seed_products.py
```

### 6. Create Systemd Service

```bash
cat > /etc/systemd/system/indistylex.service << 'EOF'
[Unit]
Description=Indistylex - Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/indistylex
Environment=PATH=/var/www/indistylex/venv/bin
EnvironmentFile=/var/www/indistylex/.env
ExecStart=/var/www/indistylex/venv/bin/gunicorn -c gunicorn.conf.py run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable indistylex
systemctl start indistylex
```

### 7. Configure Nginx

```bash
cat > /etc/nginx/sites-available/indistylex << 'EOF'
server {
    listen 80;
    server_name _;   # Replace _ with your domain

    client_max_body_size 5M;

    location /static/ {
        alias /var/www/indistylex/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/indistylex /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

### 8. Set Permissions

```bash
chown -R www-data:www-data /var/www/indistylex
chmod -R 755 /var/www/indistylex
chmod 600 /var/www/indistylex/.env
```

---

## Adding HTTPS (SSL)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

After SSL is enabled, update `.env`:
```
SESSION_COOKIE_SECURE=True
PREFERRED_URL_SCHEME=https
```

---

## Database Management

### Backup
```bash
cp /var/www/indistylex/instance/indistylex.db /var/www/indistylex/instance/indistylex_backup_$(date +%Y%m%d).db
```

### Add New Column (Example)
```bash
cd /var/www/indistylex
venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('instance/indistylex.db')
conn.execute('ALTER TABLE table_name ADD COLUMN column_name TYPE DEFAULT value')
conn.commit()
conn.close()
print('Done')
"
```

### Reseed Products (Caution: only works if no products exist)
```bash
cd /var/www/indistylex
source venv/bin/activate
python seed_products.py
```

---

## Monitoring & Logs

```bash
# Service status
systemctl status indistylex

# Live logs
journalctl -u indistylex -f

# Last 50 log lines
journalctl -u indistylex --no-pager -n 50

# Nginx access log
tail -f /var/log/nginx/access.log

# Nginx error log
tail -f /var/log/nginx/error.log
```

---

## Common Operations

### Restart After Code Change
```bash
systemctl restart indistylex
```

### Check if Port 8000 is in Use
```bash
ss -tlnp | grep 8000
```

### Redis Status
```bash
systemctl status redis-server
redis-cli ping   # Should return PONG
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **502 Bad Gateway** | `systemctl restart indistylex` â€” Gunicorn crashed |
| **CSRF token missing** | Check `SESSION_COOKIE_SECURE` matches HTTP/HTTPS |
| **Static files not loading** | `chown -R www-data:www-data /var/www/indistylex` |
| **Permission denied** | Fix ownership: `chown -R www-data:www-data /var/www/indistylex` |
| **DB locked** | Restart service; only one writer at a time with SQLite |
| **Out of memory** | Reduce Gunicorn workers in `gunicorn.conf.py` |

---

## Feature Checklist

| Feature                        | Status |
|-------------------------------|--------|
| User registration & login      | Done   |
| Product catalog (4 categories) | Done   |
| Shopping cart                   | Done   |
| Checkout (COD + Online)        | Done   |
| Order tracking                 | Done   |
| Wishlist                       | Done   |
| Admin dashboard                | Done   |
| Admin order management          | Done   |
| Admin product CRUD              | Done   |
| Contact form                   | Done   |
| Email notifications            | Needs SMTP config |
| Online payment (Razorpay)      | Needs API keys |
| Google/Facebook OAuth           | Needs OAuth keys |
| HTTPS / SSL                    | Needs domain + certbot |
| Redis caching                  | Needs `systemctl start redis-server` |
