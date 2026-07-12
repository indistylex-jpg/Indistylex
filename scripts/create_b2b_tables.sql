-- B2B Sales tables for Indistylex
-- Run on production MySQL after deploying:
--   mysql -u indistylex -p indistylex < scripts/create_b2b_tables.sql

CREATE TABLE IF NOT EXISTS b2b_sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_number VARCHAR(30) NOT NULL UNIQUE,
    shop_name VARCHAR(200) NOT NULL,
    shop_phone VARCHAR(20),
    shop_city VARCHAR(100),
    payment_terms VARCHAR(20) NOT NULL DEFAULT 'cod',
    notes TEXT,
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0,
    extra_discount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    discount_percent DECIMAL(5, 2) NOT NULL DEFAULT 0,
    discount_reason VARCHAR(200),
    total DECIMAL(10, 2) NOT NULL DEFAULT 0,
    created_by_id INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_cancelled TINYINT(1) NOT NULL DEFAULT 0,
    INDEX ix_b2b_sales_sale_number (sale_number),
    FOREIGN KEY (created_by_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS b2b_sale_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    variant_id INT NOT NULL,
    product_name VARCHAR(300) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    size VARCHAR(20),
    color VARCHAR(50),
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES b2b_sales(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
