"""Tests for SKU / HSN helpers."""
from app.utils.sku_hsn import (
    build_sku,
    color_to_code,
    product_type_to_code,
    suggest_hsn_code,
    suggest_variant_rows,
)


def test_product_type_codes():
    assert product_type_to_code('frock') == 'FRK'
    assert product_type_to_code('shirt') == 'SHT'
    assert product_type_to_code('unknown') == 'ACC'


def test_hsn_for_kids_garments():
    assert suggest_hsn_code('frock') == '6204'
    assert suggest_hsn_code('romper') == '6111'
    assert suggest_hsn_code('shirt') == '6205'


def test_build_sku_format():
    sku = build_sku('frock', '2-3Y', 'Pink', sequence=7)
    assert sku == 'IX-FRK-007-2-3Y-PNK'


def test_color_to_code():
    assert color_to_code('Pink') == 'PNK'
    assert color_to_code('navy') == 'NVY'


def test_suggest_variant_rows(db, sample_product):
    rows = suggest_variant_rows('frock', 'Pink', ['2-3y', '3-4y'])
    assert len(rows) == 2
    assert rows[0]['size'] == '2-3Y'
    assert rows[0]['sku'].startswith('IX-FRK-')
    assert rows[0]['sku'] != rows[1]['sku']
