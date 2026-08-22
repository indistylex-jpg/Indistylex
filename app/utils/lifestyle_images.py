"""Original Indistylex lifestyle images (AI-generated, royalty-free)."""

LIFESTYLE_IMAGES = {
    'hero_sale': 'images/lifestyle/hero-sale-indian-girl.jpg',
    'hero_collection': 'images/lifestyle/hero-collection-indian-kids.jpg',
    'hero_baby': 'images/lifestyle/hero-baby-indian.jpg',
    'everyday_boy': 'images/lifestyle/lifestyle-everyday-boy.jpg',
    'everyday_girl': 'images/lifestyle/lifestyle-everyday-girl.jpg',
    'ethnic_boy': 'images/lifestyle/lifestyle-ethnic-boy.jpg',
    'ethnic_girl': 'images/lifestyle/lifestyle-ethnic-girl.jpg',
    'winter_kids': 'images/lifestyle/lifestyle-winter-kids.jpg',
    'school_girl': 'images/lifestyle/lifestyle-school-girl.jpg',
    'teen_boy': 'images/lifestyle/lifestyle-teen-boy.jpg',
    'product_placeholder': 'images/lifestyle/product-placeholder-kids.jpg',
    'moment_parent': 'images/lifestyle/moment-parent-girl.jpg',
}

# Map category slugs to the correct gender/age lifestyle photo.
CATEGORY_IMAGE_BY_SLUG = {
    'newborn-infant': 'hero_baby',
    'newborn': 'hero_baby',
    'baby-essentials': 'hero_baby',
    'toddler': 'hero_collection',
    'boys-1-3': 'everyday_boy',
    'girls-1-3': 'everyday_girl',
    'boys-3-8': 'everyday_boy',
    'boys-9-12': 'everyday_boy',
    'boys-teens': 'teen_boy',
    'boys': 'everyday_boy',
    'girls-3-8': 'everyday_girl',
    'girls-9-12': 'everyday_girl',
    'girls-teens': 'school_girl',
    'girls': 'everyday_girl',
    'ethnic-festive': 'ethnic_boy',
    'nightwear': 'hero_baby',
    'winter-wear': 'winter_kids',
    'school-wear': 'school_girl',
    'activewear': 'everyday_boy',
}

MOMENT_IMAGES = [
    LIFESTYLE_IMAGES['moment_parent'],
    LIFESTYLE_IMAGES['everyday_girl'],
    LIFESTYLE_IMAGES['everyday_boy'],
    LIFESTYLE_IMAGES['school_girl'],
    LIFESTYLE_IMAGES['teen_boy'],
    LIFESTYLE_IMAGES['hero_collection'],
]

PRODUCT_PLACEHOLDER = LIFESTYLE_IMAGES['product_placeholder']

# Homepage "Find Their Perfect Fit" circular category photos.
FIT_CHIP_IMAGES = {
    'girls-frocks': 'images/fit-chips/girls-frocks.jpg',
    'girls-dresses': 'images/fit-chips/girls-dresses.jpg',
    'girls-ethnic': 'images/fit-chips/girls-ethnic.jpg',
    'boys-tshirts': 'images/fit-chips/boys-tshirts.jpg',
    'boys-shorts': 'images/fit-chips/boys-shorts.jpg',
    'boys-kurtas': 'images/fit-chips/boys-kurtas.jpg',
    'newborn': 'images/fit-chips/newborn.jpg',
    'school': 'images/fit-chips/school.jpg',
    'shop-all': 'images/fit-chips/shop-all.jpg',
}

FIT_CHIP_ITEMS = [
    {
        'gender': 'girls',
        'chip': 'girls-frocks',
        'label': 'Frocks',
        'route': 'shop.listing',
        'kwargs': {'gender': 'girls'},
    },
    {
        'gender': 'girls',
        'chip': 'girls-dresses',
        'label': 'Dresses',
        'route': 'shop.listing',
        'kwargs': {'gender': 'girls'},
    },
    {
        'gender': 'girls',
        'chip': 'girls-ethnic',
        'label': 'Ethnic',
        'route': 'shop.category',
        'kwargs': {'slug': 'ethnic-festive'},
    },
    {
        'gender': 'boys',
        'chip': 'boys-tshirts',
        'label': 'T-Shirts',
        'route': 'shop.listing',
        'kwargs': {'gender': 'boys'},
    },
    {
        'gender': 'boys',
        'chip': 'boys-shorts',
        'label': 'Shorts',
        'route': 'shop.listing',
        'kwargs': {'gender': 'boys'},
    },
    {
        'gender': 'boys',
        'chip': 'boys-kurtas',
        'label': 'Kurtas',
        'route': 'shop.listing',
        'kwargs': {'gender': 'boys'},
    },
    {
        'gender': 'all',
        'chip': 'newborn',
        'label': 'Newborn',
        'route': 'shop.listing',
        'kwargs': {'age_group': '0-3m'},
    },
    {
        'gender': 'all',
        'chip': 'school',
        'label': 'School',
        'route': 'shop.category',
        'kwargs': {'slug': 'school-wear'},
    },
    {
        'gender': 'all',
        'chip': 'shop-all',
        'label': 'Shop All',
        'route': 'shop.listing',
        'kwargs': {},
    },
]


def fit_chip_image_path(chip_key):
    """Return static relative path for a fit-chip image key."""
    return FIT_CHIP_IMAGES.get(chip_key, FIT_CHIP_IMAGES['shop-all'])


def category_lifestyle_image_key(slug):
    """Return lifestyle image key for a category slug (boys/girls aware)."""
    if not slug:
        return 'hero_collection'

    key = CATEGORY_IMAGE_BY_SLUG.get(slug)
    if key:
        return key

    slug_lower = slug.lower()
    if 'boys' in slug_lower or slug_lower.startswith('boy'):
        return 'teen_boy' if 'teen' in slug_lower else 'everyday_boy'
    if 'girls' in slug_lower or slug_lower.startswith('girl'):
        return 'school_girl' if 'teen' in slug_lower or '9-12' in slug_lower else 'everyday_girl'
    if 'baby' in slug_lower or 'newborn' in slug_lower or 'infant' in slug_lower:
        return 'hero_baby'
    if 'ethnic' in slug_lower or 'festive' in slug_lower:
        return 'ethnic_girl'
    if 'winter' in slug_lower:
        return 'winter_kids'
    if 'school' in slug_lower:
        return 'school_girl'
    if 'night' in slug_lower or 'lounge' in slug_lower:
        return 'hero_baby'
    if 'active' in slug_lower or 'sport' in slug_lower:
        return 'everyday_boy'
    return 'hero_collection'


def category_lifestyle_image_path(slug):
    """Return static relative path for a category slug."""
    return LIFESTYLE_IMAGES[category_lifestyle_image_key(slug)]
