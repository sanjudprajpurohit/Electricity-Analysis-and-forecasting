# Cheap Power Hours

German electricity prices change every hour and sometimes drop below zero.
When is power cheap, how much can an EV owner save by charging then, and can
we predict cheap hours before the price auction closes?

## Key findings
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
- Forecast (test year 2025, using only information available at 10:00):
  LightGBM is about 25% more accurate than "same as yesterday" (19.6 vs
  26.0 €/MWh average error). Warning when the forecast is below 20 €/MWh,
  it catches 63% of negative-price hours (vs 54%) with fewer false alarms
  (29% vs 46%).
  - The pattern is getting extreme: in June 2025, about 3 in 4 hours between
  13:00 and 15:00 had negative prices. In winter, cheap hours move to the
  night (wind, low demand).

## Dashboard
Two-page Power BI dashboard: when negative prices happen (by year, hour and
month, filterable by year), and what they are worth (EV savings, forecast vs
actual, forecast accuracy).

[PDF version](reports/dashboard.pdf) · [Power BI file](reports/cheap_power_hours.pbix)


## The question
1. What: (a) How much does charging an EV in the cheapest hours save compared
   with plugging in at 18:00? (b) At 10:00, before the day-ahead auction
   closes at 12:00, which hours of tomorrow will be cheap or negative?
2. Who: EV owners on dynamic tariffs, battery and EV-fleet operators.
3. When: the forecast is made at 10:00; only data known by then may be used.
4. Metric: euros saved per year; for the forecast, average error in €/MWh
   and how often negative hours are correctly found.
5. Baseline: "plug in at 18:00" for charging; "same hour yesterday" and
   "same hour last week" for the forecast.

## Method (forecast)
- Features: calendar, German public holidays, past prices (24 h, 48 h,
  1 week, 7-day average), sunshine, wind and temperature (average of six
  places across Germany).
- Time-based split: train 2019–2023, validate 2024, test 2025 once.
  The final model is retrained on 2019–2024 before the test.
- Model: LightGBM, lightly tuned on 2024 (tuning changed the error by only
  0.2 €/MWh).
- Tested on 2025 with real weather forecasts made two days in advance, so
  no information from after 10:00 is used.

## Assumptions (savings analysis)
- 10 kWh charged per day, 11 kW wallbox (about 1 hour), car at home 18:00–07:00.
- Wholesale day-ahead price only. Taxes and grid fees are the same every hour,
  so they don't change the savings.

## How to run
```bash
conda create -n power python=3.12 -y
conda activate power
pip install -r requirements.txt

python src/download_smard.py              # hourly prices
python src/download_weather.py            # hourly weather, 6 places in Germany
python src/download_weather_forecast.py   # old weather forecasts for 2025
python src/make_holidays.py               # German public holidays
python src/build_db.py                    # DuckDB tables + quality checks
pytest                                    # 5 checks on the database
python src/export_reports.py              # CSV files for Power BI in data/reports/
```
Then open the notebooks in `notebooks/` in order.
For the dashboard, open
`reports/cheap_power_hours.pbix` in Power BI Desktop and click Refresh.

## Project structure
| Folder | Contents |
| --- | --- |
| `src/` | Scripts: downloads, database build, report export |
| `sql/` | SQL for cleaning, features and EV savings (run by `build_db.py`) |
| `tests/` | Automatic checks on the database (`pytest`) |
| `notebooks/` | 01 first look, 02 when prices go negative, 03 SQL checks, 04 EV savings, 05 forecast and error analysis
| `reports/` | Power BI dashboard (`.pbix`) and its PDF export |
| `data/` | Downloaded data, database and report files (not in Git, rebuilt by the scripts) |

## Data
- Electricity prices: Bundesnetzagentur | SMARD.de (CC BY 4.0).
- Weather: Open-Meteo historical weather API, ERA5 (CC BY 4.0).
- Weather forecasts: Open-Meteo Previous Runs API (CC BY 4.0).
- Public holidays: Python package `holidays` (nationwide holidays only).

## Limitations
- The model is trained on measured weather and tested on forecasts, because
  forecast archives only go back to 2024. Results with forecasts were almost
  identical to using measured weather (19.6–20.0 vs 19.8 €/MWh).
- Hardest cases: midday solar hours, and winter days when wind changes
  suddenly (price spikes on calm days, drops on stormy days).
- The sunshine clue is crude (six places, no solar capacity), which likely
  limits accuracy at midday.
- Only nationwide holidays are included; regional holidays (e.g. Corpus
  Christi in Bavaria) are not.

## Next steps
- Use actual or forecast solar and wind generation instead of raw weather.
- Add features that describe change, e.g. "wind today minus wind yesterday".

## Status
Complete: data pipeline, analysis, EV savings, forecast model, error analysis,
tests and Power BI dashboard.