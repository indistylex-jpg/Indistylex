"""SKU + HSN helpers for Indistylex kids clothing (GST India)."""
import re

from app.models.product import ProductVariant

# IX-[TYPE]-[SEQ]-[SIZE]-[COLOR] — see operations-templates/HSN_CODES.md
PRODUCT_TYPE_CODES = {
    'frock': 'FRK',
    'dress': 'FRK',
    'shirt': 'SHT',
    'tshirt': 'POL',
    'pant': 'JNS',
    'shorts': 'JGR',
    'kurta': 'KRT',
    'romper': 'RMP',
    'nightwear': 'PJM',
    'winter': 'HDI',
    'school': 'TRK',
    'other': 'ACC',
    'ethnic': 'ETH',
}

HSN_BY_PRODUCT_TYPE = {
    'frock': '6204',
    'dress': '6204',
    'shirt': '6205',
    'tshirt': '6109',
    'pant': '6203',
    'shorts': '6203',
    'kurta': '6204',
    'romper': '6111',
    'nightwear': '6109',
    'winter': '6110',
    'school': '6112',
    'ethnic': '6204',
    'other': '6209',
}

COLOR_CODES = {
    'pink': 'PNK', 'blue': 'BLU', 'red': 'RED', 'green': 'GRN', 'yellow': 'YLW',
    'white': 'WHT', 'black': 'BLK', 'grey': 'GRY', 'gray': 'GRY', 'navy': 'NVY',
    'purple': 'PUR', 'orange': 'ORG', 'beige': 'BGE', 'brown': 'BRN', 'cream': 'CRM',
    'maroon': 'MRN', 'gold': 'GLD', 'silver': 'SLV', 'multicolor': 'MLT', 'multi': 'MLT',
}


def product_type_to_code(product_type):
    return PRODUCT_TYPE_CODES.get((product_type or 'other').lower().strip(), 'ACC')


def suggest_hsn_code(product_type):
    return HSN_BY_PRODUCT_TYPE.get((product_type or 'other').lower().strip(), '6209')


def color_to_code(color):
    key = (color or '').lower().strip()
    if key in COLOR_CODES:
        return COLOR_CODES[key]
    letters = re.sub(r'[^a-zA-Z]', '', key).upper()
    return (letters[:3] or 'MIX')[:3]


def size_to_sku_part(size):
    return re.sub(r'\s+', '', (size or '').strip().upper()) or 'OS'


def next_sku_sequence(type_code):
    """Next 3-digit sequence for IX-TYPE-###-… (avoids collisions)."""
    prefix = f'IX-{type_code}-'
    rows = ProductVariant.query.filter(ProductVariant.sku.like(f'{prefix}%')).with_entities(
        ProductVariant.sku
    ).all()
    max_n = 0
    for (sku,) in rows:
        parts = sku.split('-')
        if len(parts) >= 3:
            try:
                max_n = max(max_n, int(parts[2]))
            except ValueError:
                continue
    return max_n + 1


def build_sku(product_type, size, color, sequence=None):
    type_code = product_type_to_code(product_type)
    seq = sequence if sequence is not None else next_sku_sequence(type_code)
    return f'IX-{type_code}-{seq:03d}-{size_to_sku_part(size)}-{color_to_code(color)}'


def ensure_unique_sku(sku):
    candidate = (sku or '').strip().upper()
    if not candidate:
        return candidate
    if not ProductVariant.query.filter_by(sku=candidate).first():
        return candidate
    base = candidate
    n = 2
    while ProductVariant.query.filter_by(sku=f'{base}-{n}').first():
        n += 1
    return f'{base}-{n}'


def age_group_to_size_label(age_code):
    """Map age band code to variant size label (e.g. 2-3y → 2-3Y)."""
    code = (age_code or '').strip().lower()
    if not code:
        return ''
    if code.endswith('y'):
        return code[:-1] + 'Y'
    if code.endswith('m'):
        return code.upper()
    return code.upper()


def suggest_variant_rows(product_type, color, age_groups=None, *, max_rows=6):
    """
    Build draft variant rows with unique SKUs for admin form.
    One row per age band (up to max_rows), same color.
    """
    age_groups = age_groups or ['3-4y']
    type_code = product_type_to_code(product_type)
    seq = next_sku_sequence(type_code)
    color = (color or 'Multi').strip()
    rows = []
    seen_sizes = set()

    for age in age_groups:
        size = age_group_to_size_label(age)
        if not size or size in seen_sizes:
            continue
        seen_sizes.add(size)
        sku = ensure_unique_sku(build_sku(product_type, size, color, sequence=seq))
        rows.append({'size': size, 'color': color, 'sku': sku, 'stock': 10})
        if len(rows) >= max_rows:
            break

    if not rows:
        size = '3-4Y'
        sku = ensure_unique_sku(build_sku(product_type, size, color, sequence=seq))
        rows.append({'size': size, 'color': color, 'sku': sku, 'stock': 10})

    return rows
