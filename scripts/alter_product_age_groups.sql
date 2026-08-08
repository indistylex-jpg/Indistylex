-- Multi age groups for products
-- Run: mysql -u indistylex -p indistylex < scripts/alter_product_age_groups.sql

ALTER TABLE products
    ADD COLUMN age_groups VARCHAR(200) NULL AFTER age_group;

UPDATE products
SET age_groups = age_group
WHERE (age_groups IS NULL OR age_groups = '')
  AND age_group IS NOT NULL
  AND age_group != '';
