"""Tests for service layer."""
import pytest
from decimal import Decimal

from app.extensions import db
from app.models.product import ProductVariant
from app.services.inventory_service import (
    check_stock, reduce_stock, restore_stock, get_low_stock_products,
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
