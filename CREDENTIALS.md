# Silkensway Kids — Credentials & Access Reference

> **CONFIDENTIAL** — Do NOT commit this file to git. Keep it safe.

---

## 1. Server Access (Hetzner VPS)

| Field           | Value                          |
|-----------------|--------------------------------|
| **IP Address**  | `78.46.145.88`                 |
| **OS**          | Ubuntu 24.04 LTS               |
| **SSH User**    | `root`                         |
| **SSH Password**| `BlueApple@3$6#9@Hetzner`     |
| **Deploy Path** | `/var/www/silkensway`          |
| **Service**     | `silkensway` (systemd)         |

### SSH Quick Access
```bash
ssh root@78.46.145.88
```

---

## 2. Admin Panel

| Field          | Value                         |
|----------------|-------------------------------|
| **URL**        | http://78.46.145.88/admin/    |
| **Email**      | `admin@silkensway.com`        |
| **Password**   | `SilkAdmin2026!`              |

> Login at http://78.46.145.88/auth/login with admin credentials, then navigate to /admin/

---

## 3. GitHub Repository

| Field          | Value                                                        |
|----------------|--------------------------------------------------------------|
| **Repo**       | `shivam74826/Silkensway_Clothing_final_flask`               |
| **Branch**     | `kids`                                                       |
| **URL**        | https://github.com/shivam74826/Silkensway_Clothing_final_flask |

---

## 4. Server Environment Variables (.env)

Location: `/var/www/silkensway/.env`

```env
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=33ab6cf90e31710f7ad9b2807b3b650152d3073c0745463f9ba8368397d33946
DATABASE_URL=sqlite:////var/www/silkensway/instance/silkensway.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=RedisCache
ADMIN_EMAIL=admin@silkensway.com
ADMIN_PASSWORD=SilkAdmin2026!
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=5242880
```

### Missing / To Configure
| Variable                | Status     | Notes                                  |
|-------------------------|------------|----------------------------------------|
| `MAIL_USERNAME`         | NOT SET    | Gmail address for sending order emails |
| `MAIL_PASSWORD`         | NOT SET    | Gmail App Password (16-char)           |
| `RAZORPAY_KEY_ID`       | NOT SET    | Live key from Razorpay dashboard       |
| `RAZORPAY_KEY_SECRET`   | NOT SET    | Secret from Razorpay dashboard         |
| `GOOGLE_CLIENT_ID`      | NOT SET    | For Google OAuth login                 |
| `GOOGLE_CLIENT_SECRET`  | NOT SET    | For Google OAuth login                 |
| `SESSION_COOKIE_SECURE` | NOT SET    | Set to `True` after enabling HTTPS     |

---

## 5. Application Stack

| Component    | Details                                      |
|-------------|----------------------------------------------|
| **Python**  | 3.12                                          |
| **Framework** | Flask 3.1.0                                 |
| **Server**  | Gunicorn 23.0 (gthread, 9 workers)            |
| **Proxy**   | Nginx (port 80 → 127.0.0.1:8000)             |
| **Database**| SQLite (`instance/silkensway.db`)             |
| **Cache**   | Redis (localhost:6379) — not currently running |

---

## 6. Deployment Workflow

```bash
# 1. Push code to GitHub
git add -A && git commit -m "description" && git push origin kids

# 2. SSH to server and pull
ssh root@78.46.145.88
cd /var/www/silkensway
git fetch origin kids && git reset --hard origin/kids
chown -R www-data:www-data /var/www/silkensway
systemctl restart silkensway

# 3. Verify
systemctl status silkensway
curl -s -o /dev/null -w "%{http_code}" http://78.46.145.88/
```

---

## 7. Important File Locations (Server)

| File                          | Purpose                          |
|-------------------------------|----------------------------------|
| `/var/www/silkensway/.env`    | Environment variables            |
| `/var/www/silkensway/instance/silkensway.db` | SQLite database     |
| `/etc/systemd/system/silkensway.service` | Systemd service file  |
| `/etc/nginx/sites-enabled/silkensway` | Nginx config           |
| `/var/www/silkensway/gunicorn.conf.py` | Gunicorn config        |
