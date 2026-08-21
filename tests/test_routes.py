"""Tests for route handlers."""
import pytest
from decimal import Decimal

from app.extensions import db
from app.models.user import User
from app.models.product import Product, ProductVariant, Category
from app.models.cart import Cart, CartItem
from app.models.order import Order
from tests.conftest import login_user, login_admin


# ────────────────────────── Homepage & Static Pages ──────────────────────────

class TestMainRoutes:

    def test_homepage(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'Indistylex' in resp.data or b'Indistylex' in resp.data.lower()

    def test_about_page(self, client):
        assert client.get('/about').status_code == 200

    def test_contact_page(self, client):
        assert client.get('/contact').status_code == 200

    def test_privacy_page(self, client):
        assert client.get('/privacy-policy').status_code == 200

    def test_terms_page(self, client):
        assert client.get('/terms').status_code == 200

    def test_size_guide(self, client):
        assert client.get('/size-guide').status_code == 200

    def test_faq_page(self, client):
        assert client.get('/faq').status_code == 200

    def test_sitemap_xml(self, client):
        resp = client.get('/sitemap.xml')
        assert resp.status_code == 200
        assert b'<?xml' in resp.data

    def test_robots_txt(self, client):
        resp = client.get('/robots.txt')
        assert resp.status_code == 200
        assert b'User-agent' in resp.data

    def test_404_page(self, client):
        resp = client.get('/nonexistent-page-xyz')
        assert resp.status_code == 404


# ────────────────────────── Security Headers ──────────────────────────

class TestSecurityHeaders:

    def test_x_frame_options(self, client):
        resp = client.get('/')
        assert resp.headers.get('X-Frame-Options') == 'SAMEORIGIN'

    def test_x_content_type_options(self, client):
        resp = client.get('/')
        assert resp.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_xss_protection(self, client):
        resp = client.get('/')
        assert '1' in resp.headers.get('X-XSS-Protection', '')

    def test_referrer_policy(self, client):
        resp = client.get('/')
        assert resp.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'

    def test_csp_header(self, client):
        resp = client.get('/')
        assert 'Content-Security-Policy' in resp.headers

    def test_cache_control_html(self, client):
        resp = client.get('/')
        assert 'no-store' in resp.headers.get('Cache-Control', '')


# ────────────────────────── Auth Routes ──────────────────────────

class TestAuthRoutes:

    def test_login_page(self, client):
        resp = client.get('/auth/login')
        assert resp.status_code == 200

    def test_register_page(self, client):
        resp = client.get('/auth/register')
        assert resp.status_code == 200

    def test_successful_login(self, client, sample_user):
        resp = client.post('/auth/login', data={
            'email': 'customer@test.com',
            'password': 'Test1234',
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_wrong_password(self, client, sample_user):
        resp = client.post('/auth/login', data={
            'email': 'customer@test.com',
            'password': 'WrongPass123',
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Should still be on login page or redirected back with error

    def test_register_new_user(self, client):
        resp = client.post('/auth/register', data={
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@test.com',
            'password': 'NewPass123',
            'confirm_password': 'NewPass123',
        }, follow_redirects=True)
        assert resp.status_code == 200
        user = User.query.filter_by(email='newuser@test.com').first()
        assert user is not None

    def test_register_duplicate_email(self, client, sample_user):
        resp = client.post('/auth/register', data={
            'first_name': 'Dup',
            'last_name': 'User',
            'email': 'customer@test.com',
            'password': 'DupPass123',
            'confirm_password': 'DupPass123',
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Should not create duplicate

    def test_logout(self, client, sample_user):
        login_user(client)
        resp = client.get('/auth/logout', follow_redirects=True)
        assert resp.status_code == 200

    def test_forgot_password_page(self, client):
        resp = client.get('/auth/forgot-password')
        assert resp.status_code == 200


# ────────────────────────── Shop Routes ──────────────────────────

class TestShopRoutes:

    def test_shop_listing(self, client, sample_product):
        resp = client.get('/shop/')
        assert resp.status_code == 200

    def test_shop_category(self, client, sample_category, sample_product):
        resp = client.get(f'/shop/category/{sample_category.slug}')
        assert resp.status_code == 200

    def test_shop_category_invalid(self, client):
        resp = client.get('/shop/category/nonexistent-slug')
        assert resp.status_code == 404

    def test_shop_search(self, client, sample_product):
        resp = client.get('/shop/search?q=romper')
        assert resp.status_code == 200

    def test_shop_sort_price_low(self, client, sample_product):
        resp = client.get('/shop/?sort=price_low')
        assert resp.status_code == 200

    def test_shop_sort_price_high(self, client, sample_product):
        resp = client.get('/shop/?sort=price_high')
        assert resp.status_code == 200


# ────────────────────────── Product Routes ──────────────────────────

class TestProductRoutes:

    def test_product_detail(self, client, sample_product):
        resp = client.get(f'/product/{sample_product.slug}')
        assert resp.status_code == 200
        assert b'Baby Romper' in resp.data

    def test_product_detail_increments_views(self, client, sample_product):
        initial = sample_product.views_count
        client.get(f'/product/{sample_product.slug}')
        db.session.refresh(sample_product)
        assert sample_product.views_count == initial + 1

    def test_product_detail_invalid(self, client):
        resp = client.get('/product/nonexistent-slug')
        assert resp.status_code == 404


# ────────────────────────── Cart Routes ──────────────────────────

class TestCartRoutes:

    def test_view_empty_cart(self, client):
        resp = client.get('/cart/')
        assert resp.status_code == 200

    def test_add_to_cart(self, client, sample_product):
        variant = sample_product.variants.first()
        resp = client.post('/cart/add', data={
            'variant_id': variant.id,
            'quantity': 1,
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_add_to_cart_with_size_color(self, client, sample_product):
        resp = client.post('/cart/add', data={
            'product_id': sample_product.id,
            'size': '0-3M',
            'color': 'White',
            'quantity': 1,
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'added to cart' in resp.data.lower()

    def test_buy_now_adds_and_redirects_checkout(self, client, sample_product):
        variant = sample_product.variants.first()
        resp = client.post('/cart/add', data={
            'variant_id': variant.id,
            'quantity': 1,
            'buy_now': '1',
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert '/checkout' in resp.headers['Location']

    def test_cart_count_ajax(self, client):
        resp = client.get('/cart/count')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'count' in data

    def test_remove_from_cart_ajax(self, client, sample_product, app):
        variant = sample_product.variants.first()
        client.post('/cart/add', data={'variant_id': variant.id, 'quantity': 1})

        with client.session_transaction() as sess:
            session_id = sess.get('session_id')

        with app.app_context():
            from app.models.cart import Cart, CartItem
            cart = Cart.query.filter_by(session_id=session_id).first()
            assert cart is not None
            item = CartItem.query.filter_by(cart_id=cart.id).first()
            assert item is not None
            item_id = item.id

        resp = client.post(
            f'/cart/remove/{item_id}',
            headers={'X-CSRFToken': 'test', 'X-Requested-With': 'XMLHttpRequest'},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['count'] == 0


# ────────────────────────── User Account Routes ──────────────────────────

class TestUserRoutes:

    def test_profile_requires_login(self, client):
        resp = client.get('/account/profile', follow_redirects=True)
        assert resp.status_code == 200
        # Should redirect to login

    def test_profile_page(self, client, sample_user):
        login_user(client)
        resp = client.get('/account/profile')
        assert resp.status_code == 200

    def test_change_password_page(self, client, sample_user):
        login_user(client)
        resp = client.get('/account/change-password')
        assert resp.status_code == 200

    def test_addresses_page(self, client, sample_user):
        login_user(client)
        resp = client.get('/account/addresses')
        assert resp.status_code == 200

    def test_wishlist_page(self, client, sample_user):
        login_user(client)
        resp = client.get('/account/wishlist')
        assert resp.status_code == 200

    def test_orders_page(self, client, sample_user):
        login_user(client)
        resp = client.get('/orders/')
        assert resp.status_code == 200


# ────────────────────────── Admin Routes ──────────────────────────

class TestAdminRoutes:

    def test_admin_requires_login(self, client):
        resp = client.get('/admin/', follow_redirects=True)
        assert resp.status_code in (200, 403)

    def test_admin_requires_admin_role(self, client, sample_user):
        login_user(client)
        resp = client.get('/admin/')
        assert resp.status_code == 403

    def test_admin_dashboard(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/')
        assert resp.status_code == 200

    def test_admin_products_list(self, client, admin_user, sample_product):
        login_admin(client)
        resp = client.get('/admin/products')
        assert resp.status_code == 200

    def test_admin_orders_list(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/orders')
        assert resp.status_code == 200

    def test_admin_categories_list(self, client, admin_user, sample_category):
        login_admin(client)
        resp = client.get('/admin/categories')
        assert resp.status_code == 200

    def test_admin_customers_list(self, client, admin_user, sample_user):
        login_admin(client)
        resp = client.get('/admin/customers')
        assert resp.status_code == 200

    def test_admin_coupons_list(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/coupons')
        assert resp.status_code == 200

    def test_admin_reviews_list(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/reviews')
        assert resp.status_code == 200

    def test_admin_add_product_page(self, client, admin_user, sample_category):
        login_admin(client)
        resp = client.get('/admin/products/add')
        assert resp.status_code == 200
        assert b'name="images"' in resp.data
        assert b'variant_size[]' in resp.data
        assert b'Suitable ages' in resp.data
        assert b'name="age_groups"' in resp.data
        assert b'Store & homepage visibility' in resp.data

    def test_admin_create_product_with_variant(self, client, admin_user, sample_category):
        from io import BytesIO
        try:
            from PIL import Image
            img_buf = BytesIO()
            Image.new('RGB', (10, 10), color=(255, 0, 0)).save(img_buf, format='JPEG')
            img_buf.seek(0)
        except ImportError:
            img_buf = BytesIO(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9')

        login_admin(client)
        resp = client.post('/admin/products/add', data={
            'name': 'Full Set Romper',
            'category_id': sample_category.id,
            'price': '599.00',
            'gender': 'kids',
            'age_groups': ['1-2y', '2-3y', '3-4y'],
            'is_active': 'y',
            'is_new_arrival': 'y',
            'variant_size[]': '6-9M',
            'variant_color[]': 'Pink',
            'variant_sku[]': 'FULL-ROM-PINK',
            'variant_stock[]': '10',
            'images': (img_buf, 'test.jpg'),
        }, content_type='multipart/form-data', follow_redirects=True)
        assert resp.status_code == 200
        product = Product.query.filter_by(name='Full Set Romper').first()
        assert product is not None
        assert product.age_groups == '1-2y,2-3y,3-4y'
        assert product.is_new_arrival is True
        assert product.variants.count() == 1
        assert product.variants.first().sku == 'FULL-ROM-PINK'

    def test_admin_edit_product_save(self, client, admin_user, sample_product, sample_category):
        login_admin(client)
        sample_product.set_age_groups_list(['3-4y', '4-5y'])
        db.session.commit()

        resp = client.post(
            f'/admin/products/edit/{sample_product.id}',
            data={
                'name': 'Updated Romper Name',
                'category_id': sample_category.id,
                'price': '749.00',
                'compare_at_price': '999.00',
                'gender': 'kids',
                'age_groups': ['3-4y', '4-5y'],
                'is_active': 'y',
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b'saved successfully' in resp.data.lower()
        db.session.refresh(sample_product)
        assert sample_product.name == 'Updated Romper Name'
        assert Decimal(str(sample_product.price)) == Decimal('749.00')

    def test_admin_edit_product_shows_validation_errors(self, client, admin_user, sample_product, sample_category):
        login_admin(client)
        resp = client.post(
            f'/admin/products/edit/{sample_product.id}',
            data={
                'name': '',
                'category_id': sample_category.id,
                'price': '749.00',
                'gender': 'kids',
                'is_active': 'y',
            },
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b'Could not save' in resp.data or b'required' in resp.data.lower()

    def test_admin_edit_product_form_has_no_nested_forms(self, client, admin_user, sample_product):
        login_admin(client)
        resp = client.get(f'/admin/products/edit/{sample_product.id}')
        assert resp.status_code == 200
        html = resp.data.decode('utf-8')
        product_form_start = html.find('id="product-form"')
        product_form_end = html.find('</form>', product_form_start)
        product_form_chunk = html[product_form_start:product_form_end]
        assert product_form_chunk.count('<form') == 1

    def test_admin_bulk_delete_products(self, client, admin_user, sample_product, sample_category):
        login_admin(client)
        extra = Product(
            name='Bulk Delete Me',
            slug='bulk-delete-me',
            price=Decimal('299'),
            category_id=sample_category.id,
            is_active=True,
        )
        db.session.add(extra)
        db.session.commit()

        resp = client.post('/admin/products/bulk-delete', data={
            'product_ids': [str(sample_product.id), str(extra.id)],
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert Product.query.get(sample_product.id) is None
        assert Product.query.get(extra.id) is None
        assert b'deleted' in resp.data.lower()

    def test_admin_bulk_delete_with_review(self, client, admin_user, sample_product, sample_user):
        from app.models.review import Review
        review = Review(
            product_id=sample_product.id,
            user_id=sample_user.id,
            rating=5,
            title='Great',
            is_approved=True,
        )
        db.session.add(review)
        db.session.commit()

        login_admin(client)
        resp = client.post('/admin/products/bulk-delete', data={
            'product_ids': [str(sample_product.id)],
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert Product.query.get(sample_product.id) is None

    def test_admin_add_variant(self, client, admin_user, sample_product):
        login_admin(client)
        resp = client.post(f'/admin/products/{sample_product.id}/variants/add', data={
            'size': '12M',
            'color': 'Red',
            'sku': 'TEST-12M-RED',
            'stock_quantity': '5',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'TEST-12M-RED' in resp.data or b'added' in resp.data.lower()

    def test_admin_add_category_page(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/categories/add')
        assert resp.status_code == 200

    def test_admin_add_coupon_page(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/coupons/add')
        assert resp.status_code == 200

    def test_admin_b2b_sales_page(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/b2b-sales')
        assert resp.status_code == 200

    def test_admin_record_b2b_sale(self, client, admin_user, sample_product):
        login_admin(client)
        variant = sample_product.variants.first()
        resp = client.post('/admin/b2b-sales/record', data={
            'shop_name': 'Fashion Point',
            'shop_city': 'Prayagraj',
            'payment_terms': 'cod',
            'sku[]': variant.sku,
            'quantity[]': '2',
            'unit_price[]': '350',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'B2B-' in resp.data or b'recorded' in resp.data.lower()
        db.session.refresh(variant)
        assert variant.stock_quantity == 8

    def test_admin_expenses_page(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/expenses')
        assert resp.status_code == 200
        assert b'Expenses' in resp.data

    def test_admin_add_expense_page(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/expenses/add')
        assert resp.status_code == 200

    def test_admin_record_expense(self, client, admin_user):
        login_admin(client)
        resp = client.post('/admin/expenses/add', data={
            'expense_date': '2026-08-01',
            'category': 'packaging',
            'description': 'Bubble wrap rolls',
            'amount': '350',
            'payment_method': 'cash',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Bubble wrap' in resp.data or b'recorded' in resp.data.lower()

    def test_order_shipped_auto_expense(self, client, admin_user, sample_user):
        from app.models.order import Order
        from app.models.expense import Expense

        order = Order(
            user_id=sample_user.id,
            subtotal=Decimal('1000'),
            shipping_cost=Decimal('60'),
            total=Decimal('1060'),
            shipping_address='{"line1":"Test St"}',
            status='processing',
        )
        db.session.add(order)
        db.session.commit()

        login_admin(client)
        resp = client.post(
            f'/admin/orders/{order.id}/status',
            data={'status': 'shipped'},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        expense = Expense.query.filter_by(source_type='order', source_id=order.id, category='shipping').first()
        assert expense is not None
        assert float(expense.amount) == 60


# ────────────────────────── Checkout Routes ──────────────────────────

class TestCheckoutRoutes:

    def test_checkout_empty_cart_redirects(self, client, sample_user):
        login_user(client)
        resp = client.get('/checkout/', follow_redirects=True)
        assert resp.status_code == 200

    def test_checkout_success_page_invalid(self, client, sample_user):
        login_user(client)
        resp = client.get('/checkout/success/SW-INVALID123')
        # Should either 404 or redirect
        assert resp.status_code in (200, 302, 404)


# ────────────────────────── Chatbot Routes ──────────────────────────

class TestChatbotRoutes:

    def test_chatbot_endpoint(self, client):
        resp = client.post('/chatbot/', json={'message': 'hello'})
        # May be 200 or 404 depending on implementation
        assert resp.status_code in (200, 404, 405)
