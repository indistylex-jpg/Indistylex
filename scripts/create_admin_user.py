#!/usr/bin/env python3
"""Create or promote a user to admin role."""
import argparse
import os
import secrets
import string
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.user import User  # noqa: E402


def _generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + '!@#$%&*'
    while True:
        pwd = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in pwd)
                and any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd)):
            return pwd


def main():
    parser = argparse.ArgumentParser(description='Create or promote an admin user')
    parser.add_argument('--email', required=True, help='Login email (e.g. satyam@indistylex.com)')
    parser.add_argument('--first-name', default='Admin')
    parser.add_argument('--last-name', default='User')
    parser.add_argument(
        '--password',
        help='Login password (generated if omitted — printed once to stdout)',
    )
    args = parser.parse_args()

    config_name = os.environ.get('FLASK_CONFIG') or os.environ.get('FLASK_ENV') or 'production'
    app = create_app(config_name)
    email = args.email.lower().strip()
    password = args.password or _generate_password()

    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.role = 'admin'
            user.is_active = True
            user.first_name = args.first_name.strip()
            user.last_name = args.last_name.strip()
            user.set_password(password)
            action = 'updated'
        else:
            user = User(
                email=email,
                first_name=args.first_name.strip(),
                last_name=args.last_name.strip(),
                role='admin',
                is_active=True,
            )
            user.set_password(password)
            db.session.add(user)
            action = 'created'

        db.session.commit()
        print(f'Admin user {action}: {email}')
        print(f'Name: {user.full_name}')
        if not args.password:
            print(f'Generated password: {password}')
            print('Save this password now — it will not be shown again.')


if __name__ == '__main__':
    main()
