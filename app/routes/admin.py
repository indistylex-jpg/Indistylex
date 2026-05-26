import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db, limiter
from app.utils.decorators import admin_required
from app.models.user import User
from app.models.product import Product, ProductVariant, ProductImage, Category
from app.models.order import Order, OrderItem, Payment
from app.models.review import Review
from app.models.coupon import Coupon
from app.forms.product_forms import ProductForm, CategoryForm, ProductVariantForm
from app.services.image_service import save_image, delete_image
from app.services.inventory_service import get_low_stock_products

admin_bp = Blueprint('admin', __name__)


# ── Dashboard ─────────────────────────────────────────────────────────
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with key metrics."""
    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total)).filter(
        Order.status.notin_(['cancelled', 'refunded'])
    ).scalar() or 0
    total_customers = User.query.filter_by(role='customer').count()
    total_products = Product.query.filter_by(is_active=True).count()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    low_stock = get_low_stock_products(threshold=5)

    pending_orders = Order.query.filter_by(status='pending').count()

    # --- Analytics data for charts ---

    # Monthly revenue (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_revenue_rows = db.session.query(
        func.strftime('%Y-%m', Order.created_at).label('month'),
        func.sum(Order.total).label('revenue'),
        func.count(Order.id).label('orders')
    ).filter(
        Order.created_at >= six_months_ago,
        Order.status.notin_(['cancelled', 'refunded'])
    ).group_by(func.strftime('%Y-%m', Order.created_at)).order_by('month').all()

    monthly_labels = [r.month for r in monthly_revenue_rows]
    monthly_revenue = [float(r.revenue or 0) for r in monthly_revenue_rows]
    monthly_order_counts = [int(r.orders) for r in monthly_revenue_rows]

    # Payment method breakdown
    payment_rows = db.session.query(
        Order.payment_method, func.count(Order.id)
    ).filter(
        Order.status.notin_(['cancelled', 'refunded'])
    ).group_by(Order.payment_method).all()
    payment_labels = [r[0] or 'cod' for r in payment_rows]
    payment_counts = [r[1] for r in payment_rows]

    # Order status distribution
    status_rows = db.session.query(
        Order.status, func.count(Order.id)
    ).group_by(Order.status).all()
    status_labels = [r[0] or 'pending' for r in status_rows]
    status_counts = [r[1] for r in status_rows]

    # Top 10 selling products by quantity
    top_products_rows = db.session.query(
        OrderItem.product_name,
        func.sum(OrderItem.quantity).label('total_qty')
    ).group_by(OrderItem.product_name).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()
    top_product_names = [r.product_name for r in top_products_rows]
    top_product_qty = [int(r.total_qty) for r in top_products_rows]

    # Top selling products with images and prices for the sidebar list
    top_products = []
    for row in top_products_rows[:5]:
        product = Product.query.filter_by(name=row.product_name).first()
        if product:
            image = product.images[0].image_url if product.images else None
            top_products.append({
                'name': product.name,
                'price': float(product.price),
                'image': image,
                'qty_sold': int(row.total_qty)
            })
        else:
            top_products.append({
                'name': row.product_name,
                'price': 0,
                'image': None,
                'qty_sold': int(row.total_qty)
            })

    # If no order data, show top products from catalog
    if not top_products:
        for p in Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(5).all():
            image = p.images[0].image_url if p.images else None
            top_products.append({
                'name': p.name,
                'price': float(p.price),
                'image': image,
                'qty_sold': 0
            })

    # Category product counts for donut chart
    category_rows = db.session.query(
        Category.name,
        func.count(Product.id).label('count')
    ).join(Product, Product.category_id == Category.id).filter(
        Product.is_active == True
    ).group_by(Category.name).order_by(func.count(Product.id).desc()).limit(5).all()
    category_names = [r.name for r in category_rows]
    category_counts = [int(r.count) for r in category_rows]

    # Date range for header
    today = datetime.utcnow()
    week_ago = today - timedelta(days=6)
    today_range = f"{week_ago.strftime('%b %d')} - {today.strftime('%b %d, %Y')}"

    return render_template('admin/dashboard.html',
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           total_customers=total_customers,
                           total_products=total_products,
                           recent_orders=recent_orders,
                           low_stock=low_stock,
                           pending_orders=pending_orders,
                           monthly_labels=json.dumps(monthly_labels),
                           monthly_revenue=json.dumps(monthly_revenue),
                           monthly_order_counts=json.dumps(monthly_order_counts),
                           payment_labels=json.dumps(payment_labels),
                           payment_counts=json.dumps(payment_counts),
                           status_labels=json.dumps(status_labels),
                           status_counts=json.dumps(status_counts),
                           top_product_names=json.dumps(top_product_names),
                           top_product_qty=json.dumps(top_product_qty),
                           top_products=top_products,
                           category_names=json.dumps(category_names),
                           category_counts=json.dumps(category_counts),
                           today_range=today_range)


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
        db.session.commit()

        # Handle image uploads
        images = request.files.getlist('images')
        for i, img_file in enumerate(images):
            if img_file and img_file.filename:
                url = save_image(img_file, subfolder='products')
                if url:
                    img = ProductImage(
                        product_id=product.id,
                        image_url=url,
                        is_primary=(i == 0),
                        sort_order=i,
                    )
                    db.session.add(img)

        db.session.commit()
        flash(f'Product "{product.name}" created. Add variants now.', 'success')
        return redirect(url_for('admin.edit_product', product_id=product.id))

    return render_template('admin/product_form.html', form=form, title='Add Product')


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
        product.age_group = form.age_group.data or None

        # Handle new image uploads
        images = request.files.getlist('images')
        existing_count = product.images.count()
        for i, img_file in enumerate(images):
            if img_file and img_file.filename:
                url = save_image(img_file, subfolder='products')
                if url:
                    img = ProductImage(
                        product_id=product.id,
                        image_url=url,
                        is_primary=(existing_count == 0 and i == 0),
                        sort_order=existing_count + i,
                    )
                    db.session.add(img)

        db.session.commit()
        flash(f'Product "{product.name}" updated.', 'success')
        return redirect(url_for('admin.products'))

    variants = product.variants.all()
    images = product.images.order_by(ProductImage.sort_order).all()

    return render_template('admin/product_form.html', form=form, title='Edit Product',
                           product=product, variants=variants, images=images)


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
    name = product.name
    # Delete associated images from disk
    for img in product.images.all():
        delete_image(img.image_url)
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{name}" deleted.', 'info')
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
    if new_status == 'shipped':
        order.shipped_at = datetime.utcnow()
    elif new_status == 'delivered':
        order.delivered_at = datetime.utcnow()
    elif new_status == 'cancelled' and order.status not in ['cancelled', 'refunded']:
        # Restore stock
        from app.services.inventory_service import restore_stock
        for item in order.items.all():
            restore_stock(item.variant_id, item.quantity)

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
