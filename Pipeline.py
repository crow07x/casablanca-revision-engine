import pandas as pd

import config
import storage
import ingest
import clean
import engine
import analytics
 
 
def stage_setup():
    """Stage 0: make sure the database and tables exist."""
    storage.init_db()
 
 
def stage_ingest_and_store(tickers=None):
    """Stages 1-3: fetch prices for every ticker, clean them, save them."""
    if tickers is None:
        tickers = config.UNIVERSE

    for ticker in tickers:
        try:
            raw = ingest.get_prices(ticker)
            df = clean.clean_prices(raw, ticker)
            storage.save_prices(df)
            print(f"[ok]   {ticker}: {len(df)} rows saved")
        except Exception as e:
            # One bad ticker must not stop the whole run
            print(f"[fail] {ticker}: {e}")
 
 
def stage_compute():
    """Stage 4: turn stored estimates into revisions."""
    estimates = storage.load_estimates()
    if estimates.empty:
        print("No estimates yet. Add some with storage.add_estimate() first.")
        return None
    return engine.build_revisions(estimates, config.DEFAULT_PE)
 
 
def stage_output(revisions):
    """Stage 5: rank and display results."""
    if revisions is None:
        return
    ranked = analytics.rank_revisions(revisions)
    output_rows = []
    for ticker in ranked["ticker"].unique():
        ticker_revisions = ranked[ranked["ticker"] == ticker].copy()
        prices = storage.load_prices(ticker)
        ticker_result = analytics.upside_vs_price(ticker_revisions, prices, threshold=config.THRESHOLD_PCT)
        output_rows.append(ticker_result)

    final_table = pd.concat(output_rows, ignore_index=True)
    final_table = final_table[[
        "ticker",
        "period",
        "new_eps",
        "eps_delta_pct",
        "new_value",
        "current_price",
        "upside_pct",
        "signal",
    ]]
    print(final_table.to_string(index=False))
 
 
def run(refresh_prices=True):
    stage_setup()
    if refresh_prices:
        stage_ingest_and_store()
    revisions = stage_compute()
    stage_output(revisions)
 
 
if __name__ == "__main__":
    run()