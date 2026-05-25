"""Shared test fixtures for Indistylex."""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db as _db
from app.models.user import User, Address
from app.models.product import Product, ProductVariant, ProductImage, Category
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, Payment
from app.models.review import Review
from app.models.coupon import Coupon
from app.models.wishlist import Wishlist


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    yield app


@pytest.fixture(scope='function')
def db(app):
    """Create a fresh database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app, db):
    """Flask CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(db):
    """Create a regular customer user."""
    user = User(
        email='customer@test.com',
        first_name='Test',
        last_name='Customer',
        role='customer',
        is_active=True,
    )
    user.set_password('Test1234')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    user = User(
        email='admin@test.com',
        first_name='Admin',
        last_name='User',
        role='admin',
        is_active=True,
    )
    user.set_password('Admin1234')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_category(db):
    """Create a sample category."""
    cat = Category(
        name='Newborn (0-12M)',
        slug='newborn',
        description='Adorable clothing for newborns',
        is_active=True,
        sort_order=1,
    )
    db.session.add(cat)
    db.session.commit()
    return cat


@pytest.fixture
def sample_product(db, sample_category):
    """Create a sample product with variants and images."""
    product = Product(
        name='Baby Romper',
        slug='baby-romper',
        description='Soft cotton baby romper',
        short_description='Soft romper',
        price=Decimal('699.00'),
        compare_at_price=Decimal('999.00'),
        category_id=sample_category.id,
        brand='SilkenKids',
        gender='kids',
        age_group='0-2',
        material='100% Cotton',
        is_active=True,
        is_featured=True,
    )
    db.session.add(product)
    db.session.flush()

    # Add variants
    for size in ['0-3M', '3-6M', '6-9M']:
        for color in ['White', 'Yellow']:
            v = ProductVariant(
                product_id=product.id,
                size=size,
                color=color,
                sku=f'ROM-{size}-{color}'.upper(),
                stock_quantity=10,
                is_active=True,
            )
            db.session.add(v)

    # Add image
    img = ProductImage(
        product_id=product.id,
        image_url='https://example.com/romper.jpg',
        alt_text='Baby Romper',
        is_primary=True,
        sort_order=0,
    )
    db.session.add(img)
    db.session.commit()
    return product


@pytest.fixture
def sample_coupon(db):
    """Create a valid coupon."""
    coupon = Coupon(
        code='SAVE20',
        discount_type='percentage',
        discount_value=Decimal('20.00'),
        min_order_amount=Decimal('500.00'),
        max_discount_amount=Decimal('200.00'),
        max_uses=100,
        used_count=0,
        valid_from=datetime.utcnow() - timedelta(days=1),
        valid_until=datetime.utcnow() + timedelta(days=30),
        is_active=True,
    )
    db.session.add(coupon)
    db.session.commit()
    return coupon


@pytest.fixture
def sample_address(db, sample_user):
    """Create a sample address."""
    addr = Address(
        user_id=sample_user.id,
        full_name='Test Customer',
        phone='9876543210',
        address_line1='123 MG Road',
        city='Mumbai',
        state='Maharashtra',
        postal_code='400001',
        country='India',
        is_default=True,
    )
    db.session.add(addr)
    db.session.commit()
    return addr


def login_user(client, email='customer@test.com', password='Test1234'):
    """Helper to log in a user via the test client."""
    return client.post('/auth/login', data={
        'email': email,
        'password': password,
    }, follow_redirects=True)


def login_admin(client, email='admin@test.com', password='Admin1234'):
    """Helper to log in an admin."""
    return client.post('/auth/login', data={
        'email': email,
        'password': password,
    }, follow_redirects=True)
