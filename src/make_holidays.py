"""Making a table of all the nation wide holidays in germany throughout the year
Source: the python package "holidays"
"""

from pathlib import Path
import holidays
import pandas as pd

YEARS = range(2018, 2028)       #A little beyond today for further forecast predicitions
OUT_FILE = Path("data/raw/holidays.parquet")

def main() -> None:
    german_holidays = holidays.Germany(years=YEARS) #nationwide holidays only

    df = pd.DataFrame(
        sorted(german_holidays.items()),
        columns=["date", "holiday_name"],
    )
    df["date"] = pd.to_datetime(df["date"])

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_FILE, index=False)

    print(f"Saved {len(df)} holidays to {OUT_FILE}")
    print(df.groupby(df["date"].dt.year).size())

if __name__ == "__main__":
    main()

