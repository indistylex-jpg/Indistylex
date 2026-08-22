"""Tests for service layer."""
import os
import pytest
from decimal import Decimal

from app.extensions import db
from app.models.product import ProductVariant
from app.services.inventory_service import (
    check_stock, reduce_stock, restore_stock, get_low_stock_products,
    record_b2b_sale, cancel_b2b_sale, build_inventory_query, inventory_stock_status,
)
from app.services.inventory_export_service import export_inventory_xlsx, variant_to_export_row


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

    def test_inventory_stock_status(self):
        assert inventory_stock_status(0) == 'Out of Stock'
        assert inventory_stock_status(5) == 'Low Stock'
        assert inventory_stock_status(11) == 'In Stock'

    def test_build_inventory_query_filters_low_stock(self, db, sample_product):
        variant = sample_product.variants.first()
        variant.stock_quantity = 4
        db.session.commit()

        rows = build_inventory_query(stock_filter='low').all()
        assert any(v.id == variant.id for v in rows)

    def test_export_inventory_xlsx(self, db, sample_product):
        variants = build_inventory_query().all()
        buffer, filename = export_inventory_xlsx(variants)
        assert filename.endswith('.xlsx')
        assert buffer.getvalue()[:2] == b'PK'

        variant = sample_product.variants.first()
        row = variant_to_export_row(variant)
        assert row['sku'] == variant.sku
        assert row['product_name'] == sample_product.name

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


# ────────────────────────── Image Service ──────────────────────────

class TestImageService:

    def test_normalize_legacy_static_path(self):
        from app.services.image_service import normalize_stored_image_path
        assert normalize_stored_image_path('/static/uploads/products/abc.jpg') == '/uploads/products/abc.jpg'

    def test_normalize_relative_path(self):
        from app.services.image_service import normalize_stored_image_path
        assert normalize_stored_image_path('products/abc.jpg') == '/uploads/products/abc.jpg'

    def test_resolve_image_url_relative(self, app):
        from app.services.image_service import resolve_image_url
        with app.app_context():
            url = resolve_image_url('products/abc.jpg')
            assert url == '/uploads/products/abc.jpg'

    def test_resolve_image_url_legacy(self, app):
        from app.services.image_service import resolve_image_url
        with app.app_context():
            url = resolve_image_url('/static/uploads/products/abc.jpg')
            assert url == '/uploads/products/abc.jpg'

    def test_image_disk_path(self, app):
        from app.services.image_service import image_disk_path
        with app.app_context():
            path = image_disk_path('/static/uploads/products/abc.jpg')
            assert path.endswith(os.path.join('uploads', 'products', 'abc.jpg').replace('\\', '/')) or 'products/abc.jpg' in path.replace('\\', '/')

class TestExpenseService:

    def test_record_manual_expense(self, db, admin_user):
        from app.services.expense_service import record_expense, get_expense_totals
        from app.models.expense import Expense

        expense, error = record_expense(
            amount=500,
            category='marketing',
            description='Facebook ads',
            created_by_id=admin_user.id,
            payment_method='upi',
        )
        assert error is None
        assert expense.id is not None
        assert float(expense.amount) == 500

        total, count = get_expense_totals()
        assert float(total) == 500
        assert count == 1

    def test_record_expense_invalid_amount(self, db, admin_user):
        from app.services.expense_service import record_expense

        expense, error = record_expense(
            amount=0,
            category='other',
            description='Test',
            created_by_id=admin_user.id,
        )
        assert expense is None
        assert 'greater than zero' in error.lower()

    def test_auto_shipping_no_duplicate(self, db, admin_user, sample_user):
        from app.models.order import Order
        from app.models.expense import Expense
        from app.services.expense_service import auto_record_order_shipping

        order = Order(
            user_id=sample_user.id,
            subtotal=Decimal('1000'),
            shipping_cost=Decimal('80'),
            total=Decimal('1080'),
            shipping_address='{"line1":"Test"}',
            status='confirmed',
        )
        db.session.add(order)
        db.session.commit()

        exp1 = auto_record_order_shipping(order, created_by_id=admin_user.id)
        exp2 = auto_record_order_shipping(order, created_by_id=admin_user.id)
        assert exp1 is not None
        assert exp2.id == exp1.id
        assert Expense.query.filter_by(source_type='order', source_id=order.id, category='shipping').count() == 1

    def test_auto_refund_expense(self, db, admin_user, sample_user):
        from app.models.order import Order
        from app.models.expense import Expense
        from app.services.expense_service import auto_record_order_refund

        order = Order(
            user_id=sample_user.id,
            subtotal=Decimal('500'),
            total=Decimal('500'),
            shipping_address='{"line1":"Test"}',
            status='delivered',
        )
        db.session.add(order)
        db.session.commit()

        expense = auto_record_order_refund(order, created_by_id=admin_user.id)
        assert expense is not None
        assert expense.category == 'refund'
        assert float(expense.amount) == 500

    def test_delete_manual_expense_only(self, db, admin_user):
        from app.services.expense_service import record_expense, delete_expense
        from app.models.expense import Expense

        expense, _ = record_expense(
            amount=100,
            category='other',
            description='Tea',
            created_by_id=admin_user.id,
        )
        ok, error = delete_expense(expense.id)
        assert ok is True
        assert Expense.query.get(expense.id) is None

    def test_cannot_delete_auto_expense(self, db, admin_user):
        from app.services.expense_service import record_expense, delete_expense

        expense, _ = record_expense(
            amount=80,
            category='shipping',
            description='Auto shipping',
            source_type='order',
            source_id=1,
        )
        ok, error = delete_expense(expense.id)
        assert ok is False
        assert 'cannot be deleted' in error.lower()
