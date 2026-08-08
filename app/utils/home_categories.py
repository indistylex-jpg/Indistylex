"""Curated shop links for homepage and navigation (one Boys / Girls entry each)."""

HOME_CATEGORY_TILES = [
    {
        'label': 'Newborn & Infant',
        'image_slug': 'newborn-infant',
        'endpoint': 'shop.category',
        'kwargs': {'slug': 'newborn-infant'},
    },
    {
        'label': 'Toddler',
        'image_slug': 'toddler',
        'endpoint': 'shop.category',
        'kwargs': {'slug': 'toddler'},
    },
    {
        'label': 'Boys',
        'image_slug': 'boys-3-8',
        'endpoint': 'shop.listing',
        'kwargs': {'gender': 'boys'},
    },
    {
        'label': 'Girls',
        'image_slug': 'girls-3-8',
        'endpoint': 'shop.listing',
        'kwargs': {'gender': 'girls'},
    },
    {
        'label': 'Boys Teens',
        'image_slug': 'boys-teens',
        'endpoint': 'shop.category',
        'kwargs': {'slug': 'boys-teens'},
    },
    {
        'label': 'Girls Teens',
        'image_slug': 'girls-teens',
        'endpoint': 'shop.category',
        'kwargs': {'slug': 'girls-teens'},
    },
    {
        'label': 'Ethnic & Festive',
        'image_slug': 'ethnic-festive',
        'endpoint': 'shop.category',
        'kwargs': {'slug': 'ethnic-festive'},
    },
    {
        'label': 'Winter Wear',
        'image_slug': 'winter-wear',
        'endpoint': 'shop.category',
        'kwargs': {'slug': 'winter-wear'},
    },
]

# Junior age bands covered by the main Boys / Girls shop links.
REDUNDANT_CATEGORY_SLUGS = frozenset({'boys-9-12', 'girls-9-12'})

MARQUEE_EXTRA_LINKS = [
    {
        'label': 'New Arrivals',
        'endpoint': 'shop.listing',
        'kwargs': {'sort': 'newest'},
    },
]


def visible_home_category_tiles(categories_by_slug):
    """Category tiles whose target category exists (gender links always shown)."""
    visible = []
    for tile in HOME_CATEGORY_TILES:
        if tile['endpoint'] == 'shop.listing':
            visible.append(tile)
        elif tile['kwargs'].get('slug') in categories_by_slug:
            visible.append(tile)
    return visible


def nav_marquee_links(categories_by_slug):
    """Ticker links — no duplicate Boys / Girls labels."""
    return visible_home_category_tiles(categories_by_slug) + MARQUEE_EXTRA_LINKS


def nav_display_categories(active_categories):
    """Category lists for menus/footer without duplicate age-band parents."""
    return [c for c in active_categories if c.slug not in REDUNDANT_CATEGORY_SLUGS]
