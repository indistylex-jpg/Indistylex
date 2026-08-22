import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_file
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
    get_low_stock_products, record_b2b_sale, cancel_b2b_sale, build_inventory_query,
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
from app.services.payment_management_service import (
    backfill_missing_payments,
    get_payment_summary,
    get_payments_query,
    mark_payment_collected,
    COLLECTION_CHANNELS,
)
from app.models.order import PAYMENT_CHANNELS, PAYMENT_STATUS_LABELS
from app.services.product_catalog_service import (
    AGE_PRESETS,
    STORE_VISIBILITY_OPTIONS,
    apply_age_groups_from_request,
    apply_product_fields_from_form,
    category_metadata_for_js,
    get_category_choices_flat,
    get_category_groups,
    get_store_visibility_counts,
    listing_preview,
    validate_product_submission,
    product_form_draft_context,
)

admin_bp = Blueprint('admin', __name__)


def _set_primary_image(product, image_id):
    """Mark one product image as the main photo shown on the storefront."""
    img = ProductImage.query.filter_by(id=image_id, product_id=product.id).first()
    if not img:
        return False
    ProductImage.query.filter_by(product_id=product.id).update(
        {ProductImage.is_primary: False}, synchronize_session=False
    )
    img.is_primary = True
    return True


def _ensure_primary_image(product):
    """Ensure exactly one primary image when product has photos."""
    if not product.images.count():
        return
    primary = product.images.filter_by(is_primary=True).first()
    if primary:
        return
    first = product.images.order_by(ProductImage.sort_order).first()
    if first:
        first.is_primary = True


def _save_product_images(product):
    """Attach uploaded images to a product. Returns (saved_count, failed_count)."""
    upload_files = request.files.getlist('images')
    # Backward compat if older forms still post lifestyle_images separately
    upload_files.extend(request.files.getlist('lifestyle_images'))
    existing_count = product.images.count()
    saved = 0
    failed = 0
    new_image_ids = []

    for img_file in upload_files:
        if not img_file or not img_file.filename:
            continue
        url = save_image(img_file, subfolder='products')
        if not url:
            failed += 1
            continue
        img = ProductImage(
            product_id=product.id,
            image_url=url,
            is_primary=False,
            sort_order=existing_count + saved,
        )
        db.session.add(img)
        db.session.flush()
        new_image_ids.append(img.id)
        saved += 1

    primary_id = request.form.get('primary_image_id', type=int)
    primary_new_index = request.form.get('primary_new_upload_index', type=int)

    if primary_id and _set_primary_image(product, primary_id):
        pass
    elif (
        primary_new_index is not None
        and new_image_ids
        and 0 <= primary_new_index < len(new_image_ids)
    ):
        _set_primary_image(product, new_image_ids[primary_new_index])
    else:
        _ensure_primary_image(product)

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
    apply_age_groups_from_request(product, request.form)


def _flash_product_form_errors(form, validation_errors=None):
    """Flash WTForms and custom validation messages (deduplicated)."""
    seen = set()
    for msg in validation_errors or []:
        if msg and msg not in seen:
            flash(msg, 'danger')
            seen.add(msg)
    for field_name, field_errors in form.errors.items():
        try:
            label = form[field_name].label.text
        except KeyError:
            label = field_name.replace('_', ' ').title()
        for err in field_errors:
            msg = f'{label}: {err}'
            if msg not in seen:
                flash(msg, 'danger')
                seen.add(msg)


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
    gross_profit_month = analytics['month_gross_profit']
    net_profit = gross_profit_month - float(total_expenses)
    store_visibility = get_store_visibility_counts()
    payment_summary = get_payment_summary()
    backfill_missing_payments()

    top_products = []
    for i, name in enumerate(analytics['top_product_names'][:5]):
        qty = analytics['top_product_qty'][i] if i < len(analytics['top_product_qty']) else 0
        product = Product.query.filter_by(name=name).first()
        if product:
            img = product.images.first()
            unit_profit = product.unit_profit
            top_products.append({
                'name': product.name,
                'price': float(product.price),
                'cost_price': float(product.cost_price) if product.cost_price is not None else None,
                'unit_profit': float(unit_profit) if unit_profit is not None else None,
                'image': img.image_url if img else None,
                'qty_sold': qty,
            })
        else:
            top_products.append({
                'name': name,
                'price': 0,
                'unit_profit': None,
                'image': None,
                'qty_sold': qty,
            })

    if not top_products:
        for p in Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(5).all():
            img = p.images.first()
            unit_profit = p.unit_profit
            top_products.append({
                'name': p.name,
                'price': float(p.price),
                'unit_profit': float(unit_profit) if unit_profit is not None else None,
                'image': img.image_url if img else None,
                'qty_sold': 0,
            })

    chart_keys = (
        'monthly_labels', 'monthly_revenue', 'monthly_gross_profit', 'monthly_order_counts',
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
        gross_profit_month=gross_profit_month,
        net_profit=net_profit,
        store_visibility=store_visibility,
        payment_collected=payment_summary['total_collected'],
        payment_pending_cod=payment_summary['pending_cod'],
        payment_by_channel=payment_summary['by_channel'],
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
    visibility = request.args.get('visibility', '').strip()

    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    if visibility == 'featured':
        query = query.filter_by(is_featured=True, is_active=True)
    elif visibility == 'new':
        query = query.filter_by(is_new_arrival=True, is_active=True)
    elif visibility == 'trending':
        query = query.filter_by(is_trending=True, is_active=True)
    elif visibility == 'draft':
        query = query.filter_by(is_active=False)

    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template(
        'admin/products.html',
        products=products,
        search=search,
        visibility=visibility,
    )


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


@admin_bp.route('/products/analyze-image', methods=['POST'])
@login_required
@admin_required
@limiter.limit('12 per minute')
def analyze_product_image():
    """Analyze a product photo with AI and return suggested form fields."""
    from app.services.product_vision_service import analyze_product_image as run_analysis
    from app.services.product_vision_service import product_ai_configured

    if not product_ai_configured():
        return jsonify({
            'success': False,
            'message': 'AI autofill is not configured. Add GEMINI_API_KEY to your server .env file.',
        }), 503

    image = request.files.get('image')
    if not image or not image.filename:
        return jsonify({'success': False, 'message': 'Please choose a product photo.'}), 400

    try:
        data = run_analysis(
            image.read(),
            image.content_type or image.mimetype,
            get_category_groups(),
        )
        return jsonify({'success': True, 'data': data})
    except ValueError as exc:
        return jsonify({'success': False, 'message': str(exc)}), 400
    except Exception:
        current_app.logger.exception('Product image AI analysis failed')
        return jsonify({
            'success': False,
            'message': 'Could not analyze this photo. Try a clearer image or fill the form manually.',
        }), 500


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    form.category_id.choices = get_category_choices_flat()
    category_groups = get_category_groups()
    validation_errors = []
    draft = product_form_draft_context(
        request.form if request.method == 'POST' else None,
    )

    if request.method == 'POST':
        if form.validate_on_submit():
            validation_errors = validate_product_submission(
                form, request.form, request.files, is_new=True,
            )
            if not validation_errors:
                product = Product()
                apply_product_fields_from_form(product, form, is_new=True)
                db.session.add(product)
                db.session.flush()
                apply_age_groups_from_request(product, request.form)

                image_count, image_failed = _save_product_images(product)
                variant_count, skipped_skus = _save_variants_from_request(product)
                db.session.commit()

                places = listing_preview(product)
                flash(
                    f'Product "{product.name}" saved successfully. Visible on: {"; ".join(places)}.',
                    'success',
                )
                if image_failed:
                    flash(f'{image_failed} image(s) could not be saved — use JPG, PNG or WebP under 5 MB.', 'warning')
                if image_count:
                    flash(f'{image_count} photo(s) uploaded for this product.', 'success')
                if product.images.count() == 1:
                    flash(
                        'Tip: Add a second photo (product flat-lay + child wearing the outfit) '
                        'so customers see multiple images on the product page.',
                        'info',
                    )
                for sku in skipped_skus:
                    flash(f'SKU "{sku}" already exists — variant skipped.', 'warning')
                return redirect(url_for('admin.products'))
            _flash_product_form_errors(form, validation_errors)
        else:
            validation_errors = validate_product_submission(
                form, request.form, request.files, is_new=True,
            )
            _flash_product_form_errors(form, validation_errors)

    return render_template(
        'admin/product_form.html',
        form=form,
        title='Add Product',
        is_new=True,
        validation_errors=validation_errors,
        age_group_sections=AGE_GROUP_SECTIONS,
        age_presets=AGE_PRESETS,
        category_groups=category_groups,
        visibility_options=STORE_VISIBILITY_OPTIONS,
        category_meta_json=json.dumps(category_metadata_for_js()),
        product_ai_enabled=product_ai_configured(),
        **draft,
    )


def product_ai_configured():
    from app.services.product_vision_service import product_ai_configured as _configured
    return _configured()


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = get_category_choices_flat()
    category_groups = get_category_groups()
    validation_errors = []
    draft = product_form_draft_context(
        request.form if request.method == 'POST' else None,
        product=product,
    )

    if request.method == 'POST':
        if form.validate_on_submit():
            validation_errors = validate_product_submission(
                form, request.form, request.files, is_new=False, product=product,
            )
            if not validation_errors:
                apply_product_fields_from_form(product, form, is_new=False)
                apply_age_groups_from_request(product, request.form)

                image_count, image_failed = _save_product_images(product)
                primary_id = request.form.get('primary_image_id', type=int)
                if primary_id:
                    _set_primary_image(product, primary_id)
                _ensure_primary_image(product)
                variant_count, skipped_skus = _save_variants_from_request(product)
                db.session.commit()

                places = listing_preview(product)
                flash(
                    f'Product "{product.name}" saved successfully. Visible on: {"; ".join(places)}.',
                    'success',
                )
                if image_failed:
                    flash(f'{image_failed} image(s) could not be saved — use JPG, PNG or WebP under 5 MB.', 'warning')
                if image_count:
                    flash(f'{image_count} photo(s) uploaded for this product.', 'success')
                if product.images.count() == 1:
                    flash(
                        'This product has only one photo. Upload a model/lifestyle shot below '
                        'so the product page shows multiple images.',
                        'info',
                    )
                for sku in skipped_skus:
                    flash(f'SKU "{sku}" already exists — variant skipped.', 'warning')
                return redirect(url_for('admin.edit_product', product_id=product.id))
            _flash_product_form_errors(form, validation_errors)
        else:
            validation_errors = validate_product_submission(
                form, request.form, request.files, is_new=False, product=product,
            )
            _flash_product_form_errors(form, validation_errors)

    variants = product.variants.all()
    images = product.images.order_by(ProductImage.sort_order).all()

    return render_template(
        'admin/product_form.html',
        form=form,
        title='Edit Product',
        is_new=False,
        product=product,
        variants=variants,
        images=images,
        validation_errors=validation_errors,
        age_group_sections=AGE_GROUP_SECTIONS,
        age_presets=AGE_PRESETS,
        category_groups=category_groups,
        visibility_options=STORE_VISIBILITY_OPTIONS,
        listing_preview=listing_preview(product),
        category_meta_json=json.dumps(category_metadata_for_js()),
        product_ai_enabled=product_ai_configured(),
        **draft,
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


@admin_bp.route('/products/<int:product_id>/images/<int:image_id>/set-primary', methods=['POST'])
@login_required
@admin_required
def set_product_primary_image(product_id, image_id):
    product = Product.query.get_or_404(product_id)
    if not _set_primary_image(product, image_id):
        flash('Image not found.', 'danger')
    else:
        db.session.commit()
        flash('Main product photo updated.', 'success')
    return redirect(url_for('admin.edit_product', product_id=product_id))


@admin_bp.route('/products/<int:product_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product_image(product_id, image_id):
    img = ProductImage.query.filter_by(id=image_id, product_id=product_id).first_or_404()
    was_primary = img.is_primary
    delete_image(img.image_url)
    db.session.delete(img)
    db.session.flush()
    if was_primary:
        product = Product.query.get_or_404(product_id)
        _ensure_primary_image(product)
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
    return render_template(
        'admin/orders.html',
        orders=orders,
        current_status=status_filter,
        payment_status_labels=PAYMENT_STATUS_LABELS,
    )


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    shipping_addr = json.loads(order.shipping_address) if order.shipping_address else {}
    payment = order.payment
    collection_channels = [(c, dict(PAYMENT_CHANNELS).get(c, c.title())) for c in COLLECTION_CHANNELS]
    return render_template(
        'admin/order_detail.html',
        order=order,
        shipping_addr=shipping_addr,
        payment=payment,
        collection_channels=collection_channels,
        payment_status_labels=PAYMENT_STATUS_LABELS,
    )


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
        if order.payment and order.payment.status == 'pending':
            order.payment.status = 'failed'
    elif new_status == 'refunded' and old_status != 'refunded':
        auto_record_order_refund(order, created_by_id=current_user.id)
        if order.payment and order.payment.status != 'refunded':
            order.payment.status = 'refunded'

    order.status = new_status
    db.session.commit()

    from app.services.email_service import send_order_status_update
    send_order_status_update(order)

    flash(f'Order {order.order_number} status updated to {new_status}.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))


@admin_bp.route('/orders/<int:order_id>/collect-payment', methods=['POST'])
@login_required
@admin_required
def collect_order_payment(order_id):
    """Mark COD payment as collected with cash/card/UPI channel."""
    order = Order.query.get_or_404(order_id)
    payment = order.payment
    if not payment:
        from app.services.payment_management_service import create_cod_payment
        payment = create_cod_payment(order)
        db.session.commit()

    channel = request.form.get('channel', '').strip()
    reference = request.form.get('reference', '').strip()
    notes = request.form.get('notes', '').strip()

    updated, error = mark_payment_collected(
        payment,
        channel=channel,
        reference=reference,
        notes=notes,
        collected_by_id=current_user.id,
    )
    if error:
        flash(error, 'danger')
    else:
        flash(
            f'Payment of ₹{updated.amount:,.0f} recorded via {updated.channel_label}.',
            'success',
        )
    return redirect(url_for('admin.order_detail', order_id=order_id))


# ── Payments ──────────────────────────────────────────────────────────
@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    """Payment ledger — collected totals, pending COD, cash/card/UPI breakdown."""
    backfill_missing_payments()

    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '').strip()
    channel = request.args.get('channel', '').strip()
    method = request.args.get('method', '').strip()
    month = request.args.get('month', '').strip()
    search = request.args.get('q', '').strip()

    today = datetime.utcnow()
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    summary_all = get_payment_summary()
    summary_month = get_payment_summary(start_date=month_start)

    query = get_payments_query(
        status=status or None,
        channel=channel or None,
        method=method or None,
        month=month or None,
        search=search or None,
    )
    pagination = query.paginate(page=page, per_page=25, error_out=False)

    channel_choices = [(c, label) for c, label in PAYMENT_CHANNELS if c != 'cod']
    return render_template(
        'admin/payments.html',
        payments=pagination,
        summary_all=summary_all,
        summary_month=summary_month,
        status_filter=status,
        channel_filter=channel,
        method_filter=method,
        month_filter=month,
        search=search,
        channel_choices=channel_choices,
        payment_status_labels=PAYMENT_STATUS_LABELS,
    )


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
        if discount_type not in ('percentage', 'flat'):
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
        if discount_type not in ('percentage', 'flat'):
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

    query = build_inventory_query(search, stock_filter, category_id)

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


@admin_bp.route('/inventory/export')
@login_required
@admin_required
def export_inventory():
    """Download inventory rows as Excel (.xlsx)."""
    scope = request.args.get('scope', 'filtered')
    search = request.args.get('search', '').strip()
    stock_filter = request.args.get('stock', '')
    category_id = request.args.get('category', '', type=str)

    if scope == 'all':
        query = build_inventory_query()
        prefix = 'indistylex-inventory-all'
    else:
        query = build_inventory_query(search, stock_filter, category_id)
        prefix = 'indistylex-inventory-filtered'

    variants = query.order_by(Product.name, ProductVariant.size).all()

    try:
        from app.services.inventory_export_service import export_inventory_xlsx
    except ImportError:
        flash(
            'Excel export is unavailable — install openpyxl on the server (pip install openpyxl) and restart the app.',
            'danger',
        )
        return redirect(request.referrer or url_for('admin.inventory'))

    buffer, filename = export_inventory_xlsx(variants, filename_prefix=prefix)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


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
