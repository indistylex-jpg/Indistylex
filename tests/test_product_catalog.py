"""Tests for product catalog admin helpers."""
from decimal import Decimal
from io import BytesIO

from werkzeug.datastructures import MultiDict
from flask import request

from app.models.product import Category
from app.services.product_catalog_service import (
    validate_product_submission,
    unique_product_slug,
    listing_preview,
    get_store_visibility_counts,
    suggested_gender_for_category,
    product_form_draft_context,
)
from app.forms.product_forms import ProductForm


class TestProductCatalogService:
    def test_unique_product_slug(self, db, sample_product):
        slug = unique_product_slug('Baby Romper')
        assert slug == 'baby-romper-2'

    def test_suggested_gender_for_boys_category(self, db):
        parent = Category(name='Boys 3-8', slug='boys-3-8', is_active=True)
        db.session.add(parent)
        db.session.commit()
        assert suggested_gender_for_category(parent.id) == 'boys'

    def test_validate_requires_ages(self, app, sample_category):
        with app.app_context():
            form = ProductForm()
            form.category_id.data = sample_category.id
            form.is_active.data = True
            form.gender.data = 'boys'
            form.price.data = Decimal('100')
            data = MultiDict([
                ('variant_size[]', '3-4Y'),
                ('variant_color[]', 'Blue'),
                ('variant_sku[]', 'TEST-SKU-1'),
                ('variant_stock[]', '5'),
            ])
            errors = validate_product_submission(form, data, MultiDict(), is_new=True)
            assert any('age' in e.lower() for e in errors)

    def test_listing_preview_new_arrival(self, db, sample_product):
        sample_product.is_new_arrival = True
        places = listing_preview(sample_product)
        assert any('New Arrivals' in p for p in places)

    def test_store_visibility_counts(self, db, sample_product):
        sample_product.is_new_arrival = True
        db.session.commit()
        counts = get_store_visibility_counts()
        assert counts['new_arrival'] >= 1

    def test_product_form_draft_context_repops_from_post(self, app, sample_category):
        with app.test_request_context(method='POST', data={
            'age_groups': ['3-4y', '4-5y'],
            'variant_size[]': ['3-4Y', '5-6Y'],
            'variant_color[]': ['Pink', 'Blue'],
            'variant_sku[]': ['SKU-1', 'SKU-2'],
            'variant_stock[]': ['5', '8'],
        }):
            draft = product_form_draft_context(request.form)
        assert '3-4y' in draft['selected_age_groups']
        assert len(draft['variant_draft_rows']) == 2
        assert draft['variant_draft_rows'][0]['sku'] == 'SKU-1'
        assert draft['variant_draft_rows'][1]['stock'] == 8
