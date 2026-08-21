"""Expense recording and automatic tracking."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func

from app.extensions import db
from app.models.expense import Expense, EXPENSE_CATEGORIES


def record_expense(amount, category, description, created_by_id=None,
                   payment_method='cash', source_type='manual', source_id=None,
                   reference=None, notes=None, expense_date=None):
    """
    Record an expense. Skips duplicate auto entries (same source_type + source_id + category).
    Returns (expense, None) or (None, error_message).
    """
    try:
        amount = Decimal(str(amount))
    except Exception:
        return None, 'Invalid amount.'

    if amount <= 0:
        return None, 'Amount must be greater than zero.'

    valid_cats = {c[0] for c in EXPENSE_CATEGORIES}
    if category not in valid_cats:
        return None, 'Invalid expense category.'

    if not description or not str(description).strip():
        return None, 'Description is required.'

    if source_type != 'manual' and source_id:
        existing = Expense.query.filter_by(
            source_type=source_type,
            source_id=source_id,
            category=category,
        ).first()
        if existing:
            return existing, None

    expense = Expense(
        expense_date=expense_date or date.today(),
        category=category,
        description=description.strip(),
        amount=amount,
        payment_method=payment_method or 'cash',
        source_type=source_type,
        source_id=source_id,
        reference=reference,
        notes=notes.strip() if notes else None,
        created_by_id=created_by_id,
    )
    db.session.add(expense)
    db.session.commit()
    return expense, None


def auto_record_order_shipping(order, created_by_id=None):
    """Log shipping cost when order is marked shipped (once per order)."""
    cost = Decimal(str(order.shipping_cost or 0))
    if cost <= 0:
        return None
    expense, _ = record_expense(
        amount=cost,
        category='shipping',
        description=f'Shipping — Order {order.order_number}',
        created_by_id=created_by_id,
        payment_method='bank',
        source_type='order',
        source_id=order.id,
        reference=order.order_number,
    )
    return expense


def auto_record_order_refund(order, created_by_id=None):
    """Log refund when order is marked refunded (once per order)."""
    amount = Decimal(str(order.total or 0))
    if amount <= 0:
        return None
    expense, _ = record_expense(
        amount=amount,
        category='refund',
        description=f'Customer refund — Order {order.order_number}',
        created_by_id=created_by_id,
        payment_method='bank',
        source_type='order',
        source_id=order.id,
        reference=order.order_number,
        notes='Auto-recorded on refund',
    )
    return expense


def get_expense_totals(start_date=None, end_date=None):
    """Return total amount and count, optionally filtered by date range."""
    query = db.session.query(
        func.coalesce(func.sum(Expense.amount), 0),
        func.count(Expense.id),
    )
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    total, count = query.one()
    return Decimal(str(total or 0)), int(count or 0)


def get_expense_by_category(start_date=None, end_date=None):
    """Totals grouped by category for dashboard/charts."""
    query = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count'),
    )
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    rows = query.group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()
    labels = dict(EXPENSE_CATEGORIES)
    return [
        {
            'category': r.category,
            'label': labels.get(r.category, r.category),
            'total': float(r.total or 0),
            'count': int(r.count or 0),
        }
        for r in rows
    ]


def delete_expense(expense_id):
    """Delete manual expense only. Auto-linked expenses cannot be deleted."""
    expense = Expense.query.get(expense_id)
    if not expense:
        return False, 'Expense not found.'
    if expense.source_type != 'manual':
        return False, 'Auto-recorded expenses cannot be deleted. Change the linked order instead.'
    db.session.delete(expense)
    db.session.commit()
    return True, None
