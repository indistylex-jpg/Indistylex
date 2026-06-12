"""Tests for utility functions (validators, helpers, decorators)."""
import pytest
from decimal import Decimal

from app.utils.validators import validate_phone, validate_pincode, validate_password_strength
from app.utils.helpers import generate_session_id, format_price, format_order_number, truncate_text


# ────────────────────────── Phone Validation ──────────────────────────

class TestValidatePhone:

    def test_valid_phone(self):
        assert validate_phone('9876543210') is True

    def test_valid_phone_with_country_code(self):
        assert validate_phone('+91 9876543210') is True

    def test_valid_phone_with_91_prefix(self):
        assert validate_phone('919876543210') is True

    def test_invalid_phone_too_short(self):
        assert validate_phone('12345') is False

    def test_invalid_phone_starts_with_low(self):
        assert validate_phone('1234567890') is False

    def test_phone_starts_with_6(self):
        assert validate_phone('6394142176') is True

    def test_phone_starts_with_7(self):
        assert validate_phone('7012345678') is True

    def test_phone_starts_with_8(self):
        assert validate_phone('8012345678') is True


# ────────────────────────── Pincode Validation ──────────────────────────

class TestValidatePincode:

    def test_valid_pincode(self):
        assert validate_pincode('400001') is True

    def test_valid_pincode_number(self):
        assert validate_pincode(110001) is True

    def test_invalid_pincode_starts_with_0(self):
        assert validate_pincode('012345') is False

    def test_invalid_pincode_too_short(self):
        assert validate_pincode('1234') is False

    def test_invalid_pincode_too_long(self):
        assert validate_pincode('1234567') is False


# ────────────────────────── Password Strength ──────────────────────────

class TestValidatePasswordStrength:

    def test_strong_password(self):
        errors = validate_password_strength('StrongPass1')
        assert len(errors) == 0

    def test_too_short(self):
        errors = validate_password_strength('Sh1')
        assert any('8 characters' in e for e in errors)

    def test_no_uppercase(self):
        errors = validate_password_strength('lowercase1')
        assert any('uppercase' in e for e in errors)

    def test_no_lowercase(self):
        errors = validate_password_strength('UPPERCASE1')
        assert any('lowercase' in e for e in errors)

    def test_no_digit(self):
        errors = validate_password_strength('NoDigitHere')
        assert any('digit' in e for e in errors)

    def test_empty_password(self):
        errors = validate_password_strength('')
        assert len(errors) >= 1


# ────────────────────────── Helpers ──────────────────────────

class TestGenerateSessionId:

    def test_returns_string(self):
        sid = generate_session_id()
        assert isinstance(sid, str)

    def test_length(self):
        sid = generate_session_id()
        assert len(sid) == 32  # UUID hex

    def test_uniqueness(self):
        ids = {generate_session_id() for _ in range(100)}
        assert len(ids) == 100


class TestFormatPrice:

    def test_normal_price(self):
        assert format_price(699) == '₹699.00'

    def test_decimal_price(self):
        assert format_price(Decimal('1234.56')) == '₹1,234.56'

    def test_none_price(self):
        assert format_price(None) == '₹0.00'

    def test_zero_price(self):
        assert format_price(0) == '₹0.00'

    def test_large_price(self):
        result = format_price(99999)
        assert '99,999' in result


class TestFormatOrderNumber:

    def test_without_prefix(self):
        assert format_order_number('ABCD1234') == 'SW-ABCD1234'

    def test_with_prefix(self):
        assert format_order_number('SW-ABCD1234') == 'SW-ABCD1234'


class TestTruncateText:

    def test_short_text(self):
        assert truncate_text('Hello', 100) == 'Hello'

    def test_long_text(self):
        text = 'This is a very long text that should be truncated at some point for display purposes.'
        result = truncate_text(text, 40)
        assert len(result) <= 43  # 40 + '...'
        assert result.endswith('...')

    def test_none_text(self):
        assert truncate_text(None) == ''

    def test_empty_text(self):
        assert truncate_text('') == ''

    def test_exact_length(self):
        text = 'Exactly ten'
        assert truncate_text(text, 11) == 'Exactly ten'
