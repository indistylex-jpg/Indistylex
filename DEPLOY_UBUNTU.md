# Indistylex — Ubuntu Server Deployment Guide

**Server:** Ubuntu 24.04 LTS  
**Stack:** Python 3 + MySQL 8.0 + Nginx + Gunicorn + Redis

---

## 1. Create MySQL Database & User

```bash
sudo mysql
```

```sql
CREATE DATABASE indistylex CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'indistylex'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';
GRANT ALL PRIVILEGES ON indistylex.* TO 'indistylex'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 2. Install System Dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv libmysqlclient-dev pkg-config nginx redis-server -y
```

---

## 3. Upload Project

```bash
# Option A: Git clone
cd /home/$USER
git clone <your-repo-url> Silkensway_Clothing_final_flask
cd Silkensway_Clothing_final_flask

# Option B: SCP from local machine
# scp -r . user@server-ip:/home/user/Silkensway_Clothing_final_flask/
```

---

## 4. Python Virtual Environment

```bash
cd /home/$USER/Silkensway_Clothing_final_flask
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

---

## 5. Create `.env` File

```bash
nano .env
```

```env
FLASK_ENV=production
SECRET_KEY=PASTE_64_CHAR_RANDOM_STRING_HERE
DATABASE_URL=mysql+pymysql://indistylex:YourStrongPassword123!@localhost:3306/indistylex
REDIS_URL=redis://localhost:6379/0

# Mail (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Razorpay
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=

# Admin
ADMIN_EMAIL=admin@indistylex.in
ADMIN_PASSWORD=YourAdminPassword!

# Security
SESSION_COOKIE_SECURE=True
PREFERRED_URL_SCHEME=https
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Protect the file:

```bash
chmod 600 .env
```

---

## 6. Initialize Database & Seed Data

```bash
source venv/bin/activate
export FLASK_ENV=production

# Create all tables via migrations
flask db upgrade

# Seed products (optional)
python seed_products.py
```

If migrations folder doesn't exist yet:

```bash
flask db init
flask db migrate -m "initial"
flask db upgrade
```

---

## 7. Test Gunicorn Manually

```bash
source venv/bin/activate
gunicorn -c gunicorn.conf.py run:app
```

Visit `http://your-server-ip:8000` — if it loads, proceed to systemd.  
Press `Ctrl+C` to stop.

---

## 8. Create Systemd Service

```bash
sudo nano /etc/systemd/system/indistylex.service
```

```ini
[Unit]
Description=Indistylex Flask Application
After=network.target mysql.service redis-server.service

[Service]
User=YOUR_USERNAME
Group=www-data
WorkingDirectory=/home/YOUR_USERNAME/Silkensway_Clothing_final_flask
Environment="PATH=/home/YOUR_USERNAME/Silkensway_Clothing_final_flask/venv/bin"
EnvironmentFile=/home/YOUR_USERNAME/Silkensway_Clothing_final_flask/.env
ExecStart=/home/YOUR_USERNAME/Silkensway_Clothing_final_flask/venv/bin/gunicorn -c gunicorn.conf.py run:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

> **Replace `YOUR_USERNAME`** with your actual Linux username (run `whoami` to check).

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable indistylex
sudo systemctl start indistylex
sudo systemctl status indistylex
```

---

## 9. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/indistylex
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 5M;

    # Serve static files directly
    location /static/ {
        alias /home/YOUR_USERNAME/Silkensway_Clothing_final_flask/app/static/;
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

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/indistylex /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

## 10. Firewall (UFW)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## 11. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Auto-renewal is enabled by default. Test with:

```bash
sudo certbot renew --dry-run
```

---

## 12. Set Upload Directory Permissions

```bash
sudo chown -R YOUR_USERNAME:www-data /home/YOUR_USERNAME/Silkensway_Clothing_final_flask/app/static/uploads
chmod 775 /home/YOUR_USERNAME/Silkensway_Clothing_final_flask/app/static/uploads
```

---

## 13. Start Redis

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
redis-cli ping
# Should return: PONG
```

---

## 14. (Optional) Celery Worker for Background Tasks

```bash
sudo nano /etc/systemd/system/indistylex-celery.service
```

```ini
[Unit]
Description=Indistylex Celery Worker
After=network.target redis-server.service

[Service]
User=YOUR_USERNAME
Group=www-data
WorkingDirectory=/home/YOUR_USERNAME/Silkensway_Clothing_final_flask
Environment="PATH=/home/YOUR_USERNAME/Silkensway_Clothing_final_flask/venv/bin"
EnvironmentFile=/home/YOUR_USERNAME/Silkensway_Clothing_final_flask/.env
ExecStart=/home/YOUR_USERNAME/Silkensway_Clothing_final_flask/venv/bin/celery -A run.celery worker --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable indistylex-celery
sudo systemctl start indistylex-celery
```

---

## Troubleshooting Commands

| Task | Command |
|------|---------|
| Check app status | `sudo systemctl status indistylex` |
| View app logs | `sudo journalctl -u indistylex -f` |
| Restart app | `sudo systemctl restart indistylex` |
| Restart Nginx | `sudo systemctl restart nginx` |
| Nginx error log | `sudo tail -f /var/log/nginx/error.log` |
| MySQL shell | `mysql -u indistylex -p indistylex` |
| Test Nginx config | `sudo nginx -t` |
| Check port 8000 | `sudo ss -tlnp | grep 8000` |
| Redis check | `redis-cli ping` |

---

## Updating the Application

```bash
cd /home/YOUR_USERNAME/Silkensway_Clothing_final_flask
source venv/bin/activate
git pull origin main

# If dependencies changed:
pip install -r requirements.txt

# If models changed:
flask db upgrade

# Restart
sudo systemctl restart indistylex
```

---

## Directory Structure on Server

```
/home/YOUR_USERNAME/Silkensway_Clothing_final_flask/
├── .env                  ← secrets (chmod 600)
├── venv/                 ← Python virtual environment
├── app/
│   ├── static/           ← served directly by Nginx
│   └── ...
├── gunicorn.conf.py      ← Gunicorn config (binds to 0.0.0.0:8000)
├── run.py                ← WSGI entry point
└── requirements.txt
```
