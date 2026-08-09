"""Tests for admin-only product cost price and profit tracking."""
from decimal import Decimal
from datetime import datetime

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.routes.api import _serialize_product_detail, _serialize_product_list
from app.services.dashboard_analytics_service import get_order_item_profit_totals


def test_product_unit_profit(sample_product):
    sample_product.cost_price = Decimal('400.00')
    assert sample_product.unit_profit == Decimal('299.00')
    assert sample_product.profit_margin_percent == 42.8


def test_order_item_line_profit(db, sample_product, sample_user):
    sample_product.cost_price = Decimal('400.00')
    order = Order(
        user_id=sample_user.id,
        subtotal=Decimal('699.00'),
        total=Decimal('699.00'),
        shipping_address='{}',
        status='delivered',
        created_at=datetime.utcnow(),
    )
    db.session.add(order)
    db.session.flush()

    item = OrderItem(
        order_id=order.id,
        product_name=sample_product.name,
        price=sample_product.price,
        cost_price=sample_product.cost_price,
        quantity=2,
    )
    db.session.add(item)
    db.session.commit()

    assert item.line_profit == Decimal('598.00')
    assert item.line_cost == Decimal('800.00')


def test_get_order_item_profit_totals(db, sample_product, sample_user):
    sample_product.cost_price = Decimal('500.00')
    order = Order(
        user_id=sample_user.id,
        subtotal=Decimal('699.00'),
        total=Decimal('699.00'),
        shipping_address='{}',
        status='delivered',
        created_at=datetime.utcnow(),
    )
    db.session.add(order)
    db.session.flush()
    db.session.add(OrderItem(
        order_id=order.id,
        product_name=sample_product.name,
        price=Decimal('699.00'),
        cost_price=Decimal('500.00'),
        quantity=1,
    ))
    db.session.commit()

    revenue, cogs, gross = get_order_item_profit_totals()
    assert revenue == 699.0
    assert cogs == 500.0
    assert gross == 199.0


def test_cost_price_not_exposed_in_api(sample_product):
    sample_product.cost_price = Decimal('400.00')
    listing = _serialize_product_list(sample_product)
    detail = _serialize_product_detail(sample_product)
    assert 'cost_price' not in listing
    assert 'cost_price' not in detail
