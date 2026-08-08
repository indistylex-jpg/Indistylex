from datetime import datetime, date
from app.extensions import db

EXPENSE_CATEGORIES = [
    ('stock_purchase', 'Stock / Wholesaler Purchase'),
    ('shipping', 'Shipping & Courier'),
    ('packaging', 'Packaging & Labels'),
    ('marketing', 'Marketing & Ads'),
    ('server', 'Server & Software'),
    ('rent', 'Rent & Utilities'),
    ('salary', 'Salaries & Labor'),
    ('refund', 'Refunds & Returns'),
    ('other', 'Other'),
]


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    category = db.Column(db.String(30), nullable=False, default='other')
    description = db.Column(db.String(300), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), default='cash')  # cash, upi, bank, card
    source_type = db.Column(db.String(20), default='manual')  # manual, order, b2b
    source_id = db.Column(db.Integer)
    reference = db.Column(db.String(100))  # invoice no, order number, etc.
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    created_by = db.relationship('User', backref='expenses')

    @property
    def category_label(self):
        labels = dict(EXPENSE_CATEGORIES)
        return labels.get(self.category, self.category.replace('_', ' ').title())

    def __repr__(self):
        return f'<Expense {self.category} ₹{self.amount}>'
