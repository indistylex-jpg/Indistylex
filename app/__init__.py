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

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://checkout.razorpay.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com; "
            "frame-src https://api.razorpay.com https://checkout.razorpay.com; "
            "base-uri 'self'; "
            "form-action 'self' https://accounts.google.com https://www.facebook.com;"
        )
        # Strict Transport Security (browsers will enforce HTTPS)
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
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
        from flask import session

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

        # Get active categories for navigation (cached 5 minutes)
        cache_key = 'nav_categories'
        active_categories = cache.get(cache_key)
        if active_categories is None:
            active_categories = Category.query.filter_by(
                is_active=True, parent_id=None
            ).order_by(Category.sort_order).all()
            cache.set(cache_key, active_categories, timeout=300)

        return {
            'cart_count': cart_count,
            'nav_categories': active_categories,
            'currency_symbol': app.config.get('CURRENCY_SYMBOL', '₹'),
        }

    @app.template_global()
    def image_url(path, fallback='images/placeholders/product.png'):
        """Return the correct image URL for both external URLs and local uploads."""
        if not path:
            return url_for('static', filename=fallback)
        if path.startswith(('http://', 'https://')):
            return path
        return url_for('static', filename='uploads/' + path)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        from flask import render_template
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(429)
    def too_many_requests(error):
        from flask import render_template, request
        if request.is_json:
            return {'error': 'Too many requests. Please slow down.'}, 429
        return render_template('errors/429.html'), 429

    # Load user callback
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create tables and seed admin
    with app.app_context():
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
