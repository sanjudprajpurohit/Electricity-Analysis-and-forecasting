   -- EV charging savings per year: plugging in at 18:00 vs cheaper strategies.
   -- Assumptions: 10 kWh per day, car at home 18:00-07:00, wholesale price only.

   CREATE OR REPLACE TABLE ev_savings AS 
   WITH nights AS (
    --Step 1: We keep only the hours the car is at home (18:00 to 7:00
    -- and label each hour with the evening it belongs it 
    SELECT
        CAST(ts_local - INTERVAL 7 HOUR AS DATE) AS night,
        hour,
        price_euro_mwh
    FROM features
    WHERE hour >= 18 OR hour <7
),
per_night AS (
    -- Step 2: for each night, the price at 18:00 and the cheapest price
    SELECT
        night,
        MAX(price_euro_mwh)FILTER (WHERE hour = 18) AS price_at_18,
        MIN(price_euro_mwh)                          AS price_cheapest_night
    FROM nights
    GROUP BY night
    HAVING COUNT(*) >= 12          -- complete nights only
),
per_day AS (
    -- Step 3: the cheapest hour of each whole day
    SELECT
        CAST(ts_local AS DATE) AS day,
        MIN(price_euro_mwh)    AS price_cheapest_day
    FROM features
    GROUP BY day
),
per_year AS (
    -- Step 4: add up the cost of 10 kWh per day, per year
    SELECT
        year(n.night)                             AS year,
        COUNT(*)                                  AS n_days,
        SUM(n.price_at_18)          * 10 / 1000   AS cost_plug_in,
        SUM(n.price_cheapest_night) * 10 / 1000   AS cost_smart_night,
        SUM(d.price_cheapest_day)   * 10 / 1000   AS cost_best_hour
    FROM per_night AS n
    JOIN per_day AS d
        ON n.night = d.day
    GROUP BY year
)
SELECT
    year,
    n_days,
    ROUND(cost_plug_in, 0)                       AS cost_plug_in_eur,
    ROUND(cost_smart_night, 0)                   AS cost_smart_night_eur,
    ROUND(cost_best_hour, 0)                     AS cost_best_hour_eur,
    ROUND(cost_plug_in - cost_smart_night, 0)    AS saving_smart_night_eur,
    ROUND(cost_plug_in - cost_best_hour, 0)      AS saving_best_hour_eur
FROM per_year
ORDER BY year;