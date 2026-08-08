#!/usr/bin/env python3
"""
Replace Indistylex categories with full 0–18 catalog.

Deletes old categories (newborn, toddler, boys, girls, etc.) after
re-assigning existing products to the best matching new sub-category.

Run on server:
  cd /var/www/html/indistylex
  source venv/bin/activate
  python seed_categories.py
"""
from app import create_app
from app.extensions import db
from app.models.product import Category, Product

app = create_app()

# ── Level 1: parent categories ──────────────────────────────────────
PARENTS = [
    ('newborn-infant', 'Newborn & Infant (0–12M)',
     'Soft essentials for 0–12 months — rompers, bodysuits, swaddles', 1),
    ('toddler', 'Toddler (1–3 Years)',
     'Comfy everyday wear for active toddlers', 2),
    ('boys-3-8', 'Boys (3–8 Years)',
     'Daily & festive wear for young boys', 3),
    ('boys-9-12', 'Boys (9–12 Years)',
     'Juniors — school, casual & ethnic for pre-teens', 4),
    ('boys-teens', 'Boys Teens (13–18 Years)',
     'Teen boys — shirts, jeans, kurtas, co-ords', 5),
    ('girls-3-8', 'Girls (3–8 Years)',
     'Frocks, sets & ethnic for young girls', 6),
    ('girls-9-12', 'Girls (9–12 Years)',
     'Juniors — dresses, kurtis, lehengas for pre-teens', 7),
    ('girls-teens', 'Girls Teens (13–18 Years)',
     'Teen girls — kurtis, co-ords, western & ethnic', 8),
    ('ethnic-festive', 'Ethnic & Festive Wear',
     'Diwali, wedding, puja — all ages', 9),
    ('nightwear', 'Nightwear & Loungewear',
     'Pyjamas, night suits, robes — all ages', 10),
    ('winter-wear', 'Winter Wear',
     'Sweaters, jackets, thermals, hoodies', 11),
    ('school-wear', 'School Wear',
     'Shirts, pants, skirts, uniforms', 12),
    ('activewear', 'Activewear & Sportswear',
     'Track suits, joggers, sports tees', 13),
    ('baby-essentials', 'Baby Essentials & Accessories',
     'Caps, bibs, booties, mittens, blankets', 14),
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
    # Toddler
    ('toddler', 'dungarees-jumpsuits', 'Dungarees & Jumpsuits', 1),
    ('toddler', 'coord-sets', 'Co-ord Sets', 2),
    ('toddler', 'frocks-dresses', 'Frocks & Dresses', 3),
    ('toddler', 'jogger-sets', 'Jogger Sets', 4),
    ('toddler', 'kurta-sets', 'Kurta Sets (Toddler)', 5),
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
    'toddler': 'toddler',
    'boys': 'boys-3-8',
    'girls': 'girls-3-8',
    'men': 'boys-teens',
    'women': 'girls-teens',
    'kids': 'toddler',
}


def pick_parent_slug(product, old_slug):
    age = product.age_group or ''
    gender = (product.gender or '').lower()
    if old_slug in LEGACY_PARENT:
        base = LEGACY_PARENT[old_slug]
    else:
        base = old_slug if old_slug in {p[0] for p in PARENTS} else 'toddler'

    if base.startswith('boys') or gender == 'boys' or (old_slug == 'boys'):
        if age in ('12-14', '14-18'):
            return 'boys-teens'
        if age in ('8-12', '6-8') and any(x in (product.name or '').lower() for x in ('9-10', '11-12')):
            return 'boys-9-12'
        if age == '8-12':
            return 'boys-9-12'
        return 'boys-3-8' if base.startswith('boys') else base

    if base.startswith('girls') or gender == 'girls' or old_slug == 'girls':
        if age in ('12-14', '14-18'):
            return 'girls-teens'
        if age == '8-12':
            return 'girls-9-12'
        return 'girls-3-8' if base.startswith('girls') else base

    if old_slug == 'newborn' or age == '0-2':
        return 'newborn-infant'
    if old_slug == 'toddler' or age == '2-4':
        return 'toddler'
    return base


def pick_child_suffix(product):
    name = (product.name or '').lower()
    gender = (product.gender or '').lower()
    for keywords, suffix in KEYWORD_MAP:
        if any(k in name for k in keywords):
            if suffix == 'kurta-pajama' and gender == 'girls':
                return 'palazzo-kurti'
            return suffix
    if 'kurta' in name or 'kurti' in name:
        return 'palazzo-kurti' if gender == 'girls' else 'kurta-pajama'
    if 'frock' in name:
        return 'frocks-dresses'
    if 'footed' in name or 'pajama' in name:
        return 'rompers-onesies' if product.age_group == '0-2' else 'pyjamas-night-suits'
    return 'coord-sets'


def migrate_products(cat_by_slug):
    migrated = 0
    for product in Product.query.all():
        old_cat = Category.query.get(product.category_id)
        old_slug = old_cat.slug if old_cat else 'toddler'
        parent_slug = pick_parent_slug(product, old_slug)
        child_suffix = pick_child_suffix(product)
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
