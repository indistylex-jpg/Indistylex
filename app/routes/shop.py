from flask import Blueprint, render_template, request, redirect, url_for, current_app

from app.models.product import Category
from app.services.shop_filter_service import (
    GENDER_FILTER_CHOICES,
    SORT_OPTIONS,
    active_filter_count,
    build_listing_query,
    get_filter_colors,
    get_filter_sizes,
)
from app.utils.product_ages import AGE_GROUP_SECTIONS
from app.utils.home_categories import nav_display_categories

shop_bp = Blueprint('shop', __name__)


def _listing_context(args, category=None):
    page = args.get('page', 1, type=int)
    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 12)
    query, sort = build_listing_query(args)
    products = query.paginate(page=page, per_page=per_page, error_out=False)

    category_slug = args.get('category') or (category.slug if category else None)
    categories = Category.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(Category.sort_order).all()

    return {
        'products': products,
        'categories': categories,
        'age_group_sections': AGE_GROUP_SECTIONS,
        'gender_choices': GENDER_FILTER_CHOICES,
        'sort_options': SORT_OPTIONS,
        'filter_colors': get_filter_colors(),
        'filter_sizes': get_filter_sizes(),
        'current_category': category_slug,
        'current_sort': sort,
        'search_query': (args.get('q') or '').strip(),
        'active_filters': active_filter_count(args),
        'category': category,
    }


@shop_bp.route('/')
def listing():
    """Product listing with Miarcus-style filters."""
    ctx = _listing_context(request.args)
    return render_template('shop/listing.html', **ctx)


@shop_bp.route('/category/<slug>')
def category(slug):
    """Category page — same layout as shop listing."""
    cat = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    args = request.args.copy()
    args['category'] = slug
    ctx = _listing_context(args, category=cat)
    return render_template('shop/listing.html', **ctx)


@shop_bp.route('/search')
def search():
    """Search results page."""
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('shop.listing'))
    ctx = _listing_context(request.args)
    return render_template('shop/listing.html', **ctx)
