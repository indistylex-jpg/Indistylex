from flask import current_app
from app.extensions import db
from app.models.product import ProductVariant


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
