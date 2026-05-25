"""Tests for form validation."""
import pytest

from app.forms.auth_forms import LoginForm, RegisterForm, ForgotPasswordForm
from app.forms.user_forms import ProfileForm, ChangePasswordForm
from app.forms.checkout_forms import CouponForm


# ────────────────────────── Auth Forms ──────────────────────────

class TestLoginForm:

    def test_valid_login(self, app):
        with app.test_request_context():
            form = LoginForm(data={
                'email': 'user@test.com',
                'password': 'password123',
            })
            assert form.validate() is True

    def test_missing_email(self, app):
        with app.test_request_context():
            form = LoginForm(data={
                'email': '',
                'password': 'password123',
            })
            assert form.validate() is False

    def test_missing_password(self, app):
        with app.test_request_context():
            form = LoginForm(data={
                'email': 'user@test.com',
                'password': '',
            })
            assert form.validate() is False

    def test_invalid_email_format(self, app):
        with app.test_request_context():
            form = LoginForm(data={
                'email': 'not-an-email',
                'password': 'password123',
            })
            assert form.validate() is False


class TestRegisterForm:

    def test_valid_registration(self, app, db):
        with app.test_request_context():
            form = RegisterForm(data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'register@test.com',
                'password': 'Register123',
                'confirm_password': 'Register123',
            })
            assert form.validate() is True

    def test_password_mismatch(self, app, db):
        with app.test_request_context():
            form = RegisterForm(data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'register@test.com',
                'password': 'Register123',
                'confirm_password': 'Different123',
            })
            assert form.validate() is False

    def test_short_password(self, app, db):
        with app.test_request_context():
            form = RegisterForm(data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'register@test.com',
                'password': 'short',
                'confirm_password': 'short',
            })
            assert form.validate() is False

    def test_missing_first_name(self, app, db):
        with app.test_request_context():
            form = RegisterForm(data={
                'first_name': '',
                'last_name': 'User',
                'email': 'register@test.com',
                'password': 'Register123',
                'confirm_password': 'Register123',
            })
            assert form.validate() is False


class TestForgotPasswordForm:

    def test_valid_email(self, app):
        with app.test_request_context():
            form = ForgotPasswordForm(data={'email': 'user@test.com'})
            assert form.validate() is True

    def test_invalid_email(self, app):
        with app.test_request_context():
            form = ForgotPasswordForm(data={'email': 'bad'})
            assert form.validate() is False


# ────────────────────────── User Forms ──────────────────────────

class TestProfileForm:

    def test_valid_profile(self, app):
        with app.test_request_context():
            form = ProfileForm(data={
                'first_name': 'Updated',
                'last_name': 'Name',
            })
            assert form.validate() is True

    def test_missing_first_name(self, app):
        with app.test_request_context():
            form = ProfileForm(data={
                'first_name': '',
                'last_name': 'Name',
            })
            assert form.validate() is False


# ────────────────────────── Checkout Forms ──────────────────────────

class TestCouponForm:

    def test_valid_coupon(self, app):
        with app.test_request_context():
            form = CouponForm(data={'code': 'SAVE20'})
            assert form.validate() is True

    def test_empty_coupon(self, app):
        with app.test_request_context():
            form = CouponForm(data={'code': ''})
            assert form.validate() is False
