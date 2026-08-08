import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app.extensions import db, limiter
from app.utils.decorators import admin_required
from app.models.user import User
from app.models.product import Product, ProductVariant, ProductImage, Category
from app.models.order import Order, OrderItem, Payment
from app.models.review import Review
from app.models.coupon import Coupon
from app.forms.product_forms import ProductForm, CategoryForm, ProductVariantForm
from app.utils.product_ages import AGE_GROUP_SECTIONS
from app.services.image_service import save_image, delete_image
from app.services.inventory_service import (
    get_low_stock_products, record_b2b_sale, cancel_b2b_sale,
)
from app.models.b2b_sale import B2BSale, B2BSaleItem
from app.models.expense import Expense
from app.models.wishlist import Wishlist
from app.models.cart import CartItem
from app.forms.expense_forms import ExpenseForm
from app.services.expense_service import (
    record_expense, delete_expense, get_expense_totals, get_expense_by_category,
    auto_record_order_shipping, auto_record_order_refund,
)
from app.services.dashboard_analytics_service import get_dashboard_analytics

admin_bp = Blueprint('admin', __name__)


def _save_product_images(product):
    """Attach uploaded images to a product. Returns (saved_count, failed_count)."""
    images = request.files.getlist('images')
    existing_count = product.images.count()
    has_primary = product.images.filter_by(is_primary=True).count() > 0
    saved = 0
    failed = 0

    for i, img_file in enumerate(images):
        if not img_file or not img_file.filename:
            continue
        url = save_image(img_file, subfolder='products')
        if not url:
            failed += 1
            continue
        img = ProductImage(
            product_id=product.id,
            image_url=url,
            is_primary=(not has_primary and saved == 0),
            sort_order=existing_count + saved,
        )
        db.session.add(img)
        saved += 1

    return saved, failed


def _save_variants_from_request(product):
    """Create variants from variant_*[] form fields. Returns (added_count, skipped_skus)."""
    sizes = request.form.getlist('variant_size[]')
    colors = request.form.getlist('variant_color[]')
    skus = request.form.getlist('variant_sku[]')
    stocks = request.form.getlist('variant_stock[]')

    added = 0
    skipped = []

    for size, color, sku, stock in zip(sizes, colors, skus, stocks):
        size = (size or '').strip()
        color = (color or '').strip()
        sku = (sku or '').strip()
        if not all([size, color, sku]):
            continue

        if ProductVariant.query.filter_by(sku=sku).first():
            skipped.append(sku)
            continue

        try:
            stock_qty = int(stock or 0)
        except (TypeError, ValueError):
            stock_qty = 0

        variant = ProductVariant(
            product_id=product.id,
            size=size,
            color=color,
            sku=sku,
            stock_quantity=max(0, stock_qty),
        )
        db.session.add(variant)
        added += 1

    return added, skipped


def _apply_product_age_groups(product):
    product.set_age_groups_list(request.form.getlist('age_groups'))


def _delete_product_record(product):
    """Delete a product and clean up related records."""
    name = product.name
    variant_ids = [v.id for v in product.variants.all()]

    if variant_ids:
        b2b_refs = B2BSaleItem.query.filter(B2BSaleItem.variant_id.in_(variant_ids)).count()
        if b2b_refs:
            raise ValueError(f'"{name}" has B2B sale history and cannot be deleted.')

        CartItem.query.filter(CartItem.variant_id.in_(variant_ids)).delete(synchronize_session=False)
        OrderItem.query.filter(OrderItem.variant_id.in_(variant_ids)).update(
            {OrderItem.variant_id: None}, synchronize_session=False
        )

    Review.query.filter_by(product_id=product.id).delete(synchronize_session=False)
    Wishlist.query.filter_by(product_id=product.id).delete(synchronize_session=False)

    for img in product.images.all():
        delete_image(img.image_url)

    db.session.delete(product)
    return name


# ── Dashboard ─────────────────────────────────────────────────────────
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with key metrics and charts."""
    analytics = get_dashboard_analytics()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    low_stock = get_low_stock_products(threshold=5)

    today = datetime.utcnow()
    month_start = today.replace(day=1).date()
    total_expenses, expense_count = get_expense_totals(start_date=month_start)
    expense_by_category = get_expense_by_category(start_date=month_start)
    net_profit = analytics['total_revenue'] - float(total_expenses)

    top_products = []
    for i, name in enumerate(analytics['top_product_names'][:5]):
        qty = analytics['top_product_qty'][i] if i < len(analytics['top_product_qty']) else 0
        product = Product.query.filter_by(name=name).first()
        if product:
            img = product.images.first()
            top_products.append({
                'name': product.name,
                'price': float(product.price),
                'image': img.image_url if img else None,
                'qty_sold': qty,
            })
        else:
            top_products.append({'name': name, 'price': 0, 'image': None, 'qty_sold': qty})

    if not top_products:
        for p in Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(5).all():
            img = p.images.first()
            top_products.append({
                'name': p.name,
                'price': float(p.price),
                'image': img.image_url if img else None,
                'qty_sold': 0,
            })

    chart_keys = (
        'monthly_labels', 'monthly_revenue', 'monthly_order_counts',
        'status_labels', 'status_counts', 'payment_labels', 'payment_counts',
        'top_product_names', 'top_product_qty', 'category_names', 'category_counts',
        'gender_labels', 'gender_counts', 'gender_colors',
    )
    chart_json = {k: json.dumps(analytics[k]) for k in chart_keys}
    template_data = {k: v for k, v in analytics.items() if k not in chart_keys}

    return render_template(
        'admin/dashboard.html',
        recent_orders=recent_orders,
        low_stock=low_stock,
        top_products=top_products,
        total_expenses=total_expenses,
        expense_count=expense_count,
        expense_by_category=expense_by_category,
        net_profit=net_profit,
        **template_data,
        **chart_json,
    )


# ── Categories ────────────────────────────────────────────────────────
@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    cats = Category.query.order_by(Category.sort_order, Category.name).all()
    return render_template('admin/categories.html', categories=cats)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    form = CategoryForm()
    form.parent_id.choices = [(0, 'None (Top Level)')] + [
        (c.id, c.name) for c in Category.query.filter_by(parent_id=None).order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        from slugify import slugify
        cat = Category(
            name=form.name.data.strip(),
            slug=slugify(form.name.data.strip()),
            description=form.description.data,
            parent_id=form.parent_id.data if form.parent_id.data != 0 else None,
            is_active=form.is_active.data,
            sort_order=form.sort_order.data or 0,
        )

        if form.image.data:
            cat.image_url = save_image(form.image.data, subfolder='categories')

        db.session.add(cat)
        db.session.commit()
        flash(f'Category "{cat.name}" created.', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', form=form, title='Add Category')


@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(category_id):
    cat = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=cat)
    form.parent_id.choices = [(0, 'None (Top Level)')] + [
        (c.id, c.name) for c in Category.query.filter(
            Category.parent_id == None, Category.id != category_id
        ).order_by(Category.name).all()
    ]

    if request.method == 'GET':
        form.parent_id.data = cat.parent_id or 0

    if form.validate_on_submit():
        cat.name = form.name.data.strip()
        cat.description = form.description.data
        cat.parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        cat.is_active = form.is_active.data
        cat.sort_order = form.sort_order.data or 0

        if form.image.data:
            if cat.image_url:
                delete_image(cat.image_url)
            cat.image_url = save_image(form.image.data, subfolder='categories')

        db.session.commit()
        flash(f'Category "{cat.name}" updated.', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', form=form, title='Edit Category', category=cat)


@admin_bp.route('/categories/toggle/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def toggle_category(category_id):
    """Toggle category active status — enables/disables on storefront."""
    cat = Category.query.get_or_404(category_id)
    cat.is_active = not cat.is_active

    # Also toggle all child categories
    for child in cat.children.all():
        child.is_active = cat.is_active

    db.session.commit()

    status = 'enabled' if cat.is_active else 'disabled'
    flash(f'Category "{cat.name}" has been {status}.', 'success')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': status, 'is_active': cat.is_active})
    return redirect(url_for('admin.categories'))


# ── Products ──────────────────────────────────────────────────────────
@admin_bp.route('/products')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ADMIN_ITEMS_PER_PAGE', 20)

    query = Product.query
    search = request.args.get('q', '').strip()
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template('admin/products.html', products=products, search=search)


@admin_bp.route('/products/bulk-delete', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_delete_products():
    """Delete multiple products at once."""
    if request.method == 'GET':
        return redirect(url_for('admin.products'))

    raw_ids = request.form.getlist('product_ids')
    if not raw_ids:
        flash('Select at least one product to delete.', 'warning')
        return redirect(url_for('admin.products'))

    product_ids = []
    for raw_id in raw_ids:
        try:
            product_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue

    if not product_ids:
        flash('No valid products selected.', 'warning')
        return redirect(url_for('admin.products'))

    products = Product.query.filter(Product.id.in_(product_ids)).all()
    if not products:
        flash('Selected products were not found.', 'warning')
        return redirect(url_for('admin.products'))

    deleted_names = []
    failed_messages = []
    for product in products:
        try:
            deleted_names.append(_delete_product_record(product))
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            failed_messages.append(str(exc))

    if deleted_names:
        if len(deleted_names) == 1:
            flash(f'Product "{deleted_names[0]}" deleted.', 'success')
        else:
            flash(f'{len(deleted_names)} products deleted.', 'success')
    for msg in failed_messages:
        flash(msg, 'danger')
    if not deleted_names and not failed_messages:
        flash('No products were deleted.', 'warning')

    return redirect(url_for('admin.products'))


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    form.category_id.choices = [
        (c.id, f'{c.parent.name} > {c.name}' if c.parent else c.name)
        for c in Category.query.order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        from slugify import slugify
        product = Product(
            name=form.name.data.strip(),
            slug=slugify(form.name.data.strip()),
            short_description=form.short_description.data,
            description=form.description.data,
            price=form.price.data,
            compare_at_price=form.compare_at_price.data,
            category_id=form.category_id.data,
            brand=form.brand.data,
            gender=form.gender.data or None,
            material=form.material.data,
            care_instructions=form.care_instructions.data,
            is_active=form.is_active.data,
            is_featured=form.is_featured.data,
            is_trending=form.is_trending.data,
        )
        db.session.add(product)
        db.session.flush()
        _apply_product_age_groups(product)

        image_count, image_failed = _save_product_images(product)
        variant_count, skipped_skus = _save_variants_from_request(product)
        db.session.commit()

        parts = [f'Product "{product.name}" created']
        if image_count:
            parts.append(f'{image_count} image(s)')
        if variant_count:
            parts.append(f'{variant_count} variant(s)')
        flash('. '.join(parts) + '.', 'success')
        if image_failed:
            flash(f'{image_failed} image(s) could not be saved — use JPG, PNG or WebP under 5 MB.', 'warning')
        for sku in skipped_skus:
            flash(f'SKU "{sku}" already exists — variant skipped.', 'warning')
        return redirect(url_for('admin.products'))

    return render_template(
        'admin/product_form.html',
        form=form,
        title='Add Product',
        age_group_sections=AGE_GROUP_SECTIONS,
        selected_age_groups=[],
    )


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [
        (c.id, f'{c.parent.name} > {c.name}' if c.parent else c.name)
        for c in Category.query.order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        form.populate_obj(product)
        product.gender = form.gender.data or None
        _apply_product_age_groups(product)

        image_count, image_failed = _save_product_images(product)
        variant_count, skipped_skus = _save_variants_from_request(product)
        db.session.commit()

        parts = [f'Product "{product.name}" updated']
        if image_count:
            parts.append(f'{image_count} new image(s)')
        if variant_count:
            parts.append(f'{variant_count} new variant(s)')
        flash('. '.join(parts) + '.', 'success')
        if image_failed:
            flash(f'{image_failed} image(s) could not be saved — use JPG, PNG or WebP under 5 MB.', 'warning')
        for sku in skipped_skus:
            flash(f'SKU "{sku}" already exists — variant skipped.', 'warning')
        return redirect(url_for('admin.products'))

    variants = product.variants.all()
    images = product.images.order_by(ProductImage.sort_order).all()

    return render_template(
        'admin/product_form.html',
        form=form,
        title='Edit Product',
        product=product,
        variants=variants,
        images=images,
        age_group_sections=AGE_GROUP_SECTIONS,
        selected_age_groups=product.age_groups_list,
    )


@admin_bp.route('/products/<int:product_id>/variants/add', methods=['POST'])
@login_required
@admin_required
def add_variant(product_id):
    product = Product.query.get_or_404(product_id)

    size = request.form.get('size', '').strip()
    color = request.form.get('color', '').strip()
    sku = request.form.get('sku', '').strip()
    stock = request.form.get('stock_quantity', 0, type=int)

    if not all([size, color, sku]):
        flash('Size, color, and SKU are required.', 'danger')
        return redirect(url_for('admin.edit_product', product_id=product_id))

    existing = ProductVariant.query.filter_by(sku=sku).first()
    if existing:
        flash('SKU already exists.', 'danger')
        return redirect(url_for('admin.edit_product', product_id=product_id))

    variant = ProductVariant(
        product_id=product_id,
        size=size,
        color=color,
        sku=sku,
        stock_quantity=stock,
    )
    db.session.add(variant)
    db.session.commit()
    flash(f'Variant {sku} added.', 'success')
    return redirect(url_for('admin.edit_product', product_id=product_id))


@admin_bp.route('/variants/<int:variant_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_variant(variant_id):
    variant = ProductVariant.query.get_or_404(variant_id)
    product_id = variant.product_id
    db.session.delete(variant)
    db.session.commit()
    flash('Variant deleted.', 'info')
    return redirect(url_for('admin.edit_product', product_id=product_id))


@admin_bp.route('/products/<int:product_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product_image(product_id, image_id):
    img = ProductImage.query.filter_by(id=image_id, product_id=product_id).first_or_404()
    delete_image(img.image_url)
    db.session.delete(img)
    db.session.commit()
    flash('Image deleted.', 'info')
    return redirect(url_for('admin.edit_product', product_id=product_id))


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        name = _delete_product_record(product)
        db.session.commit()
        flash(f'Product "{name}" deleted.', 'success')
    except Exception as exc:
        db.session.rollback()
        flash(str(exc), 'danger')
    return redirect(url_for('admin.products'))


# ── Orders ────────────────────────────────────────────────────────────
@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ADMIN_ITEMS_PER_PAGE', 20)

    status_filter = request.args.get('status')
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template('admin/orders.html', orders=orders, current_status=status_filter)


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    shipping_addr = json.loads(order.shipping_address) if order.shipping_address else {}
    return render_template('admin/order_detail.html', order=order, shipping_addr=shipping_addr)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']

    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order_id))

    from datetime import datetime
    old_status = order.status
    if new_status == 'shipped':
        order.shipped_at = datetime.utcnow()
        auto_record_order_shipping(order, created_by_id=current_user.id)
    elif new_status == 'delivered':
        order.delivered_at = datetime.utcnow()
    elif new_status == 'cancelled' and old_status not in ['cancelled', 'refunded']:
        # Restore stock
        from app.services.inventory_service import restore_stock
        for item in order.items.all():
            restore_stock(item.variant_id, item.quantity)
    elif new_status == 'refunded' and old_status != 'refunded':
        auto_record_order_refund(order, created_by_id=current_user.id)

    order.status = new_status
    db.session.commit()

    from app.services.email_service import send_order_status_update
    send_order_status_update(order)

    flash(f'Order {order.order_number} status updated to {new_status}.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))


# ── Customers ─────────────────────────────────────────────────────────
@admin_bp.route('/customers')
@login_required
@admin_required
def customers():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ADMIN_ITEMS_PER_PAGE', 20)

    customers = User.query.filter_by(role='customer').order_by(
        User.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/customers.html', customers=customers)


# ── Coupons ───────────────────────────────────────────────────────────
@admin_bp.route('/coupons')
@login_required
@admin_required
def coupons():
    all_coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template('admin/coupons.html', coupons=all_coupons)


@admin_bp.route('/coupons/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_coupon():
    if request.method == 'POST':
        from datetime import datetime
        discount_type = request.form['discount_type']
        if discount_type not in ('percentage', 'fixed'):
            flash('Invalid discount type.', 'danger')
            return redirect(url_for('admin.add_coupon'))
        coupon = Coupon(
            code=request.form['code'].strip().upper(),
            discount_type=discount_type,
            discount_value=float(request.form['discount_value']),
            min_order_amount=float(request.form.get('min_order_amount', 0)),
            max_discount_amount=float(request.form['max_discount_amount']) if request.form.get('max_discount_amount') else None,
            max_uses=int(request.form['max_uses']) if request.form.get('max_uses') else None,
            valid_from=datetime.strptime(request.form['valid_from'], '%Y-%m-%d'),
            valid_until=datetime.strptime(request.form['valid_until'], '%Y-%m-%d'),
            is_active=bool(request.form.get('is_active')),
        )
        db.session.add(coupon)
        db.session.commit()
        flash(f'Coupon "{coupon.code}" created.', 'success')
        return redirect(url_for('admin.coupons'))

    return render_template('admin/coupon_form.html', title='Add Coupon')


@admin_bp.route('/coupons/<int:coupon_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    if request.method == 'POST':
        from datetime import datetime
        discount_type = request.form['discount_type']
        if discount_type not in ('percentage', 'fixed'):
            flash('Invalid discount type.', 'danger')
            return redirect(url_for('admin.edit_coupon', coupon_id=coupon_id))
        coupon.code = request.form['code'].strip().upper()
        coupon.discount_type = discount_type
        coupon.discount_value = float(request.form['discount_value'])
        coupon.min_order_amount = float(request.form.get('min_order_amount', 0))
        coupon.max_discount_amount = float(request.form['max_discount_amount']) if request.form.get('max_discount_amount') else None
        coupon.max_uses = int(request.form['max_uses']) if request.form.get('max_uses') else None
        coupon.valid_from = datetime.strptime(request.form['valid_from'], '%Y-%m-%d')
        coupon.valid_until = datetime.strptime(request.form['valid_until'], '%Y-%m-%d')
        coupon.is_active = bool(request.form.get('is_active'))
        db.session.commit()
        flash(f'Coupon "{coupon.code}" updated.', 'success')
        return redirect(url_for('admin.coupons'))

    return render_template('admin/coupon_form.html', title='Edit Coupon', coupon=coupon)


@admin_bp.route('/coupons/<int:coupon_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    db.session.delete(coupon)
    db.session.commit()
    flash(f'Coupon "{coupon.code}" deleted.', 'success')
    return redirect(url_for('admin.coupons'))


# ── Reviews ───────────────────────────────────────────────────────────
@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/reviews.html', reviews=reviews)


@admin_bp.route('/reviews/<int:review_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    db.session.commit()
    flash('Review approved.', 'success')
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/reviews/<int:review_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review rejected and removed.', 'info')
    return redirect(url_for('admin.reviews'))


# ── Inventory ─────────────────────────────────────────────────────────
@admin_bp.route('/inventory')
@login_required
@admin_required
def inventory():
    """Full inventory view with filtering and stock management."""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ADMIN_ITEMS_PER_PAGE', 20)

    # Filters
    search = request.args.get('search', '').strip()
    stock_filter = request.args.get('stock', '')  # all, low, out
    category_id = request.args.get('category', '', type=str)

    query = ProductVariant.query.join(Product).filter(Product.is_active == True)

    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                ProductVariant.sku.ilike(f'%{search}%')
            )
        )

    if stock_filter == 'low':
        query = query.filter(ProductVariant.stock_quantity <= 10, ProductVariant.stock_quantity > 0)
    elif stock_filter == 'out':
        query = query.filter(ProductVariant.stock_quantity == 0)

    if category_id:
        query = query.filter(Product.category_id == int(category_id))

    variants = query.order_by(Product.name, ProductVariant.size).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Summary stats
    total_variants = ProductVariant.query.join(Product).filter(Product.is_active == True).count()
    total_stock = db.session.query(func.sum(ProductVariant.stock_quantity)).join(Product).filter(
        Product.is_active == True
    ).scalar() or 0
    low_stock_count = ProductVariant.query.join(Product).filter(
        Product.is_active == True,
        ProductVariant.stock_quantity <= 10,
        ProductVariant.stock_quantity > 0
    ).count()
    out_of_stock_count = ProductVariant.query.join(Product).filter(
        Product.is_active == True,
        ProductVariant.stock_quantity == 0
    ).count()

    categories = Category.query.order_by(Category.name).all()

    return render_template('admin/inventory.html',
                           variants=variants,
                           total_variants=total_variants,
                           total_stock=total_stock,
                           low_stock_count=low_stock_count,
                           out_of_stock_count=out_of_stock_count,
                           categories=categories,
                           search=search,
                           stock_filter=stock_filter,
                           category_id=category_id)


@admin_bp.route('/inventory/<int:variant_id>/update-stock', methods=['POST'])
@login_required
@admin_required
def update_stock(variant_id):
    """Update stock quantity for a variant."""
    variant = ProductVariant.query.get_or_404(variant_id)
    new_stock = request.form.get('stock_quantity', type=int)

    if new_stock is None or new_stock < 0:
        flash('Invalid stock quantity.', 'danger')
        return redirect(url_for('admin.inventory'))

    variant.stock_quantity = new_stock
    db.session.commit()
    flash(f'Stock updated for {variant.product.name} ({variant.size}/{variant.color}).', 'success')
    return redirect(request.referrer or url_for('admin.inventory'))


@admin_bp.route('/inventory/bulk-update', methods=['POST'])
@login_required
@admin_required
def bulk_update_stock():
    """Bulk update stock from form."""
    updates = 0
    for key, value in request.form.items():
        if key.startswith('stock_'):
            variant_id = int(key.replace('stock_', ''))
            new_qty = int(value)
            variant = ProductVariant.query.get(variant_id)
            if variant and variant.stock_quantity != new_qty and new_qty >= 0:
                variant.stock_quantity = new_qty
                updates += 1
    db.session.commit()
    flash(f'{updates} stock quantities updated.', 'success')
    return redirect(url_for('admin.inventory'))


# ── B2B Shop Sales ────────────────────────────────────────────────────
@admin_bp.route('/b2b-sales')
@login_required
@admin_required
def b2b_sales():
    """List B2B shop sales history."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()

    query = B2BSale.query
    if search:
        query = query.filter(
            db.or_(
                B2BSale.shop_name.ilike(f'%{search}%'),
                B2BSale.sale_number.ilike(f'%{search}%'),
            )
        )

    sales = query.order_by(B2BSale.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    recent_shops = db.session.query(B2BSale.shop_name).filter(
        B2BSale.is_cancelled == False
    ).distinct().order_by(B2BSale.shop_name).limit(20).all()
    recent_shops = [s[0] for s in recent_shops]

    return render_template('admin/b2b_sales.html',
                           sales=sales, search=search, recent_shops=recent_shops)


@admin_bp.route('/b2b-sales/record', methods=['GET', 'POST'])
@login_required
@admin_required
def record_b2b_sale_view():
    """Record a B2B shop sale and deduct website stock."""
    if request.method == 'POST':
        shop_name = request.form.get('shop_name', '').strip()
        shop_phone = request.form.get('shop_phone', '').strip()
        shop_city = request.form.get('shop_city', '').strip()
        payment_terms = request.form.get('payment_terms', 'cod')
        notes = request.form.get('notes', '').strip()
        extra_discount = request.form.get('extra_discount', '0').strip()
        discount_percent = request.form.get('discount_percent', '0').strip()
        discount_reason = request.form.get('discount_reason', '').strip()

        items = []
        skus = request.form.getlist('sku[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('unit_price[]')

        for sku, qty, price in zip(skus, quantities, prices):
            sku = sku.strip()
            if not sku:
                continue
            variant = ProductVariant.query.filter_by(sku=sku).first()
            if not variant:
                flash(f'SKU not found: {sku}', 'danger')
                return redirect(url_for('admin.record_b2b_sale_view'))

            items.append({
                'variant_id': variant.id,
                'quantity': qty,
                'unit_price': price if price else None,
            })

        sale, error = record_b2b_sale(
            shop_name=shop_name,
            items=items,
            created_by_id=current_user.id,
            shop_phone=shop_phone,
            shop_city=shop_city,
            payment_terms=payment_terms,
            notes=notes,
            extra_discount=extra_discount,
            discount_percent=discount_percent,
            discount_reason=discount_reason,
        )

        if error:
            flash(error, 'danger')
            return redirect(url_for('admin.record_b2b_sale_view'))

        flash(
            f'B2B sale {sale.sale_number} recorded. '
            f'{sale.item_count} items sold to {sale.shop_name}. Stock updated.',
            'success',
        )
        return redirect(url_for('admin.b2b_sales'))

    recent_shops = db.session.query(B2BSale.shop_name).filter(
        B2BSale.is_cancelled == False
    ).distinct().order_by(B2BSale.shop_name).limit(15).all()
    recent_shops = [s[0] for s in recent_shops]

    in_stock_variants = ProductVariant.query.join(Product).filter(
        Product.is_active == True,
        ProductVariant.is_active == True,
        ProductVariant.stock_quantity > 0,
    ).order_by(Product.name, ProductVariant.size).limit(200).all()

    return render_template('admin/record_b2b_sale.html',
                           recent_shops=recent_shops,
                           variants=in_stock_variants)


@admin_bp.route('/b2b-sales/<int:sale_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_b2b_sale_view(sale_id):
    """Cancel B2B sale and restore stock."""
    ok, error = cancel_b2b_sale(sale_id)
    if ok:
        flash('B2B sale cancelled. Stock restored.', 'success')
    else:
        flash(error, 'danger')
    return redirect(url_for('admin.b2b_sales'))


@admin_bp.route('/api/variant-by-sku/<sku>')
@login_required
@admin_required
def variant_by_sku(sku):
    """Lookup variant by SKU for B2B sale form."""
    variant = ProductVariant.query.filter_by(sku=sku.strip()).first()
    if not variant or not variant.is_active:
        return jsonify({'error': 'SKU not found'}), 404

    return jsonify({
        'id': variant.id,
        'sku': variant.sku,
        'product_name': variant.product.name,
        'size': variant.size,
        'color': variant.color,
        'stock': variant.stock_quantity,
        'retail_price': float(variant.product.price),
        'suggested_wholesale': round(float(variant.product.price) * 0.7, 2),
    })


# ── Expenses ──────────────────────────────────────────────────────────
@admin_bp.route('/expenses')
@login_required
@admin_required
def expenses():
    """List all expenses with filters and monthly totals."""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '').strip()
    month = request.args.get('month', '')

    query = Expense.query
    if category:
        query = query.filter_by(category=category)
    if month:
        try:
            y, m = month.split('-')
            query = query.filter(
                extract('year', Expense.expense_date) == int(y),
                extract('month', Expense.expense_date) == int(m),
            )
        except ValueError:
            pass

    pagination = query.order_by(Expense.expense_date.desc(), Expense.id.desc()).paginate(
        page=page, per_page=25, error_out=False
    )

    today = datetime.utcnow()
    month_start = today.replace(day=1).date()
    total_all, count_all = get_expense_totals()
    total_month, count_month = get_expense_totals(start_date=month_start)
    by_category = get_expense_by_category(start_date=month_start)

    from app.models.expense import EXPENSE_CATEGORIES
    return render_template(
        'admin/expenses.html',
        expenses=pagination,
        category_filter=category,
        month_filter=month,
        total_all=total_all,
        count_all=count_all,
        total_month=total_month,
        count_month=count_month,
        by_category=by_category,
        categories=EXPENSE_CATEGORIES,
    )


@admin_bp.route('/expenses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_expense():
    """Add a manual business expense."""
    form = ExpenseForm()
    if form.validate_on_submit():
        expense, error = record_expense(
            amount=form.amount.data,
            category=form.category.data,
            description=form.description.data,
            created_by_id=current_user.id,
            payment_method=form.payment_method.data,
            reference=form.reference.data,
            notes=form.notes.data,
            expense_date=form.expense_date.data,
        )
        if error:
            flash(error, 'danger')
        else:
            flash(f'Expense recorded: ₹{expense.amount:,.0f} — {expense.description}', 'success')
            return redirect(url_for('admin.expenses'))
    elif request.method == 'GET':
        form.expense_date.data = datetime.utcnow().date()

    return render_template('admin/expense_form.html', form=form, title='Add Expense')


@admin_bp.route('/expenses/<int:expense_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_expense_view(expense_id):
    ok, error = delete_expense(expense_id)
    if ok:
        flash('Expense deleted.', 'success')
    else:
        flash(error, 'danger')
    return redirect(url_for('admin.expenses'))
