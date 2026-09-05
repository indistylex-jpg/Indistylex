"""Tests for AI product vision autofill."""
from app.services.product_vision_service import (
    _normalize_result,
    _parse_ai_json,
    _resolve_category_id,
    build_category_catalog,
)


SAMPLE_CATALOG = [
    {'id': 1, 'name': 'Frocks & Dresses', 'slug': 'frocks-dresses', 'parent': 'Girls'},
    {'id': 2, 'name': 'Shirts & Formal', 'slug': 'shirts-formal', 'parent': 'Boys'},
    {'id': 3, 'name': 'Kurta Pajama', 'slug': 'kurta-pajama', 'parent': 'Boys'},
]


class TestProductVisionService:
    def test_parse_ai_json_strips_markdown(self):
        raw = '```json\n{"name": "Pink Frock"}\n```'
        data = _parse_ai_json(raw)
        assert data['name'] == 'Pink Frock'

    def test_normalize_result_maps_fields(self):
        raw = {
            'name': 'Cotton Frock — Floral Pink',
            'product_type': 'frock',
            'gender': 'girls',
            'primary_color': 'Pink',
            'material': '100% Cotton',
            'quality_notes': 'Soft finish',
            'short_description': 'Pretty pink frock for parties',
            'description': 'Light cotton frock. Machine wash cold.',
            'category_id': 1,
            'suggested_price': 499,
            'suggested_compare_price': 899,
            'age_groups': ['3-4y', '4-5y'],
            'variant_color': 'Pink',
        }
        result = _normalize_result(raw, SAMPLE_CATALOG)
        assert result['name'] == 'Cotton Frock — Floral Pink'
        assert result['category_id'] == 1
        assert result['gender'] == 'girls'
        assert result['price'] == 499.0
        assert '3-4y' in result['age_groups']
        assert 'Cotton' in result['material']

    def test_resolve_category_from_product_type(self):
        raw = {'product_type': 'kurta', 'name': 'Ethnic wear'}
        cat_id = _resolve_category_id(raw, SAMPLE_CATALOG)
        assert cat_id == 3

    def test_build_category_catalog(self):
        groups = [{
            'label': 'Girls',
            'options': [{'id': 10, 'name': 'Dresses', 'slug': 'dresses'}],
        }]
        catalog = build_category_catalog(groups)
        assert catalog[0]['id'] == 10
        assert catalog[0]['parent'] == 'Girls'
