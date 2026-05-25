import uuid
from datetime import datetime
from app.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # nullable for guest checkout
    guest_email = db.Column(db.String(255))
    guest_phone = db.Column(db.String(20))

    # Status
    status = db.Column(db.String(30), default='pending', nullable=False)
    # pending, confirmed, processing, shipped, delivered, cancelled, refunded

    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax = db.Column(db.Numeric(10, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    discount = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    # Addresses (stored as JSON string for order history immutability)
    shipping_address = db.Column(db.Text, nullable=False)
    billing_address = db.Column(db.Text)

    # Payment method: cod, online
    payment_method = db.Column(db.String(20), default='cod')

    # Coupon
    coupon_code = db.Column(db.String(50))

    # Notes
    notes = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.order_number:
            self.order_number = f'SW-{uuid.uuid4().hex[:8].upper()}'

    @property
    def status_badge_class(self):
        status_map = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'info',
            'delivered': 'success',
            'cancelled': 'danger',
            'refunded': 'secondary',
        }
        return status_map.get(self.status, 'secondary')

    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'))
    product_name = db.Column(db.String(300), nullable=False)
    product_slug = db.Column(db.String(350))
    size = db.Column(db.String(20))
    color = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500))

    variant = db.relationship('ProductVariant', backref='order_items')

    @property
    def line_total(self):
        return self.price * self.quantity

    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    provider = db.Column(db.String(30), default='razorpay', nullable=False)
    razorpay_order_id = db.Column(db.String(255))
    razorpay_payment_id = db.Column(db.String(255))
    razorpay_signature = db.Column(db.String(500))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default='INR')
    status = db.Column(db.String(30), default='pending')  # pending, captured, failed, refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.razorpay_payment_id} - {self.status}>'
