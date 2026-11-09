-- Aşama 2: SQL ile Veri Yönetimi ve Sorgulama
-- Veritabanı: SQLite (ecommerce.db). Aynı sorgular MySQL/PostgreSQL/SQL Server'da küçük tarih/saat fonksiyonu
-- farklarıyla çalışır (SQLite: strftime, SQL Server: DATEPART).

-- 1) Veri ilişkilendirme: customers + orders -> tek analitik görünüm (View)
DROP VIEW IF EXISTS vw_order_analytics;
CREATE VIEW vw_order_analytics AS
SELECT
    o.order_id,
    o.order_date,
    o.order_time,
    CAST(strftime('%H', o.order_time) AS INTEGER) AS order_hour,
    strftime('%Y-%m', o.order_date)               AS order_month,
    o.total_amount,
    o.category,
    c.customer_id,
    c.signup_date,
    c.city,
    c.age,
    c.income_group,
    c.gender
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id;

-- 2a) En yüksek toplam ciro getiren ilk 5 şehir
-- name: top5_cities
SELECT
    city,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    COUNT(*)                    AS order_count
FROM vw_order_analytics
GROUP BY city
ORDER BY total_revenue DESC
LIMIT 5;

-- 2b) Günün saatlerine göre sipariş yoğunluğu (saatlik sipariş sayısı)
-- name: hourly_orders
SELECT
    order_hour,
    COUNT(*) AS order_count
FROM vw_order_analytics
GROUP BY order_hour
ORDER BY order_hour;

-- 2c) Kategorilere göre ortalama harcama tutarı
-- name: avg_by_category
SELECT
    category,
    ROUND(AVG(total_amount), 2) AS avg_order_value,
    COUNT(*)                    AS order_count
FROM vw_order_analytics
GROUP BY category
ORDER BY avg_order_value DESC;

-- Ek analizler (Power BI kırılımları ve veri hikayesi için)
-- name: kpis
SELECT
    ROUND(SUM(total_amount), 2)      AS total_revenue,
    COUNT(*)                         AS total_orders,
    COUNT(DISTINCT customer_id)      AS active_customers
FROM vw_order_analytics;

-- name: monthly_revenue
SELECT order_month, ROUND(SUM(total_amount), 2) AS revenue, COUNT(*) AS order_count
FROM vw_order_analytics
GROUP BY order_month
ORDER BY order_month;

-- name: by_gender
SELECT gender, ROUND(SUM(total_amount), 2) AS revenue, ROUND(AVG(total_amount), 2) AS avg_order_value
FROM vw_order_analytics
GROUP BY gender;

-- name: by_income
SELECT income_group, ROUND(SUM(total_amount), 2) AS revenue, ROUND(AVG(total_amount), 2) AS avg_order_value
FROM vw_order_analytics
GROUP BY income_group
ORDER BY revenue DESC;
