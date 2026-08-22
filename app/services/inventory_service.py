from flask import current_app
from datetime import datetime
from app.extensions import db
from app.models.product import Product, ProductVariant


def inventory_stock_status(stock_quantity):
    """Human-readable stock status for inventory views and exports."""
    if stock_quantity == 0:
        return 'Out of Stock'
    if stock_quantity <= 10:
        return 'Low Stock'
    return 'In Stock'


def build_inventory_query(search='', stock_filter='', category_id=''):
    """Build the shared inventory query used by the admin list and export."""
    query = ProductVariant.query.join(Product).filter(Product.is_active == True)

    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                ProductVariant.sku.ilike(f'%{search}%'),
            )
        )

    if stock_filter == 'low':
        query = query.filter(
            ProductVariant.stock_quantity <= 10,
            ProductVariant.stock_quantity > 0,
        )
    elif stock_filter == 'out':
        query = query.filter(ProductVariant.stock_quantity == 0)

    if category_id:
        query = query.filter(Product.category_id == int(category_id))

    return query


def check_stock(variant_id, quantity):
    """Check if requested quantity is available."""
    variant = ProductVariant.query.get(variant_id)
    if not variant or not variant.is_active:
        return False, 'Product variant not found or inactive.'
    if variant.stock_quantity < quantity:
        return False, f'Only {variant.stock_quantity} items available.'
    return True, 'In stock.'


def reduce_stock(variant_id, quantity):
    """Reduce stock after successful order."""
    variant = ProductVariant.query.get(variant_id)
    if variant and variant.stock_quantity >= quantity:
        variant.stock_quantity -= quantity
        db.session.commit()
        return True
    return False


def restore_stock(variant_id, quantity):
    """Restore stock on order cancellation/refund."""
    variant = ProductVariant.query.get(variant_id)
    if variant:
        variant.stock_quantity += quantity
        db.session.commit()
        return True
    return False


def get_low_stock_products(threshold=5):
    """Get variants with stock below threshold."""
    return ProductVariant.query.filter(
        ProductVariant.stock_quantity <= threshold,
        ProductVariant.is_active == True,
    ).all()


def generate_b2b_sale_number():
    """Generate next B2B sale number: B2B-2026-0001."""
    from app.models.b2b_sale import B2BSale
    year = datetime.utcnow().year
    prefix = f'B2B-{year}-'
    last = B2BSale.query.filter(
        B2BSale.sale_number.like(f'{prefix}%')
    ).order_by(B2BSale.id.desc()).first()
    if last:
        try:
            seq = int(last.sale_number.split('-')[-1]) + 1
        except ValueError:
            seq = last.id + 1
    else:
        seq = 1
    return f'{prefix}{seq:04d}'


def record_b2b_sale(shop_name, items, created_by_id, shop_phone='', shop_city='',
                    payment_terms='cod', notes='', extra_discount=0, discount_percent=0,
                    discount_reason=''):
    """
    Record a B2B shop sale and deduct stock from website inventory.

    items: list of dicts with keys variant_id, quantity, unit_price (optional)
    Returns (sale, None) on success or (None, error_message) on failure.
    """
    from decimal import Decimal
    from app.models.b2b_sale import B2BSale, B2BSaleItem

    if not shop_name or not shop_name.strip():
        return None, 'Shop name is required.'
    if not items:
        return None, 'Add at least one item.'

    # Validate all items before deducting stock
    parsed = []
    for i, item in enumerate(items, 1):
        variant_id = item.get('variant_id')
        quantity = item.get('quantity', 0)
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return None, f'Line {i}: invalid quantity.'

        if quantity < 1:
            return None, f'Line {i}: quantity must be at least 1.'

        variant = ProductVariant.query.get(variant_id)
        if not variant or not variant.is_active:
            return None, f'Line {i}: product variant not found.'

        ok, msg = check_stock(variant.id, quantity)
        if not ok:
            return None, f'Line {i} ({variant.sku}): {msg}'

        unit_price = item.get('unit_price')
        if unit_price is None or unit_price == '':
            unit_price = variant.product.price * Decimal('0.7')
        else:
            unit_price = Decimal(str(unit_price))

        if unit_price < 0:
            return None, f'Line {i}: invalid price.'

        parsed.append({
            'variant': variant,
            'quantity': quantity,
            'unit_price': unit_price,
            'line_total': unit_price * quantity,
        })

    subtotal = sum(row['line_total'] for row in parsed)

    try:
        extra_discount = Decimal(str(extra_discount or 0))
        discount_percent = Decimal(str(discount_percent or 0))
    except Exception:
        return None, 'Invalid discount value.'

    if extra_discount < 0 or discount_percent < 0:
        return None, 'Discount cannot be negative.'
    if discount_percent > 100:
        return None, 'Discount percent cannot exceed 100%.'
    if extra_discount > 0 and discount_percent > 0:
        return None, 'Use either flat discount (₹) or percent (%), not both.'

    if discount_percent > 0:
        discount_applied = subtotal * discount_percent / Decimal('100')
    else:
        discount_applied = extra_discount

    if discount_applied > subtotal:
        return None, 'Discount cannot exceed subtotal.'

    final_total = subtotal - discount_applied

    sale = B2BSale(
        sale_number=generate_b2b_sale_number(),
        shop_name=shop_name.strip(),
        shop_phone=shop_phone.strip() if shop_phone else None,
        shop_city=shop_city.strip() if shop_city else None,
        payment_terms=payment_terms or 'cod',
        notes=notes.strip() if notes else None,
        subtotal=subtotal,
        extra_discount=extra_discount,
        discount_percent=discount_percent,
        discount_reason=discount_reason.strip() if discount_reason else None,
        created_by_id=created_by_id,
    )
    db.session.add(sale)
    db.session.flush()

    for row in parsed:
        variant = row['variant']
        if not reduce_stock(variant.id, row['quantity']):
            db.session.rollback()
            return None, f'Failed to deduct stock for {variant.sku}.'

        item = B2BSaleItem(
            sale_id=sale.id,
            variant_id=variant.id,
            product_name=variant.product.name,
            sku=variant.sku,
            size=variant.size,
            color=variant.color,
            quantity=row['quantity'],
            unit_price=row['unit_price'],
            line_total=row['line_total'],
        )
        db.session.add(item)

    sale.total = final_total
    db.session.commit()
    return sale, None


def cancel_b2b_sale(sale_id):
    """Cancel a B2B sale and restore stock. Returns (True, None) or (False, error)."""
    from app.models.b2b_sale import B2BSale

    sale = B2BSale.query.get(sale_id)
    if not sale:
        return False, 'Sale not found.'
    if sale.is_cancelled:
        return False, 'Sale already cancelled.'

    for item in sale.items:
        restore_stock(item.variant_id, item.quantity)

    sale.is_cancelled = True
    db.session.commit()
    return True, None
