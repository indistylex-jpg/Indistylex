#!/usr/bin/env python3
"""
Replace Indistylex categories with full 0–18 catalog.

Includes gender-specific toddler bands:
  boys-1-3  → Boys (1–3 Years)
  girls-1-3 → Girls (1–3 Years)  e.g. frocks for 1-year girls

Deletes legacy gender-neutral `toddler` parent after migrating products.

Run on server:
  cd /var/www/html/indistylex
  source venv/bin/activate
  python seed_categories.py
"""
from app import create_app
from app.extensions import db
from app.models.product import Category, Product

app = create_app()

TODDLER_AGE_CODES = frozenset({'1y', '1-2y', '2-3y'})
NEWBORN_AGE_CODES = frozenset({'0-3m', '3-6m', '6-9m', '9-12m'})

# ── Level 1: parent categories ──────────────────────────────────────
PARENTS = [
    ('newborn-infant', 'Newborn & Infant (0–12M)',
     'Soft essentials for 0–12 months — rompers, bodysuits, swaddles', 1),
    ('boys-1-3', 'Boys (1–3 Years)',
     'Everyday & festive wear for toddler boys — dungarees, co-ords, kurta sets', 2),
    ('girls-1-3', 'Girls (1–3 Years)',
     'Frocks, dresses & sets for toddler girls — perfect from 1 year up', 3),
    ('boys-3-8', 'Boys (3–8 Years)',
     'Daily & festive wear for young boys', 4),
    ('boys-9-12', 'Boys (9–12 Years)',
     'Juniors — school, casual & ethnic for pre-teens', 5),
    ('boys-teens', 'Boys Teens (13–18 Years)',
     'Teen boys — shirts, jeans, kurtas, co-ords', 6),
    ('girls-3-8', 'Girls (3–8 Years)',
     'Frocks, sets & ethnic for young girls', 7),
    ('girls-9-12', 'Girls (9–12 Years)',
     'Juniors — dresses, kurtis, lehengas for pre-teens', 8),
    ('girls-teens', 'Girls Teens (13–18 Years)',
     'Teen girls — kurtis, co-ords, western & ethnic', 9),
    ('ethnic-festive', 'Ethnic & Festive Wear',
     'Diwali, wedding, puja — all ages', 10),
    ('nightwear', 'Nightwear & Loungewear',
     'Pyjamas, night suits, robes — all ages', 11),
    ('winter-wear', 'Winter Wear',
     'Sweaters, jackets, thermals, hoodies', 12),
    ('school-wear', 'School Wear',
     'Shirts, pants, skirts, uniforms', 13),
    ('activewear', 'Activewear & Sportswear',
     'Track suits, joggers, sports tees', 14),
    ('baby-essentials', 'Baby Essentials & Accessories',
     'Caps, bibs, booties, mittens, blankets', 15),
]

# ── Level 2: (parent_slug, child_slug, name, sort_order) ───────────
CHILDREN = [
    # Newborn
    ('newborn-infant', 'rompers-onesies', 'Rompers & Onesies', 1),
    ('newborn-infant', 'bodysuits-vests', 'Bodysuits & Vests', 2),
    ('newborn-infant', 'swaddles-wraps', 'Swaddles & Wraps', 3),
    ('newborn-infant', 'baby-gift-sets', 'Baby Sets & Gift Sets', 4),
    ('newborn-infant', 'baby-caps-booties', 'Caps, Booties & Mittens', 5),
    ('newborn-infant', 'bibs-burp-cloths', 'Bibs & Burp Cloths', 6),
    # Boys 1–3
    ('boys-1-3', 'dungarees-jumpsuits', 'Dungarees & Jumpsuits', 1),
    ('boys-1-3', 'coord-sets', 'Co-ord Sets', 2),
    ('boys-1-3', 'jogger-sets', 'Jogger Sets', 3),
    ('boys-1-3', 'kurta-sets', 'Kurta Sets', 4),
    ('boys-1-3', 't-shirts-tops', 'T-Shirts & Tops', 5),
    # Girls 1–3
    ('girls-1-3', 'frocks-dresses', 'Frocks & Dresses', 1),
    ('girls-1-3', 'dungarees-jumpsuits', 'Dungarees & Jumpsuits', 2),
    ('girls-1-3', 'coord-sets', 'Co-ord Sets', 3),
    ('girls-1-3', 'jogger-sets', 'Jogger Sets', 4),
    ('girls-1-3', 'lehenga-choli', 'Lehenga & Party Wear', 5),
    ('girls-1-3', 'kurta-kurti-sets', 'Kurta & Kurti Sets', 6),
    # Boys 3-8 & 9-12 (same subs, different parents)
    *[(p, s, n, o) for p in ('boys-3-8', 'boys-9-12') for s, n, o in [
        ('t-shirts-polos', 'T-Shirts & Polos', 1),
        ('shirts-formal', 'Shirts & Formal', 2),
        ('jeans-trousers', 'Jeans & Trousers', 3),
        ('shorts-bermudas', 'Shorts & Bermudas', 4),
        ('track-suits-joggers', 'Track Suits & Joggers', 5),
        ('hoodies-sweatshirts', 'Hoodies & Sweatshirts', 6),
        ('kurta-pajama', 'Kurta Pajama', 7),
        ('sherwani-indo-western', 'Sherwani & Indo-Western', 8),
        ('nehru-jacket-sets', 'Nehru Jacket Sets', 9),
        ('pyjamas-night-suits', 'Pyjamas & Night Suits', 10),
    ]],
    # Boys teens
    ('boys-teens', 'tees-oversized', 'T-Shirts & Oversized Tees', 1),
    ('boys-teens', 'casual-shirts', 'Shirts & Casual Shirts', 2),
    ('boys-teens', 'jeans-cargo', 'Jeans & Cargo Pants', 3),
    ('boys-teens', 'kurta-sets-teen', 'Kurta & Kurta Sets', 4),
    ('boys-teens', 'coord-sets-teen', 'Co-ord Sets', 5),
    ('boys-teens', 'hoodies-jackets-teen', 'Hoodies & Jackets', 6),
    ('boys-teens', 'shorts-joggers-teen', 'Shorts & Joggers', 7),
    # Girls 3-8 & 9-12
    *[(p, s, n, o) for p in ('girls-3-8', 'girls-9-12') for s, n, o in [
        ('frocks-dresses', 'Frocks & Dresses', 1),
        ('lehenga-choli', 'Lehenga Choli', 2),
        ('anarkali-gown', 'Anarkali & Gown', 3),
        ('salwar-sharara', 'Salwar Kameez & Sharara', 4),
        ('palazzo-kurti', 'Palazzo & Kurti Sets', 5),
        ('pattu-half-saree', 'Pattu Pavadai / Half Saree', 6),
        ('dungarees-jumpsuits', 'Dungarees & Jumpsuits', 7),
        ('skirts-tops', 'Skirts & Tops', 8),
        ('jeans-trousers', 'Jeans & Trousers', 9),
        ('nightgowns-pyjamas', 'Nightgowns & Pyjamas', 10),
        ('jogger-coord-sets', 'Jogger & Co-ord Sets', 11),
    ]],
    # Girls teens
    ('girls-teens', 'kurtis-sets', 'Kurtis & Kurti Sets', 1),
    ('girls-teens', 'coord-sets', 'Co-ord Sets', 2),
    ('girls-teens', 'tops-tunics', 'Tops & Tunics', 3),
    ('girls-teens', 'jeans-palazzos', 'Jeans & Palazzos', 4),
    ('girls-teens', 'lehenga-anarkali-teen', 'Lehenga & Anarkali (Teen)', 5),
    ('girls-teens', 'dresses-maxi', 'Dresses & Maxi Dresses', 6),
    ('girls-teens', 'sharara-gharara', 'Sharara & Gharara Sets', 7),
    # Ethnic festive
    ('ethnic-festive', 'diwali', 'Diwali Collection', 1),
    ('ethnic-festive', 'wedding-party', 'Wedding & Party Wear', 2),
    ('ethnic-festive', 'rakhi-bhai-dooj', 'Rakhi / Bhai Dooj', 3),
    ('ethnic-festive', 'eid', 'Eid Collection', 4),
    ('ethnic-festive', 'puja-traditional', 'Puja & Traditional', 5),
    # Nightwear
    ('nightwear', 'pyjama-sets', 'Pyjama Sets', 1),
    ('nightwear', 'night-suits', 'Night Suits (Full)', 2),
    ('nightwear', 'nightgowns-robes', 'Nightgowns & Robes', 3),
    ('nightwear', 'onesie-sleepwear', 'Onesie Sleepwear', 4),
    # Winter
    ('winter-wear', 'sweaters-cardigans', 'Sweaters & Cardigans', 1),
    ('winter-wear', 'jackets-coats', 'Jackets & Coats', 2),
    ('winter-wear', 'hoodies-sweatshirts', 'Hoodies & Sweatshirts', 3),
    ('winter-wear', 'thermals-inners', 'Thermals & Inners', 4),
    ('winter-wear', 'winter-accessories', 'Caps, Gloves & Mufflers', 5),
    # School
    ('school-wear', 'school-shirts', 'School Shirts', 1),
    ('school-wear', 'school-trousers', 'School Trousers & Pants', 2),
    ('school-wear', 'school-skirts', 'School Skirts', 3),
    ('school-wear', 'school-uniform-sets', 'School Uniform Sets', 4),
    # Activewear
    ('activewear', 'track-suits', 'Track Suits', 1),
    ('activewear', 'sports-t-shirts', 'Sports T-Shirts', 2),
    ('activewear', 'sports-shorts', 'Sports Shorts', 3),
    ('activewear', 'leggings-sports-pants', 'Leggings & Sports Pants', 4),
    # Baby essentials
    ('baby-essentials', 'caps-booties-mittens', 'Caps, Booties & Mittens', 1),
    ('baby-essentials', 'bibs-burp-cloths', 'Bibs & Burp Cloths', 2),
    ('baby-essentials', 'blankets-swaddles', 'Blankets & Swaddles', 3),
    ('baby-essentials', 'baby-care-accessories', 'Baby Care Accessories', 4),
]

# Product name keywords → child slug suffix (within parent context)
KEYWORD_MAP = [
    (('romper', 'onesie'), 'rompers-onesies'),
    (('bodysuit', 'vest'), 'bodysuits-vests'),
    (('swaddle', 'blanket'), 'swaddles-wraps'),
    (('bib', 'burp'), 'bibs-burp-cloths'),
    (('bootie', 'mitten', 'cap'), 'baby-caps-booties'),
    (('gift set', 'baby set'), 'baby-gift-sets'),
    (('dungaree', 'jumpsuit'), 'dungarees-jumpsuits'),
    (('lehenga',), 'lehenga-choli'),
    (('sherwani',), 'sherwani-indo-western'),
    (('anarkali',), 'anarkali-gown'),
    (('salwar',), 'salwar-sharara'),
    (('sharara', 'gharara'), 'sharara-gharara'),
    (('palazzo',), 'palazzo-kurti'),
    (('pattu', 'pavadai'), 'pattu-half-saree'),
    (('gown', 'cinderella'), 'anarkali-gown'),
    (('frock', 'dress'), 'frocks-dresses'),
    (('kurta', 'kurti'), 'kurta-pajama'),
    (('track suit', 'tracksuit'), 'track-suits-joggers'),
    (('jogger',), 'jogger-sets'),
    (('hoodie', 'sweatshirt'), 'hoodies-sweatshirts'),
    (('polo',), 't-shirts-polos'),
    (('jeans', 'denim'), 'jeans-trousers'),
    (('bermuda', 'shorts', 'cargo short'), 'shorts-bermudas'),
    (('formal shirt', 'gentleman'), 'shirts-formal'),
    (('t-shirt', 'tee', 'campus'), 't-shirts-polos'),
    (('pajama', 'pyjama', 'night suit', 'nightgown', 'sleep'), 'pyjamas-night-suits'),
    (('tutu', 'skirt'), 'skirts-tops'),
    (('coord', 'co-ord'), 'coord-sets'),
    (('thermal', 'sweater'), 'sweaters-cardigans'),
    (('uniform', 'school'), 'school-uniform-sets'),
]

LEGACY_PARENT = {
    'newborn': 'newborn-infant',
    'toddler': 'girls-1-3',
    'boys': 'boys-3-8',
    'girls': 'girls-3-8',
    'men': 'boys-teens',
    'women': 'girls-teens',
    'kids': 'girls-1-3',
}

BOYS_ONLY_SUFFIXES = frozenset({
    't-shirts-tops', 't-shirts-polos', 'shirts-formal', 'kurta-pajama',
    'sherwani-indo-western', 'nehru-jacket-sets', 'shorts-bermudas',
})
GIRLS_ONLY_SUFFIXES = frozenset({
    'frocks-dresses', 'lehenga-choli', 'anarkali-gown', 'salwar-sharara',
    'palazzo-kurti', 'pattu-half-saree', 'skirts-tops', 'kurta-kurti-sets',
    'nightgowns-pyjamas',
})


def product_age_codes(product):
    raw = (product.age_groups or product.age_group or '').strip()
    if not raw:
        return set()
    return {code.strip() for code in raw.split(',') if code.strip()}


def is_toddler_product(product):
    codes = product_age_codes(product)
    if codes & TODDLER_AGE_CODES:
        return True
    legacy = product.age_group or ''
    return legacy in ('2-4', '1-2', '2-3')


def is_newborn_product(product):
    codes = product_age_codes(product)
    if codes & NEWBORN_AGE_CODES:
        return True
    return (product.age_group or '') == '0-2'


def toddler_parent_for_gender(gender, product_name=''):
    gender = (gender or '').lower()
    name = (product_name or '').lower()
    if gender == 'boys':
        return 'boys-1-3'
    if gender == 'girls':
        return 'girls-1-3'
    if any(k in name for k in ('frock', 'dress', 'lehenga', 'gown', 'kurti')):
        return 'girls-1-3'
    return 'boys-1-3'


def pick_parent_slug(product, old_slug):
    age = product.age_group or ''
    gender = (product.gender or '').lower()
    old_base = old_slug.split('-')[0] if old_slug else ''

    if old_slug.startswith('toddler') or old_base == 'toddler' or is_toddler_product(product):
        return toddler_parent_for_gender(gender, product.name)

    if old_slug in LEGACY_PARENT:
        base = LEGACY_PARENT[old_slug]
    else:
        base = old_slug if old_slug in {p[0] for p in PARENTS} else toddler_parent_for_gender(gender, product.name)

    if is_newborn_product(product) or old_slug == 'newborn' or age == '0-2':
        return 'newborn-infant'

    if base.startswith('boys') or gender == 'boys' or old_slug == 'boys':
        if age in ('12-14', '14-18') or any(a.startswith(('12-', '13-', '14-', '15-', '16-', '17-')) for a in product_age_codes(product)):
            return 'boys-teens'
        if age == '8-12' or any(a in ('8-9y', '9-10y', '10-11y', '11-12y') for a in product_age_codes(product)):
            return 'boys-9-12'
        if is_toddler_product(product):
            return 'boys-1-3'
        return 'boys-3-8' if base.startswith('boys') else base

    if base.startswith('girls') or gender == 'girls' or old_slug == 'girls':
        if age in ('12-14', '14-18') or any(a.startswith(('12-', '13-', '14-', '15-', '16-', '17-')) for a in product_age_codes(product)):
            return 'girls-teens'
        if age == '8-12' or any(a in ('8-9y', '9-10y', '10-11y', '11-12y') for a in product_age_codes(product)):
            return 'girls-9-12'
        if is_toddler_product(product):
            return 'girls-1-3'
        return 'girls-3-8' if base.startswith('girls') else base

    if is_toddler_product(product):
        return toddler_parent_for_gender(gender, product.name)
    return base


def normalize_child_suffix(parent_slug, suffix, gender):
    gender = (gender or '').lower()
    if parent_slug == 'boys-1-3':
        if suffix in GIRLS_ONLY_SUFFIXES:
            if suffix == 'frocks-dresses':
                return 'coord-sets'
            if suffix in ('kurta-pajama', 'kurta-sets'):
                return 'kurta-sets'
            return 'coord-sets'
        if suffix == 'kurta-pajama':
            return 'kurta-sets'
        if suffix == 'kurta-sets':
            return 'kurta-sets'
    if parent_slug == 'girls-1-3':
        if suffix in BOYS_ONLY_SUFFIXES:
            return 'coord-sets'
        if suffix in ('kurta-pajama', 'palazzo-kurti'):
            return 'kurta-kurti-sets'
        if suffix == 'kurta-sets':
            return 'kurta-kurti-sets'
    if parent_slug.startswith('girls') and suffix == 'kurta-pajama':
        return 'palazzo-kurti'
    return suffix


def pick_child_suffix(product, parent_slug=None):
    name = (product.name or '').lower()
    gender = (product.gender or '').lower()
    for keywords, suffix in KEYWORD_MAP:
        if any(k in name for k in keywords):
            if suffix == 'kurta-pajama' and gender == 'girls':
                if parent_slug == 'girls-1-3':
                    return 'kurta-kurti-sets'
                return 'palazzo-kurti'
            if parent_slug:
                return normalize_child_suffix(parent_slug, suffix, gender)
            return suffix
    if 'kurta' in name or 'kurti' in name:
        if parent_slug == 'girls-1-3':
            return 'kurta-kurti-sets'
        return 'palazzo-kurti' if gender == 'girls' else 'kurta-pajama'
    if 'frock' in name or 'dress' in name:
        return 'frocks-dresses'
    if 'footed' in name or 'pajama' in name:
        return 'rompers-onesies' if is_newborn_product(product) else 'pyjamas-night-suits'
    if parent_slug == 'boys-1-3':
        return 'coord-sets'
    if parent_slug == 'girls-1-3':
        return 'frocks-dresses' if gender == 'girls' else 'coord-sets'
    return 'coord-sets'


def child_suffix_from_old_slug(old_slug):
    """Extract child suffix from legacy or current parent-child slug."""
    known_parents = sorted([p[0] for p in PARENTS], key=len, reverse=True)
    for legacy in ('toddler',):
        if legacy not in known_parents:
            known_parents.insert(0, legacy)
    for parent in known_parents:
        prefix = f'{parent}-'
        if old_slug.startswith(prefix):
            return old_slug[len(prefix):]
    return None


def migrate_products(cat_by_slug):
    migrated = 0
    for product in Product.query.all():
        old_cat = Category.query.get(product.category_id)
        if old_cat and old_cat.parent_id:
            parent_cat = Category.query.get(old_cat.parent_id)
            old_parent_slug = parent_cat.slug if parent_cat else old_cat.slug
        else:
            old_parent_slug = old_cat.slug if old_cat else 'girls-1-3'

        parent_slug = pick_parent_slug(product, old_parent_slug)
        child_suffix = child_suffix_from_old_slug(old_cat.slug if old_cat else '') or pick_child_suffix(product, parent_slug)
        child_suffix = normalize_child_suffix(parent_slug, child_suffix, product.gender)

        full_slug = f'{parent_slug}-{child_suffix}'
        if full_slug not in cat_by_slug:
            full_slug = parent_slug
        if full_slug in cat_by_slug:
            product.category_id = cat_by_slug[full_slug].id
            migrated += 1
        elif parent_slug in cat_by_slug:
            product.category_id = cat_by_slug[parent_slug].id
            migrated += 1
    return migrated


def delete_legacy_categories(keep_slugs):
    deleted = 0
    for _ in range(20):
        progress = 0
        for cat in Category.query.order_by(Category.parent_id.desc()).all():
            if cat.slug in keep_slugs:
                continue
            if cat.products.count() > 0:
                continue
            if cat.children.filter(Category.slug.notin_(keep_slugs)).count() > 0:
                continue
            db.session.delete(cat)
            progress += 1
            deleted += 1
        if not progress:
            break
        db.session.flush()
    return deleted


def seed_categories():
    with app.app_context():
        db.create_all()
        cat_by_slug = {}

        print('Creating parent categories...')
        for slug, name, desc, sort_order in PARENTS:
            existing = Category.query.filter_by(slug=slug).first()
            if existing:
                existing.name = name
                existing.description = desc
                existing.sort_order = sort_order
                existing.parent_id = None
                existing.is_active = True
                cat = existing
            else:
                cat = Category(
                    name=name, slug=slug, description=desc,
                    sort_order=sort_order, is_active=True,
                )
                db.session.add(cat)
                db.session.flush()
            cat_by_slug[slug] = cat
            print(f'  + {name}')

        print('\nCreating sub-categories...')
        for parent_slug, child_slug, name, sort_order in CHILDREN:
            full_slug = f'{parent_slug}-{child_slug}'
            parent = cat_by_slug[parent_slug]
            existing = Category.query.filter_by(slug=full_slug).first()
            if existing:
                existing.name = name
                existing.parent_id = parent.id
                existing.sort_order = sort_order
                existing.is_active = True
                cat = existing
            else:
                cat = Category(
                    name=name, slug=full_slug, parent_id=parent.id,
                    sort_order=sort_order, is_active=True,
                )
                db.session.add(cat)
                db.session.flush()
            cat_by_slug[full_slug] = cat

        db.session.flush()
        print(f'  Total categories: {len(cat_by_slug)}')

        print('\nMigrating existing products...')
        migrated = migrate_products(cat_by_slug)
        print(f'  Products re-assigned: {migrated}')

        keep_slugs = set(cat_by_slug.keys())
        print('\nDeleting old categories...')
        deleted = delete_legacy_categories(keep_slugs)
        print(f'  Old categories removed: {deleted}')

        db.session.commit()

        parents = Category.query.filter_by(parent_id=None).count()
        children = Category.query.filter(Category.parent_id.isnot(None)).count()
        print(f'\nDone! {parents} parent + {children} sub-categories active.')
        print(f'Products: {Product.query.count()}')


if __name__ == '__main__':
    seed_categories()
