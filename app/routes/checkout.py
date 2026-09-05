import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, abort
from flask_login import current_user, login_required
from app.extensions import db, limiter
from app.models.cart import Cart
from app.models.order import Order, OrderItem
from app.models.coupon import Coupon
from app.forms.checkout_forms import ShippingAddressForm
from app.services.payment_service import create_razorpay_order, verify_payment, capture_payment
from app.services.inventory_service import check_stock, reduce_stock
from app.services.email_service import send_order_confirmation
from app.services.order_fraud_service import validate_checkout

checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def checkout_page():
    """Checkout — login required (no guest orders)."""
    if not current_user.is_active:
        flash('Your account is disabled. Contact support.', 'danger')
        return redirect(url_for('main.index'))

    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart or cart.item_count == 0:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('shop.listing'))

    for item in cart.items.all():
        in_stock, msg = check_stock(item.variant_id, item.quantity)
        if not in_stock:
            flash(f'{item.variant.product.name} ({item.variant.size}/{item.variant.color}): {msg}', 'warning')
            return redirect(url_for('cart.view'))

    form = ShippingAddressForm()
    if request.method == 'GET':
        addr = current_user.default_address()
        if addr:
            form.full_name.data = addr.full_name
            form.phone.data = addr.phone
            form.email.data = current_user.email
            form.address_line1.data = addr.address_line1
            form.address_line2.data = addr.address_line2
            form.city.data = addr.city
            form.state.data = addr.state
            form.postal_code.data = addr.postal_code
        else:
            form.full_name.data = current_user.full_name
            form.email.data = current_user.email
            form.phone.data = current_user.phone

    if form.validate_on_submit():
        subtotal = float(cart.subtotal)
        shipping_cost = 0 if subtotal >= 999 else 79
        discount = 0

        coupon_code = session.get('coupon_code')
        if coupon_code:
            coupon = Coupon.query.filter_by(code=coupon_code).first()
            if coupon and coupon.is_valid:
                discount = float(coupon.calculate_discount(subtotal))

        tax = round((subtotal - discount) * 0.05, 2)
        total = subtotal - discount + tax + shipping_cost

        ok, fraud_msg = validate_checkout(current_user, total, form.payment_method.data)
        if not ok:
            flash(fraud_msg, 'danger')
            return render_template(
                'checkout/checkout.html',
                form=form,
                cart=cart,
                discount=session.get('discount', 0),
                coupon_code=session.get('coupon_code'),
            )

        if form.phone.data:
            current_user.phone = form.phone.data.strip()

        shipping_address = json.dumps({
            'full_name': form.full_name.data,
            'phone': form.phone.data,
            'email': current_user.email,
            'address_line1': form.address_line1.data,
            'address_line2': form.address_line2.data or '',
            'city': form.city.data,
            'state': form.state.data,
            'postal_code': form.postal_code.data,
            'country': 'India',
        })

        order = Order(
            user_id=current_user.id,
            guest_email=None,
            guest_phone=None,
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            discount=discount,
            total=total,
            shipping_address=shipping_address,
            billing_address=shipping_address,
            coupon_code=coupon_code,
            payment_method=form.payment_method.data,
            notes=form.notes.data if hasattr(form, 'notes') else None,
        )
        db.session.add(order)
        db.session.flush()

        for item in cart.items.all():
            order_item = OrderItem(
                order_id=order.id,
                variant_id=item.variant_id,
                product_name=item.variant.product.name,
                product_slug=item.variant.product.slug,
                size=item.variant.size,
                color=item.variant.color,
                price=item.variant.product.price,
                cost_price=item.variant.product.cost_price,
                quantity=item.quantity,
                image_url=item.variant.product.primary_image_url,
            )
            db.session.add(order_item)

        db.session.commit()

        if form.payment_method.data == 'cod':
            order.status = 'confirmed'

            from app.services.payment_management_service import create_cod_payment
            create_cod_payment(order)

            for item in order.items.all():
                reduce_stock(item.variant_id, item.quantity)

            if order.coupon_code:
                coupon = Coupon.query.filter_by(code=order.coupon_code).first()
                if coupon:
                    coupon.used_count += 1

            db.session.commit()

            c = Cart.query.filter_by(user_id=current_user.id).first()
            if c:
                for ci in c.items.all():
                    db.session.delete(ci)
                db.session.delete(c)
                db.session.commit()

            session.pop('coupon_code', None)
            session.pop('discount', None)

            send_order_confirmation(order)

            flash('Order placed successfully! Pay on delivery.', 'success')
            return redirect(url_for('checkout.success', order_number=order.order_number))

        try:
            razorpay_order = create_razorpay_order(order)
        except Exception as e:
            current_app.logger.error(f'Razorpay order creation failed: {e}')
            flash('Online payment is currently unavailable. Please choose Cash on Delivery.', 'danger')
            db.session.delete(order)
            db.session.commit()
            return redirect(url_for('checkout.checkout_page'))

        return render_template('checkout/payment.html',
                               order=order,
                               razorpay_order=razorpay_order,
                               razorpay_key=current_app.config['RAZORPAY_KEY_ID'],
                               form=form)

    return render_template('checkout/checkout.html', form=form, cart=cart,
                           discount=session.get('discount', 0),
                           coupon_code=session.get('coupon_code'))


@checkout_bp.route('/verify', methods=['POST'])
@login_required
def verify():
    """Verify Razorpay payment after checkout."""
    razorpay_payment_id = request.form.get('razorpay_payment_id')
    razorpay_order_id = request.form.get('razorpay_order_id')
    razorpay_signature = request.form.get('razorpay_signature')

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        flash('Payment verification failed. Missing data.', 'danger')
        return redirect(url_for('cart.view'))

    from app.models.order import Payment
    payment = Payment.query.filter_by(razorpay_order_id=razorpay_order_id).first()
    if not payment:
        flash('Payment not found.', 'danger')
        return redirect(url_for('cart.view'))

    order = payment.order
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    is_valid = verify_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature)
    if not is_valid:
        flash('Payment verification failed. Please contact support.', 'danger')
        payment.status = 'failed'
        db.session.commit()
        return redirect(url_for('cart.view'))

    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    capture_payment(payment)

    order.status = 'confirmed'

    for item in order.items.all():
        reduce_stock(item.variant_id, item.quantity)

    if order.coupon_code:
        coupon = Coupon.query.filter_by(code=order.coupon_code).first()
        if coupon:
            coupon.used_count += 1

    db.session.commit()

    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart:
        for item in cart.items.all():
            db.session.delete(item)
        db.session.delete(cart)
        db.session.commit()

    session.pop('coupon_code', None)
    session.pop('discount', None)

    send_order_confirmation(order)

    flash('Payment successful! Your order has been placed.', 'success')
    return redirect(url_for('checkout.success', order_number=order.order_number))


@checkout_bp.route('/success/<order_number>')
@login_required
def success(order_number):
    """Order success page — owner only."""
    order = Order.query.filter_by(order_number=order_number).first_or_404()

    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    return render_template('checkout/success.html', order=order)
