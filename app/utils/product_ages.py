"""Product age group options and helpers."""

from sqlalchemy import or_, func

from app.extensions import db

AGE_GROUP_CHOICES = [
    ('0-2', '0–2 Years'),
    ('2-4', '2–4 Years'),
    ('4-6', '4–6 Years'),
    ('6-8', '6–8 Years'),
    ('8-12', '8–12 Years'),
    ('12-14', '12–14 Years (Teen)'),
    ('14-18', '14–18 Years (Teen)'),
]

VALID_AGE_GROUPS = {value for value, _ in AGE_GROUP_CHOICES}
AGE_GROUP_ORDER = [value for value, _ in AGE_GROUP_CHOICES]
AGE_GROUP_LABELS = dict(AGE_GROUP_CHOICES)


def normalize_age_groups(selected):
    """Return sorted valid age group codes."""
    if not selected:
        return []
    cleaned = []
    for item in selected:
        value = (item or '').strip()
        if value in VALID_AGE_GROUPS and value not in cleaned:
            cleaned.append(value)
    cleaned.sort(key=lambda x: AGE_GROUP_ORDER.index(x))
    return cleaned


def age_groups_to_storage(selected):
    groups = normalize_age_groups(selected)
    return ','.join(groups) if groups else None


def parse_age_groups(stored, legacy_single=None):
    if stored:
        return normalize_age_groups(stored.split(','))
    if legacy_single and legacy_single in VALID_AGE_GROUPS:
        return [legacy_single]
    return []


def age_groups_display(groups):
    groups = normalize_age_groups(groups)
    if not groups:
        return ''
    if len(groups) == 1:
        return AGE_GROUP_LABELS.get(groups[0], groups[0])
    return f"{AGE_GROUP_LABELS.get(groups[0], groups[0])} – {AGE_GROUP_LABELS.get(groups[-1], groups[-1])}"


def apply_age_group_filter(query, age_group, product_model):
    """Filter products that match a shop age band."""
    if not age_group or age_group not in VALID_AGE_GROUPS:
        return query

    dialect = db.engine.dialect.name
    if dialect == 'mysql':
        return query.filter(or_(
            product_model.age_group == age_group,
            func.find_in_set(age_group, product_model.age_groups) > 0,
        ))

    return query.filter(or_(
        product_model.age_group == age_group,
        product_model.age_groups == age_group,
        product_model.age_groups.like(f'{age_group},%'),
        product_model.age_groups.like(f'%,{age_group}'),
        product_model.age_groups.like(f'%,{age_group},%'),
    ))
