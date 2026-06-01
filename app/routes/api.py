"""
REST API Blueprint for Indistylex Android App.
All endpoints return JSON responses.
"""
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_user
from app.extensions import db, bcrypt, limiter
from app.models.user import User, Address
from app.models.product import Product, Category, ProductVariant, ProductImage
from app.models.cart import Cart, CartItem
from app.models.wishlist import Wishlist
from app.models.order import Order, OrderItem, Payment
from app.models.review import Review
from app.models.coupon import Coupon
from app.utils.helpers import sanitize_input
import jwt

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# ── JWT Authentication ─────────────────────────────────────────────────────

def generate_token(user_id):
    """Generate a JWT token for the user."""
    lifetime = current_app.config.get('JWT_TOKEN_LIFETIME_DAYS', 7)
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=lifetime),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def token_required(f):
    """Decorator to require valid JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authentication required'}), 401

        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                return jsonify({'error': 'Invalid or expired token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(user, *args, **kwargs)
    return decorated


def token_optional(f):
    """Decorator for optional authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                user = User.query.get(payload['user_id'])
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                pass
        return f(user, *args, **kwargs)
    return decorated


# ── Auth Endpoints ─────────────────────────────────────────────────────────

@api_bp.route('/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    required = ['email', 'password', 'first_name', 'last_name']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(email=data['email'].lower().strip()).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        email=data['email'].lower().strip(),
        first_name=sanitize_input(data['first_name']),
        last_name=sanitize_input(data['last_name']),
        phone=sanitize_input(data.get('phone', ''))
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        'token': token,
        'user': _serialize_user(user)
    }), 201


@api_bp.route('/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Login with email and password."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email'].lower().strip()).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403

    if user.is_locked:
        return jsonify({'error': 'Account is temporarily locked'}), 403

    token = generate_token(user.id)
    return jsonify({
        'token': token,
        'user': _serialize_user(user)
    })


@api_bp.route('/auth/google', methods=['POST'])
@limiter.limit("10 per minute")
def google_auth():
    """Authenticate with Google ID token."""
    data = request.get_json()
    if not data or not data.get('id_token'):
        return jsonify({'error': 'Google ID token required'}), 400

    # Verify the Google ID token
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    try:
        idinfo = google_id_token.verify_oauth2_token(
            data['id_token'],
            google_requests.Request(),
            current_app.config['GOOGLE_CLIENT_ID']
        )
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        oauth_id = idinfo['sub']
    except Exception:
        return jsonify({'error': 'Invalid Google token'}), 401

    # Find or create user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            oauth_provider='google',
            oauth_id=oauth_id
        )
        db.session.add(user)
        db.session.commit()
    elif not user.oauth_provider:
        user.oauth_provider = 'google'
        user.oauth_id = oauth_id
        db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        'token': token,
        'user': _serialize_user(user)
    })


@api_bp.route('/auth/me', methods=['GET'])
@token_required
def get_me(user):
    """Get current user profile."""
    return jsonify({'user': _serialize_user(user)})


# ── Categories ─────────────────────────────────────────────────────────────

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all active categories."""
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return jsonify({
        'categories': [_serialize_category(c) for c in categories]
    })


# ── Products ──────────────────────────────────────────────────────────────

@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get products with optional filters."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 50)

    query = Product.query.filter_by(is_active=True)

    # Filters
    category_slug = request.args.get('category')
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)

    gender = request.args.get('gender')
    if gender:
        query = query.filter_by(gender=gender)

    search = request.args.get('q')
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%'),
                Product.brand.ilike(f'%{search}%')
            )
        )

    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    featured = request.args.get('featured', type=int)
    if featured:
        query = query.filter_by(is_featured=True)

    trending = request.args.get('trending', type=int)
    if trending:
        query = query.filter_by(is_trending=True)

    # Sorting
    sort = request.args.get('sort', 'newest')
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.views_count.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'products': [_serialize_product_list(p) for p in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'has_next': pagination.has_next
    })


@api_bp.route('/products/<slug>', methods=['GET'])
def get_product_detail(slug):
    """Get product detail by slug."""
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # Increment view count
    product.views_count += 1
    db.session.commit()

    return jsonify({'product': _serialize_product_detail(product)})


@api_bp.route('/products/<slug>/reviews', methods=['GET'])
def get_product_reviews(slug):
    """Get reviews for a product."""
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    reviews = product.reviews.filter_by(is_approved=True).order_by(Review.created_at.desc()).all()
    return jsonify({
        'reviews': [_serialize_review(r) for r in reviews],
        'average_rating': product.average_rating,
        'review_count': product.review_count
    })


@api_bp.route('/products/<slug>/reviews', methods=['POST'])
@token_required
def add_review(user, slug):
    """Add a review for a product."""
    product = Product.query.filter_by(slug=slug, is_active=True).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()
    if not data or not data.get('rating'):
        return jsonify({'error': 'Rating is required'}), 400

    rating = int(data['rating'])
    if rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    existing = Review.query.filter_by(product_id=product.id, user_id=user.id).first()
    if existing:
        return jsonify({'error': 'You have already reviewed this product'}), 409

    review = Review(
        product_id=product.id,
        user_id=user.id,
        rating=rating,
        title=data.get('title', '').strip(),
        comment=data.get('comment', '').strip(),
        is_approved=True
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({'review': _serialize_review(review)}), 201


# ── Cart ───────────────────────────────────────────────────────────────────

@api_bp.route('/cart', methods=['GET'])
@token_required
def get_cart(user):
    """Get user's cart."""
    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        return jsonify({'items': [], 'subtotal': 0, 'item_count': 0})

    return jsonify(_serialize_cart(cart))


@api_bp.route('/cart/add', methods=['POST'])
@token_required
def add_to_cart(user):
    """Add item to cart."""
    data = request.get_json()
    if not data or not data.get('variant_id'):
        return jsonify({'error': 'variant_id is required'}), 400

    variant = ProductVariant.query.get(data['variant_id'])
    if not variant or not variant.is_active:
        return jsonify({'error': 'Variant not found'}), 404

    if variant.stock_quantity < 1:
        return jsonify({'error': 'Out of stock'}), 400

    quantity = data.get('quantity', 1)
    if quantity < 1:
        return jsonify({'error': 'Invalid quantity'}), 400

    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.flush()

    item = CartItem.query.filter_by(cart_id=cart.id, variant_id=variant.id).first()
    if item:
        new_qty = item.quantity + quantity
        if new_qty > variant.stock_quantity:
            return jsonify({'error': 'Not enough stock'}), 400
        item.quantity = new_qty
    else:
        if quantity > variant.stock_quantity:
            return jsonify({'error': 'Not enough stock'}), 400
        item = CartItem(cart_id=cart.id, variant_id=variant.id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return jsonify(_serialize_cart(cart))


@api_bp.route('/cart/update', methods=['PUT'])
@token_required
def update_cart_item(user):
    """Update cart item quantity."""
    data = request.get_json()
    if not data or not data.get('item_id') or 'quantity' not in data:
        return jsonify({'error': 'item_id and quantity required'}), 400

    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404

    item = CartItem.query.filter_by(id=data['item_id'], cart_id=cart.id).first()
    if not item:
        return jsonify({'error': 'Item not found in cart'}), 404

    quantity = int(data['quantity'])
    if quantity < 1:
        db.session.delete(item)
    else:
        if quantity > item.variant.stock_quantity:
            return jsonify({'error': 'Not enough stock'}), 400
        item.quantity = quantity

    db.session.commit()
    return jsonify(_serialize_cart(cart))


@api_bp.route('/cart/remove', methods=['DELETE'])
@token_required
def remove_from_cart(user):
    """Remove item from cart."""
    data = request.get_json()
    if not data or not data.get('item_id'):
        return jsonify({'error': 'item_id is required'}), 400

    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404

    item = CartItem.query.filter_by(id=data['item_id'], cart_id=cart.id).first()
    if not item:
        return jsonify({'error': 'Item not found in cart'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify(_serialize_cart(cart))


# ── Wishlist ───────────────────────────────────────────────────────────────

@api_bp.route('/wishlist', methods=['GET'])
@token_required
def get_wishlist(user):
    """Get user's wishlist."""
    items = Wishlist.query.filter_by(user_id=user.id).order_by(Wishlist.created_at.desc()).all()
    return jsonify({
        'items': [_serialize_wishlist_item(w) for w in items]
    })


@api_bp.route('/wishlist/toggle', methods=['POST'])
@token_required
def toggle_wishlist(user):
    """Add or remove product from wishlist."""
    data = request.get_json()
    if not data or not data.get('product_id'):
        return jsonify({'error': 'product_id is required'}), 400

    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    existing = Wishlist.query.filter_by(user_id=user.id, product_id=product.id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'added': False, 'message': 'Removed from wishlist'})
    else:
        wishlist_item = Wishlist(user_id=user.id, product_id=product.id)
        db.session.add(wishlist_item)
        db.session.commit()
        return jsonify({'added': True, 'message': 'Added to wishlist'})


# ── Orders ─────────────────────────────────────────────────────────────────

@api_bp.route('/orders', methods=['GET'])
@token_required
def get_orders(user):
    """Get user's orders."""
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return jsonify({
        'orders': [_serialize_order_list(o) for o in orders]
    })


@api_bp.route('/orders/<order_number>', methods=['GET'])
@token_required
def get_order_detail(user, order_number):
    """Get order detail."""
    order = Order.query.filter_by(order_number=order_number, user_id=user.id).first()
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    return jsonify({'order': _serialize_order_detail(order)})


@api_bp.route('/orders/create', methods=['POST'])
@token_required
def create_order(user):
    """Create a new order from cart."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart or cart.item_count == 0:
        return jsonify({'error': 'Cart is empty'}), 400

    # Validate address
    address_id = data.get('address_id')
    address = Address.query.filter_by(id=address_id, user_id=user.id).first()
    if not address:
        return jsonify({'error': 'Valid address required'}), 400

    payment_method = data.get('payment_method', 'cod')
    if payment_method not in ('cod', 'online'):
        return jsonify({'error': 'Invalid payment method'}), 400

    # Calculate totals
    subtotal = float(cart.subtotal)
    shipping_cost = 0 if subtotal >= 499 else 49
    tax = round(subtotal * 0.05, 2)
    discount = 0

    # Apply coupon if provided
    coupon_code = data.get('coupon_code')
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code.upper()).first()
        if coupon and coupon.is_valid:
            discount = float(coupon.calculate_discount(subtotal))
            coupon.used_count += 1

    total = subtotal + tax + shipping_cost - discount

    # Create order
    order = Order(
        user_id=user.id,
        subtotal=subtotal,
        tax=tax,
        shipping_cost=shipping_cost,
        discount=discount,
        total=total,
        shipping_address=json.dumps({
            'full_name': address.full_name,
            'phone': address.phone,
            'address_line1': address.address_line1,
            'address_line2': address.address_line2,
            'city': address.city,
            'state': address.state,
            'postal_code': address.postal_code,
            'country': address.country
        }),
        payment_method=payment_method,
        coupon_code=coupon_code,
        status='pending' if payment_method == 'cod' else 'pending'
    )
    db.session.add(order)
    db.session.flush()

    # Create order items from cart
    for cart_item in cart.items.all():
        variant = cart_item.variant
        product = variant.product
        order_item = OrderItem(
            order_id=order.id,
            variant_id=variant.id,
            product_name=product.name,
            product_slug=product.slug,
            size=variant.size,
            color=variant.color,
            price=float(product.price),
            quantity=cart_item.quantity,
            image_url=product.primary_image
        )
        db.session.add(order_item)

        # Reduce stock
        variant.stock_quantity -= cart_item.quantity

    # Clear cart
    for item in cart.items.all():
        db.session.delete(item)

    db.session.commit()

    return jsonify({'order': _serialize_order_detail(order)}), 201


# ── Addresses ──────────────────────────────────────────────────────────────

@api_bp.route('/addresses', methods=['GET'])
@token_required
def get_addresses(user):
    """Get user's addresses."""
    addresses = Address.query.filter_by(user_id=user.id).order_by(Address.is_default.desc()).all()
    return jsonify({
        'addresses': [_serialize_address(a) for a in addresses]
    })


@api_bp.route('/addresses', methods=['POST'])
@token_required
def add_address(user):
    """Add a new address."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    required = ['full_name', 'phone', 'address_line1', 'city', 'state', 'postal_code']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # If this is the first address or set as default, unset others
    if data.get('is_default') or Address.query.filter_by(user_id=user.id).count() == 0:
        Address.query.filter_by(user_id=user.id).update({'is_default': False})
        is_default = True
    else:
        is_default = False

    address = Address(
        user_id=user.id,
        full_name=data['full_name'].strip(),
        phone=data['phone'].strip(),
        address_line1=data['address_line1'].strip(),
        address_line2=data.get('address_line2', '').strip(),
        city=data['city'].strip(),
        state=data['state'].strip(),
        postal_code=data['postal_code'].strip(),
        country=data.get('country', 'India'),
        is_default=is_default
    )
    db.session.add(address)
    db.session.commit()

    return jsonify({'address': _serialize_address(address)}), 201


@api_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@token_required
def update_address(user, address_id):
    """Update an address."""
    address = Address.query.filter_by(id=address_id, user_id=user.id).first()
    if not address:
        return jsonify({'error': 'Address not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    for field in ['full_name', 'phone', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']:
        if field in data:
            setattr(address, field, data[field].strip() if data[field] else '')

    if data.get('is_default'):
        Address.query.filter_by(user_id=user.id).update({'is_default': False})
        address.is_default = True

    db.session.commit()
    return jsonify({'address': _serialize_address(address)})


@api_bp.route('/addresses/<int:address_id>', methods=['DELETE'])
@token_required
def delete_address(user, address_id):
    """Delete an address."""
    address = Address.query.filter_by(id=address_id, user_id=user.id).first()
    if not address:
        return jsonify({'error': 'Address not found'}), 404

    db.session.delete(address)
    db.session.commit()
    return jsonify({'message': 'Address deleted'})


# ── User Profile ───────────────────────────────────────────────────────────

@api_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(user):
    """Update user profile."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    if 'first_name' in data:
        user.first_name = data['first_name'].strip()
    if 'last_name' in data:
        user.last_name = data['last_name'].strip()
    if 'phone' in data:
        user.phone = data['phone'].strip()

    db.session.commit()
    return jsonify({'user': _serialize_user(user)})


@api_bp.route('/profile/change-password', methods=['POST'])
@token_required
def change_password(user):
    """Change user password."""
    data = request.get_json()
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password required'}), 400

    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 400

    if len(data['new_password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'})


# ── Coupons ────────────────────────────────────────────────────────────────

@api_bp.route('/coupons/validate', methods=['POST'])
@token_required
def validate_coupon(user):
    """Validate a coupon code."""
    data = request.get_json()
    if not data or not data.get('code'):
        return jsonify({'error': 'Coupon code required'}), 400

    coupon = Coupon.query.filter_by(code=data['code'].upper()).first()
    if not coupon or not coupon.is_valid:
        return jsonify({'error': 'Invalid or expired coupon'}), 400

    cart = Cart.query.filter_by(user_id=user.id).first()
    subtotal = float(cart.subtotal) if cart else 0

    if subtotal < float(coupon.min_order_amount):
        return jsonify({'error': f'Minimum order amount is ₹{coupon.min_order_amount}'}), 400

    discount = float(coupon.calculate_discount(subtotal))
    return jsonify({
        'valid': True,
        'discount': discount,
        'discount_type': coupon.discount_type,
        'discount_value': float(coupon.discount_value)
    })


# ── Home Data ──────────────────────────────────────────────────────────────

@api_bp.route('/home', methods=['GET'])
def get_home_data():
    """Get home page data (featured, trending, categories)."""
    featured = Product.query.filter_by(is_active=True, is_featured=True).limit(10).all()
    trending = Product.query.filter_by(is_active=True, is_trending=True).limit(10).all()
    new_arrivals = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(10).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()

    return jsonify({
        'featured': [_serialize_product_list(p) for p in featured],
        'trending': [_serialize_product_list(p) for p in trending],
        'new_arrivals': [_serialize_product_list(p) for p in new_arrivals],
        'categories': [_serialize_category(c) for c in categories]
    })


# ── Serializers ────────────────────────────────────────────────────────────

def _serialize_user(user):
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.full_name,
        'phone': user.phone,
        'role': user.role,
        'oauth_provider': user.oauth_provider,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }


def _serialize_category(cat):
    return {
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug,
        'description': cat.description,
        'image_url': cat.image_url,
        'product_count': cat.active_products_count
    }


def _serialize_product_list(product):
    return {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'price': float(product.price),
        'compare_at_price': float(product.compare_at_price) if product.compare_at_price else None,
        'discount_percent': product.discount_percent,
        'image': product.primary_image,
        'brand': product.brand,
        'average_rating': product.average_rating,
        'review_count': product.review_count,
        'in_stock': product.in_stock,
        'is_featured': product.is_featured,
        'is_trending': product.is_trending
    }


def _serialize_product_detail(product):
    variants = product.variants.filter_by(is_active=True).all()
    return {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'description': product.description,
        'short_description': product.short_description,
        'price': float(product.price),
        'compare_at_price': float(product.compare_at_price) if product.compare_at_price else None,
        'discount_percent': product.discount_percent,
        'brand': product.brand,
        'gender': product.gender,
        'material': product.material,
        'care_instructions': product.care_instructions,
        'images': product.all_images,
        'category': _serialize_category(product.category),
        'average_rating': product.average_rating,
        'review_count': product.review_count,
        'in_stock': product.in_stock,
        'total_stock': product.total_stock,
        'available_sizes': product.available_sizes,
        'available_colors': product.available_colors,
        'variants': [{
            'id': v.id,
            'size': v.size,
            'color': v.color,
            'sku': v.sku,
            'stock_quantity': v.stock_quantity
        } for v in variants]
    }


def _serialize_review(review):
    return {
        'id': review.id,
        'rating': review.rating,
        'title': review.title,
        'comment': review.comment,
        'user_name': review.user.full_name if review.user else 'Anonymous',
        'created_at': review.created_at.isoformat() if review.created_at else None
    }


def _serialize_cart(cart):
    items = []
    for item in cart.items.all():
        if item.variant and item.variant.product:
            product = item.variant.product
            items.append({
                'id': item.id,
                'variant_id': item.variant_id,
                'product_name': product.name,
                'product_slug': product.slug,
                'product_image': product.primary_image,
                'size': item.variant.size,
                'color': item.variant.color,
                'price': float(product.price),
                'quantity': item.quantity,
                'line_total': float(item.line_total),
                'stock_available': item.variant.stock_quantity
            })
    return {
        'items': items,
        'subtotal': float(cart.subtotal),
        'item_count': cart.item_count
    }


def _serialize_wishlist_item(wishlist_item):
    product = wishlist_item.product
    return {
        'id': wishlist_item.id,
        'product': _serialize_product_list(product) if product else None,
        'added_at': wishlist_item.created_at.isoformat() if wishlist_item.created_at else None
    }


def _serialize_order_list(order):
    return {
        'id': order.id,
        'order_number': order.order_number,
        'status': order.status,
        'total': float(order.total),
        'item_count': order.items.count(),
        'payment_method': order.payment_method,
        'created_at': order.created_at.isoformat() if order.created_at else None
    }


def _serialize_order_detail(order):
    items = []
    for item in order.items.all():
        items.append({
            'id': item.id,
            'product_name': item.product_name,
            'product_slug': item.product_slug,
            'size': item.size,
            'color': item.color,
            'price': float(item.price),
            'quantity': item.quantity,
            'line_total': float(item.line_total),
            'image_url': item.image_url
        })

    shipping_addr = json.loads(order.shipping_address) if order.shipping_address else {}

    return {
        'id': order.id,
        'order_number': order.order_number,
        'status': order.status,
        'subtotal': float(order.subtotal),
        'tax': float(order.tax),
        'shipping_cost': float(order.shipping_cost),
        'discount': float(order.discount),
        'total': float(order.total),
        'payment_method': order.payment_method,
        'coupon_code': order.coupon_code,
        'shipping_address': shipping_addr,
        'items': items,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
        'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None
    }


def _serialize_address(address):
    return {
        'id': address.id,
        'full_name': address.full_name,
        'phone': address.phone,
        'address_line1': address.address_line1,
        'address_line2': address.address_line2,
        'city': address.city,
        'state': address.state,
        'postal_code': address.postal_code,
        'country': address.country,
        'is_default': address.is_default
    }
