-- analysis_queries.sql
-- Business-intelligence SQL queries: revenue trends, top products,
-- customer RFM segments, and country-level breakdowns.

-- 1. What is the monthly revenue trend and how many orders were placed each month?
SELECT year_month, total_revenue, total_orders
FROM monthly_aggregates
ORDER BY year_month;

-- 2. Which 10 products generate the most total revenue?
SELECT stock_code, description, SUM(revenue) AS total_revenue
FROM orders
GROUP BY stock_code, description
ORDER BY total_revenue DESC
LIMIT 10;

-- 3. Who are the top 10 customers by total revenue, excluding guest checkouts?
SELECT customer_id, SUM(revenue) AS total_revenue
FROM orders
WHERE customer_id != 'Guest'
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;

-- 4. How are customers distributed across RFM segments, in count and percentage of total?
SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM rfm
GROUP BY segment
ORDER BY customer_count DESC;

-- 5. Which 10 countries generate the most revenue and orders?
SELECT
    country,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT invoice) AS total_orders
FROM orders
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;

-- 6. What is the average revenue per order for each month?
SELECT
    year_month,
    ROUND(total_revenue / NULLIF(total_orders, 0), 2) AS avg_revenue_per_order
FROM monthly_aggregates
ORDER BY year_month;

-- 7. Who are the VIP customers, and what are their recency, frequency, and monetary values?
SELECT customer_id, recency, frequency, monetary
FROM rfm
WHERE segment = 'VIP'
ORDER BY monetary DESC;
