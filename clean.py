import logging
from datetime import date, datetime

import pandas as pd

LOGGER = logging.getLogger(__name__)
MONTHS = {
	"janv.": "01",
	"févr.": "02",
	"mars": "03",
	"avr.": "04",
	"mai": "05",
	"juin": "06",
	"juil.": "07",
	"août": "08",
	"sept.": "09",
	"oct.": "10",
	"nov.": "11",
	"déc.": "12",
}


def _normalize_number(value):
	if pd.isna(value):
		return pd.NA

	text = str(value).strip()
	if text in {"", "-", "nan", "NaN", "None", "null"}:
		return pd.NA

	text = text.replace(" ", "")
	is_percent = text.endswith("%")
	if is_percent:
		text = text[:-1]

	multiplier = 1.0
	last_char = text[-1].upper() if text else ""
	if last_char in {"K", "M", "B"}:
		multiplier = {"K": 1_000.0, "M": 1_000_000.0, "B": 1_000_000_000.0}[last_char]
		text = text[:-1]

	if "," in text and "." in text:
		text = text.replace(".", "").replace(",", ".")
	elif "," in text:
		text = text.replace(",", ".")
	elif "." in text and text.count(".") > 1:
		text = text.replace(".", "")

	try:
		value = float(text) * multiplier
		return value if not is_percent else value / 100.0
	except ValueError:
		return pd.NA


def _parse_french_date(value):
	if pd.isna(value):
		return pd.NaT
	if isinstance(value, (date, datetime, pd.Timestamp)):
		return pd.to_datetime(value, errors="coerce")

	date_text = str(value).strip()
	if not date_text:
		return pd.NaT

	lower_text = date_text.lower()
	for french_month, month_number in MONTHS.items():
		lower_text = lower_text.replace(french_month, month_number)

	parsed = pd.to_datetime(lower_text, dayfirst=True, errors="coerce")
	if pd.isna(parsed):
		parsed = pd.to_datetime(date_text, format="%d %m %Y", errors="coerce")
	return parsed


def clean_prices(raw_df, ticker):
	columns = ["ticker", "date", "close", "low", "high", "volume"]
	if raw_df is None or raw_df.empty:
		return pd.DataFrame(columns=columns)

	raw_df = raw_df.copy()
	raw_df.columns = [str(col).strip() for col in raw_df.columns]

	source_columns = {
		"Dernier": "close",
		"Ouv.": "open",
		"Plus Haut": "high",
		"Plus Bas": "low",
		"Vol.": "volume",
	}
	required_columns = set(source_columns) | {"Date"}
	missing_columns = required_columns - set(raw_df.columns)
	if missing_columns:
		raise ValueError(f"clean_prices: missing export columns {missing_columns}")

	cleaned = pd.DataFrame({
		"ticker": ticker,
		"date": raw_df["Date"].map(_parse_french_date).dt.strftime("%Y-%m-%d"),
		**{
			target: raw_df[source].map(_normalize_number)
			for source, target in source_columns.items()
		},
	})

	missing_close = cleaned["close"].isna()
	if missing_close.any():
		LOGGER.warning(
			"%s: dropped %d rows with missing close",
			ticker,
			int(missing_close.sum()),
		)
	cleaned = cleaned.loc[~missing_close]
	cleaned = cleaned.dropna(subset=["date"])
	cleaned = cleaned.drop_duplicates(subset=["date"], keep="last")
	cleaned = cleaned.sort_values("date", kind="stable")
	return cleaned[columns].reset_index(drop=True)