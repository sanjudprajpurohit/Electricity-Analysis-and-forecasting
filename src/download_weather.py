"""We will now download the hourly weather for six places in Germany form Open-Meteo.
The source is - Open-meteo historical weather API (ERAS), CC by 4.0
Run this scirpt as python src/download_weather.py once finished. All these comments are for understandig it clearly and a better documentation"""

import time
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import requests

URL = "https://archive-api.open-meteo.com/v1/archive" #The website

#Windy north and sunny south, so the average reflects the all of germany
PLACES = {
    "husum": (54.48, 9.05), #north sea coast: wind
    "emden": (53.37, 7.21), #north sea coast: wind
    "rostock": (54.09, 12.10), #Baltic coast: wind
    "berlin": (52.52, 13.41), #East and where I live :)
    "stuttgart": (48.78, 9.18), #south-west: sun
    "munich": (48.14, 11.58), #south:sun

}

VARIABLES = ["shortwave_radiation", "wind_speed_100m", "temperature_2m"]
FIRST_YEAR = 2018
LAST_DAY = date.today() - timedelta(days=6) #newest data arrives ~5 days late
OUT_FILE = Path("data/raw/weather.parquet")

def get_json(params: dict, max_tries: int = 5) -> list:
    """Ask Open-Meteo for data and return its JSON answer.

    If the server is busy (503) or we ask too often (429),
    wait and try again, a little longer each time.
    """
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
def get_year(year: int) -> pd.DataFrame:
    """Downloading one year of hourly weather for all places at once"""
    start = date(year, 1, 1)
    end = min(date(year, 12, 31), LAST_DAY)

    params= {
        "latitude": ",".join(str(lat) for lat, lon in PLACES.values()),
        "longitude": ",".join(str(lon) for lat, lon in PLACES.values()),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "hourly": ",".join(VARIABLES),
        "timezone": "GMT",
    
}
    answer = get_json(params) #a list- one entry per place, same order as PLACES 

    tables =[]
    for place, entry in zip(PLACES, answer):
        table = pd.DataFrame(entry["hourly"])
        table["place"] = place
        tables.append(table)
    return pd.concat(tables, ignore_index=True)

def main() -> None:
    years = range(FIRST_YEAR, LAST_DAY.year + 1)
    tables =[]
    for year in years:
        print(f"Downloading {year}...")
        tables.append(get_year(year))
        time.sleep(1) 

    df = pd.concat(tables, ignore_index=True)
    df["ts_utc"] = pd.to_datetime(df["time"], utc=True)
    df = df[["ts_utc", "place", *VARIABLES]]

    OUT_FILE.parent.mkdir(parents=True,exist_ok=True)
    df.to_parquet(OUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUT_FILE}")
    print(f"From {df['ts_utc'].min()} to {df['ts_utc'].max()}")
    print(f"Places: {df['place'].nunique()}")
    print("missing values per column:")
    print(df.isna().sum())

   
if __name__ == "__main__":
    main()