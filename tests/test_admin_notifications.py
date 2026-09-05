"""Tests for admin header notifications."""
from decimal import Decimal

from app.extensions import db
from app.models.order import Order
from app.models.review import Review
from app.services.admin_notification_service import get_admin_header_notifications


class TestAdminNotifications:
    def test_counts_pending_orders_and_reviews(self, app, db, sample_product, sample_user):
        with app.app_context():
            order = Order(
                user_id=sample_user.id,
                status='pending',
                subtotal=Decimal('500'),
                shipping_cost=Decimal('99'),
                total=Decimal('599'),
                shipping_address='{}',
            )
            db.session.add(order)
            review = Review(
                user_id=sample_user.id,
                product_id=sample_product.id,
                rating=5,
                title='Great',
                comment='Love it',
                is_approved=False,
            )
            db.session.add(review)
            db.session.commit()

            data = get_admin_header_notifications()
            assert data['order_count'] >= 1
            assert data['alert_count'] >= 1
            assert any('review' in item['label'].lower() for item in data['alert_items'])

    def test_empty_notifications(self, app, db):
        with app.app_context():
            data = get_admin_header_notifications()
            assert data['order_count'] == 0
            assert isinstance(data['order_items'], list)
