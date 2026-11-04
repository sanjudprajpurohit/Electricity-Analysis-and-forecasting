# Cheap Power Hours

German electricity prices change every hour and sometimes drop below zero.
When is power cheap, how much can an EV owner save by charging then, and can
we predict cheap hours before the price auction closes?

## Key findings so far
- Negative-price hours rose from 2.4% of all hours (2019) to 6.5% (2025).
  They happen mostly at midday (13:00–15:00), on weekends and holidays, and
  in spring.
- In very sunny hours, the price was negative 19% of the time, compared with
  1% in dark hours.
- In 2025, an EV owner charging 10 kWh/day would have cut the wholesale cost
  of charging by €176 (39%) by using the cheapest night hour instead of
  plugging in at 18:00, and by €326 (72%) using the cheapest hour of the day.
- The cheapest hours are moving from night to midday: the extra saving from
  daytime charging grew from €11 (2019) to €150 (2025).

## The question
1. What: (a) How much does charging an EV in the cheapest hours save compared
   with plugging in at 18:00? (b) At 10:00, before the day-ahead auction
   closes at 12:00, which hours of tomorrow will be cheap or negative?
2. Who: EV owners on dynamic tariffs, battery and EV-fleet operators.
3. When: the forecast is made at 10:00; only data known by then may be used.
4. Metric: euros saved per year; for the forecast, price error in €/MWh
   and how often cheap hours are correctly found.
5. Baseline: "plug in at 18:00" for charging; "tomorrow's prices look like
   the same hour last week" for the forecast.

## Assumptions (savings analysis)
- 10 kWh charged per day, 11 kW wallbox (about 1 hour), car at home 18:00–07:00.
- Wholesale day-ahead price only. Taxes and grid fees are the same every hour,
  so they don't change the savings.

## How to run
```bash
conda create -n power python=3.12 -y
conda activate power
pip install -r requirements.txt

python src/download_smard.py     # hourly prices
python src/download_weather.py   # hourly weather, 6 places in Germany
python src/make_holidays.py      # German public holidays
python src/build_db.py           # DuckDB tables + quality checks
```
Then open the notebooks in `notebooks/` in order.

## Project structure
| Folder | Contents |
| --- | --- |
| `src/` | Scripts: download, build database |
| `sql/` | SQL for cleaning and features (run by `build_db.py`) |
| `notebooks/` | 01 first look, 02 when prices go negative, 03 SQL checks, 04 EV savings |
| `data/` | Downloaded data and database (not in Git, rebuilt by the scripts) |

## Data
- Electricity prices: Bundesnetzagentur | SMARD.de (CC BY 4.0).
- Weather: Open-Meteo historical weather API, ERA5 (CC BY 4.0).
- Public holidays: Python package `holidays` (nationwide holidays only).

## Limitations
- Weather is the actual measured weather, not a forecast. A real forecast
  at 10:00 would only have predicted weather, so model results will look
  slightly better than in practice.
- Only nationwide holidays are included; regional holidays (e.g. Corpus
  Christi in Bavaria) are not.

## Status
Work in progress: data pipeline, analysis and savings done. Next: forecast
model, error analysis, Power BI dashboard.