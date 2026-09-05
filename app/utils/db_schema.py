"""Lightweight schema patches for production DBs created via db.create_all()."""
from sqlalchemy import inspect, text

from app.extensions import db


def ensure_payment_columns():
    """Add payment tracking columns if missing (safe to run on every startup)."""
    inspector = inspect(db.engine)
    if 'payments' not in inspector.get_table_names():
        return

    existing = {c['name'] for c in inspector.get_columns('payments')}
    dialect = db.engine.dialect.name

    additions = [
        ('channel', "VARCHAR(30) DEFAULT 'cod'"),
        ('collected_at', 'DATETIME NULL'),
        ('collected_by_id', 'INTEGER NULL'),
        ('reference', 'VARCHAR(100) NULL'),
        ('notes', 'TEXT NULL'),
    ]

    for name, col_def in additions:
        if name in existing:
            continue
        if dialect == 'mysql':
            db.session.execute(text(f'ALTER TABLE payments ADD COLUMN {name} {col_def}'))
        else:
            db.session.execute(text(f'ALTER TABLE payments ADD COLUMN {name} {col_def}'))

    db.session.commit()
