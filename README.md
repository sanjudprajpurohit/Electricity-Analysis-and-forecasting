# Cheap Power Hours

German electricity prices change every hour and sometimes drop below zero.
When is power cheap, how much can an EV owner save by charging then, and can
we predict cheap hours before the price auction closes?

## The question
1. What: (a) How much does charging an EV in the cheapest hours save compared
   with charging every evening? (b) At 10:00, before the day-ahead auction
   closes at 12:00, which hours of tomorrow will be cheap or negative?
2. Who: EV owners on dynamic tariffs, battery and EV-fleet operators.
3. When: the forecast is made at 10:00; only data known by then may be used.
4. Metric: euros saved per year; for the forecast, price error in EUR/MWh
   and how often cheap hours are correctly found.
5. Baseline: "always charge at 13:00" and "tomorrow's prices look like the
   same hour last week".

## Data
Electricity market data: Bundesnetzagentur | SMARD.de (CC BY 4.0).
Weather: Open-Meteo (CC BY 4.0).

## Status
Work in progress.