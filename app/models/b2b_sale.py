from datetime import datetime
from app.extensions import db


class B2BSale(db.Model):
    __tablename__ = 'b2b_sales'

    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    shop_name = db.Column(db.String(200), nullable=False)
    shop_phone = db.Column(db.String(20))
    shop_city = db.Column(db.String(100))
    payment_terms = db.Column(db.String(20), default='cod', nullable=False)  # cod, credit
    notes = db.Column(db.Text)
    subtotal = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    extra_discount = db.Column(db.Numeric(10, 2), default=0, nullable=False)  # flat ₹ off
    discount_percent = db.Column(db.Numeric(5, 2), default=0, nullable=False)  # % off subtotal
    discount_reason = db.Column(db.String(200))
    total = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_cancelled = db.Column(db.Boolean, default=False, nullable=False)

    created_by = db.relationship('User', backref='b2b_sales')
    items = db.relationship('B2BSaleItem', backref='sale', lazy='dynamic',
                            cascade='all, delete-orphan')

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items)

    @property
    def discount_amount(self):
        """Total discount applied (flat or percent)."""
        from decimal import Decimal
        subtotal = Decimal(str(self.subtotal or 0))
        if self.discount_percent and Decimal(str(self.discount_percent)) > 0:
            return subtotal * Decimal(str(self.discount_percent)) / Decimal('100')
        return Decimal(str(self.extra_discount or 0))

    def __repr__(self):
        return f'<B2BSale {self.sale_number}>'


class B2BSaleItem(db.Model):
    __tablename__ = 'b2b_sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('b2b_sales.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    product_name = db.Column(db.String(300), nullable=False)
    sku = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(20))
    color = db.Column(db.String(50))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)

    variant = db.relationship('ProductVariant', backref='b2b_sale_items')

    def __repr__(self):
        return f'<B2BSaleItem {self.sku} x{self.quantity}>'
