from flask import Blueprint, render_template, request, current_app
from app.models.product import Product, Category
from app.extensions import cache

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/')
def listing():
    """Product listing with filters, search, and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 12)

    # Base query - only active products in active categories
    query = Product.query.filter_by(is_active=True).join(Category).filter(
        Category.is_active == True
    )

    # Category filter
    category_slug = request.args.get('category')
    if category_slug:
        category = Category.query.filter_by(slug=category_slug, is_active=True).first()
        if category:
            # Include sub-categories
            cat_ids = [category.id] + [c.id for c in category.children.filter_by(is_active=True).all()]
            query = query.filter(Product.category_id.in_(cat_ids))

    # Gender filter
    gender = request.args.get('gender')
    if gender:
        query = query.filter(Product.gender == gender)

    # Age group filter
    age_group = request.args.get('age_group')
    if age_group:
        query = query.filter(Product.age_group == age_group)

    # Price filter
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Search
    search = request.args.get('q', '').strip()
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (Product.name.ilike(search_term)) |
            (Product.description.ilike(search_term)) |
            (Product.brand.ilike(search_term))
        )

    # Sort
    sort = request.args.get('sort', 'newest')
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.views_count.desc())
    elif sort == 'name':
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    # Paginate
    products = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get categories for sidebar filter
    categories = Category.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(Category.sort_order).all()

    return render_template('shop/listing.html',
                           products=products,
                           categories=categories,
                           current_category=category_slug,
                           current_sort=sort,
                           search_query=search)


@shop_bp.route('/category/<slug>')
def category(slug):
    """Category page with products."""
    cat = Category.query.filter_by(slug=slug, is_active=True).first_or_404()

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 12)

    cat_ids = [cat.id] + [c.id for c in cat.children.filter_by(is_active=True).all()]

    products = Product.query.filter(
        Product.is_active == True,
        Product.category_id.in_(cat_ids)
    ).order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('shop/listing.html',
                           products=products,
                           category=cat,
                           current_category=slug,
                           categories=Category.query.filter_by(is_active=True, parent_id=None).all())


@shop_bp.route('/search')
def search():
    """Search results page."""
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('shop.listing'))

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 12)

    search_term = f'%{q}%'
    products = Product.query.filter(
        Product.is_active == True,
        (Product.name.ilike(search_term)) |
        (Product.description.ilike(search_term)) |
        (Product.brand.ilike(search_term))
    ).join(Category).filter(
        Category.is_active == True
    ).order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('shop/listing.html',
                           products=products,
                           search_query=q,
                           categories=Category.query.filter_by(is_active=True, parent_id=None).all())
