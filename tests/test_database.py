"""Tests for the DuckDB database built by src/build_db.py.

"""

import duckdb
import pytest

DB_FILE = "data/power.duckdb"


@pytest.fixture(scope="module")
def con():
    """Open the database once, share it with every test, close it at the end."""
    connection = duckdb.connect(DB_FILE, read_only=True)
    connection.sql("SET TimeZone = 'UTC'")
    yield connection
    connection.close()


def one_value(con, query):
    """Run a query that returns a single value, and return that value."""
    return con.sql(query).fetchall()[0][0]


def test_no_duplicate_hours(con):
    n_duplicates = one_value(con, """
        SELECT COUNT(*) FROM (
            SELECT ts_utc FROM features
            GROUP BY ts_utc
            HAVING COUNT(*) > 1
        )
    """)
    assert n_duplicates == 0


def test_no_gaps_between_hours(con):
    n_gaps = one_value(con, """
        SELECT COUNT(*) FROM (
            SELECT ts_utc - LAG(ts_utc) OVER (ORDER BY ts_utc) AS step
            FROM features
        )
        WHERE step <> INTERVAL 1 HOUR
    """)
    assert n_gaps == 0


def test_lag_24h_is_price_24_hours_earlier(con):
    n_wrong = one_value(con, """
        SELECT COUNT(*)
        FROM features AS now
        JOIN features AS before
            ON before.ts_utc = now.ts_utc - INTERVAL 24 HOUR
        WHERE now.price_lag_24h IS DISTINCT FROM before.price_euro_mwh
    """)
    assert n_wrong == 0


def test_joins_keep_one_row_per_price_hour(con):
    n_features = one_value(con, "SELECT COUNT(*) FROM features")
    n_prices = one_value(con, "SELECT COUNT(*) FROM prices_clean")
    assert n_features == n_prices


def test_holidays_are_marked(con):
    def is_holiday(day):
        return one_value(con, f"""
            SELECT BOOL_AND(is_holiday)
            FROM features
            WHERE CAST(ts_local AS DATE) = DATE '{day}'
        """)

    assert is_holiday("2025-05-01")        # Labour Day
    assert is_holiday("2025-12-25")        # Christmas
    assert not is_holiday("2025-05-06")    # a normal Tuesday