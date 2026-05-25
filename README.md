# Indistylex — E-Commerce Platform

> A full-featured, production-ready e-commerce web application built with Flask.

**Trade Name:** Indistylex  
**Proprietor:** Satyam Pandey  
**GSTIN:** 09GVUPP6447P1Z3  
**Domain:** indistylex.in  

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Setup & Installation](#setup--installation)
5. [Configuration](#configuration)
6. [Features](#features)
7. [API Routes](#api-routes)
8. [Database Models](#database-models)
9. [Deployment](#deployment)
10. [Testing](#testing)

---

## Overview

Indistylex is a modern, responsive e-commerce platform for selling clothing online. It features:

- Full product catalog with categories, variants (size/color), and image galleries
- User authentication (email/password + Google OAuth)
- Shopping cart with coupon system
- Razorpay payment integration (UPI, cards, net banking)
- Order management with status tracking
- Admin dashboard for products, orders, customers, and coupons
- AI chatbot for customer support
- Wishlist, reviews & ratings
- Email notifications (order confirmation, shipping updates, password reset)
- SEO-optimized pages with JSON-LD structured data
- Mobile-first responsive design

---

## Tech Stack

| Layer           | Technology                                              |
|-----------------|--------------------------------------------------------|
| **Backend**     | Python 3.10+, Flask 3.x                               |
| **Database**    | SQLite (dev/prod) / MySQL (Docker)                     |
| **ORM**        | SQLAlchemy + Flask-Migrate                             |
| **Auth**       | Flask-Login + Flask-Bcrypt + Authlib (Google OAuth)    |
| **Payments**   | Razorpay (UPI, Cards, Net Banking)                    |
| **Email**      | Flask-Mail (SMTP)                                     |
| **Caching**    | Redis / SimpleCache                                   |
| **Rate Limit** | Flask-Limiter (Redis backend)                         |
| **CSRF**       | Flask-WTF                                             |
| **Server**     | Gunicorn + Nginx                                      |
| **Frontend**   | Bootstrap 5, Bootstrap Icons, Jinja2 templates         |
| **Fonts**      | Poppins (headings), Inter (body)                      |

---

## Project Structure

```
Indistylex/
├── run.py                  # Application entry point
├── gunicorn.conf.py        # Gunicorn production config
├── seed_products.py        # Database seeder (sample products)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container build
├── docker-compose.yml      # Multi-service Docker setup
├── .env.example            # Environment template
│
├── app/
│   ├── __init__.py         # App factory (create_app)
│   ├── config.py           # Configuration classes (Dev/Prod/Test)
│   ├── extensions.py       # Flask extensions initialization
│   │
│   ├── models/             # SQLAlchemy models
│   │   ├── user.py         # User, Address
│   │   ├── product.py      # Product, Category, Variant, Image
│   │   ├── cart.py         # Cart, CartItem
│   │   ├── order.py        # Order, OrderItem
│   │   ├── coupon.py       # Coupon
│   │   ├── review.py       # Review
│   │   └── wishlist.py     # Wishlist
│   │
│   ├── routes/             # Blueprint route handlers
│   │   ├── main.py         # Home, about, contact, FAQ, etc.
│   │   ├── auth.py         # Login, register, password reset, OAuth
│   │   ├── shop.py         # Product listing, category, search
│   │   ├── product.py      # Product detail, reviews
│   │   ├── cart.py         # Cart CRUD operations
│   │   ├── checkout.py     # Checkout flow
│   │   ├── order.py        # Order history, tracking
│   │   ├── user.py         # Profile, addresses, wishlist
│   │   ├── admin.py        # Admin dashboard & management
│   │   └── chatbot.py      # AI chatbot endpoint
│   │
│   ├── forms/              # WTForms form classes
│   │   ├── auth_forms.py   # Login, Register, ForgotPassword
│   │   ├── product_forms.py# Product/Category admin forms
│   │   ├── checkout_forms.py# Checkout form
│   │   └── user_forms.py   # Profile, Address forms
│   │
│   ├── services/           # Business logic services
│   │   ├── email_service.py    # Email sending
│   │   ├── image_service.py    # Image upload/resize
│   │   ├── inventory_service.py# Stock management
│   │   └── payment_service.py  # Razorpay integration
│   │
│   ├── utils/              # Utility functions
│   │   ├── decorators.py   # @admin_required, @confirmed_required
│   │   ├── helpers.py      # Slugify, pagination, formatters
│   │   └── validators.py   # Input validation
│   │
│   ├── static/             # CSS, JS, images, uploads
│   │   ├── css/            # style.css, admin.css, chatbot.css
│   │   ├── js/             # main.js, admin.js, chatbot.js, checkout.js
│   │   └── images/         # Logo, favicon, category images
│   │
│   └── templates/          # Jinja2 HTML templates (52 templates)
│       ├── base.html       # Master layout
│       ├── navbar.html     # Navigation
│       ├── footer.html     # Footer
│       ├── home/           # Homepage
│       ├── shop/           # Product listing & detail
│       ├── cart/           # Shopping cart
│       ├── checkout/       # Checkout & payment
│       ├── auth/           # Login, register, password reset
│       ├── user/           # User account pages
│       ├── admin/          # Admin dashboard
│       ├── pages/          # Static pages (about, FAQ, etc.)
│       ├── components/     # Reusable partials
│       ├── emails/         # Email templates
│       └── errors/         # 403, 404, 429, 500
│
├── tests/                  # Pytest test suite
│   ├── conftest.py         # Test fixtures & app factory
│   ├── test_models.py      # Model unit tests
│   ├── test_routes.py      # Route integration tests
│   ├── test_services.py    # Service unit tests
│   ├── test_utils.py       # Utility function tests
│   └── test_forms.py       # Form validation tests
│
└── instance/               # SQLite database (gitignored)
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- pip
- Redis (optional, for caching/rate limiting)

### Local Development

```bash
# Clone
git clone https://github.com/shivam74826/Silkensway_Clothing_final_flask.git
cd Silkensway_Clothing_final_flask

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env with your values

# Run development server
flask run
# or
python run.py
```

The app will be available at `http://127.0.0.1:5000`.

### Docker

```bash
docker-compose up --build
```

---

## Configuration

Configuration is managed via environment variables and `app/config.py`.

| Variable                 | Description                          | Default              |
|--------------------------|--------------------------------------|----------------------|
| `SECRET_KEY`             | Flask session secret                 | (required)           |
| `DATABASE_URL`           | SQLAlchemy database URI              | SQLite (instance/)   |
| `MAIL_SERVER`            | SMTP server                          | smtp.gmail.com       |
| `MAIL_PORT`              | SMTP port                            | 587                  |
| `MAIL_USERNAME`          | SMTP username                        | (required for email) |
| `MAIL_PASSWORD`          | SMTP password/app password           | (required for email) |
| `RAZORPAY_KEY_ID`        | Razorpay API key                     | (required for pay)   |
| `RAZORPAY_KEY_SECRET`    | Razorpay secret                      | (required for pay)   |
| `REDIS_URL`              | Redis connection URL                 | redis://localhost:6379|
| `GOOGLE_CLIENT_ID`       | Google OAuth client ID               | (optional)           |
| `GOOGLE_CLIENT_SECRET`   | Google OAuth secret                  | (optional)           |
| `ADMIN_EMAIL`            | Admin user email                     | admin@indistylex.in  |
| `ADMIN_PASSWORD`         | Admin user password                  | (set on first run)   |

---

## Features

### Customer-Facing
- **Product Browsing:** Category filtering, search, sort (price, newest, popular)
- **Product Detail:** Image gallery, size/color variants, reviews, related products
- **Shopping Cart:** Add/remove items, quantity update, coupon codes
- **Checkout:** Address management, Razorpay payment (UPI/Card/NetBanking)
- **User Account:** Profile, order history, addresses, wishlist, password change
- **AI Chatbot:** Order tracking, size help, return policy, product recommendations

### Admin Dashboard
- **Dashboard:** Revenue, orders, customers at a glance
- **Products:** Create/edit/delete products with variants and image uploads
- **Categories:** Manage product categories with images
- **Orders:** View, update status (pending → confirmed → shipped → delivered)
- **Customers:** View all registered users
- **Coupons:** Create percentage/fixed discount codes with limits
- **Reviews:** Moderate customer reviews

### Security
- CSRF protection on all forms
- Bcrypt password hashing
- Rate limiting on sensitive endpoints
- Session cookie security (httponly, secure in prod)
- Input validation and sanitization
- Admin role separation with `@admin_required` decorator

---

## API Routes

### Public
| Method | Route                    | Description              |
|--------|--------------------------|--------------------------|
| GET    | `/`                      | Homepage                 |
| GET    | `/shop`                  | Product listing          |
| GET    | `/shop/<slug>`           | Category listing         |
| GET    | `/product/<slug>`        | Product detail           |
| GET    | `/about`                 | About page               |
| GET    | `/contact`               | Contact page             |
| GET    | `/faq`                   | FAQ page                 |

### Auth
| Method | Route                    | Description              |
|--------|--------------------------|--------------------------|
| GET/POST | `/auth/login`          | Login                    |
| GET/POST | `/auth/register`       | Registration             |
| GET    | `/auth/logout`           | Logout                   |
| GET/POST | `/auth/forgot-password`| Password reset request   |
| GET/POST | `/auth/reset/<token>`  | Password reset           |
| GET    | `/auth/google`           | Google OAuth initiate     |
| GET    | `/auth/google/callback`  | Google OAuth callback     |

### Cart (Login Required)
| Method | Route                    | Description              |
|--------|--------------------------|--------------------------|
| GET    | `/cart`                  | View cart                |
| POST   | `/cart/add`              | Add item                 |
| POST   | `/cart/update/<id>`      | Update quantity          |
| POST   | `/cart/remove/<id>`      | Remove item              |
| POST   | `/cart/coupon`           | Apply coupon             |

### Checkout (Login Required)
| Method | Route                    | Description              |
|--------|--------------------------|--------------------------|
| GET/POST | `/checkout`            | Checkout page            |
| GET    | `/checkout/payment/<id>` | Payment page             |
| POST   | `/checkout/verify`       | Verify Razorpay payment  |
| GET    | `/checkout/success/<id>` | Order success            |

### Admin (`/admin/` — Admin Required)
| Method | Route                      | Description              |
|--------|----------------------------|--------------------------|
| GET    | `/admin/`                  | Dashboard                |
| GET    | `/admin/products`          | Product list             |
| GET/POST | `/admin/products/new`    | Create product           |
| GET/POST | `/admin/products/<id>/edit` | Edit product          |
| POST   | `/admin/products/<id>/delete` | Delete product        |
| GET    | `/admin/orders`            | Order list               |
| GET/POST | `/admin/orders/<id>`     | Order detail & status    |
| GET    | `/admin/customers`         | Customer list            |
| GET    | `/admin/categories`        | Category management      |
| GET    | `/admin/coupons`           | Coupon management        |
| GET    | `/admin/reviews`           | Review moderation        |

### Chatbot
| Method | Route                    | Description              |
|--------|--------------------------|--------------------------|
| POST   | `/chatbot/message`       | Send message, get reply  |

---

## Database Models

### User
- id, email, password_hash, first_name, last_name, phone
- is_admin, is_active, google_id
- orders (relationship), addresses (relationship)

### Product
- id, name, slug, description, short_description, price, compare_at_price
- brand, gender, is_active, is_featured
- category_id → Category
- variants (relationship: size, color, sku, stock)
- images (relationship), reviews (relationship)

### Order
- id, user_id, order_number, status, total, subtotal, discount
- shipping_address, payment_method, razorpay_order_id, razorpay_payment_id
- items (relationship: product, variant, quantity, price)

### Cart & CartItem
- Cart: user_id, items (relationship)
- CartItem: cart_id, variant_id, quantity

### Coupon
- code, discount_type (percentage/fixed), discount_value
- min_order_amount, max_uses, used_count, is_active, expires_at

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full server setup instructions.

### Quick Deploy (Existing Server)
```bash
ssh root@78.46.145.88
cd /var/www/indistylex
git fetch origin kids && git reset --hard origin/kids
chown -R www-data:www-data /var/www/indistylex
systemctl restart indistylex
```

### Production Stack
- **Server:** Ubuntu 24.04 LTS on Hetzner
- **App Server:** Gunicorn (4 workers, port 8000)
- **Reverse Proxy:** Nginx (static file serving, SSL termination)
- **Database:** SQLite (single-server deployment)
- **Cache:** Redis

---

## Testing

```bash
# Install test dependencies
pip install pytest

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_routes.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

**Test Suite:** 165+ tests covering models, routes, services, utilities, and forms.

---

## License

Proprietary — Indistylex (Prop: Satyam Pandey). All rights reserved.

---

## Contact

- **Email:** support@indistylex.in
- **Phone:** +91 63941 42176
- **Address:** MIG 79, Dhoomanganj, Preetam Nagar, Prayagraj, UP 211011
# Silkensway_Clothing_final_flask
# Silkensway_Clothing_final_flask
