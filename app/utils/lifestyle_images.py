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

# Rotating sets for grids / carousels
CATEGORY_IMAGES = [
    LIFESTYLE_IMAGES['hero_baby'],
    LIFESTYLE_IMAGES['everyday_girl'],
    LIFESTYLE_IMAGES['everyday_boy'],
    LIFESTYLE_IMAGES['ethnic_girl'],
    LIFESTYLE_IMAGES['ethnic_boy'],
    LIFESTYLE_IMAGES['winter_kids'],
]

MOMENT_IMAGES = [
    LIFESTYLE_IMAGES['moment_parent'],
    LIFESTYLE_IMAGES['everyday_girl'],
    LIFESTYLE_IMAGES['everyday_boy'],
    LIFESTYLE_IMAGES['school_girl'],
    LIFESTYLE_IMAGES['teen_boy'],
    LIFESTYLE_IMAGES['hero_collection'],
]

PRODUCT_PLACEHOLDER = LIFESTYLE_IMAGES['product_placeholder']
