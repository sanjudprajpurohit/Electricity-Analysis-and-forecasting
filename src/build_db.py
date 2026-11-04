""" Building the DuckDB databse from the raw price file
Runs from the project folder: python src/build_db.py"""

from pathlib import Path
import duckdb
DB_FILE = Path("data/power.duckdb")
SQL_DIR = Path("sql")

def one_value(con, query: str):
    """Run a query that returns a single number and reuturn the that number"""
    return con.sql(query).fetchall()[0][0]

def main() -> None:
    con = duckdb.connect(str(DB_FILE))
    con.sql("Set Timezone = 'UTC'")
    ### Run every SQL file in the sql folder, in name order (01, 02, ...)
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        print(f"Running {sql_file}...")
        con.sql(sql_file.read_text(encoding="utf-8"))
    ##Quality checks
    n_raw = one_value(con, "SELECT COUNT(*) FROM prices_raw")
    n_clean = one_value(con, "SELECT COUNT(*) FROM prices_clean")

    n_duplicates = one_value(con, """
        SELECT COUNT(*) FROM (
            SELECT ts_utc FROM prices_raw
            GROUP BY ts_utc
            HAVING COUNT(*) > 1
        )
    """)

    n_odd_days = one_value(con, """
        SELECT COUNT(*) FROM (
            SELECT CAST(ts_local AS DATE) AS day_local
            FROM prices_clean
            GROUP BY day_local
            HAVING COUNT(*) NOT IN (23, 24, 25)
        )
    """)

    print(f"prices_raw: {n_raw} rows")
    print(f"prices_clean: {n_clean} rows ({n_raw - n_clean}without a price removed)")
    print(f"Duplicate timestamp: {n_duplicates}")
    print(f"Days with an unusual number of hours: {n_odd_days}")
    n_features = one_value(con, "SELECT COUNT(*) FROM features")
    n_no_weather = one_value(con, "SELECT COUNT(*) FROM features WHERE radiation IS NULL")
    n_holidays_hours = one_value(con, "SELECT COUNT(*) FROM features WHERE is_holiday")
    print(f"features: {n_features} rows")
    print(f"hours without weather: {n_no_weather}")
    print(f"holiday hours: {n_holidays_hours}")

    assert n_duplicates == 0, "duplicate timestamps found" ##Stop if something went wrong
    assert n_odd_days == 0, "Some days have missing or extra hours!"
    assert n_features ==n_clean, "The joins added or lost rows"
    con.close()

if __name__ == "__main__":
    main()