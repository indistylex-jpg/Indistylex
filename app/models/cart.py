from datetime import datetime
from app.extensions import db


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(255), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('CartItem', backref='cart', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def subtotal(self):
        total = 0
        for item in self.items.all():
            if item.variant and item.variant.product:
                total += item.variant.product.price * item.quantity
        return total

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    def __repr__(self):
        return f'<Cart {self.id}>'


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    variant = db.relationship('ProductVariant', backref='cart_items')

    __table_args__ = (
        db.UniqueConstraint('cart_id', 'variant_id', name='uq_cart_variant'),
    )

    @property
    def line_total(self):
        if self.variant and self.variant.product:
            return self.variant.product.price * self.quantity
        return 0

    @property
    def subtotal(self):
        return self.line_total

    def __repr__(self):
        return f'<CartItem variant={self.variant_id} qty={self.quantity}>'
