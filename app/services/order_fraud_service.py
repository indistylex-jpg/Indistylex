"""Checkout fraud prevention — limits abuse on COD and repeat orders."""
from datetime import datetime, timedelta

from app.models.order import Order

MAX_ORDERS_PER_24H = 5
MAX_OPEN_COD_ORDERS = 2
NEW_ACCOUNT_HOURS = 48
NEW_ACCOUNT_COD_MAX_INR = 3000
DUPLICATE_ORDER_MINUTES = 5

_OPEN_ORDER_STATUSES = ('pending', 'confirmed', 'processing', 'shipped')


def validate_checkout(user, total, payment_method):
    """
    Return (ok, error_message). error_message is set when ok is False.
    """
    if not user:
        return False, 'Please log in to place an order.'
    if not user.is_active:
        return False, 'Your account is disabled. Contact support for help.'

    phone_digits = ''.join(c for c in (user.phone or '') if c.isdigit())
    if len(phone_digits) < 10:
        return False, 'Add a valid 10-digit phone number on checkout before placing an order.'

    since_24h = datetime.utcnow() - timedelta(hours=24)
    recent_orders = Order.query.filter(
        Order.user_id == user.id,
        Order.created_at >= since_24h,
    ).count()
    if recent_orders >= MAX_ORDERS_PER_24H:
        return False, (
            f'Too many orders in 24 hours (limit: {MAX_ORDERS_PER_24H}). '
            'Please try again tomorrow or contact support.'
        )

    if payment_method == 'cod':
        open_cod = Order.query.filter(
            Order.user_id == user.id,
            Order.payment_method == 'cod',
            Order.status.in_(_OPEN_ORDER_STATUSES),
        ).count()
        if open_cod >= MAX_OPEN_COD_ORDERS:
            return False, (
                'You already have open Cash on Delivery orders. '
                'Please wait for delivery or use online payment.'
            )

        created = user.created_at or datetime.utcnow()
        account_age = datetime.utcnow() - created
        if account_age < timedelta(hours=NEW_ACCOUNT_HOURS) and float(total) > NEW_ACCOUNT_COD_MAX_INR:
            return False, (
                f'For new accounts, COD is limited to ₹{NEW_ACCOUNT_COD_MAX_INR:,}. '
                'Use online payment or contact us on WhatsApp.'
            )

    window = datetime.utcnow() - timedelta(minutes=DUPLICATE_ORDER_MINUTES)
    duplicate = Order.query.filter(
        Order.user_id == user.id,
        Order.created_at >= window,
        Order.total == float(total),
    ).first()
    if duplicate:
        return False, (
            f'A similar order ({duplicate.order_number}) was placed recently. '
            'Check My Orders before ordering again.'
        )

    return True, None
