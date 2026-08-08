-- Expenses table for Indistylex admin
-- Run: mysql -u indistylex -p indistylex < scripts/create_expenses_table.sql

CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    expense_date DATE NOT NULL,
    category VARCHAR(30) NOT NULL DEFAULT 'other',
    description VARCHAR(300) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL DEFAULT 'cash',
    source_type VARCHAR(20) NOT NULL DEFAULT 'manual',
    source_id INT NULL,
    reference VARCHAR(100) NULL,
    notes TEXT NULL,
    created_by_id INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_expenses_expense_date (expense_date),
    INDEX ix_expenses_category (category),
    INDEX ix_expenses_source (source_type, source_id),
    FOREIGN KEY (created_by_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
