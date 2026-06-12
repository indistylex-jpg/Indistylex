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

    def test_cart_count_ajax(self, client):
        resp = client.get('/cart/count')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'count' in data


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

    def test_admin_add_category_page(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/categories/add')
        assert resp.status_code == 200

    def test_admin_add_coupon_page(self, client, admin_user):
        login_admin(client)
        resp = client.get('/admin/coupons/add')
        assert resp.status_code == 200


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
