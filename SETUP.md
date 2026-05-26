# Setup Guide — indistylex Clothing (Flask)

Follow these steps after cloning the repository to get the app running locally.

---

## Prerequisites

- **Python 3.10+** installed
- **Git** installed
- (Optional) **Redis** — needed only for caching/Celery in production; dev mode uses SimpleCache

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/indistylex-jpg/Silkensway_Clothing_final_flask.git
cd Silkensway_Clothing_final_flask
```

---

## Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Create Environment File (Optional)

Create a `.env` file in the project root for custom configuration:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Mail (optional)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Razorpay (optional, for payments)
RAZORPAY_KEY_ID=your-key-id
RAZORPAY_KEY_SECRET=your-key-secret

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

> The app runs fine without a `.env` file — it uses built-in defaults for development.

---

## Step 5 — Initialize the Database

```bash
python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

This creates the SQLite database file (`instance/Indistylex_dev.db`) with all required tables.

---

## Step 6 — Seed Sample Data

```bash
python seed_products.py
```

This populates the database with sample categories and 30 products.

---

## Step 7 — Run the Application

```bash
python run.py
```

The app will be available at: **http://127.0.0.1:5000**

---

## Admin Panel

- **URL:** http://127.0.0.1:5000/admin
- **Login page:** http://127.0.0.1:5000/auth/login

### Default Admin Credentials

| Field    | Value                  |
|----------|------------------------|
| Email    | `admin@indistylex.in`  |
| Password | `change-this-password` |

> The admin user is auto-created on first run using `ADMIN_EMAIL` and `ADMIN_PASSWORD` from your `.env` file (or the defaults above). You can change these by setting the environment variables before starting the app.

---

## Quick Reference

| Action | Command |
|--------|---------|
| Activate venv (Windows PS) | `.\venv\Scripts\Activate.ps1` |
| Install deps | `pip install -r requirements.txt` |
| Create DB tables | `python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"` |
| Seed products | `python seed_products.py` |
| Run server | `python run.py` |
| Run tests | `pytest` |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `no such table: categories` | You skipped Step 5. Run the database initialization command. |
| `ModuleNotFoundError` | You skipped Step 3. Run `pip install -r requirements.txt`. |
| Rate limiter warning | Safe to ignore in development. Install Redis for production. |
