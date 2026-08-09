-- Admin-only purchase cost for profit tracking (not shown on storefront)
ALTER TABLE products ADD COLUMN cost_price DECIMAL(10, 2) NULL;
