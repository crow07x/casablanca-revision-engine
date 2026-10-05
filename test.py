import clean
import ingest

raw = ingest.get_prices("BCP")
prices = clean.clean_prices(raw, "BCP")

expected_columns = ["ticker", "date", "close", "low", "high", "volume"]
assert prices.columns.tolist() == expected_columns
assert prices["date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}").all()
assert prices["close"].notna().all()
assert not prices["date"].duplicated().any()

print(f"[ok] BCP: {len(prices)} rows; ISO dates, no missing closes, no duplicate dates")