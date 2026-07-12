"""Tests for service layer."""
import pytest
from decimal import Decimal

from app.extensions import db
from app.models.product import ProductVariant
from app.services.inventory_service import (
    check_stock, reduce_stock, restore_stock, get_low_stock_products,
    record_b2b_sale, cancel_b2b_sale,
)


# ────────────────────────── Inventory Service ──────────────────────────

class TestInventoryService:

    def test_check_stock_available(self, db, sample_product):
        variant = sample_product.variants.first()
        available, msg = check_stock(variant.id, 5)
        assert available is True
        assert 'stock' in msg.lower() or 'In stock' in msg

    def test_check_stock_insufficient(self, db, sample_product):
        variant = sample_product.variants.first()
        available, msg = check_stock(variant.id, 999)
        assert available is False
        assert 'available' in msg.lower()

    def test_check_stock_invalid_variant(self, db):
        available, msg = check_stock(99999, 1)
        assert available is False

    def test_check_stock_inactive_variant(self, db, sample_product):
        variant = sample_product.variants.first()
        variant.is_active = False
        db.session.commit()
        available, msg = check_stock(variant.id, 1)
        assert available is False

    def test_reduce_stock(self, db, sample_product):
        variant = sample_product.variants.first()
        initial = variant.stock_quantity
        result = reduce_stock(variant.id, 3)
        assert result is True
        db.session.refresh(variant)
        assert variant.stock_quantity == initial - 3

    def test_reduce_stock_insufficient(self, db, sample_product):
        variant = sample_product.variants.first()
        result = reduce_stock(variant.id, 999)
        assert result is False

    def test_reduce_stock_invalid_variant(self, db):
        result = reduce_stock(99999, 1)
        assert result is False

    def test_restore_stock(self, db, sample_product):
        variant = sample_product.variants.first()
        initial = variant.stock_quantity
        result = restore_stock(variant.id, 5)
        assert result is True
        db.session.refresh(variant)
        assert variant.stock_quantity == initial + 5

    def test_restore_stock_invalid_variant(self, db):
        result = restore_stock(99999, 1)
        assert result is False

    def test_get_low_stock_products(self, db, sample_product):
        # Set one variant to low stock
        variant = sample_product.variants.first()
        variant.stock_quantity = 2
        db.session.commit()

        low = get_low_stock_products(threshold=5)
        assert any(v.id == variant.id for v in low)

    def test_get_low_stock_empty(self, db, sample_product):
        # All have 10 stock, threshold 5 → none
        low = get_low_stock_products(threshold=5)
        assert len(low) == 0

    def test_record_b2b_sale(self, db, sample_product, admin_user):
        variant = sample_product.variants.first()
        initial_stock = variant.stock_quantity

        sale, error = record_b2b_sale(
            shop_name='Fashion Point',
            items=[{'variant_id': variant.id, 'quantity': 3}],
            created_by_id=admin_user.id,
            shop_city='Prayagraj',
        )
        assert error is None
        assert sale.sale_number.startswith('B2B-')
        assert sale.item_count == 3
        db.session.refresh(variant)
        assert variant.stock_quantity == initial_stock - 3

    def test_record_b2b_sale_insufficient_stock(self, db, sample_product, admin_user):
        variant = sample_product.variants.first()
        sale, error = record_b2b_sale(
            shop_name='Test Shop',
            items=[{'variant_id': variant.id, 'quantity': 999}],
            created_by_id=admin_user.id,
        )
        assert sale is None
        assert 'available' in error.lower()

    def test_cancel_b2b_sale_restores_stock(self, db, sample_product, admin_user):
        variant = sample_product.variants.first()
        initial_stock = variant.stock_quantity

        sale, _ = record_b2b_sale(
            shop_name='Test Shop',
            items=[{'variant_id': variant.id, 'quantity': 2}],
            created_by_id=admin_user.id,
        )
        ok, error = cancel_b2b_sale(sale.id)
        assert ok is True
        assert error is None
        db.session.refresh(variant)
        assert variant.stock_quantity == initial_stock

    def test_record_b2b_sale_with_flat_discount(self, db, sample_product, admin_user):
        variant = sample_product.variants.first()
        sale, error = record_b2b_sale(
            shop_name='Fashion Point',
            items=[{'variant_id': variant.id, 'quantity': 2, 'unit_price': 100}],
            created_by_id=admin_user.id,
            extra_discount=50,
            discount_reason='Shop requested',
        )
        assert error is None
        assert float(sale.subtotal) == 200
        assert float(sale.total) == 150
        assert sale.discount_reason == 'Shop requested'

    def test_record_b2b_sale_with_percent_discount(self, db, sample_product, admin_user):
        variant = sample_product.variants.first()
        sale, error = record_b2b_sale(
            shop_name='Fashion Point',
            items=[{'variant_id': variant.id, 'quantity': 2, 'unit_price': 100}],
            created_by_id=admin_user.id,
            discount_percent=10,
        )
        assert error is None
        assert float(sale.subtotal) == 200
        assert float(sale.total) == 180
