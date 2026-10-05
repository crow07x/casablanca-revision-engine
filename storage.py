import sqlite3
from contextlib import contextmanager

import pandas as pd

from config import DB_PATH, UNIVERSE

PRICE_COLUMNS = ["ticker", "date", "close", "low", "high", "volume"]


@contextmanager
def get_connection():
	conn = sqlite3.connect(DB_PATH)
	try:
		yield conn
		conn.commit()
	except Exception:
		conn.rollback()
		raise
	finally:
		conn.close()


def init_db():
	with get_connection() as conn:
		conn.execute("""
			CREATE TABLE IF NOT EXISTS companies (
				ticker TEXT PRIMARY KEY,
				name   TEXT NOT NULL,
				sector TEXT
			)
		""")
		conn.execute("""
			CREATE TABLE IF NOT EXISTS prices (
				ticker TEXT NOT NULL,
				date   TEXT NOT NULL,
				close  REAL,
				low    REAL,
				high   REAL,
				volume REAL,
				PRIMARY KEY (ticker, date)
			)
		""")
		conn.execute("""
			CREATE TABLE IF NOT EXISTS estimates (
				id            INTEGER PRIMARY KEY AUTOINCREMENT,
				ticker        TEXT NOT NULL,
				period        TEXT NOT NULL,
				eps           REAL NOT NULL,
				source        TEXT,
				date_recorded TEXT NOT NULL
			)
		""")
		conn.execute("""
			CREATE INDEX IF NOT EXISTS idx_estimates_lookup
			ON estimates (ticker, period, date_recorded)
		""")
		conn.executemany(
			"INSERT OR IGNORE INTO companies (ticker, name) VALUES (?, ?)",
			list(UNIVERSE.items()),
		)


def save_prices(df):
	if df is None or df.empty:
		return 0

	missing = set(PRICE_COLUMNS) - set(df.columns)
	if missing:
		raise ValueError(f"save_prices: missing columns {missing}")

	rows_df = df[PRICE_COLUMNS].astype(object)
	rows_df = rows_df.where(rows_df.notna(), None)
	rows = [tuple(r) for r in rows_df.itertuples(index=False, name=None)]

	with get_connection() as conn:
		conn.executemany(
			"INSERT OR REPLACE INTO prices "
			"(ticker, date, close, low, high, volume) VALUES (?, ?, ?, ?, ?, ?)",
			rows,
		)
	return len(rows)


def load_prices(ticker, start=None, end=None):
	query = "SELECT date, close, low, high, volume FROM prices WHERE ticker = ?"
	params = [ticker]

	if start:
		query += " AND date >= ?"
		params.append(start)
	if end:
		query += " AND date <= ?"
		params.append(end)
	query += " ORDER BY date"

	with get_connection() as conn:
		df = pd.read_sql_query(query, conn, params=params)

	df["date"] = pd.to_datetime(df["date"])
	return df.set_index("date")


def add_estimate(ticker, period, eps, source, date_recorded):
	with get_connection() as conn:
		conn.execute(
			"INSERT INTO estimates (ticker, period, eps, source, date_recorded) "
			"VALUES (?, ?, ?, ?, ?)",
			(ticker, period, eps, source, date_recorded),
		)


def delete_estimates(ticker=None):
	with get_connection() as conn:
		if ticker is None:
			cursor = conn.execute("DELETE FROM estimates")
		else:
			cursor = conn.execute("DELETE FROM estimates WHERE ticker = ?", (ticker,))
		return cursor.rowcount


def load_estimates(ticker=None):
	query = "SELECT id, ticker, period, eps, source, date_recorded FROM estimates"
	params = []

	if ticker:
		query += " WHERE ticker = ?"
		params.append(ticker)
	query += " ORDER BY ticker, period, date_recorded, id"

	with get_connection() as conn:
		return pd.read_sql_query(query, conn, params=params)
