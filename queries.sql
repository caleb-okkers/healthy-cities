-- =========================================================
-- Healthy Cities Data Lake Queries
-- =========================================================

-- =========================================================
-- 1. Create raw table (CSV import)
-- =========================================================
CREATE EXTERNAL TABLE healthy_cities_db.healthy_lifestyle_2021_raw (
    city STRING,
    rank STRING,
    sunshine_hours_city STRING,
    cost_bottle_water_city STRING,
    obesity_levels_country STRING,
    life_expectancy_years_country STRING,
    pollution_index_city STRING,
    annual_avg_hours_worked STRING,
    happiness_levels_country STRING,
    outdoor_activities_city STRING,
    number_takeout_places_city STRING,
    cost_monthly_gym_membership_city STRING
)
ROW FORMAT SERDE 
    'org.apache.hadoop.hive.serde2.OpenCSVSerde' 
WITH SERDEPROPERTIES (
    'escapeChar'='\\',
    'quoteChar'='"',
    'separatorChar'=',' 
)
STORED AS INPUTFORMAT 
    'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
    'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://healthy-cities-data-lake-caleb-okkers-2026/raw/healthy_lifestyle_2021'
TBLPROPERTIES (
    'skip.header.line.count'='1',
    'transient_lastDdlTime'='1771248921'
);

-- =========================================================
-- 2. Create processed table (cleaned, numeric types, imputed missing values)
-- =========================================================
CREATE TABLE healthy_cities_db.healthy_cities_processed
WITH (
    external_location = 's3://healthy-cities-data-lake-caleb-okkers-2026/processed/healthy_lifestyle_2021_parquet/',
    format = 'PARQUET',
    parquet_compression = 'SNAPPY'
) AS
SELECT
    city,
    CAST(rank AS INTEGER) AS rank,
    CAST(sunshine_hours_city AS DOUBLE) AS sunshine_hours_city,
    CAST(REPLACE(cost_bottle_water_city,'£','') AS DOUBLE) AS cost_bottle_water_city,
    CAST(REPLACE(obesity_levels_country, '%','') AS DOUBLE) AS obesity_levels_country,
    CAST(life_expectancy_years_country AS DOUBLE) AS life_expectancy_years_country,
    CAST(pollution_index_city AS DOUBLE) AS pollution_index_city,
    CAST(annual_avg_hours_worked AS DOUBLE) AS annual_avg_hours_worked,
    CAST(happiness_levels_country AS DOUBLE) AS happiness_levels_country,
    CAST(outdoor_activities_city AS DOUBLE) AS outdoor_activities_city,
    CAST(number_takeout_places_city AS DOUBLE) AS number_takeout_places_city,
    CAST(REPLACE(cost_monthly_gym_membership_city,'£','') AS DOUBLE) AS cost_monthly_gym_membership_city
FROM healthy_cities_db.healthy_lifestyle_2021_raw;

-- =========================================================
-- 3. Create view for health index (optional computed metrics)
-- =========================================================
CREATE OR REPLACE VIEW healthy_cities_db.vw_healthy_cities_index AS
SELECT
    city,
    -- Health score: example metric
    (100 - obesity_levels_country + life_expectancy_years_country) / 2 AS health_score,
    -- Cost proxy: simple normalized sum of gym + water cost
    (cost_bottle_water_city + cost_monthly_gym_membership_city) AS cost_proxy
FROM healthy_cities_db.healthy_cities_processed;

-- =========================================================
-- 4. Create gold table combining processed + computed metrics
-- =========================================================
CREATE TABLE healthy_cities_db.healthy_cities_gold
WITH (
    external_location = 's3://healthy-cities-data-lake-caleb-okkers-2026/gold/healthy_lifestyle_2021/',
    format = 'PARQUET',
    parquet_compression = 'SNAPPY'
) AS
SELECT
    p.city,
    p.rank,
    p.sunshine_hours_city,
    p.cost_bottle_water_city,
    p.obesity_levels_country,
    p.life_expectancy_years_country,
    p.pollution_index_city,
    p.annual_avg_hours_worked,
    p.happiness_levels_country,
    p.outdoor_activities_city,
    p.number_takeout_places_city,
    p.cost_monthly_gym_membership_city,
    v.health_score,
    v.cost_proxy
FROM healthy_cities_db.healthy_cities_processed p
JOIN healthy_cities_db.vw_healthy_cities_index v
    ON TRIM(LOWER(p.city)) = TRIM(LOWER(v.city));

-- =========================================================
-- 5. Export query (ready for dashboard)
-- =========================================================
SELECT *
FROM healthy_cities_db.healthy_cities_gold
ORDER BY health_score DESC, cost_proxy ASC, city ASC;

-- =========================================================
-- 6. Sample queries for screenshots
-- =========================================================

-- a) View top 10 healthiest cities
SELECT *
FROM healthy_cities_db.healthy_cities_gold
ORDER BY health_score DESC
LIMIT 10;

-- b) View top 10 cheapest cities (cost proxy)
SELECT *
FROM healthy_cities_db.healthy_cities_gold
ORDER BY cost_proxy ASC
LIMIT 10;

-- c) Scatter plot metrics: health_score vs cost_proxy (for dashboard)
SELECT city, health_score, cost_proxy
FROM healthy_cities_db.healthy_cities_gold;