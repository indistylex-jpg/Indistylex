"""Tests for curated homepage / nav category links."""
from app.utils.home_categories import (
    nav_display_categories,
    nav_marquee_links,
    visible_home_category_tiles,
)


class _Cat:
    def __init__(self, slug, name):
        self.slug = slug
        self.name = name


def test_home_tiles_have_single_boys_and_girls():
    slugs = {
        'newborn-infant', 'toddler', 'boys-3-8', 'boys-teens',
        'girls-3-8', 'girls-teens', 'ethnic-festive', 'winter-wear',
    }
    tiles = visible_home_category_tiles(slugs)
    labels = [t['label'] for t in tiles]
    assert labels.count('Boys') == 1
    assert labels.count('Girls') == 1


def test_marquee_has_no_trailing_duplicate_boys_girls():
    slugs = {
        'newborn-infant', 'toddler', 'boys-3-8', 'boys-teens',
        'girls-3-8', 'girls-teens', 'ethnic-festive', 'winter-wear',
    }
    links = nav_marquee_links(slugs)
    labels = [link['label'] for link in links]
    assert labels.count('Boys') == 1
    assert labels.count('Girls') == 1
    assert 'New Arrivals' in labels


def test_nav_display_categories_hides_redundant_age_bands():
    cats = [
        _Cat('boys-3-8', 'Boys (3–8 Years)'),
        _Cat('boys-9-12', 'Boys (9–12 Years)'),
        _Cat('girls-3-8', 'Girls (3–8 Years)'),
        _Cat('girls-9-12', 'Girls (9–12 Years)'),
    ]
    displayed = nav_display_categories(cats)
    assert [c.slug for c in displayed] == ['boys-3-8', 'girls-3-8']
