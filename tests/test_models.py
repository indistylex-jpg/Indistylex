"""Tests for database models."""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from app.extensions import db
from app.models.user import User, Address
from app.models.product import Product, ProductVariant, ProductImage, Category
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, Payment
from app.models.review import Review
from app.models.coupon import Coupon
from app.models.wishlist import Wishlist


# ────────────────────────── User Model ──────────────────────────

class TestUserModel:

    def test_create_user(self, db, sample_user):
        assert sample_user.id is not None
        assert sample_user.email == 'customer@test.com'
        assert sample_user.full_name == 'Test Customer'
        assert sample_user.role == 'customer'
        assert sample_user.is_active is True

    def test_password_hashing(self, db, sample_user):
        assert sample_user.password_hash is not None
        assert sample_user.check_password('Test1234') is True
        assert sample_user.check_password('wrong') is False

    def test_password_hash_not_plaintext(self, db, sample_user):
        assert sample_user.password_hash != 'Test1234'

    def test_is_admin_property(self, db, sample_user, admin_user):
        assert sample_user.is_admin is False
        assert admin_user.is_admin is True

    def test_full_name(self, db, sample_user):
        assert sample_user.full_name == 'Test Customer'

    def test_is_locked_default(self, db, sample_user):
        assert sample_user.is_locked is False

    def test_is_locked_when_locked(self, db, sample_user):
        sample_user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        assert sample_user.is_locked is True

    def test_is_locked_when_expired(self, db, sample_user):
        sample_user.locked_until = datetime.utcnow() - timedelta(minutes=1)
        assert sample_user.is_locked is False

    def test_no_password_check_returns_false(self, db):
        user = User(email='nopass@test.com', first_name='No', last_name='Pass', role='customer')
        db.session.add(user)
        db.session.commit()
        assert user.check_password('anything') is False

    def test_default_address(self, db, sample_user, sample_address):
        addr = sample_user.default_address()
        assert addr is not None
        assert addr.city == 'Mumbai'

    def test_user_repr(self, db, sample_user):
        assert 'customer@test.com' in repr(sample_user)

    def test_unique_email_constraint(self, db, sample_user):
        dup = User(email='customer@test.com', first_name='Dup', last_name='User')
        db.session.add(dup)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


# ────────────────────────── Address Model ──────────────────────────

class TestAddressModel:

    def test_create_address(self, db, sample_address):
        assert sample_address.id is not None
        assert sample_address.city == 'Mumbai'
        assert sample_address.is_default is True

    def test_formatted_address(self, db, sample_address):
        formatted = sample_address.formatted()
        assert '123 MG Road' in formatted
        assert 'Mumbai' in formatted
        assert 'Maharashtra' in formatted
        assert '400001' in formatted

    def test_formatted_with_line2(self, db, sample_user):
        addr = Address(
            user_id=sample_user.id, full_name='Test', phone='9876543210',
            address_line1='123 MG Road', address_line2='Floor 4',
            city='Mumbai', state='Maharashtra', postal_code='400001',
        )
        db.session.add(addr)
        db.session.commit()
        assert 'Floor 4' in addr.formatted()


# ────────────────────────── Category Model ──────────────────────────

class TestCategoryModel:

    def test_create_category(self, db, sample_category):
        assert sample_category.id is not None
        assert sample_category.slug == 'newborn'
        assert sample_category.is_active is True

    def test_auto_slug_generation(self, db):
        cat = Category(name='Boys (3-12Y)', description='Boys clothing')
        db.session.add(cat)
        db.session.commit()
        assert cat.slug == 'boys-3-12y'

    def test_active_products_count(self, db, sample_category, sample_product):
        assert sample_category.active_products_count == 1

    def test_active_products_count_zero(self, db, sample_category):
        assert sample_category.active_products_count == 0

    def test_subcategories(self, db, sample_category):
        child = Category(name='Onesies', slug='onesies', parent_id=sample_category.id)
        db.session.add(child)
        db.session.commit()
        assert child.parent.id == sample_category.id


# ────────────────────────── Product Model ──────────────────────────

class TestProductModel:

    def test_create_product(self, db, sample_product):
        assert sample_product.id is not None
        assert sample_product.slug == 'baby-romper'
        assert sample_product.price == Decimal('699.00')

    def test_discount_percent(self, db, sample_product):
        # (999 - 699) / 999 ≈ 30%
        assert sample_product.discount_percent == 30

    def test_discount_percent_no_compare(self, db, sample_category):
        p = Product(
            name='No Discount', slug='no-discount',
            price=Decimal('500'), category_id=sample_category.id,
        )
        db.session.add(p)
        db.session.commit()
        assert p.discount_percent == 0

    def test_in_stock(self, db, sample_product):
        assert sample_product.in_stock is True

    def test_out_of_stock(self, db, sample_category):
        p = Product(
            name='Empty', slug='empty', price=Decimal('100'),
            category_id=sample_category.id,
        )
        db.session.add(p)
        db.session.flush()
        v = ProductVariant(
            product_id=p.id, size='S', color='Red', sku='EMPTY-S-RED',
            stock_quantity=0, is_active=True,
        )
        db.session.add(v)
        db.session.commit()
        assert p.in_stock is False

    def test_total_stock(self, db, sample_product):
        # 3 sizes × 2 colors × 10 each = 60
        assert sample_product.total_stock == 60

    def test_available_sizes(self, db, sample_product):
        sizes = sample_product.available_sizes
        assert '0-3M' in sizes
        assert '3-6M' in sizes
        assert '6-9M' in sizes

    def test_available_colors(self, db, sample_product):
        colors = sample_product.available_colors
        assert 'White' in colors
        assert 'Yellow' in colors

    def test_primary_image(self, db, sample_product):
        assert 'romper.jpg' in sample_product.primary_image

    def test_primary_image_fallback(self, db, sample_category):
        p = Product(
            name='No Image', slug='no-image', price=Decimal('100'),
            category_id=sample_category.id,
        )
        db.session.add(p)
        db.session.commit()
        assert 'placeholder' in p.primary_image

    def test_average_rating_no_reviews(self, db, sample_product):
        assert sample_product.average_rating == 0

    def test_review_count_no_reviews(self, db, sample_product):
        assert sample_product.review_count == 0

    def test_product_repr(self, db, sample_product):
        assert 'Baby Romper' in repr(sample_product)


# ────────────────────────── ProductVariant Model ──────────────────────────

class TestProductVariantModel:

    def test_variant_sku_unique(self, db, sample_product):
        dup = ProductVariant(
            product_id=sample_product.id, size='0-3M', color='White',
            sku='ROM-0-3M-WHITE', stock_quantity=5,
        )
        db.session.add(dup)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()

    def test_variant_repr(self, db, sample_product):
        v = sample_product.variants.first()
        assert 'ROM' in repr(v)


# ────────────────────────── Cart Model ──────────────────────────

class TestCartModel:

    def test_create_user_cart(self, db, sample_user, sample_product):
        cart = Cart(user_id=sample_user.id)
        db.session.add(cart)
        db.session.flush()

        variant = sample_product.variants.first()
        item = CartItem(cart_id=cart.id, variant_id=variant.id, quantity=2)
        db.session.add(item)
        db.session.commit()

        assert cart.item_count == 2
        assert cart.subtotal == sample_product.price * 2

    def test_guest_cart(self, db, sample_product):
        cart = Cart(session_id='abc123')
        db.session.add(cart)
        db.session.flush()

        variant = sample_product.variants.first()
        item = CartItem(cart_id=cart.id, variant_id=variant.id, quantity=1)
        db.session.add(item)
        db.session.commit()

        assert cart.session_id == 'abc123'
        assert cart.item_count == 1

    def test_cart_item_line_total(self, db, sample_user, sample_product):
        cart = Cart(user_id=sample_user.id)
        db.session.add(cart)
        db.session.flush()

        variant = sample_product.variants.first()
        item = CartItem(cart_id=cart.id, variant_id=variant.id, quantity=3)
        db.session.add(item)
        db.session.commit()

        assert item.line_total == sample_product.price * 3


# ────────────────────────── Order Model ──────────────────────────

class TestOrderModel:

    def test_create_order(self, db, sample_user):
        order = Order(
            order_number='SW-ABCD1234',
            user_id=sample_user.id,
            subtotal=Decimal('699.00'),
            tax=Decimal('34.95'),
            shipping_cost=Decimal('0.00'),
            discount=Decimal('0.00'),
            total=Decimal('733.95'),
            status='pending',
            shipping_address='{"city": "Mumbai"}',
        )
        db.session.add(order)
        db.session.commit()
        assert order.id is not None
        assert order.order_number == 'SW-ABCD1234'

    def test_status_badge_class(self, db, sample_user):
        order = Order(
            order_number='SW-TEST0001', user_id=sample_user.id,
            subtotal=Decimal('100'), total=Decimal('105'),
            status='delivered', shipping_address='{}',
        )
        db.session.add(order)
        db.session.commit()
        assert 'success' in order.status_badge_class.lower() or order.status_badge_class


# ────────────────────────── Review Model ──────────────────────────

class TestReviewModel:

    def test_create_review(self, db, sample_user, sample_product):
        review = Review(
            product_id=sample_product.id,
            user_id=sample_user.id,
            rating=5,
            title='Great romper!',
            comment='Very soft and comfortable.',
            is_approved=True,
        )
        db.session.add(review)
        db.session.commit()

        assert review.id is not None
        assert sample_product.average_rating == 5.0
        assert sample_product.review_count == 1

    def test_unapproved_review_not_counted(self, db, sample_user, sample_product):
        review = Review(
            product_id=sample_product.id, user_id=sample_user.id,
            rating=4, title='Good', is_approved=False,
        )
        db.session.add(review)
        db.session.commit()
        assert sample_product.review_count == 0
        assert sample_product.average_rating == 0


# ────────────────────────── Coupon Model ──────────────────────────

class TestCouponModel:

    def test_valid_coupon(self, db, sample_coupon):
        assert sample_coupon.is_valid is True

    def test_expired_coupon(self, db):
        coupon = Coupon(
            code='EXPIRED', discount_type='flat', discount_value=Decimal('100'),
            valid_from=datetime.utcnow() - timedelta(days=10),
            valid_until=datetime.utcnow() - timedelta(days=1),
            is_active=True,
        )
        db.session.add(coupon)
        db.session.commit()
        assert coupon.is_valid is False

    def test_inactive_coupon(self, db):
        coupon = Coupon(
            code='INACTIVE', discount_type='flat', discount_value=Decimal('50'),
            valid_from=datetime.utcnow() - timedelta(days=1),
            valid_until=datetime.utcnow() + timedelta(days=30),
            is_active=False,
        )
        db.session.add(coupon)
        db.session.commit()
        assert coupon.is_valid is False

    def test_maxed_out_coupon(self, db):
        coupon = Coupon(
            code='MAXED', discount_type='flat', discount_value=Decimal('50'),
            valid_from=datetime.utcnow() - timedelta(days=1),
            valid_until=datetime.utcnow() + timedelta(days=30),
            max_uses=10, used_count=10, is_active=True,
        )
        db.session.add(coupon)
        db.session.commit()
        assert coupon.is_valid is False

    def test_percentage_discount(self, db, sample_coupon):
        # 20% of 1000 = 200, max discount 200
        discount = sample_coupon.calculate_discount(Decimal('1000'))
        assert discount == Decimal('200.00')

    def test_percentage_discount_capped(self, db, sample_coupon):
        # 20% of 2000 = 400, capped at 200
        discount = sample_coupon.calculate_discount(Decimal('2000'))
        assert discount == Decimal('200.00')

    def test_flat_discount(self, db):
        coupon = Coupon(
            code='FLAT100', discount_type='flat', discount_value=Decimal('100'),
            min_order_amount=Decimal('0'),
            valid_from=datetime.utcnow() - timedelta(days=1),
            valid_until=datetime.utcnow() + timedelta(days=30),
            is_active=True,
        )
        db.session.add(coupon)
        db.session.commit()
        assert coupon.calculate_discount(Decimal('500')) == Decimal('100')

    def test_min_order_not_met(self, db, sample_coupon):
        # Min is 500, subtotal is 200
        assert sample_coupon.calculate_discount(Decimal('200')) == 0

    def test_invalid_coupon_no_discount(self, db):
        coupon = Coupon(
            code='DEAD', discount_type='flat', discount_value=Decimal('100'),
            valid_from=datetime.utcnow() - timedelta(days=10),
            valid_until=datetime.utcnow() - timedelta(days=1),
            is_active=True,
        )
        db.session.add(coupon)
        db.session.commit()
        assert coupon.calculate_discount(Decimal('1000')) == 0


# ────────────────────────── Wishlist Model ──────────────────────────

class TestWishlistModel:

    def test_add_to_wishlist(self, db, sample_user, sample_product):
        item = Wishlist(user_id=sample_user.id, product_id=sample_product.id)
        db.session.add(item)
        db.session.commit()
        assert item.id is not None

    def test_unique_wishlist_entry(self, db, sample_user, sample_product):
        item1 = Wishlist(user_id=sample_user.id, product_id=sample_product.id)
        db.session.add(item1)
        db.session.commit()

        item2 = Wishlist(user_id=sample_user.id, product_id=sample_product.id)
        db.session.add(item2)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()
