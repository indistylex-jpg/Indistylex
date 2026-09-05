import os
from flask import Flask, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from app.config import config
from app.extensions import db, migrate, login_manager, bcrypt, csrf, mail, limiter, cache, compress


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Trust X-Forwarded-* headers from reverse proxy (Nginx)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    compress.init_app(app)

    # Resolve upload folder to an absolute path under app/static/uploads
    upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
    if not os.path.isabs(upload_folder):
        upload_folder = upload_folder.replace('\\', '/')
        if upload_folder.startswith('app/'):
            upload_folder = upload_folder[4:]
        upload_folder = os.path.normpath(os.path.join(app.root_path, upload_folder))
    app.config['UPLOAD_FOLDER'] = upload_folder
    os.makedirs(upload_folder, exist_ok=True)
    for sub in ('products', 'categories', 'thumbnails'):
        os.makedirs(os.path.join(upload_folder, sub), exist_ok=True)

    # Serve uploaded files through Flask (works even when nginx static alias differs)
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        from flask import send_from_directory, abort
        upload_root = os.path.normpath(app.config['UPLOAD_FOLDER'])
        safe_path = os.path.normpath(os.path.join(upload_root, filename))
        if not safe_path.startswith(upload_root) or not os.path.isfile(safe_path):
            abort(404)
        return send_from_directory(upload_root, filename)

    # ── Security Headers ───────────────────────────────────────────
    @app.after_request
    def set_security_headers(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # Prevent MIME-type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # XSS protection (legacy browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Permissions policy
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=(self)'
        # Cross-Origin policies
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
        response.headers['Cross-Origin-Resource-Policy'] = 'same-site'
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://checkout.razorpay.com "
            "https://www.googletagmanager.com https://www.google-analytics.com "
            "https://www.clarity.ms https://scripts.clarity.ms https://connect.facebook.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: blob: https:; "
            "connect-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com "
            "https://www.googletagmanager.com https://www.google-analytics.com https://analytics.google.com "
            "https://region1.google-analytics.com https://region1.analytics.google.com "
            "https://www.clarity.ms https://c.clarity.ms https://b.clarity.ms https://www.facebook.com; "
            "frame-src https://api.razorpay.com https://checkout.razorpay.com https://www.googletagmanager.com; "
            "base-uri 'self'; "
            "form-action 'self' https://accounts.google.com https://www.facebook.com; "
            "object-src 'none'; "
            "frame-ancestors 'self';"
        )
        # Strict Transport Security (browsers will enforce HTTPS)
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
        # Cache static assets aggressively, don't cache HTML
        if 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
        return response

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.shop import shop_bp
    from app.routes.product import product_bp
    from app.routes.cart import cart_bp
    from app.routes.checkout import checkout_bp
    from app.routes.order import order_bp
    from app.routes.user import user_bp
    from app.routes.admin import admin_bp
    from app.routes.chatbot import chatbot_bp
    from app.routes.oauth import oauth_bp, init_oauth
    from app.routes.api import api_bp

    # Initialize OAuth providers
    init_oauth(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(shop_bp, url_prefix='/shop')
    app.register_blueprint(product_bp, url_prefix='/product')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(checkout_bp, url_prefix='/checkout')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(user_bp, url_prefix='/account')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(api_bp)

    # Context processors
    @app.context_processor
    def inject_globals():
        from app.models.cart import Cart
        from app.models.product import Category
        from flask_login import current_user
        from flask import session, request

        # Get cart count
        cart_count = 0
        if current_user.is_authenticated:
            cart = Cart.query.filter_by(user_id=current_user.id).first()
            if cart:
                cart_count = sum(item.quantity for item in cart.items)
        elif 'session_id' in session:
            cart = Cart.query.filter_by(session_id=session['session_id']).first()
            if cart:
                cart_count = sum(item.quantity for item in cart.items)

        # Navigation categories (fresh query — avoids detached lazy-load on cached objects)
        active_categories = Category.query.filter_by(
            is_active=True, parent_id=None
        ).order_by(Category.sort_order).all()

        child_rows = Category.query.filter(
            Category.is_active.is_(True),
            Category.parent_id.isnot(None),
        ).order_by(Category.sort_order).all()
        children_by_parent = {}
        for child in child_rows:
            children_by_parent.setdefault(child.parent_id, []).append(child)

        from app.utils.product_ages import SHOP_BY_AGE_NAV
        from app.utils.lifestyle_images import MOMENT_IMAGES, PRODUCT_PLACEHOLDER, FIT_CHIP_ITEMS
        from app.utils.home_categories import (
            nav_display_categories,
            nav_marquee_links,
            visible_home_category_tiles,
        )

        categories_by_slug = {c.slug: c for c in active_categories}

        def _mega_block(slug):
            parent = categories_by_slug.get(slug)
            if not parent:
                return None
            return {
                'parent': parent,
                'children': children_by_parent.get(parent.id, [])[:14],
            }

        # Clothing dropdown: age-neutral + one Boys + one Girls column (not first 4 by sort).
        nav_mega_clothing = [
            b for slug in ('newborn-infant', 'girls-1-3', 'boys-1-3', 'girls-3-8')
            if (b := _mega_block(slug))
        ]

        # Top nav quick links — gender/teen/ethnic, not sliced categories (avoids duplicate "Girls").
        nav_quick_links = [
            {'label': 'Boys', 'endpoint': 'shop.listing', 'kwargs': {'gender': 'boys'}},
            {'label': 'Girls', 'endpoint': 'shop.listing', 'kwargs': {'gender': 'girls'}},
            {'label': 'Boys Teens', 'endpoint': 'shop.category', 'kwargs': {'slug': 'boys-teens'}},
            {'label': 'Girls Teens', 'endpoint': 'shop.category', 'kwargs': {'slug': 'girls-teens'}},
            {'label': 'Ethnic & Festive', 'endpoint': 'shop.category', 'kwargs': {'slug': 'ethnic-festive'}},
        ]
        nav_quick_links = [
            link for link in nav_quick_links
            if link['endpoint'] == 'shop.listing' or link['kwargs']['slug'] in categories_by_slug
        ]

        admin_notifications = None
        if request.endpoint and request.endpoint.startswith('admin.'):
            from app.services.admin_notification_service import get_admin_header_notifications
            admin_notifications = get_admin_header_notifications()

        return {
            'cart_count': cart_count,
            'nav_categories': nav_display_categories(active_categories),
            'home_category_tiles': visible_home_category_tiles(categories_by_slug),
            'nav_marquee_links': nav_marquee_links(categories_by_slug),
            'nav_mega_clothing': nav_mega_clothing,
            'nav_quick_links': nav_quick_links,
            'shop_by_age_nav': SHOP_BY_AGE_NAV,
            'moment_lifestyle_images': MOMENT_IMAGES,
            'fit_chip_items': FIT_CHIP_ITEMS,
            'product_placeholder_image': PRODUCT_PLACEHOLDER,
            'currency_symbol': app.config.get('CURRENCY_SYMBOL', '₹'),
            'social_links': {
                'facebook': app.config.get('SOCIAL_FACEBOOK'),
                'instagram': app.config.get('SOCIAL_INSTAGRAM'),
                'twitter': app.config.get('SOCIAL_TWITTER'),
                'pinterest': app.config.get('SOCIAL_PINTEREST'),
                'whatsapp': app.config.get('SOCIAL_WHATSAPP'),
            },
            'admin_notifications': admin_notifications,
            'support_email': app.config.get('SUPPORT_EMAIL', 'indistylex@gmail.com'),
        }

    @app.template_global()
    def static_v(filename):
        """Versioned static URL so logo/favicon updates bypass long browser cache."""
        version = app.config.get('ASSET_VERSION', '1')
        return f"{url_for('static', filename=filename)}?v={version}"

    @app.template_global()
    def lifestyle_img(name):
        """URL for original Indistylex lifestyle photo by key."""
        from app.utils.lifestyle_images import LIFESTYLE_IMAGES, PRODUCT_PLACEHOLDER
        rel = LIFESTYLE_IMAGES.get(name, PRODUCT_PLACEHOLDER)
        return url_for('static', filename=rel)

    @app.template_global()
    def category_lifestyle_img(slug):
        """URL for category tile photo matched to boys/girls/age slug."""
        from app.utils.lifestyle_images import category_lifestyle_image_path
        return url_for('static', filename=category_lifestyle_image_path(slug))

    @app.template_global()
    def fit_chip_img(chip_key):
        """URL for homepage fit-chip circular category photo."""
        from app.utils.lifestyle_images import fit_chip_image_path
        return url_for('static', filename=fit_chip_image_path(chip_key))

    @app.template_global()
    def image_url(path, fallback=None):
        """Return the correct image URL for both external URLs and local uploads."""
        from app.services.image_service import resolve_image_url
        from app.utils.lifestyle_images import PRODUCT_PLACEHOLDER
        if fallback is None:
            fallback = PRODUCT_PLACEHOLDER
        return resolve_image_url(path, fallback=fallback)

    @app.template_global()
    def shop_page_url(page_num):
        """Build paginated shop URL preserving filters and category slug."""
        from flask import request, url_for
        kwargs = dict(request.view_args or {})
        for key, value in request.args.items():
            if key != 'page':
                kwargs[key] = value
        kwargs['page'] = page_num
        return url_for(request.endpoint, **kwargs)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template, jsonify
        from app.utils.request_helpers import wants_json_response
        if wants_json_response():
            return jsonify({'success': False, 'message': 'Not found.'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        from flask import render_template, jsonify
        from app.utils.request_helpers import wants_json_response
        if wants_json_response():
            return jsonify({
                'success': False,
                'message': 'Server error. Try again or fill the form manually.',
            }), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template, jsonify
        from app.utils.request_helpers import wants_json_response
        if wants_json_response():
            return jsonify({'success': False, 'message': 'Access denied.'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(429)
    def too_many_requests(error):
        from flask import render_template, jsonify
        from app.utils.request_helpers import wants_json_response
        if wants_json_response():
            return jsonify({
                'success': False,
                'message': 'Too many requests. Wait a minute and try again.',
            }), 429
        return render_template('errors/429.html'), 429

    @app.errorhandler(400)
    def bad_request(error):
        from flask import request, flash, redirect, jsonify
        from app.utils.request_helpers import wants_json_response
        description = str(getattr(error, 'description', '') or error)
        if 'CSRF' in description or 'csrf' in description.lower():
            if wants_json_response():
                return jsonify({
                    'success': False,
                    'message': 'Session expired. Refresh the page and try again.',
                }), 400
            flash('Your session expired. Please try saving again.', 'warning')
            return redirect(request.referrer or request.path or '/')
        if wants_json_response():
            return jsonify({'success': False, 'message': description or 'Bad request'}), 400
        return description or 'Bad Request', 400

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, redirect, url_for, jsonify
        from app.utils.request_helpers import wants_json_response
        if wants_json_response():
            return jsonify({
                'success': False,
                'message': 'Session expired. Refresh the page and log in again.',
            }), 401
        return redirect(url_for('auth.login', next=request.url))

    # Load user callback
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create tables and seed admin
    with app.app_context():
        from app.utils.db_schema import ensure_payment_columns
        try:
            ensure_payment_columns()
        except Exception:
            db.session.rollback()
        _seed_admin(app)

    return app


def _seed_admin(app):
    """Create default admin user if not exists."""
    from app.models.user import User
    from sqlalchemy.exc import OperationalError, ProgrammingError

    admin_email = app.config.get('ADMIN_EMAIL')
    try:
        if admin_email and not User.query.filter_by(email=admin_email).first():
            admin = User(
                email=admin_email,
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True,
            )
            admin.set_password(app.config.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            db.session.commit()
    except (OperationalError, ProgrammingError):
        # Tables not created yet — skip seeding
        db.session.rollback()
