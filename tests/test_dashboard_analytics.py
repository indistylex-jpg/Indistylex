"""Tests for admin dashboard analytics."""
from app.services.dashboard_analytics_service import (
    get_gender_category_inventory,
    _normalize_gender,
    _build_gender_bar,
)


def test_normalize_gender():
    assert _normalize_gender('boys') == 'boys'
    assert _normalize_gender('girl') == 'girls'
    assert _normalize_gender('kids') == 'kids'


def test_build_gender_bar_segments():
    raw = [
        {'name': 'Boys 3-8', 'slug': 'boys-3-8', 'products': 5, 'stock': 100},
        {'name': 'Boys Teens', 'slug': 'boys-teens', 'products': 2, 'stock': 50},
    ]
    bar = _build_gender_bar(raw, ['#2563EB', '#60A5FA'])
    assert bar['total_stock'] == 150
    assert len(bar['segments']) == 2
    assert bar['segments'][0]['pct'] == round(100 / 150 * 100, 2)


def test_gender_category_inventory_structure(app, db):
    with app.app_context():
        data = get_gender_category_inventory()
        assert 'boys' in data
        assert 'girls' in data
        assert 'segments' in data['boys']
        assert 'total_stock' in data['girls']
