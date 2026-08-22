"""Live admin header notifications — orders to action and store alerts."""
from datetime import datetime, timedelta

from app.models.order import Order
from app.models.review import Review
from app.services.inventory_service import get_low_stock_products


def get_admin_header_notifications(*, low_stock_threshold=5, order_preview_limit=5):
    """
    Return counts and dropdown items for the admin top bar.

    Orders (bag): pending + confirmed + processing — need fulfillment action.
    Alerts (bell): low stock variants + reviews waiting for approval.
    """
    action_statuses = ['pending', 'confirmed', 'processing']
    orders_q = Order.query.filter(Order.status.in_(action_statuses))
    order_count = orders_q.count()

    recent_orders = (
        orders_q.order_by(Order.created_at.desc())
        .limit(order_preview_limit)
        .all()
    )
    order_items = []
    for order in recent_orders:
        label = order.order_number or f'Order #{order.id}'
        status_label = (order.status or 'pending').replace('_', ' ').title()
        order_items.append({
            'label': label,
            'meta': f'{status_label} · ₹{float(order.total or 0):,.0f}',
            'url': f'/admin/orders/{order.id}',
            'when': _time_ago(order.created_at),
        })

    low_stock_variants = get_low_stock_products(threshold=low_stock_threshold)
    low_stock_count = len(low_stock_variants)
    pending_review_count = Review.query.filter_by(is_approved=False).count()
    alert_count = low_stock_count + pending_review_count

    alert_items = []
    if low_stock_count:
        preview = low_stock_variants[:3]
        names = ', '.join(
            f'{v.product.name} ({v.size})' if v.product else v.sku
            for v in preview
        )
        extra = f' +{low_stock_count - 3} more' if low_stock_count > 3 else ''
        alert_items.append({
            'label': f'{low_stock_count} low-stock variant{"s" if low_stock_count != 1 else ""}',
            'meta': names + extra,
            'url': '/admin/inventory',
            'icon': 'bi-box-seam',
        })
    if pending_review_count:
        alert_items.append({
            'label': f'{pending_review_count} review{"s" if pending_review_count != 1 else ""} to approve',
            'meta': 'Customer reviews waiting for moderation',
            'url': '/admin/reviews',
            'icon': 'bi-star',
        })

    return {
        'order_count': order_count,
        'alert_count': alert_count,
        'order_items': order_items,
        'alert_items': alert_items,
        'orders_url': '/admin/orders?status=pending',
        'alerts_url': '/admin/inventory' if low_stock_count else '/admin/reviews',
    }


def _time_ago(when):
    if not when:
        return ''
    now = datetime.utcnow()
    delta = now - when
    if delta < timedelta(minutes=1):
        return 'Just now'
    if delta < timedelta(hours=1):
        mins = int(delta.total_seconds() // 60)
        return f'{mins}m ago'
    if delta < timedelta(days=1):
        hrs = int(delta.total_seconds() // 3600)
        return f'{hrs}h ago'
    days = delta.days
    if days == 1:
        return 'Yesterday'
    if days < 7:
        return f'{days}d ago'
    return when.strftime('%d %b')
