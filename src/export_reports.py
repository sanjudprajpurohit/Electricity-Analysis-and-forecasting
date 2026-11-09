"""We will now be exporting the result table from the database as csv files just so we can use it for making our report on power bi"""
from pathlib import Path
import duckdb

DB_FILE = Path("data/power.duckdb")
OUT_DIR = Path("data/reports")

EXPORTS = {
    "hourly_prices.csv": """
        Select
            ts_local,
            CAST(ts_local AS DATE) AS date,
            year, month, weekday, hour,
            is_weekend, is_holiday,
            price_euro_mwh, is_negative,
            radiation, wind_Speed, temperature
        FROM features
        ORDER BY ts_local
    """,
    "ev_savings.csv": "SELECT * FROM ev_Savings ORDER BY year",

}

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_FILE), read_only=True)
    con.sql("Set Timezone ='UTC'")

    for file_name, query in EXPORTS.items():
        out_file = OUT_DIR / file_name
        con.sql(query).write_csv(str(out_file))
        n_rows = con.sql(f"SELECT COUNT (*) FROM ({query})").fetchall()[0][0]
        print(f"Saved {n_rows} rows to {out_file}")

    con.close()

if __name__ == "__main__":
    main()