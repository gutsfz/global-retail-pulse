-- schema.sql
-- Defines all PostgreSQL tables for the Global Retail Pulse project.

DROP TABLE IF EXISTS orders;

-- orders: cleaned transaction-level data
CREATE TABLE orders (
    invoice TEXT,
    stock_code TEXT,
    description TEXT,
    quantity INTEGER,
    invoice_date DATE,
    price NUMERIC(10, 2),
    customer_id TEXT,
    country TEXT,
    revenue NUMERIC(10, 2)
);

DROP TABLE IF EXISTS monthly_aggregates;

-- monthly_aggregates: pre-computed monthly KPIs
CREATE TABLE monthly_aggregates (
    year_month TEXT PRIMARY KEY,
    total_revenue NUMERIC(12, 2),
    total_orders INTEGER,
    unique_customers INTEGER
);

DROP TABLE IF EXISTS rfm;

-- rfm: customer segmentation
CREATE TABLE rfm (
    customer_id TEXT PRIMARY KEY,
    recency INTEGER,
    frequency INTEGER,
    monetary NUMERIC(12, 2),
    segment TEXT
);
