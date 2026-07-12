-- Add extra discount columns to existing b2b_sales table
-- Run if b2b_sales already exists without discount fields:
--   mysql -u indistylex -p indistylex < scripts/alter_b2b_discount_columns.sql

ALTER TABLE b2b_sales
  ADD COLUMN subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0 AFTER notes,
  ADD COLUMN extra_discount DECIMAL(10, 2) NOT NULL DEFAULT 0 AFTER subtotal,
  ADD COLUMN discount_percent DECIMAL(5, 2) NOT NULL DEFAULT 0 AFTER extra_discount,
  ADD COLUMN discount_reason VARCHAR(200) NULL AFTER discount_percent;

-- Backfill subtotal from items for existing sales
UPDATE b2b_sales s
SET s.subtotal = (
    SELECT COALESCE(SUM(i.line_total), 0)
    FROM b2b_sale_items i
    WHERE i.sale_id = s.id
)
WHERE s.subtotal = 0;
