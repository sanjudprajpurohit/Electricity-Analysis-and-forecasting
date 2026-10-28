"""Download hourly German day-ahead electricity prices from SMARD.

Source: Bundesnetzagentur | SMARD.de (CC BY 4.0)
Run with: python src/download_smard.py
"""

import time 
from pathlib import Path
import pandas as pd 
import requests
BASE_URL = "https://www.smard.de/app/chart_data" #The website used for the data
FILTER = 4169  #which data series: day-ahead price, Germany/Luxembourg
REGION = "DE"   #GERMANY
RESOLUTION = "hour"     #means one value per hour
OUT_FILE = Path("data/raw/prices.parquet")

def get_json(url: str) -> dict:     #Download the data and returns as a python dict
    response = requests.get(url, timeout=60)
    response.raise_for_status() #Stop if the server returns an error
    return response.json()

def get_week_starts() -> list[int]:  #it reutns the start time in ms of every week smard has data for.
    url =f"{BASE_URL}/{FILTER}/{REGION}/index_{RESOLUTION}.json"
    return get_json(url)["timestamps"]

def get_week(week_start: int) ->list[list]:     #returns pairs of one week of pairs such as (timestamps_ms, price) 
    url = (
        f"{BASE_URL}/{FILTER}/{REGION}/"
        f"{FILTER}_{REGION}_{RESOLUTION}_{week_start}.json"
    )
    return get_json(url)["series"]

def main() -> None:
    week_starts = get_week_starts()
    print(f"SMARD has {len(week_starts)} weeks of data. Downloading")

    rows =[]
    for i, week_start in enumerate(week_starts,start=1):
        rows.extend(get_week(week_start))
        if i %50 ==0:
            print(f"{i}/{len(week_starts)} weeks done")
        time.sleep(0.2)     #a short pause between requests

    df = pd.DataFrame(rows, columns=["timestamp_ms","price_euro_mwh"])
    df["ts_utc"] = pd.to_datetime(df["timestamp_ms"], unit="ms", utc=True)
    df = df[["ts_utc", "price_euro_mwh"]]

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_FILE, index=False)
    print(f"Saved {len(df)} rows to {OUT_FILE}")
    print(f"From {df["ts_utc"].min()} to {df['ts_utc'].max()}")
    print(f"Missing prices: {df['price_euro_mwh'].isna().sum()}")

if __name__ == "__main__":
    main()

