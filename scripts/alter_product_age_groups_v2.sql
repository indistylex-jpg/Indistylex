-- Widen age_groups column for granular multi-select storage
-- Run: mysql -u indistylex -p indistylex < scripts/alter_product_age_groups_v2.sql

ALTER TABLE products
    MODIFY COLUMN age_groups VARCHAR(500) NULL;
