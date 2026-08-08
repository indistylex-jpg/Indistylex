"""Tests for lifestyle image slug mapping."""
from app.utils.lifestyle_images import category_lifestyle_image_key


def test_boys_categories_use_boy_photos():
    assert category_lifestyle_image_key('boys-3-8') == 'everyday_boy'
    assert category_lifestyle_image_key('boys-9-12') == 'everyday_boy'
    assert category_lifestyle_image_key('boys-teens') == 'teen_boy'
    assert category_lifestyle_image_key('boys') == 'everyday_boy'


def test_girls_categories_use_girl_photos():
    assert category_lifestyle_image_key('girls-3-8') == 'everyday_girl'
    assert category_lifestyle_image_key('girls-9-12') == 'everyday_girl'
    assert category_lifestyle_image_key('girls-teens') == 'school_girl'
    assert category_lifestyle_image_key('girls') == 'everyday_girl'


def test_neutral_categories_use_appropriate_photos():
    assert category_lifestyle_image_key('newborn-infant') == 'hero_baby'
    assert category_lifestyle_image_key('boys-1-3') == 'everyday_boy'
    assert category_lifestyle_image_key('girls-1-3') == 'everyday_girl'
    assert category_lifestyle_image_key('toddler') == 'hero_collection'
    assert category_lifestyle_image_key('winter-wear') == 'winter_kids'
