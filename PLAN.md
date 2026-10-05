# Casablanca Earnings Revision Engine: Plan

## Goal
Track changes in EPS estimates for Casablanca Bourse stocks and show how each revision changes implied fair value (EPS x target P/E).

## Core logic
- Fair value = EPS x P/E multiple
- Percent change = (new - old) / abs(old) x 100
- Rank stocks by the absolute size of their value change

## Data sources
| Data | Source | Status |
|---|---|---|
| Prices | Manual Excel/CSV exports from casablanca-bourse.com | local ingest implemented; exports required |
| EPS estimates | Manual entry from broker research and company guidance | manual |
| P/E multiples | My own assumptions, based on Moroccan sector comparables | to decide |

yfinance does NOT cover Casablanca (404 Error confirmed).
Official instrument-page exports are loaded from `raw_data/<ticker>/`; each
folder can contain multiple overlapping `.xlsx` or `.csv` export windows.

## Project layout
```
casablanca_revisions/
├── PLAN.md         this file (notes only, no code)
├── config.py
├── storage.py
├── ingest.py       only file allowed to read raw Excel/CSV exports
├── clean.py
├── engine.py
├── analytics.py
├── pipeline.py     runs everything in order
└── notebooks/
```

## Build order (tick off as I go)
- [ ] 1. config.py: UNIVERSE, DB_PATH, START_DATE, DEFAULT_PE
- [ ] 2. storage.py: init_db, save_prices, load_prices, add_estimate, load_estimates
- [ ] 3. ingest.py: get_prices(ticker)
- [ ] 4. clean.py: clean_prices(raw_df, ticker)
- [ ] 5. engine.py: fair_value, percent_change, build_revisions
- [ ] 6. analytics.py: rank_revisions, upside_vs_price
- [ ] 7. run pipeline.py end to end

## Database design
- companies: ticker, name, sector
- prices: ticker, date, close, low, high, volume (primary key: ticker + date)
- estimates: id, ticker, period, eps, source, date_recorded (append-only, never update)

## Decisions made
- SQLite for storage (single file, works in Colab and locally)
- Dates stored as ISO text (YYYY-MM-DD). French export dates are converted before storage.
- Short ticker (ATW) is the internal ID and names raw folders under `raw_data/`.
- Estimates use period labels (FY2025, H1 2026) because many Moroccan companies report semi-annually.
- Loading must be safe to run twice (no duplicate rows).

## Open questions
- Which 10 to 15 stocks go in the universe?
- What target P/E per sector?
- Where do I get estimates: which broker reports?

## Notes / problems log
(write anything that breaks or surprises you here)

## Module contracts (inputs and outputs)
- config.py: UNIVERSE {"ATW": "Attijariwafa"}, DB_PATH, START_DATE, DEFAULT_PE {"ATW": 14.0}
- storage.py:
  - init_db() creates the tables if missing
  - save_prices(df) is safe to run twice
  - load_prices(ticker, start=None, end=None) returns a DataFrame indexed by date
  - add_estimate(ticker, period, eps, source, date_recorded) is append-only
  - load_estimates(ticker=None) returns a DataFrame
- ingest.py: get_prices(ticker) combines the raw Excel/CSV exports for that ticker
- clean.py: clean_prices(raw_df, ticker) returns columns ticker, date (ISO text), close, low, high, volume
- engine.py:
  - fair_value(eps, multiple) returns a float
  - percent_change(old, new) guards old == 0 and uses abs(old)
  - build_revisions(estimates_df, default_pe) compares the latest estimate to the previous one per ticker and period, and returns eps_delta_pct, prev_value, new_value, value_delta_pct
- analytics.py:
  - rank_revisions(revisions_df) sorts by abs(value_delta_pct), largest first
  - upside_vs_price(revisions_df, prices_df) adds the current price and % upside
