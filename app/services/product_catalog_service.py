"""Product catalog helpers — admin form, validation, and store visibility."""
from slugify import slugify

from app.extensions import db
from app.models.product import Product, ProductVariant, Category
from app.utils.product_ages import AGE_GROUP_SECTIONS, normalize_age_groups


# Quick age presets for the admin product form (label → age codes).
AGE_PRESETS = [
    {
        'id': 'newborn',
        'label': 'Newborn 0–12M',
        'ages': ['0-3m', '3-6m', '6-9m', '9-12m'],
    },
    {
        'id': 'toddler',
        'label': 'Toddler 1–3Y',
        'ages': ['1y', '1-2y', '2-3y'],
    },
    {
        'id': 'kids',
        'label': 'Kids 3–8Y',
        'ages': ['3-4y', '4-5y', '5-6y', '6-7y', '7-8y'],
    },
    {
        'id': 'preteen',
        'label': 'Pre-teen 9–12Y',
        'ages': ['8-9y', '9-10y', '10-11y', '11-12y'],
    },
    {
        'id': 'teen',
        'label': 'Teens 13–18Y',
        'ages': ['12-13y', '13-14y', '14-15y', '15-16y', '16-17y', '17-18y'],
    },
]

STORE_VISIBILITY_OPTIONS = [
    {
        'field': 'is_active',
        'label': 'Live on store',
        'icon': 'bi-shop-window',
        'description': 'Product appears in shop search, categories, and can be purchased.',
        'color': '#10B981',
    },
    {
        'field': 'is_new_arrival',
        'label': 'New Arrivals',
        'icon': 'bi-stars',
        'description': 'Homepage “New Arrivals” carousel and New Arrivals shop filter.',
        'color': '#2563EB',
    },
    {
        'field': 'is_featured',
        'label': 'Parent Favorites',
        'icon': 'bi-heart-fill',
        'description': 'Homepage “Parent Favorites” section and Featured sort in shop.',
        'color': '#EC4899',
    },
    {
        'field': 'is_trending',
        'label': 'Trending',
        'icon': 'bi-fire',
        'description': 'Trending badge on product cards and trending API feeds.',
        'color': '#F59E0B',
    },
]

# Category slug prefix → suggested gender for admin hints.
CATEGORY_GENDER_HINTS = {
    'boys': 'boys',
    'girls': 'girls',
    'newborn': 'kids',
    'boys-1-3': 'boys',
    'girls-1-3': 'girls',
    'baby': 'kids',
    'ethnic': None,
    'nightwear': 'kids',
    'winter': 'kids',
    'school': None,
    'activewear': 'kids',
}


def suggested_gender_for_category(category_id):
    """Return suggested gender code from category slug, or None."""
    cat = Category.query.get(category_id)
    if not cat:
        return None
    slug = cat.slug.lower()
    parent = Category.query.get(cat.parent_id) if cat.parent_id else None
    for key, gender in CATEGORY_GENDER_HINTS.items():
        if key in slug or (parent and key in parent.slug.lower()):
            return gender
    if slug.startswith('boys'):
        return 'boys'
    if slug.startswith('girls'):
        return 'girls'
    return None


def get_category_groups(*, include_inactive=False):
    """Categories grouped for optgroup select in admin form."""
    q = Category.query
    if not include_inactive:
        q = q.filter_by(is_active=True)
    all_cats = q.order_by(Category.sort_order, Category.name).all()
    by_id = {c.id: c for c in all_cats}
    parents = [c for c in all_cats if c.parent_id is None]
    grouped = []

    for parent in sorted(parents, key=lambda c: (c.sort_order, c.name)):
        children = sorted(
            [c for c in all_cats if c.parent_id == parent.id],
            key=lambda c: (c.sort_order, c.name),
        )
        if children:
            grouped.append({
                'label': parent.name,
                'parent_slug': parent.slug,
                'options': [
                    {'id': child.id, 'name': child.name, 'slug': child.slug}
                    for child in children
                ],
            })
        else:
            grouped.append({
                'label': parent.name,
                'parent_slug': parent.slug,
                'options': [{'id': parent.id, 'name': parent.name, 'slug': parent.slug}],
            })

    # Orphan sub-categories (parent inactive/missing)
    covered = {opt['id'] for g in grouped for opt in g['options']}
    orphans = [c for c in all_cats if c.id not in covered]
    if orphans:
        grouped.append({
            'label': 'Other',
            'parent_slug': '',
            'options': [{'id': c.id, 'name': c.name, 'slug': c.slug} for c in orphans],
        })
    return grouped


def get_category_choices_flat():
    """Flat (id, label) choices for WTForms fallback."""
    choices = []
    for group in get_category_groups():
        for opt in group['options']:
            label = f"{group['label']} › {opt['name']}" if len(group['options']) > 1 or group['label'] != opt['name'] else opt['name']
            choices.append((opt['id'], label))
    return choices


def category_metadata_for_js():
    """JSON-serializable category → gender hints for admin form JS."""
    meta = {}
    for group in get_category_groups():
        for opt in group['options']:
            meta[str(opt['id'])] = {
                'slug': opt['slug'],
                'parent_slug': group['parent_slug'],
                'suggested_gender': suggested_gender_for_category(opt['id']),
            }
    return meta


def unique_product_slug(name, product_id=None):
    base = slugify((name or '').strip()) or 'product'
    slug = base
    n = 2
    while True:
        query = Product.query.filter_by(slug=slug)
        if product_id:
            query = query.filter(Product.id != product_id)
        if not query.first():
            return slug
        slug = f'{base}-{n}'
        n += 1


def parse_all_variant_rows_from_request(form_data):
    """Return every variant row from the form (including blank rows)."""
    sizes = form_data.getlist('variant_size[]')
    colors = form_data.getlist('variant_color[]')
    skus = form_data.getlist('variant_sku[]')
    stocks = form_data.getlist('variant_stock[]')
    rows = []
    for size, color, sku, stock in zip(sizes, colors, skus, stocks):
        try:
            stock_qty = max(0, int(stock or 0))
        except (TypeError, ValueError):
            stock_qty = 0
        rows.append({
            'size': (size or '').strip(),
            'color': (color or '').strip(),
            'sku': (sku or '').strip(),
            'stock': stock_qty,
        })
    return rows


def product_form_draft_context(form_data=None, *, product=None):
    """Repopulate admin product form after a failed save."""
    default_row = {'size': '', 'color': '', 'sku': '', 'stock': 10}
    if form_data is not None:
        rows = parse_all_variant_rows_from_request(form_data)
        return {
            'selected_age_groups': normalize_age_groups(form_data.getlist('age_groups')),
            'variant_draft_rows': rows if rows else [default_row.copy()],
        }
    return {
        'selected_age_groups': product.age_groups_list if product else [],
        'variant_draft_rows': [default_row.copy()],
    }


def parse_variant_rows_from_request(form_data):
    """Extract variant rows from variant_*[] form fields."""
    sizes = form_data.getlist('variant_size[]')
    colors = form_data.getlist('variant_color[]')
    skus = form_data.getlist('variant_sku[]')
    stocks = form_data.getlist('variant_stock[]')
    rows = []
    for size, color, sku, stock in zip(sizes, colors, skus, stocks):
        size = (size or '').strip()
        color = (color or '').strip()
        sku = (sku or '').strip()
        if not any([size, color, sku]):
            continue
        try:
            stock_qty = max(0, int(stock or 0))
        except (TypeError, ValueError):
            stock_qty = 0
        rows.append({'size': size, 'color': color, 'sku': sku, 'stock': stock_qty})
    return rows


def validate_product_submission(form, form_data, files, *, is_new=False, product=None):
    """Return list of user-facing validation error strings."""
    errors = []

    age_values = form_data.getlist('age_groups')
    normalized_ages = normalize_age_groups(age_values)
    if not normalized_ages:
        errors.append('Select at least one suitable age band so customers can filter by age.')

    if form.is_active.data and not (form.gender.data or '').strip():
        errors.append('Choose a gender (Boys, Girls, or Kids) for products that are live on the store.')

    variant_rows = parse_variant_rows_from_request(form_data)
    complete_variants = [r for r in variant_rows if all([r['size'], r['color'], r['sku']])]
    partial_variants = [r for r in variant_rows if any([r['size'], r['color'], r['sku']]) and r not in complete_variants]

    if partial_variants:
        errors.append('Each variant row needs Size, Color, and SKU — or leave the row blank.')

    if is_new and not complete_variants:
        errors.append('Add at least one variant (size, color, SKU, stock) so customers can buy this product.')

    if is_new and product is None:
        has_images = any(f and f.filename for f in files.getlist('images'))
        if not has_images:
            errors.append('Upload at least one product photo before publishing.')

    if form.compare_at_price.data and form.price.data:
        if form.compare_at_price.data <= form.price.data:
            errors.append('Compare-at price should be higher than selling price (for sale badge).')

    return errors


def apply_product_fields_from_form(product, form, *, is_new=False):
    """Apply ProductForm fields to a Product instance."""
    product.name = form.name.data.strip()
    if is_new:
        product.slug = unique_product_slug(product.name)
    product.short_description = form.short_description.data
    product.description = form.description.data
    product.price = form.price.data
    product.compare_at_price = form.compare_at_price.data or None
    product.cost_price = form.cost_price.data or None
    product.category_id = form.category_id.data
    product.brand = form.brand.data or None
    product.gender = form.gender.data or None
    product.material = form.material.data or None
    product.care_instructions = form.care_instructions.data or None
    product.is_active = form.is_active.data
    product.is_featured = form.is_featured.data
    product.is_trending = form.is_trending.data
    product.is_new_arrival = form.is_new_arrival.data


def apply_age_groups_from_request(product, form_data):
    product.set_age_groups_list(form_data.getlist('age_groups'))


def listing_preview(product):
    """Human-readable list of where this product will appear."""
    places = []
    if not product.is_active:
        places.append('Hidden (draft — not visible on store)')
    else:
        places.append('Shop & category pages')
    if product.is_active and product.is_new_arrival:
        places.append('Homepage → New Arrivals')
    if product.is_active and product.is_featured:
        places.append('Homepage → Parent Favorites')
    if product.is_active and product.is_trending:
        places.append('Trending badge on cards')
    if product.age_groups_list:
        places.append(f'Shop by age filters ({len(product.age_groups_list)} band(s))')
    return places


def get_store_visibility_counts():
    """Counts for admin dashboard."""
    base = Product.query.filter_by(is_active=True)
    return {
        'featured': base.filter_by(is_featured=True).count(),
        'new_arrival': base.filter_by(is_new_arrival=True).count(),
        'trending': base.filter_by(is_trending=True).count(),
        'draft': Product.query.filter_by(is_active=False).count(),
    }
