"""Product age options (0–18 years) and helpers."""

from sqlalchemy import or_, func

from app.extensions import db

# Granular age bands from newborn through teens.
AGE_GROUP_SECTIONS = [
    {
        'id': 'baby',
        'title': 'Baby (0–12 months)',
        'hint': 'Newborn & infant sizes',
        'choices': [
            ('0-3m', '0–3 Months'),
            ('3-6m', '3–6 Months'),
            ('6-9m', '6–9 Months'),
            ('9-12m', '9–12 Months'),
        ],
    },
    {
        'id': 'kids',
        'title': 'Kids (1–12 years)',
        'hint': 'Toddler through pre-teen',
        'choices': [
            ('1y', '1 Year'),
            ('1-2y', '1–2 Years'),
            ('2-3y', '2–3 Years'),
            ('3-4y', '3–4 Years'),
            ('4-5y', '4–5 Years'),
            ('5-6y', '5–6 Years'),
            ('6-7y', '6–7 Years'),
            ('7-8y', '7–8 Years'),
            ('8-9y', '8–9 Years'),
            ('9-10y', '9–10 Years'),
            ('10-11y', '10–11 Years'),
            ('11-12y', '11–12 Years'),
        ],
    },
    {
        'id': 'teen',
        'title': 'Teens (12–18 years)',
        'hint': 'Teen & young adult sizes',
        'choices': [
            ('12-13y', '12–13 Years'),
            ('13-14y', '13–14 Years'),
            ('14-15y', '14–15 Years'),
            ('15-16y', '15–16 Years'),
            ('16-17y', '16–17 Years'),
            ('17-18y', '17–18 Years'),
        ],
    },
]

AGE_GROUP_CHOICES = [
    choice for section in AGE_GROUP_SECTIONS for choice in section['choices']
]

# Quick links for header "Shop By Age" mega menu (Miarcus-style).
SHOP_BY_AGE_NAV = [
    ('0-3m', '0–3 Months', '👶'),
    ('3-6m', '3–6 Months', '🍼'),
    ('6-9m', '6–9 Months', '🧸'),
    ('9-12m', '9–12 Months', '🍼'),
    ('1-2y', '1–2 Years', '🚶'),
    ('2-3y', '2–3 Years', '🏃'),
    ('3-4y', '3–4 Years', '🎒'),
    ('4-5y', '4–5 Years', '⭐'),
    ('5-6y', '5–6 Years', '🌟'),
    ('6-7y', '6–8 Years', '⚽'),
    ('10-11y', '9–12 Years', '📚'),
    ('14-15y', '14–15 Years', '🎓'),
]

VALID_AGE_GROUPS = {value for value, _ in AGE_GROUP_CHOICES}
AGE_GROUP_ORDER = [value for value, _ in AGE_GROUP_CHOICES]
AGE_GROUP_LABELS = dict(AGE_GROUP_CHOICES)

# Old coarse bands → new granular codes (for existing products in DB).
LEGACY_AGE_EXPANSION = {
    '0-2': ['0-3m', '3-6m', '6-9m', '9-12m', '1y', '1-2y'],
    '2-4': ['2-3y', '3-4y'],
    '4-6': ['4-5y', '5-6y'],
    '6-8': ['6-7y', '7-8y'],
    '8-12': ['8-9y', '9-10y', '10-11y', '11-12y'],
    '12-14': ['12-13y', '13-14y'],
    '14-18': ['14-15y', '15-16y', '16-17y', '17-18y'],
}


def _expand_legacy_code(code):
    if code in VALID_AGE_GROUPS:
        return [code]
    return LEGACY_AGE_EXPANSION.get(code, [])


def normalize_age_groups(selected):
    """Return sorted valid age group codes."""
    if not selected:
        return []
    cleaned = []
    for item in selected:
        value = (item or '').strip()
        for expanded in _expand_legacy_code(value):
            if expanded not in cleaned:
                cleaned.append(expanded)
    cleaned.sort(key=lambda x: AGE_GROUP_ORDER.index(x))
    return cleaned


def age_groups_to_storage(selected):
    groups = normalize_age_groups(selected)
    return ','.join(groups) if groups else None


def parse_age_groups(stored, legacy_single=None):
    raw = []
    if stored:
        raw.extend(stored.split(','))
    elif legacy_single:
        raw.append(legacy_single)
    return normalize_age_groups(raw)


def _parse_age_code(code):
    if code.endswith('m'):
        lo, hi = code[:-1].split('-')
        return {'unit': 'months', 'min': int(lo), 'max': int(hi)}
    if code.endswith('y'):
        parts = code[:-1].split('-')
        if len(parts) == 1:
            age = int(parts[0])
            return {'unit': 'years', 'min': age, 'max': age}
        return {'unit': 'years', 'min': int(parts[0]), 'max': int(parts[1])}
    return None


def _format_age_span(start_code, end_code):
    start = _parse_age_code(start_code)
    end = _parse_age_code(end_code)
    if not start or not end or start['unit'] != end['unit']:
        return f"{AGE_GROUP_LABELS[start_code]} – {AGE_GROUP_LABELS[end_code]}"

    lo, hi = start['min'], end['max']
    if start['unit'] == 'months':
        return f"{lo}–{hi} Months" if lo != hi else f"{lo} Months"

    if lo == hi == 1:
        return "1 Year"
    if lo == hi:
        return f"{lo} Years"
    return f"{lo}–{hi} Years"


def age_groups_display(groups):
    """Collapse consecutive bands into readable ranges."""
    groups = normalize_age_groups(groups)
    if not groups:
        return ''

    indices = [AGE_GROUP_ORDER.index(code) for code in groups]
    ranges = []
    start_idx = indices[0]
    prev_idx = indices[0]

    for idx in indices[1:]:
        if idx == prev_idx + 1:
            prev_idx = idx
            continue
        ranges.append(_format_age_span(AGE_GROUP_ORDER[start_idx], AGE_GROUP_ORDER[prev_idx]))
        start_idx = idx
        prev_idx = idx

    ranges.append(_format_age_span(AGE_GROUP_ORDER[start_idx], AGE_GROUP_ORDER[prev_idx]))
    return ', '.join(ranges)


def apply_age_group_filter(query, age_group, product_model):
    """Filter products that match a shop age band."""
    if not age_group:
        return query

    match_codes = normalize_age_groups([age_group])
    if not match_codes:
        return query

    dialect = db.engine.dialect.name
    filters = []
    for code in match_codes:
        if dialect == 'mysql':
            filters.append(func.find_in_set(code, product_model.age_groups) > 0)
        else:
            filters.extend([
                product_model.age_groups == code,
                product_model.age_groups.like(f'{code},%'),
                product_model.age_groups.like(f'%,{code}'),
                product_model.age_groups.like(f'%,{code},%'),
            ])
        # Also match legacy coarse bands stored on older products.
        for legacy_code, expanded in LEGACY_AGE_EXPANSION.items():
            if code in expanded:
                if dialect == 'mysql':
                    filters.append(func.find_in_set(legacy_code, product_model.age_groups) > 0)
                else:
                    filters.extend([
                        product_model.age_groups == legacy_code,
                        product_model.age_groups.like(f'{legacy_code},%'),
                        product_model.age_groups.like(f'%,{legacy_code}'),
                        product_model.age_groups.like(f'%,{legacy_code},%'),
                    ])
                filters.append(product_model.age_group == legacy_code)

        filters.append(product_model.age_group == code)

    return query.filter(or_(*filters))
