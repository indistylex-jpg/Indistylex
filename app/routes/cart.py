from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import current_user
from app.extensions import db, csrf, limiter
from app.models.cart import Cart, CartItem
from app.models.product import ProductVariant
from app.models.coupon import Coupon
from app.services.inventory_service import check_stock
from app.utils.helpers import generate_session_id

cart_bp = Blueprint('cart', __name__)


def _get_or_create_cart():
    """Get current user's cart or create one."""
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        return cart

    # Guest cart via session
    if 'session_id' not in session:
        session['session_id'] = generate_session_id()

    cart = Cart.query.filter_by(session_id=session['session_id']).first()
    if not cart:
        cart = Cart(session_id=session['session_id'])
        db.session.add(cart)
        db.session.commit()
    return cart


@cart_bp.route('/')
def view():
    """View shopping cart."""
    cart = _get_or_create_cart()
    return render_template('cart/cart.html', cart=cart)


@cart_bp.route('/add', methods=['POST'])
@limiter.limit("20 per minute")
def add_to_cart():
    """Add item to cart."""
    variant_id = request.form.get('variant_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)

    # If variant_id not provided, resolve from product_id + size + color
    if not variant_id:
        product_id = request.form.get('product_id', type=int)
        size = request.form.get('size', '').strip()
        color = request.form.get('color', '').strip()
        if product_id and size and color:
            variant = ProductVariant.query.filter_by(
                product_id=product_id, size=size, color=color, is_active=True
            ).first()
            if variant:
                variant_id = variant.id

    if not variant_id or quantity < 1:
        flash('Please select a size and color.', 'danger')
        return redirect(request.referrer or url_for('shop.listing'))

    variant = ProductVariant.query.get(variant_id)
    if not variant or not variant.is_active:
        flash('Product variant not available.', 'danger')
        return redirect(request.referrer or url_for('shop.listing'))

    # Check stock
    in_stock, msg = check_stock(variant_id, quantity)
    if not in_stock:
        flash(msg, 'warning')
        return redirect(request.referrer or url_for('shop.listing'))

    cart = _get_or_create_cart()

    # Check if variant already in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, variant_id=variant_id).first()
    if cart_item:
        new_qty = cart_item.quantity + quantity
        in_stock, msg = check_stock(variant_id, new_qty)
        if not in_stock:
            flash(msg, 'warning')
            return redirect(url_for('cart.view'))
        cart_item.quantity = new_qty
    else:
        cart_item = CartItem(cart_id=cart.id, variant_id=variant_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    flash('Item added to cart!', 'success')
    return redirect(url_for('cart.view'))


@cart_bp.route('/update', methods=['POST'])
def update_cart():
    """Update cart item quantity."""
    item_id = request.form.get('item_id', type=int)
    quantity = request.form.get('quantity', type=int)

    if not item_id or quantity is None:
        flash('Invalid request.', 'danger')
        return redirect(url_for('cart.view'))

    cart = _get_or_create_cart()
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()

    if not cart_item:
        flash('Item not found in cart.', 'danger')
        return redirect(url_for('cart.view'))

    if quantity <= 0:
        db.session.delete(cart_item)
        flash('Item removed from cart.', 'info')
    else:
        in_stock, msg = check_stock(cart_item.variant_id, quantity)
        if not in_stock:
            flash(msg, 'warning')
            return redirect(url_for('cart.view'))
        cart_item.quantity = quantity

    db.session.commit()
    return redirect(url_for('cart.view'))


@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    """Remove item from cart."""
    cart = _get_or_create_cart()
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.', 'info')

    return redirect(url_for('cart.view'))


@cart_bp.route('/apply-coupon', methods=['POST'])
def apply_coupon():
    """Apply coupon code to cart."""
    code = request.form.get('code', '').strip().upper()
    if not code:
        flash('Please enter a coupon code.', 'warning')
        return redirect(url_for('cart.view'))

    coupon = Coupon.query.filter_by(code=code).first()
    if not coupon or not coupon.is_valid:
        flash('Invalid or expired coupon code.', 'danger')
        return redirect(url_for('cart.view'))

    cart = _get_or_create_cart()
    discount = coupon.calculate_discount(float(cart.subtotal))
    if discount <= 0:
        flash(f'Minimum order of ₹{coupon.min_order_amount} required for this coupon.', 'warning')
        return redirect(url_for('cart.view'))

    session['coupon_code'] = code
    session['discount'] = float(discount)
    flash(f'Coupon applied! You save ₹{discount:,.2f}', 'success')
    return redirect(url_for('cart.view'))


@cart_bp.route('/count')
def count():
    """Get cart item count (for AJAX navbar updates)."""
    cart = _get_or_create_cart()
    return jsonify({'count': cart.item_count})
