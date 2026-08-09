-- Snapshot product cost on each order line for historical profit
ALTER TABLE order_items ADD COLUMN cost_price DECIMAL(10, 2) NULL;
