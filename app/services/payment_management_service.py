"""Admin payment ledger — collection tracking, summaries, COD workflow."""
from datetime import datetime

from sqlalchemy import func, or_, extract

from app.extensions import db
from app.models.order import Order, Payment, PAYMENT_CHANNELS
from app.models.user import User


COLLECTION_CHANNELS = ('cash', 'card', 'upi', 'netbanking', 'wallet')


def create_cod_payment(order):
    """Create a pending COD payment record when order is placed."""
    existing = Payment.query.filter_by(order_id=order.id).first()
    if existing:
        return existing

    payment = Payment(
        order_id=order.id,
        provider='cod',
        amount=order.total,
        currency='INR',
        status='pending',
        channel='cod',
    )
    db.session.add(payment)
    return payment


def ensure_online_payment_defaults(payment):
    """Set channel for Razorpay payments after capture."""
    if payment.status == 'captured' and payment.channel in (None, '', 'cod'):
        payment.channel = 'online'


def backfill_missing_payments():
    """Create Payment rows for legacy orders that have none."""
    missing = (
        Order.query.outerjoin(Payment, Payment.order_id == Order.id)
        .filter(Payment.id.is_(None))
        .all()
    )
    created = 0
    for order in missing:
        if order.payment_method == 'online':
            status = 'captured' if order.status in (
                'confirmed', 'processing', 'shipped', 'delivered',
            ) else 'pending'
            if order.status in ('cancelled', 'refunded'):
                status = 'refunded' if order.status == 'refunded' else 'failed'
            payment = Payment(
                order_id=order.id,
                provider='razorpay',
                amount=order.total,
                currency='INR',
                status=status,
                channel='online' if status == 'captured' else 'cod',
            )
        else:
            status = 'pending'
            if order.status == 'refunded':
                status = 'refunded'
            elif order.status == 'cancelled':
                status = 'failed'
            payment = Payment(
                order_id=order.id,
                provider='cod',
                amount=order.total,
                currency='INR',
                status=status,
                channel='cod',
            )
        db.session.add(payment)
        created += 1

    if created:
        db.session.commit()
    return created


def mark_payment_collected(payment, *, channel, reference='', notes='', collected_by_id=None):
    """Record COD / manual collection with payment channel."""
    channel = (channel or '').strip().lower()
    if channel not in COLLECTION_CHANNELS:
        return None, 'Choose a valid collection method (cash, card, UPI, etc.).'

    if payment.status == 'captured':
        return None, 'Payment is already marked as collected.'
    if payment.status in ('refunded', 'failed'):
        return None, f'Cannot collect — payment status is {payment.status}.'

    payment.status = 'captured'
    payment.channel = channel
    payment.collected_at = datetime.utcnow()
    payment.collected_by_id = collected_by_id
    payment.reference = (reference or '').strip() or None
    payment.notes = (notes or '').strip() or None
    db.session.commit()
    return payment, None


def get_payment_summary(*, start_date=None, end_date=None):
    """Totals for admin payment dashboard cards."""
    collected_q = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.status == 'captured',
    )
    pending_cod_q = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).join(Order).filter(
        Payment.status == 'pending',
        Order.payment_method == 'cod',
        Order.status.notin_(['cancelled', 'refunded']),
    )
    by_channel_q = db.session.query(
        Payment.channel,
        func.sum(Payment.amount).label('total'),
        func.count(Payment.id).label('count'),
    ).filter(Payment.status == 'captured')

    if start_date:
        collected_q = collected_q.filter(Payment.collected_at >= start_date)
        pending_cod_q = pending_cod_q.filter(Payment.created_at >= start_date)
        by_channel_q = by_channel_q.filter(Payment.collected_at >= start_date)
    if end_date:
        collected_q = collected_q.filter(Payment.collected_at < end_date)
        by_channel_q = by_channel_q.filter(Payment.collected_at < end_date)

    by_channel_rows = by_channel_q.group_by(Payment.channel).all()

    channel_labels = dict(PAYMENT_CHANNELS)
    by_channel = []
    for row in by_channel_rows:
        by_channel.append({
            'channel': row.channel or 'unknown',
            'label': channel_labels.get(row.channel, (row.channel or 'Other').title()),
            'total': float(row.total or 0),
            'count': int(row.count or 0),
        })

    status_rows = db.session.query(
        Payment.status,
        func.count(Payment.id),
        func.coalesce(func.sum(Payment.amount), 0),
    ).group_by(Payment.status).all()

    return {
        'total_collected': float(collected_q.scalar() or 0),
        'pending_cod': float(pending_cod_q.scalar() or 0),
        'by_channel': by_channel,
        'by_status': [
            {
                'status': r[0],
                'count': int(r[1]),
                'total': float(r[2] or 0),
            }
            for r in status_rows
        ],
    }


def get_payments_query(*, status=None, channel=None, method=None, month=None, search=None):
    """Filtered payment history query for admin list."""
    query = (
        Payment.query.join(Order, Payment.order_id == Order.id)
        .outerjoin(User, Order.user_id == User.id)
    )

    if status:
        query = query.filter(Payment.status == status)
    if channel:
        query = query.filter(Payment.channel == channel)
    if method:
        query = query.filter(Order.payment_method == method)
    if month:
        try:
            y, m = month.split('-')
            query = query.filter(
                extract('year', func.coalesce(Payment.collected_at, Payment.created_at)) == int(y),
                extract('month', func.coalesce(Payment.collected_at, Payment.created_at)) == int(m),
            )
        except ValueError:
            pass
    if search:
        like = f'%{search}%'
        query = query.filter(or_(
            Order.order_number.ilike(like),
            Payment.reference.ilike(like),
            Payment.razorpay_payment_id.ilike(like),
        ))

    return query.order_by(
        func.coalesce(Payment.collected_at, Payment.created_at).desc(),
        Payment.id.desc(),
    )
