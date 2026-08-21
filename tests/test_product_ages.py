"""Tests for multi age group helpers."""
from app.models.product import Product
from app.utils.product_ages import (
    normalize_age_groups, parse_age_groups, age_groups_display, apply_age_group_filter,
    LEGACY_AGE_EXPANSION,
)


class TestProductAges:

    def test_normalize_age_groups(self):
        assert normalize_age_groups(['2-3y', '1-2y', '1y']) == ['1y', '1-2y', '2-3y']

    def test_parse_legacy_single_age(self):
        assert parse_age_groups(None, '4-6') == ['4-5y', '5-6y']

    def test_parse_legacy_stored_list(self):
        assert parse_age_groups('2-4,4-6', None) == ['2-3y', '3-4y', '4-5y', '5-6y']

    def test_age_groups_display_range(self):
        display = age_groups_display(['1y', '1-2y', '2-3y', '4-5y'])
        assert '1–3 Years' in display
        assert '4–5 Years' in display

    def test_age_groups_display_months(self):
        display = age_groups_display(['6-9m', '9-12m'])
        assert '6–12 Months' in display

    def test_product_set_multiple_ages(self, db, sample_category):
        product = Product(
            name='Multi Age Dress',
            slug='multi-age-dress',
            price=500,
            category_id=sample_category.id,
            is_active=True,
        )
        product.set_age_groups_list(['2-3y', '1-2y', '1y'])
        db.session.add(product)
        db.session.commit()

        assert product.age_groups == '1y,1-2y,2-3y'
        assert product.age_group is None
        assert product.age_groups_list == ['1y', '1-2y', '2-3y']

    def test_age_filter_matches_multi_age_product(self, db, sample_category):
        product = Product(
            name='Wide Range Top',
            slug='wide-range-top',
            price=400,
            category_id=sample_category.id,
            is_active=True,
        )
        product.set_age_groups_list(['1-2y', '2-3y', '3-4y'])
        db.session.add(product)
        db.session.commit()

        query = apply_age_group_filter(Product.query, '2-3y', Product)
        assert product in query.all()

        query = apply_age_group_filter(Product.query, '6-7y', Product)
        assert product not in query.all()

    def test_age_filter_matches_legacy_stored_product(self, db, sample_category):
        product = Product(
            name='Legacy Band Top',
            slug='legacy-band-top',
            price=400,
            category_id=sample_category.id,
            is_active=True,
            age_groups='4-6,6-8',
        )
        db.session.add(product)
        db.session.commit()

        query = apply_age_group_filter(Product.query, '5-6y', Product)
        assert product in query.all()

        query = apply_age_group_filter(Product.query, '7-8y', Product)
        assert product in query.all()

    def test_legacy_expansion_covers_all_old_bands(self):
        old_bands = ['0-2', '2-4', '4-6', '6-8', '8-12', '12-14', '14-18']
        for band in old_bands:
            assert band in LEGACY_AGE_EXPANSION
