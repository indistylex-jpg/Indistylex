import uuid
from decimal import Decimal


def generate_session_id():
    """Generate a unique session ID for guest carts."""
    return uuid.uuid4().hex


def format_price(amount):
    """Format price in INR."""
    if amount is None:
        return '₹0.00'
    return f'₹{Decimal(str(amount)):,.2f}'


def format_order_number(number):
    """Ensure order number has prefix."""
    if not number.startswith('SW-'):
        return f'SW-{number}'
    return number


def truncate_text(text, length=100):
    """Truncate text with ellipsis."""
    if not text or len(text) <= length:
        return text or ''
    return text[:length].rsplit(' ', 1)[0] + '...'
