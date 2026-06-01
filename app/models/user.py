from datetime import datetime, timedelta
import secrets
from flask_login import UserMixin
from app.extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='customer', nullable=False)  # customer, admin
    oauth_provider = db.Column(db.String(20))  # google, facebook
    oauth_id = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    addresses = db.relationship('Address', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    wishlist_items = db.relationship('Wishlist', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def default_address(self):
        return self.addresses.filter_by(is_default=True).first()

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    @staticmethod
    def verify_reset_token(token):
        user = User.query.filter_by(reset_token=token).first()
        if user and user.reset_token_expiry and user.reset_token_expiry > datetime.utcnow():
            return user
        return None

    def clear_reset_token(self):
        self.reset_token = None
        self.reset_token_expiry = None

    def __repr__(self):
        return f'<User {self.email}>'


class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address_line1 = db.Column(db.String(500), nullable=False)
    address_line2 = db.Column(db.String(500))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(100), default='India', nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def formatted(self):
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.append(f'{self.city}, {self.state} {self.postal_code}')
        parts.append(self.country)
        return ', '.join(parts)

    def __repr__(self):
        return f'<Address {self.full_name} - {self.city}>'
