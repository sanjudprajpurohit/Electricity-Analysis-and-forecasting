--- Building the features table, everything the model will learn from
---It needs prices_clean (from 01_prices_clean_sql)"""

---Weather and holidays exactly as downloaded"""

CREATE OR REPLACE TABLE weather_raw AS
SELECT * FROM read_parquet('data/raw/weather.parquet');

CREATE OR REPLACE TABLE holidays_raw AS
SELECT CAST(date AS DATE) AS date, holiday_name
FROM read_parquet('data/raw/holidays.parquet');

----One weather value per hour for germany: the average of the six places"""
CREATE OR REPLACE TABLE weather_de AS
WITH hourly_avg AS (
    SELECT
        ts_utc,
        AVG(shortwave_radiation) AS radiation,
        AVG(wind_speed_100m) AS wind_speed,
        AVG(temperature_2m) AS temperature,
    FROM weather_raw
    GROUP BY ts_utc
)
SELECT 
    ts_utc,
    -- Radiation at 13:00 is the average of 12:00-13-00, so it belongs to the 
    --price hour starting at 12:00 take the value from the NExt row.
    LEAD(radiation, 1) over (ORDER BY ts_utc) AS radiation,
    wind_speed,
    temperature
FROM hourly_avg;

--3. The feature table: one row per price hour
CREATE OR REPLACE TABLE features AS 
with price_history AS (
    SELECT
    *,
    -- PAST PRICES. ROWS ARE HOURLY WITH NO GAPS (CHECKED IN OUR PREVIOUS FILE BUILD_DB.PY),
    -- SO 24 ROWS BACK = 24 HOURS BACK.
    LAG(price_euro_mwh, 24) OVER (ORDER BY ts_utc) AS price_lag_24h,
    LAG(price_euro_mwh, 48) OVER(ORDER BY ts_utc) AS price_lag_48h,
    LAG(price_euro_mwh, 168) OVER(ORDER BY ts_utc) AS price_lag_168h,
    AVG(price_euro_mwh) OVER (
        ORDER BY ts_utc
        ROWS BETWEEN 191 PRECEDING AND 24 PRECEDING
    ) AS price_avg_7d
FROM prices_clean
)
SELECT
    p.ts_utc,
    p.ts_local,
    p.price_euro_mwh,
    p.is_negative,
    --Calender
    p.year,
    p.month,
    p.weekday,
    p.hour,
    p.weekday >= 6 AS is_weekend,
    h.date IS NOT NULL AS is_holiday,
    -- past prices
    p.price_lag_24h,
    p.price_lag_48h,
    p.price_lag_168h,
    p.price_avg_7d,
    --weather
    w.radiation,
    w.wind_speed,
    w.temperature
FROM price_history AS p 
LEFT JOIN holidays_raw AS h 
    ON CAST (p.ts_local AS DATE) = h.date
LEFT JOIN weather_de AS w 
    ON p.ts_utc = w.ts_utc;
