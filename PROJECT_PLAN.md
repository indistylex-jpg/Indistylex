# Indistylex â€” Project Plan Document
> **Version:** 1.1 | **Date:** March 20, 2026 | **Stack:** Python Flask | **Status:** APPROVED â€” Building

---

## 1. Project Overview

**Indistylex** is a production-ready e-commerce web application for selling clothing online. Built with Python Flask, it will feature a modern, responsive storefront, secure payment processing, inventory management, and an admin dashboard.

---

## 2. Tech Stack

| Layer              | Technology                                      |
|--------------------|--------------------------------------------------|
| **Backend**        | Python 3.11+, Flask 3.x                          |
| **Database**       | MySQL 8.x (production & development)              |
| **ORM**            | SQLAlchemy + Flask-Migrate (Alembic)              |
| **Authentication** | Flask-Login + Flask-Bcrypt                        |
| **Forms**          | Flask-WTF (CSRF protection built-in)              |
| **Frontend**       | Jinja2 templates, Bootstrap 5, Custom CSS         |
| **Payments**       | Razorpay (INR, UPI, Cards, Net Banking)            |
| **Email**          | Flask-Mail (SMTP for order confirmations, etc.)   |
| **File Storage**   | Local uploads (dev) / AWS S3 or Cloudinary (prod) |
| **Caching**        | Flask-Caching with Redis                          |
| **Task Queue**     | Celery + Redis (for emails, reports)              |
| **Deployment**     | Gunicorn + Nginx on a VPS / Docker containers     |
| **Testing**        | Pytest + Coverage                                 |

---

## 3. Project Structure

```
Indistylex_Clothing_final_flask/
â”‚
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ __init__.py              # App factory
â”‚   â”œâ”€â”€ config.py                # Configuration (dev, prod, test)
â”‚   â”œâ”€â”€ extensions.py            # Initialize extensions (db, mail, login, etc.)
â”‚   â”‚
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ user.py              # User & Address models
â”‚   â”‚   â”œâ”€â”€ product.py           # Product, Category, ProductImage models
â”‚   â”‚   â”œâ”€â”€ cart.py              # Cart & CartItem models
â”‚   â”‚   â”œâ”€â”€ order.py             # Order, OrderItem, Payment models
â”‚   â”‚   â”œâ”€â”€ review.py            # Product reviews & ratings
â”‚   â”‚   â””â”€â”€ coupon.py            # Discount coupons
â”‚   â”‚
â”‚   â”œâ”€â”€ routes/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ main.py              # Homepage, About, Contact
â”‚   â”‚   â”œâ”€â”€ auth.py              # Login, Register, Password reset
â”‚   â”‚   â”œâ”€â”€ shop.py              # Product listing, filtering, search
â”‚   â”‚   â”œâ”€â”€ product.py           # Product detail page
â”‚   â”‚   â”œâ”€â”€ cart.py              # Cart operations
â”‚   â”‚   â”œâ”€â”€ checkout.py          # Checkout & payment
â”‚   â”‚   â”œâ”€â”€ order.py             # Order history, tracking
â”‚   â”‚   â”œâ”€â”€ user.py              # Profile, addresses, wishlist
â”‚   â”‚   â””â”€â”€ admin.py             # Admin dashboard routes
â”‚   â”‚
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ payment_service.py   # Stripe/Razorpay integration
â”‚   â”‚   â”œâ”€â”€ email_service.py     # Transactional emails
â”‚   â”‚   â”œâ”€â”€ inventory_service.py # Stock management
â”‚   â”‚   â””â”€â”€ image_service.py     # Image upload & processing
â”‚   â”‚
â”‚   â”œâ”€â”€ templates/
â”‚   â”‚   â”œâ”€â”€ base.html            # Master layout
â”‚   â”‚   â”œâ”€â”€ navbar.html          # Navigation partial
â”‚   â”‚   â”œâ”€â”€ footer.html          # Footer partial
â”‚   â”‚   â”œâ”€â”€ home/
â”‚   â”‚   â”‚   â””â”€â”€ index.html       # Homepage
â”‚   â”‚   â”œâ”€â”€ auth/
â”‚   â”‚   â”‚   â”œâ”€â”€ login.html
â”‚   â”‚   â”‚   â”œâ”€â”€ register.html
â”‚   â”‚   â”‚   â””â”€â”€ reset_password.html
â”‚   â”‚   â”œâ”€â”€ shop/
â”‚   â”‚   â”‚   â”œâ”€â”€ listing.html     # Product grid with filters
â”‚   â”‚   â”‚   â””â”€â”€ detail.html      # Single product page
â”‚   â”‚   â”œâ”€â”€ cart/
â”‚   â”‚   â”‚   â””â”€â”€ cart.html
â”‚   â”‚   â”œâ”€â”€ checkout/
â”‚   â”‚   â”‚   â”œâ”€â”€ checkout.html
â”‚   â”‚   â”‚   â””â”€â”€ success.html
â”‚   â”‚   â”œâ”€â”€ user/
â”‚   â”‚   â”‚   â”œâ”€â”€ profile.html
â”‚   â”‚   â”‚   â”œâ”€â”€ orders.html
â”‚   â”‚   â”‚   â””â”€â”€ wishlist.html
â”‚   â”‚   â”œâ”€â”€ admin/
â”‚   â”‚   â”‚   â”œâ”€â”€ dashboard.html
â”‚   â”‚   â”‚   â”œâ”€â”€ products.html
â”‚   â”‚   â”‚   â”œâ”€â”€ orders.html
â”‚   â”‚   â”‚   â””â”€â”€ users.html
â”‚   â”‚   â””â”€â”€ emails/              # Email templates
â”‚   â”‚       â”œâ”€â”€ welcome.html
â”‚   â”‚       â”œâ”€â”€ order_confirmation.html
â”‚   â”‚       â””â”€â”€ password_reset.html
â”‚   â”‚
â”‚   â”œâ”€â”€ static/
â”‚   â”‚   â”œâ”€â”€ css/
â”‚   â”‚   â”‚   â”œâ”€â”€ style.css        # Custom styles
â”‚   â”‚   â”‚   â””â”€â”€ admin.css        # Admin panel styles
â”‚   â”‚   â”œâ”€â”€ js/
â”‚   â”‚   â”‚   â”œâ”€â”€ main.js          # Core JS (cart, search, etc.)
â”‚   â”‚   â”‚   â”œâ”€â”€ checkout.js      # Payment form handling
â”‚   â”‚   â”‚   â””â”€â”€ admin.js         # Admin panel JS
â”‚   â”‚   â”œâ”€â”€ images/
â”‚   â”‚   â”‚   â”œâ”€â”€ logo.png
â”‚   â”‚   â”‚   â”œâ”€â”€ hero-banner.jpg
â”‚   â”‚   â”‚   â””â”€â”€ placeholders/
â”‚   â”‚   â””â”€â”€ uploads/             # User-uploaded product images (dev)
â”‚   â”‚
â”‚   â”œâ”€â”€ forms/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ auth_forms.py        # Login, Register forms
â”‚   â”‚   â”œâ”€â”€ product_forms.py     # Add/Edit product forms
â”‚   â”‚   â”œâ”€â”€ checkout_forms.py    # Address, payment forms
â”‚   â”‚   â””â”€â”€ user_forms.py        # Profile update forms
â”‚   â”‚
â”‚   â””â”€â”€ utils/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â”œâ”€â”€ decorators.py        # admin_required, etc.
â”‚       â”œâ”€â”€ helpers.py           # Formatting, slug generation
â”‚       â””â”€â”€ validators.py        # Custom validation logic
â”‚
â”œâ”€â”€ migrations/                  # Alembic migrations
â”œâ”€â”€ tests/
â”‚   â”œâ”€â”€ conftest.py
â”‚   â”œâ”€â”€ test_auth.py
â”‚   â”œâ”€â”€ test_shop.py
â”‚   â”œâ”€â”€ test_cart.py
â”‚   â”œâ”€â”€ test_checkout.py
â”‚   â””â”€â”€ test_admin.py
â”‚
â”œâ”€â”€ .env.example                 # Environment variable template
â”œâ”€â”€ .gitignore
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ docker-compose.yml
â”œâ”€â”€ gunicorn.conf.py
â”œâ”€â”€ run.py                       # Entry point
â””â”€â”€ README.md
```

---

## 4. Core Features

### 4.1 Customer-Facing (Storefront)

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Homepage** | Hero banner, featured categories, new arrivals, trending products, testimonials, newsletter signup |
| 2 | **Product Catalog** | Grid/list view, filter by category/size/color/price, sort options, pagination |
| 3 | **Product Detail** | Multiple images, size selector, color variants, add to cart, reviews & ratings, related products |
| 4 | **Search** | Full-text search with autocomplete suggestions |
| 5 | **Shopping Cart** | Add/remove items, update quantities, size/color selection, coupon codes, cart summary |
| 6 | **Checkout** | Guest checkout + logged-in checkout, address form, order summary, Stripe/Razorpay payment |
| 7 | **User Accounts** | Register, login, forgot password, profile management, saved addresses |
| 8 | **Order Tracking** | Order history, order status updates, email notifications |
| 9 | **Wishlist** | Save products for later |
| 10 | **Reviews** | Star ratings + text reviews on products |

### 4.2 Admin Dashboard

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Dashboard Overview** | Sales stats, revenue charts, recent orders, low stock alerts |
| 2 | **Product Management** | CRUD products, bulk upload, manage categories, image upload |
| 3 | **Order Management** | View/update order status, process refunds, print invoices |
| 4 | **Customer Management** | View customers, order history per customer |
| 5 | **Inventory Management** | Stock tracking, low stock alerts, restock notifications |
| 6 | **Coupon Management** | Create/edit discount codes (% off, flat off, free shipping) |
| 7 | **Reports** | Sales reports, best sellers, revenue by period |

---

## 5. Database Schema (Key Models)

### Users
- id, email, password_hash, first_name, last_name, phone, role (customer/admin), is_active, created_at

### Products
- id, name, slug, description, price, compare_at_price, category_id, brand, gender (men/women/unisex), is_active, created_at

### ProductVariants
- id, product_id, size, color, sku, stock_quantity, is_active

### ProductImages
- id, product_id, image_url, is_primary, sort_order

### Categories
- id, name, slug, description, image_url, parent_id (for sub-categories)

### Cart / CartItems
- cart: id, user_id (nullable for guests), session_id, created_at
- cart_items: id, cart_id, variant_id, quantity

### Orders / OrderItems
- order: id, user_id, order_number, status, subtotal, tax, shipping_cost, discount, total, shipping_address, billing_address, payment_id, created_at
- order_items: id, order_id, variant_id, product_name, price, quantity

### Payments
- id, order_id, provider (stripe/razorpay), transaction_id, amount, currency, status, created_at

### Reviews
- id, product_id, user_id, rating (1-5), comment, is_approved, created_at

### Coupons
- id, code, discount_type (percentage/flat), discount_value, min_order_amount, max_uses, used_count, valid_from, valid_until, is_active

### Addresses
- id, user_id, full_name, phone, address_line1, address_line2, city, state, postal_code, country, is_default

### Wishlist
- id, user_id, product_id, created_at

---

## 6. Homepage Design Specification

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  NAVBAR                                                         â”‚
â”‚  [Logo: Indistylex]    [Shop â–¾] [Collections] [About] [Contact]â”‚
â”‚                                        [ðŸ”] [â™¡] [ðŸ›’ Cart (0)]  â”‚
â”‚                                        [Login / Register]       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚                     â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—                   â”‚
â”‚                     â•‘    HERO SECTION       â•‘                   â”‚
â”‚                     â•‘                       â•‘                   â”‚
â”‚                     â•‘  "Elevate Your Style" â•‘                   â”‚
â”‚                     â•‘   New Summer          â•‘                   â”‚
â”‚                     â•‘   Collection 2026     â•‘                   â”‚
â”‚                     â•‘                       â•‘                   â”‚
â”‚                     â•‘  [ Shop Now â†’ ]       â•‘                   â”‚
â”‚                     â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•                   â”‚
â”‚              (Full-width hero image with overlay text)           â”‚
â”‚                                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚               ðŸ“¦ Free Shipping    ðŸ”„ Easy Returns               â”‚
â”‚               ðŸ’³ Secure Payment   âœ¨ Premium Quality             â”‚
â”‚                     (Trust Badges Bar)                           â”‚
â”‚                                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚                  â”€â”€ SHOP BY CATEGORY â”€â”€                          â”‚
â”‚                                                                 â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”‚
â”‚   â”‚          â”‚  â”‚          â”‚  â”‚          â”‚  â”‚          â”‚        â”‚
â”‚   â”‚  [IMG]   â”‚  â”‚  [IMG]   â”‚  â”‚  [IMG]   â”‚  â”‚  [IMG]   â”‚      â”‚
â”‚   â”‚          â”‚  â”‚          â”‚  â”‚          â”‚  â”‚          â”‚        â”‚
â”‚   â”‚  Men's   â”‚  â”‚ Women's  â”‚  â”‚  Kids    â”‚  â”‚  Acces-  â”‚      â”‚
â”‚   â”‚  Wear    â”‚  â”‚  Wear    â”‚  â”‚  Wear    â”‚  â”‚  sories  â”‚      â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜      â”‚
â”‚                                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚                  â”€â”€ NEW ARRIVALS â”€â”€                              â”‚
â”‚                                                                 â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”         â”‚
â”‚   â”‚  [IMG]  â”‚  â”‚  [IMG]  â”‚  â”‚  [IMG]  â”‚  â”‚  [IMG]  â”‚         â”‚
â”‚   â”‚         â”‚  â”‚         â”‚  â”‚         â”‚  â”‚         â”‚          â”‚
â”‚   â”‚ Product â”‚  â”‚ Product â”‚  â”‚ Product â”‚  â”‚ Product â”‚          â”‚
â”‚   â”‚ â‚¹1,299  â”‚  â”‚ â‚¹2,499  â”‚  â”‚ â‚¹899    â”‚  â”‚ â‚¹1,799  â”‚         â”‚
â”‚   â”‚ â­â­â­â­Â½ â”‚  â”‚ â­â­â­â­â­ â”‚  â”‚ â­â­â­â­  â”‚  â”‚ â­â­â­â­Â½ â”‚         â”‚
â”‚   â”‚ [AddðŸ›’] â”‚  â”‚ [AddðŸ›’] â”‚  â”‚ [AddðŸ›’] â”‚  â”‚ [AddðŸ›’] â”‚         â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜         â”‚
â”‚                                                                 â”‚
â”‚                    [ View All â†’ ]                                â”‚
â”‚                                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚   â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—   â”‚
â”‚   â•‘            PROMOTIONAL BANNER                           â•‘   â”‚
â”‚   â•‘       "Up to 50% Off â€” Summer Sale Live Now"            â•‘   â”‚
â”‚   â•‘              [ Shop the Sale â†’ ]                        â•‘   â”‚
â”‚   â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•   â”‚
â”‚                                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚                  â”€â”€ TRENDING NOW â”€â”€                              â”‚
â”‚                                                                 â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”         â”‚
â”‚   â”‚  [IMG]  â”‚  â”‚  [IMG]  â”‚  â”‚  [IMG]  â”‚  â”‚  [IMG]  â”‚         â”‚
â”‚   â”‚ Product â”‚  â”‚ Product â”‚  â”‚ Product â”‚  â”‚ Product â”‚          â”‚
â”‚   â”‚ â‚¹X,XXX  â”‚  â”‚ â‚¹X,XXX  â”‚  â”‚ â‚¹X,XXX  â”‚  â”‚ â‚¹X,XXX  â”‚         â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜         â”‚
â”‚                                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚               â”€â”€ WHAT OUR CUSTOMERS SAY â”€â”€                      â”‚
â”‚                                                                 â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”           â”‚
â”‚   â”‚ â­â­â­â­â­      â”‚  â”‚ â­â­â­â­â­      â”‚  â”‚ â­â­â­â­â­      â”‚           â”‚
â”‚   â”‚ "Amazing     â”‚  â”‚ "Love the   â”‚  â”‚ "Best       â”‚           â”‚
â”‚   â”‚  quality!"   â”‚  â”‚  fabric!"   â”‚  â”‚  prices!"   â”‚           â”‚
â”‚   â”‚  â€” Priya S.  â”‚  â”‚  â€” Rahul M. â”‚  â”‚  â€” Anita K. â”‚           â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜           â”‚
â”‚                                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                 â”‚
â”‚          â”€â”€ STAY IN THE LOOP â”€â”€                                 â”‚
â”‚   Subscribe for exclusive offers & new arrivals                 â”‚
â”‚   [ Enter your email...        ] [ Subscribe ]                  â”‚
â”‚                                                                 â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  FOOTER                                                         â”‚
â”‚                                                                 â”‚
â”‚  Indistylex        Quick Links     Customer Care    Follow Us   â”‚
â”‚  Premium clothing  Shop Men        Contact Us       [FB] [IG]   â”‚
â”‚  for the modern    Shop Women      Shipping Policy  [TW] [PIN]  â”‚
â”‚  you.              Shop Kids       Returns Policy                â”‚
â”‚                    New Arrivals    FAQs                          â”‚
â”‚                    Sale            Size Guide                    â”‚
â”‚                                                                 â”‚
â”‚  Â© 2026 Indistylex. All rights reserved.               â”‚
â”‚  [Privacy Policy] [Terms of Service]                            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Color Palette
| Usage       | Color      | Hex Code  |
|-------------|------------|-----------|
| Primary     | Deep Plum  | `#5B2C6F` |
| Secondary   | Soft Gold  | `#D4AC0D` |
| Background  | Off White  | `#FDFEFE` |
| Text        | Charcoal   | `#2C3E50` |
| Accent      | Rose Pink  | `#E74C8B` |
| Success     | Sage Green | `#27AE60` |

### Typography
- **Headings:** Playfair Display (elegant, serif)
- **Body:** Inter or Poppins (clean, modern sans-serif)

---

## 7. Security Measures

### 7.1 Authentication & Authorization

| Threat | Protection | Implementation |
|--------|-----------|----------------|
| **Brute Force Attacks** | Account lockout + rate limiting | Lock account after 5 failed attempts for 15 min; Flask-Limiter (5 req/min on login) |
| **Credential Stuffing** | Multi-layer defense | Rate limiting per IP + CAPTCHA after 3 failed attempts + breach password check |
| **Weak Passwords** | Password policy enforcement | Min 8 chars, uppercase, lowercase, digit, special char; zxcvbn strength meter |
| **Session Hijacking** | Secure session management | HttpOnly + Secure + SameSite cookies; session regeneration on login; 30-min idle timeout |
| **Privilege Escalation** | Role-based access control (RBAC) | `@admin_required` decorator; server-side role checks on every protected route |
| **Password Storage** | Bcrypt hashing | Flask-Bcrypt with cost factor 12; never store or log plaintext passwords |

### 7.2 Injection Attacks

| Threat | Protection | Implementation |
|--------|-----------|----------------|
| **SQL Injection** | Parameterized queries | SQLAlchemy ORM exclusively; NO raw SQL; input type validation on all query parameters |
| **Cross-Site Scripting (XSS)** | Output encoding + CSP | Jinja2 auto-escaping enabled; `Content-Security-Policy` headers; sanitize user-generated HTML with Bleach |
| **Cross-Site Request Forgery (CSRF)** | Token validation | Flask-WTF CSRF tokens on ALL forms and AJAX requests; SameSite cookie attribute |
| **Command Injection** | Input sanitization | No `os.system()` or `subprocess` with user input; whitelist allowed characters |
| **LDAP / NoSQL Injection** | Not applicable | Pure SQLAlchemy + MySQL â€” no LDAP or NoSQL surfaces exposed |
| **Template Injection (SSTI)** | Safe template rendering | Never pass user input as template strings; use `render_template()` only with predefined templates |

### 7.3 DDoS & Rate Limiting

| Threat | Protection | Implementation |
|--------|-----------|----------------|
| **Volumetric DDoS** | Multi-layer mitigation | Cloudflare/AWS Shield in front; Nginx `limit_req_zone` (100 req/s per IP); connection limits |
| **Application-Layer DDoS (L7)** | Intelligent rate limiting | Flask-Limiter with tiered limits: 200/day, 50/hour on API; 5/min on login/register/checkout |
| **Slowloris Attack** | Timeout enforcement | Nginx `client_body_timeout 10s`; `client_header_timeout 10s`; Gunicorn `--timeout 30` |
| **Cart/Checkout Abuse** | Transaction rate limiting | Max 10 cart updates/min; max 3 checkout attempts/hour per session; CAPTCHA on repeated failures |
| **Search/API Abuse** | Endpoint-specific limits | Search: 30 req/min; Product API: 60 req/min; Admin API: 120 req/min |
| **Bot Protection** | CAPTCHA + fingerprinting | Google reCAPTCHA v3 on forms; honeypot fields on registration; User-Agent validation |

### 7.4 Data Protection

| Threat | Protection | Implementation |
|--------|-----------|----------------|
| **Data in Transit** | TLS encryption | HTTPS enforced via Nginx with TLS 1.2+; HSTS header (`max-age=31536000`) |
| **Data at Rest** | Encryption + access control | MySQL encryption at rest (InnoDB tablespace encryption); encrypted backups |
| **Sensitive Data Exposure** | Minimal data storage | Never store full card numbers (Stripe/Razorpay handles PCI); mask emails in logs |
| **Database Breach** | Defense in depth | Bcrypt passwords; encrypted PII fields; DB user with least-privilege permissions |
| **Secrets Management** | Environment isolation | `.env` file (never committed); separate secrets per environment; rotate keys quarterly |
| **Backup Security** | Encrypted backups | Automated daily MySQL backups; encrypted with AES-256; stored offsite with restricted access |

### 7.5 File Upload Security

| Threat | Protection | Implementation |
|--------|-----------|----------------|
| **Malicious File Upload** | Strict validation | Whitelist extensions (`.jpg`, `.png`, `.webp` only); MIME type verification; max 5MB |
| **Path Traversal** | Filename sanitization | `werkzeug.utils.secure_filename()`; store in isolated upload directory; no user-controlled paths |
| **Executable Upload** | Content validation | Strip EXIF metadata; re-encode images with Pillow; serve from separate static domain |
| **Storage Abuse** | Size + count limits | Max 5MB per image; max 10 images per product; per-user upload quotas |

### 7.6 Infrastructure & Network Security

| Threat | Protection | Implementation |
|--------|-----------|----------------|
| **Server-Side Request Forgery (SSRF)** | URL validation | Whitelist allowed external domains; block internal IP ranges (127.x, 10.x, 192.168.x) |
| **Open Ports** | Firewall rules | Only expose ports 80/443; MySQL (3306) and Redis (6379) bound to localhost only |
| **Insecure Dependencies** | Dependency scanning | `pip-audit` in CI/CD; Dependabot alerts; pin all package versions in `requirements.txt` |
| **Container Escape** | Docker hardening | Non-root user in containers; read-only filesystem; no `--privileged` flag |
| **Misconfiguration** | Secure defaults | Debug mode OFF in production; remove default error pages; custom 404/500 templates |
| **Information Leakage** | Header hardening | Remove `Server` header; add `X-Content-Type-Options: nosniff`; `X-Frame-Options: DENY` |

### 7.7 Payment Security

| Threat | Protection | Implementation |
|--------|-----------|----------------|
| **Card Data Theft** | PCI DSS compliance | Stripe.js / Razorpay.js handles card data client-side; NO card numbers touch our server |
| **Payment Fraud** | Verification layers | Stripe Radar fraud detection; address verification (AVS); 3D Secure for high-risk transactions |
| **Replay Attacks** | Idempotency keys | Unique idempotency key per checkout; prevent duplicate charges |
| **Webhook Tampering** | Signature verification | Verify Stripe/Razorpay webhook signatures; reject unsigned payloads |
| **Price Manipulation** | Server-side pricing | Cart totals calculated server-side only; never trust client-side price values |

### 7.8 Monitoring & Incident Response

| Area | Implementation |
|------|---------------|
| **Security Logging** | Log all auth events (login, failed login, password reset), admin actions, and payment events with timestamps + IP |
| **Anomaly Detection** | Alert on: >10 failed logins/min from same IP; sudden traffic spikes; unusual admin activity |
| **Audit Trail** | Immutable log of all order modifications, refunds, product changes, and user role changes |
| **Error Handling** | Custom error pages (no stack traces in production); generic error messages to users; detailed logs server-side |
| **Incident Response Plan** | Documented procedure: isolate â†’ investigate â†’ patch â†’ notify affected users â†’ post-mortem |
| **Regular Audits** | Quarterly dependency audit; annual penetration testing; monthly review of access logs |

### 7.9 Security Headers (Nginx Configuration)

```
# Applied via Nginx in production
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://js.stripe.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.stripe.com;" always;
```

---

## 8. Performance Optimizations

- Redis caching for product listings and categories
- Lazy loading for product images
- Pagination on all listing pages
- Database query optimization with eager loading
- Static file minification and compression
- CDN for static assets in production
- Database connection pooling

---

## 9. Deployment Architecture

```
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚  Client  â”‚
                    â”‚ (Browser)â”‚
                    â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
                         â”‚ HTTPS
                    â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”
                    â”‚  Nginx   â”‚  (Reverse Proxy + SSL + Static Files)
                    â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
                         â”‚
                    â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”
                    â”‚ Gunicorn â”‚  (WSGI Server, multiple workers)
                    â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
                         â”‚
                    â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”
                    â”‚  Flask   â”‚  (Application)
                    â””â”€â”€â”¬â”€â”€â”€â”¬â”€â”€â”€â”˜
                       â”‚   â”‚
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â–¼â”  â”Œâ–¼â”€â”€â”€â”€â”€â”€â”€â”€â”
              â”‚  MySQL   â”‚  â”‚  Redis  â”‚  (Cache + Celery Broker)
              â”‚ Database â”‚  â”‚         â”‚
              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 10. Development Phases

### Phase 1 â€” Foundation (Core Setup)
- [ ] Project scaffolding & configuration
- [ ] Database models & migrations
- [ ] User authentication (register, login, logout, password reset)
- [ ] Base templates (navbar, footer, layout)

### Phase 2 â€” Storefront
- [ ] Homepage with all sections
- [ ] Product catalog with filters & search
- [ ] Product detail page
- [ ] Category pages

### Phase 3 â€” Shopping Experience
- [ ] Shopping cart (add, update, remove)
- [ ] Wishlist functionality
- [ ] Coupon/discount system
- [ ] Product reviews & ratings

### Phase 4 â€” Checkout & Payments
- [ ] Checkout flow (address, summary)
- [ ] Stripe/Razorpay payment integration
- [ ] Order confirmation & email notifications
- [ ] Order history & tracking

### Phase 5 â€” Admin Dashboard
- [ ] Admin dashboard with analytics
- [ ] Product management (CRUD)
- [ ] Order management
- [ ] Customer management
- [ ] Inventory & coupon management

### Phase 6 â€” Polish & Production
- [ ] SEO optimization (meta tags, sitemap, structured data)
- [ ] Performance optimization (caching, lazy loading)
- [ ] Security hardening
- [ ] Testing (unit + integration)
- [ ] Docker setup & deployment configuration
- [ ] Documentation

---

## 11. Third-Party Integrations

| Service | Purpose |
|---------|---------|
| **Stripe / Razorpay** | Payment processing |
| **SendGrid / SMTP** | Transactional emails |
| **Cloudinary / AWS S3** | Image storage (production) |
| **Google Analytics** | Traffic analytics |
| **Google reCAPTCHA** | Bot protection on forms |

---

## 12. Estimated File Count

| Area | Files |
|------|-------|
| Models | ~8 |
| Routes/Views | ~10 |
| Templates | ~25 |
| Forms | ~5 |
| Services | ~5 |
| Static (CSS/JS) | ~6 |
| Tests | ~6 |
| Config/Setup | ~8 |
| **Total** | **~73 files** |

---

## Confirmed Decisions

| Question | Decision |
|----------|----------|
| Tech Stack | Approved as-is |
| Payment Gateway | **Razorpay** (native INR, UPI, cards, net banking) |
| Currency | **INR (â‚¹)** |
| Categories | **All** (Kids, Girls, Women, Men) with **admin enable/disable toggle** |
| Guest Checkout | **Enabled** (best practice â€” reduces cart abandonment) |
| Deployment | **Docker** |
| Extra Features | Recently viewed, social sharing, SMS alerts, inventory notifications |

---

*Document prepared for Indistylex | March 2026*
