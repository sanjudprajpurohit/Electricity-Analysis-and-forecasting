-- Build the raw and clean price tables.
-- Run from the project folder: python src/build_db.py

-- 1. Raw table: the Parquet file exactly as downloaded
CREATE OR REPLACE TABLE prices_raw AS
SELECT *
FROM read_parquet('data/raw/prices.parquet');

-- 2. Clean table: drop future hours, add German time and helper columns
CREATE OR REPLACE TABLE prices_clean AS
WITH with_local AS (
    SELECT
        ts_utc,
        ts_utc AT TIME ZONE 'Europe/Berlin' AS ts_local,
        price_euro_mwh
    FROM prices_raw
    WHERE price_euro_mwh IS NOT NULL
)
SELECT
    ts_utc,
    ts_local,
    price_euro_mwh,
    year(ts_local)      AS year,
    month(ts_local)     AS month,
    isodow(ts_local)    AS weekday,   -- 1 = Monday ... 7 = Sunday
    hour(ts_local)      AS hour,
    price_euro_mwh < 0  AS is_negative
FROM with_local;
