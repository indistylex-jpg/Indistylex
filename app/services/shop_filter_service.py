"""Shop listing filters — query building and facet options."""

from sqlalchemy import func, or_

from app.extensions import db
from app.models.product import Product, Category, ProductVariant
from app.utils.product_ages import AGE_GROUP_SECTIONS, apply_age_group_filter

GENDER_FILTER_CHOICES = [
    ('boys', 'Boys'),
    ('girls', 'Girls'),
    ('kids', 'Kids (Unisex)'),
]

SORT_OPTIONS = [
    ('featured', 'Featured'),
    ('popular', 'Best Selling'),
    ('name_asc', 'Title, A–Z'),
    ('name_desc', 'Title, Z–A'),
    ('price_low', 'Price, low to high'),
    ('price_high', 'Price, high to low'),
    ('newest', 'Date, new to old'),
    ('new_arrivals', 'New Arrivals'),
    ('oldest', 'Date, old to new'),
]

DEFAULT_COLORS = [
    'Black', 'White', 'Blue', 'Red', 'Green', 'Pink', 'Yellow',
    'Brown', 'Grey', 'Navy', 'Purple', 'Orange', 'Beige', 'Multicolor',
]


def base_product_query():
    return Product.query.filter_by(is_active=True).join(Category).filter(
        Category.is_active.is_(True)
    )


def apply_shop_filters(query, args):
    category_slug = args.get('category')
    if category_slug:
        category = Category.query.filter_by(slug=category_slug, is_active=True).first()
        if category:
            cat_ids = [category.id] + [
                c.id for c in category.children.filter_by(is_active=True).all()
            ]
            query = query.filter(Product.category_id.in_(cat_ids))

    gender = args.get('gender')
    if gender:
        query = query.filter(Product.gender == gender)

    age_group = args.get('age_group')
    query = apply_age_group_filter(query, age_group, Product)

    min_price = args.get('min_price', type=float)
    max_price = args.get('max_price', type=float)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    color = (args.get('color') or '').strip()
    if color:
        query = query.filter(Product.variants.any(
            func.lower(ProductVariant.color) == color.lower(),
            ProductVariant.is_active.is_(True),
        ))

    size = (args.get('size') or '').strip()
    if size:
        query = query.filter(Product.variants.any(
            ProductVariant.size == size,
            ProductVariant.is_active.is_(True),
        ))

    search = (args.get('q') or '').strip()
    if search:
        term = f'%{search}%'
        query = query.filter(or_(
            Product.name.ilike(term),
            Product.description.ilike(term),
            Product.brand.ilike(term),
        ))

    return query


def apply_shop_sort(query, sort_key):
    if sort_key == 'price_low':
        return query.order_by(Product.price.asc())
    if sort_key == 'price_high':
        return query.order_by(Product.price.desc())
    if sort_key == 'popular':
        return query.order_by(Product.views_count.desc())
    if sort_key == 'name_asc':
        return query.order_by(Product.name.asc())
    if sort_key == 'name_desc':
        return query.order_by(Product.name.desc())
    if sort_key == 'oldest':
        return query.order_by(Product.created_at.asc())
    if sort_key == 'featured':
        return query.order_by(Product.is_featured.desc(), Product.created_at.desc())
    return query.order_by(Product.created_at.desc())


def get_filter_colors():
    rows = db.session.query(ProductVariant.color).join(Product).filter(
        Product.is_active.is_(True),
        ProductVariant.is_active.is_(True),
    ).distinct().all()
    colors = sorted({r[0].strip() for r in rows if r[0]})
    return colors or DEFAULT_COLORS


def get_filter_sizes():
    rows = db.session.query(ProductVariant.size).join(Product).filter(
        Product.is_active.is_(True),
        ProductVariant.is_active.is_(True),
    ).distinct().all()
    sizes = [r[0].strip() for r in rows if r[0]]
    return _sort_sizes(sizes)


def _sort_sizes(sizes):
    order = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
    ranked = []
    rest = []
    for size in sizes:
        if size.upper() in order:
            ranked.append(size)
        else:
            rest.append(size)
    ranked.sort(key=lambda s: order.index(s.upper()) if s.upper() in order else 999)
    rest.sort()
    return ranked + rest


def active_filter_count(args):
    count = 0
    for key in ('category', 'gender', 'age_group', 'color', 'size'):
        if args.get(key):
            count += 1
    if args.get('min_price') or args.get('max_price'):
        count += 1
    return count


def build_listing_query(args):
    query = apply_shop_filters(base_product_query(), args)
    sort = args.get('sort', 'newest')
    if sort not in {value for value, _ in SORT_OPTIONS}:
        sort = 'newest'
    if sort == 'new_arrivals':
        query = query.filter(Product.is_new_arrival.is_(True))
        query = apply_shop_sort(query, 'newest')
        return query, 'new_arrivals'
    query = apply_shop_sort(query, sort)
    return query, sort
