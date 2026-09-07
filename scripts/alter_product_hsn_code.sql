-- Add GST HSN code column for product invoices (safe to re-run).
ALTER TABLE products ADD COLUMN hsn_code VARCHAR(10) NULL;
