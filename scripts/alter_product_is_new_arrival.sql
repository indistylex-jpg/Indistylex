-- Add explicit New Arrivals flag for homepage / shop curation
ALTER TABLE products ADD COLUMN is_new_arrival TINYINT(1) NOT NULL DEFAULT 0;
