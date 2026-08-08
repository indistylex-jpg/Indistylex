"""Resolve product variants for add-to-cart."""


def resolve_variant_id(product_id=None, variant_id=None, size='', color=''):
    """Return variant id from explicit id or product + size/color."""
    from app.models.product import ProductVariant

    size = (size or '').strip()
    color = (color or '').strip()

    if variant_id:
        variant = ProductVariant.query.get(variant_id)
        if variant and variant.is_active and variant.stock_quantity > 0:
            return variant.id
        return None

    if not product_id:
        return None

    in_stock = ProductVariant.query.filter_by(
        product_id=product_id, is_active=True
    ).filter(ProductVariant.stock_quantity > 0).all()

    if len(in_stock) == 1:
        return in_stock[0].id

    if size and color:
        match = next(
            (v for v in in_stock if v.size == size and v.color == color),
            None,
        )
        return match.id if match else None

    if size:
        matches = [v for v in in_stock if v.size == size]
        if len(matches) == 1:
            return matches[0].id

    if color:
        matches = [v for v in in_stock if v.color == color]
        if len(matches) == 1:
            return matches[0].id

    return None


def cart_add_error_message(product_id=None, size='', color=''):
    """User-facing hint when variant could not be resolved."""
    from app.models.product import Product, ProductVariant

    if not product_id:
        return 'Invalid product.'

    product = Product.query.get(product_id)
    if not product:
        return 'Product not found.'

    in_stock = ProductVariant.query.filter_by(
        product_id=product_id, is_active=True
    ).filter(ProductVariant.stock_quantity > 0).all()

    if not in_stock:
        return 'This product is currently out of stock.'

    sizes = sorted({v.size for v in in_stock})
    colors = sorted({v.color for v in in_stock})

    if len(sizes) > 1 and not size:
        return 'Please select a size.'
    if len(colors) > 1 and not color:
        return 'Please select a color.'
    if size and color:
        return 'The selected size and color combination is not available.'
    return 'Please select a size and color.'
