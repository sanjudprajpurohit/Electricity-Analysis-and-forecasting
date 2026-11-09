"""Download old weather FORECASTS for 2025 from Open-Meteo.

For each hour, what the forecast said 1 day and 2 days in advance.
Used to test the model with information that really existed at 10:00.

Source: Open-Meteo Previous Runs API, CC BY 4.0
Run with: python src/download_weather_forecast.py
"""

import time
from pathlib import Path

import pandas as pd
import requests

# --- Settings -------------------------------------------------------------
URL = "https://previous-runs-api.open-meteo.com/v1/forecast"

# Same six places as download_weather.py
PLACES = {
    "husum":     (54.48, 9.05),
    "emden":     (53.37, 7.21),
    "rostock":   (54.09, 12.10),
    "berlin":    (52.52, 13.41),
    "stuttgart": (48.78, 9.18),
    "munich":    (48.14, 11.58),
}

BASE_VARIABLES = ["shortwave_radiation", "wind_speed_100m", "temperature_2m"]
DAYS_AHEAD = [1, 2]
VARIABLES = [f"{v}_previous_day{d}" for d in DAYS_AHEAD for v in BASE_VARIABLES]

YEAR = 2025
OUT_FILE = Path("data/raw/weather_forecast_2025.parquet")


def get_json(params: dict, max_tries: int = 5) -> list:
    """Ask Open-Meteo for data; wait and retry if the server is busy."""
    for attempt in range(1, max_tries + 1):
        response = requests.get(URL, params=params, timeout=120)
        if response.status_code in (429, 503):
            wait = 30 * attempt
            print(f"  Server busy ({response.status_code}), waiting {wait} s "
                  f"(try {attempt} of {max_tries})...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("Open-Meteo is still busy. Try again later.")


def get_month(month_start: pd.Timestamp) -> pd.DataFrame:
    """Download one month of forecasts for all places at once."""
    month_end = month_start + pd.offsets.MonthEnd(0)
    params = {
        "latitude": ",".join(str(lat) for lat, lon in PLACES.values()),
        "longitude": ",".join(str(lon) for lat, lon in PLACES.values()),
        "start_date": month_start.date().isoformat(),
        "end_date": month_end.date().isoformat(),
        "hourly": ",".join(VARIABLES),
        "timezone": "GMT",
    }
    answer = get_json(params)   # a list: one entry per place

    tables = []
    for place, entry in zip(PLACES, answer):
        table = pd.DataFrame(entry["hourly"])
        table["place"] = place
        tables.append(table)
    return pd.concat(tables, ignore_index=True)


def main() -> None:
    months = pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-01", freq="MS")
    tables = []
    for month_start in months:
        print(f"Downloading {month_start:%Y-%m}...")
        tables.append(get_month(month_start))
        time.sleep(1)   # be polite to a free service

    df = pd.concat(tables, ignore_index=True)
    df["ts_utc"] = pd.to_datetime(df["time"], utc=True)
    df = df[["ts_utc", "place", *VARIABLES]]

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_FILE, index=False)

    print(f"Saved {len(df)} rows to {OUT_FILE}")
    print(f"From {df['ts_utc'].min()} to {df['ts_utc'].max()}")
    print("Missing values per column:")
    print(df.isna().sum())


if __name__ == "__main__":
    main()
    