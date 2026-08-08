"""Admin dashboard analytics — inventory, gender, orders, revenue."""
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy import func

from app.extensions import db
from app.models.product import Product, ProductVariant, Category
from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.review import Review
from app.models.cart import CartItem
from app.models.wishlist import Wishlist


BOYS_BAR_COLORS = ['#1E4D8C', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
GIRLS_BAR_COLORS = ['#9D174D', '#DB2777', '#EC4899', '#F472B6', '#F9A8D4', '#FBCFE8']


def _pct_change(current, previous):
    if not previous:
        return None
    return round(((current - previous) / previous) * 100, 1)


def _normalize_gender(value):
    g = (value or '').lower()
    if g in ('boys', 'boy'):
        return 'boys'
    if g in ('girls', 'girl'):
        return 'girls'
    return 'kids'


def _gender_from_category_slug(slug):
    if not slug:
        return None
    if slug.startswith('boys') or slug == 'boy':
        return 'boys'
    if slug.startswith('girls') or slug == 'girl':
        return 'girls'
    return None


def _parent_category(category, by_id):
    if category.parent_id and category.parent_id in by_id:
        return by_id[category.parent_id]
    return category


def _segment_color(palette, index):
    return palette[index % len(palette)]


def _build_gender_bar(segments_raw, palette):
    """Build stacked bar segments with width % and count labels."""
    segments = []
    total_stock = sum(s['stock'] for s in segments_raw)
    total_products = sum(s['products'] for s in segments_raw)
    for i, seg in enumerate(segments_raw):
        pct = round((seg['stock'] / total_stock) * 100, 2) if total_stock else 0
        segments.append({
            **seg,
            'pct': pct,
            'color': _segment_color(palette, i),
        })
    return {
        'segments': segments,
        'total_stock': total_stock,
        'total_products': total_products,
    }


def get_gender_category_inventory():
    """
    Stock & product counts grouped by gender (boys/girls) and parent category.
    Returns custom chart data for horizontal stacked bars.
    """
    categories = Category.query.filter_by(is_active=True).all()
    by_id = {c.id: c for c in categories}

    boys_cats = defaultdict(lambda: {'products': 0, 'stock': 0, 'name': '', 'slug': ''})
    girls_cats = defaultdict(lambda: {'products': 0, 'stock': 0, 'name': '', 'slug': ''})

    products = Product.query.filter_by(is_active=True).all()
    for product in products:
        cat = by_id.get(product.category_id)
        if not cat:
            continue
        parent = _parent_category(cat, by_id)
        gender = _normalize_gender(product.gender)
        if gender == 'kids':
            inferred = _gender_from_category_slug(parent.slug)
            gender = inferred or 'kids'
        if gender not in ('boys', 'girls'):
            continue

        stock = sum(
            v.stock_quantity for v in product.variants.filter_by(is_active=True).all()
        )
        bucket = boys_cats if gender == 'boys' else girls_cats
        key = parent.slug
        bucket[key]['name'] = parent.name.split('(')[0].strip()
        bucket[key]['slug'] = parent.slug
        bucket[key]['products'] += 1
        bucket[key]['stock'] += stock

    def _to_segments(bucket):
        rows = sorted(bucket.values(), key=lambda x: x['stock'], reverse=True)
        return [{'name': r['name'], 'slug': r['slug'], 'products': r['products'], 'stock': r['stock']} for r in rows if r['stock'] or r['products']]

    boys_raw = _to_segments(boys_cats)
    girls_raw = _to_segments(girls_cats)
    return {
        'boys': _build_gender_bar(boys_raw, BOYS_BAR_COLORS),
        'girls': _build_gender_bar(girls_raw, GIRLS_BAR_COLORS),
    }


def get_dashboard_analytics():
    """Collect all dashboard metrics and chart payloads."""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    six_months_ago = now - timedelta(days=180)

    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total)).filter(
        Order.status.notin_(['cancelled', 'refunded'])
    ).scalar() or 0
    total_customers = User.query.filter_by(role='customer').count()
    total_products = Product.query.filter_by(is_active=True).count()

    revenue_this_week = db.session.query(func.sum(Order.total)).filter(
        Order.created_at >= week_ago,
        Order.status.notin_(['cancelled', 'refunded']),
    ).scalar() or 0
    revenue_prev_week = db.session.query(func.sum(Order.total)).filter(
        Order.created_at >= two_weeks_ago,
        Order.created_at < week_ago,
        Order.status.notin_(['cancelled', 'refunded']),
    ).scalar() or 0

    orders_this_week = Order.query.filter(Order.created_at >= week_ago).count()
    orders_prev_week = Order.query.filter(
        Order.created_at >= two_weeks_ago,
        Order.created_at < week_ago,
    ).count()

    customers_this_week = User.query.filter(
        User.role == 'customer', User.created_at >= week_ago
    ).count()
    customers_prev_week = User.query.filter(
        User.role == 'customer',
        User.created_at >= two_weeks_ago,
        User.created_at < week_ago,
    ).count()

    total_stock_units = db.session.query(func.sum(ProductVariant.stock_quantity)).filter(
        ProductVariant.is_active == True
    ).scalar() or 0

    boys_products = Product.query.filter_by(is_active=True, gender='boys').count()
    girls_products = Product.query.filter_by(is_active=True, gender='girls').count()
    kids_products = Product.query.filter_by(is_active=True, gender='kids').count()

    low_stock_count = ProductVariant.query.filter(
        ProductVariant.is_active == True,
        ProductVariant.stock_quantity <= 5,
        ProductVariant.stock_quantity > 0,
    ).count()
    out_of_stock_count = ProductVariant.query.filter(
        ProductVariant.is_active == True,
        ProductVariant.stock_quantity == 0,
    ).count()

    pending_orders = Order.query.filter_by(status='pending').count()
    processing_orders = Order.query.filter_by(status='processing').count()
    pending_reviews = Review.query.filter_by(is_approved=False).count()
    wishlist_count = Wishlist.query.count()
    cart_items_count = CartItem.query.count()

    avg_order_value = float(total_revenue) / total_orders if total_orders else 0

    db_engine = db.engine.dialect.name
    month_expr = (
        func.strftime('%Y-%m', Order.created_at)
        if db_engine == 'sqlite'
        else func.date_format(Order.created_at, '%Y-%m')
    )

    monthly_rows = db.session.query(
        month_expr.label('month'),
        func.sum(Order.total).label('revenue'),
        func.count(Order.id).label('orders'),
    ).filter(
        Order.created_at >= six_months_ago,
        Order.status.notin_(['cancelled', 'refunded']),
    ).group_by(month_expr).order_by('month').all()

    status_rows = db.session.query(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()

    payment_rows = db.session.query(
        Order.payment_method, func.count(Order.id)
    ).filter(
        Order.status.notin_(['cancelled', 'refunded'])
    ).group_by(Order.payment_method).all()

    gender_rows = db.session.query(
        Product.gender, func.count(Product.id)
    ).filter(Product.is_active == True).group_by(Product.gender).all()
    gender_labels = []
    gender_counts = []
    gender_colors = []
    gender_color_map = {'boys': '#2563EB', 'girls': '#EC4899', 'kids': '#8B5CF6', 'boy': '#2563EB', 'girl': '#EC4899'}
    for g, count in gender_rows:
        key = (g or 'kids').lower()
        gender_labels.append({'boys': 'Boys', 'girls': 'Girls', 'kids': 'Kids'}.get(key, key.title()))
        gender_counts.append(int(count))
        gender_colors.append(gender_color_map.get(key, '#6B7280'))

    top_products_rows = db.session.query(
        OrderItem.product_name,
        func.sum(OrderItem.quantity).label('total_qty'),
    ).group_by(OrderItem.product_name).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()

    category_rows = db.session.query(
        Category.name,
        func.count(Product.id).label('count'),
    ).join(Product, Product.category_id == Category.id).filter(
        Product.is_active == True
    ).group_by(Category.name).order_by(func.count(Product.id).desc()).limit(8).all()

    week_start = now - timedelta(days=6)
    today_range = f"{week_start.strftime('%b %d')} - {now.strftime('%b %d, %Y')}"

    return {
        'today_range': today_range,
        'total_orders': total_orders,
        'total_revenue': float(total_revenue or 0),
        'total_customers': total_customers,
        'total_products': total_products,
        'total_stock_units': int(total_stock_units),
        'boys_products': boys_products,
        'girls_products': girls_products,
        'kids_products': kids_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'pending_reviews': pending_reviews,
        'wishlist_count': wishlist_count,
        'cart_items_count': cart_items_count,
        'avg_order_value': avg_order_value,
        'revenue_change_pct': _pct_change(float(revenue_this_week), float(revenue_prev_week)),
        'orders_change_pct': _pct_change(orders_this_week, orders_prev_week),
        'customers_change_pct': _pct_change(customers_this_week, customers_prev_week),
        'monthly_labels': [r.month for r in monthly_rows],
        'monthly_revenue': [float(r.revenue or 0) for r in monthly_rows],
        'monthly_order_counts': [int(r.orders) for r in monthly_rows],
        'status_labels': [r[0] or 'pending' for r in status_rows],
        'status_counts': [r[1] for r in status_rows],
        'payment_labels': [(r[0] or 'cod').upper() for r in payment_rows],
        'payment_counts': [r[1] for r in payment_rows],
        'gender_labels': gender_labels,
        'gender_counts': gender_counts,
        'gender_colors': gender_colors,
        'top_product_names': [r.product_name for r in top_products_rows],
        'top_product_qty': [int(r.total_qty) for r in top_products_rows],
        'category_names': [r.name.split('(')[0].strip() for r in category_rows],
        'category_counts': [int(r.count) for r in category_rows],
        'gender_category_bars': get_gender_category_inventory(),
    }
