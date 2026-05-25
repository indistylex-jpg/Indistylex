import re


def validate_phone(phone):
    """Validate Indian phone number."""
    pattern = r'^[6-9]\d{9}$'
    clean = re.sub(r'[\s\-\+]', '', phone)
    if clean.startswith('91') and len(clean) == 12:
        clean = clean[2:]
    return bool(re.match(pattern, clean))


def validate_pincode(pincode):
    """Validate Indian PIN code."""
    return bool(re.match(r'^[1-9]\d{5}$', str(pincode)))


def validate_password_strength(password):
    """Check password meets minimum requirements."""
    errors = []
    if len(password) < 8:
        errors.append('Password must be at least 8 characters.')
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one digit.')
    return errors
