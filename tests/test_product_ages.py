"""Tests for multi age group helpers."""
from app.models.product import Product
from app.utils.product_ages import (
    normalize_age_groups, parse_age_groups, age_groups_display, apply_age_group_filter,
)


class TestProductAges:

    def test_normalize_age_groups(self):
        assert normalize_age_groups(['6-8', '2-4', '4-6']) == ['2-4', '4-6', '6-8']

    def test_parse_legacy_single_age(self):
        assert parse_age_groups(None, '4-6') == ['4-6']

    def test_age_groups_display_range(self):
        assert '2–4 Years' in age_groups_display(['2-4', '4-6', '6-8'])

    def test_product_set_multiple_ages(self, db, sample_category):
        product = Product(
            name='Multi Age Dress',
            slug='multi-age-dress',
            price=500,
            category_id=sample_category.id,
            is_active=True,
        )
        product.set_age_groups_list(['6-8', '2-4', '4-6'])
        db.session.add(product)
        db.session.commit()

        assert product.age_groups == '2-4,4-6,6-8'
        assert product.age_group is None
        assert product.age_groups_list == ['2-4', '4-6', '6-8']

    def test_age_filter_matches_multi_age_product(self, db, sample_category):
        product = Product(
            name='Wide Range Top',
            slug='wide-range-top',
            price=400,
            category_id=sample_category.id,
            is_active=True,
        )
        product.set_age_groups_list(['2-4', '4-6', '6-8'])
        db.session.add(product)
        db.session.commit()

        query = apply_age_group_filter(Product.query, '6-8', Product)
        assert product in query.all()

        query = apply_age_group_filter(Product.query, '8-12', Product)
        assert product not in query.all()
