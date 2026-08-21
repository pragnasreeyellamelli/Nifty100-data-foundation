-- NIFTY 100 DATA FOUNDATION
-- DAY 07: EXPLORATORY QUERIES

-- 1. Total number of companies
SELECT COUNT(*) AS total_companies
FROM companies;


-- 2. List all companies
SELECT company_id, company_name, ticker
FROM companies
ORDER BY company_id;


-- 3. Companies with the most P&L records
SELECT company_id, COUNT(*) AS year_count
FROM profit_and_loss
GROUP BY company_id
ORDER BY year_count DESC
LIMIT 10;


-- 4. Companies with fewer than 5 P&L records
SELECT company_id, COUNT(*) AS year_count
FROM profit_and_loss
GROUP BY company_id
HAVING COUNT(*) < 5
ORDER BY company_id;


-- 5. Year coverage in the P&L table
SELECT year, COUNT(*) AS company_count
FROM profit_and_loss
GROUP BY year
ORDER BY year;


-- 6. Top 10 companies by revenue/sales
SELECT company_id, year, sales
FROM profit_and_loss
WHERE sales IS NOT NULL
ORDER BY sales DESC
LIMIT 10;


-- 7. Top 10 companies by net profit
SELECT company_id, year, net_profit
FROM profit_and_loss
WHERE net_profit IS NOT NULL
ORDER BY net_profit DESC
LIMIT 10;


-- 8. Companies with the highest OPM percentage
SELECT company_id, year, opm_percentage
FROM profit_and_loss
WHERE opm_percentage IS NOT NULL
ORDER BY opm_percentage DESC
LIMIT 10;


-- 9. Count records by sector
SELECT sector, COUNT(*) AS company_count
FROM sectors
GROUP BY sector
ORDER BY company_count DESC;


-- 10. Stock price record count by company
SELECT company_id, COUNT(*) AS price_records
FROM stock_prices
GROUP BY company_id
ORDER BY price_records DESC
LIMIT 10;