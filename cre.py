from datetime import date

import pandas as pd
import streamlit as st

import analytics
import clean
import config
import engine
import ingest
import storage

storage.init_db()

st.set_page_config(page_title="Casablanca Revision Engine", layout="wide")


def render_add_estimate_tab():
    st.header("Add EPS estimate")
    ticker = st.selectbox("Ticker", options=list(config.UNIVERSE.keys()))
    period = st.text_input("Period", value="FY2025")
    eps = st.number_input("EPS value", min_value=0.0, value=0.0, step=0.1, format="%.2f")
    source = st.text_input("Source", value="my research")
    date_recorded = st.date_input("Date recorded", value=date.today())

    if st.button("Save estimate"):
        storage.add_estimate(ticker, period, float(eps), source, date_recorded.isoformat())
        st.success(f"Saved estimate for {ticker} ({period})")

    st.subheader(f"Estimate history for {ticker}")
    history = storage.load_estimates(ticker)
    if history.empty:
        st.info("No estimates yet for this ticker.")
    else:
        st.dataframe(history, use_container_width=True)


def render_refresh_tab():
    st.header("Refresh prices")
    st.info(
        "Manually download the latest price export files from the exchange and save them into raw_data/<TICKER>/ before clicking refresh."
    )

    if st.button("Refresh all prices"):
        rows = []
        for ticker in config.UNIVERSE:
            try:
                raw = ingest.get_prices(ticker)
                cleaned = clean.clean_prices(raw, ticker)
                saved = storage.save_prices(cleaned)
                rows.append({"ticker": ticker, "status": "ok", "rows_saved": saved, "message": ""})
            except Exception as exc:
                rows.append({"ticker": ticker, "status": "fail", "rows_saved": 0, "message": str(exc)})

        results = pd.DataFrame(rows)
        st.dataframe(results, use_container_width=True)


def render_analysis_tab():
    st.header("Analysis")
    threshold = st.slider("Over/undervalued threshold %", min_value=5, max_value=30, value=15, step=1)

    if st.button("Run analysis"):
        estimates = storage.load_estimates()
        if estimates.empty:
            st.warning("No estimates available yet. Add at least one estimate before running analysis.")
            return

        revisions = engine.build_revisions(estimates, config.DEFAULT_PE)
        ranked = analytics.rank_revisions(revisions)

        results = []
        missing_prices = []

        for ticker in ranked["ticker"].drop_duplicates():
            ticker_revisions = ranked[ranked["ticker"] == ticker].copy()
            prices = storage.load_prices(ticker)

            if prices.empty:
                missing_prices.append(ticker)
                continue

            ticker_result = analytics.upside_vs_price(ticker_revisions, prices, threshold=threshold)
            results.append(ticker_result)

        if not results:
            st.warning("No analysis rows could be produced because no ticker has price data yet.")
            if missing_prices:
                st.write("Missing price data for: " + ", ".join(missing_prices))
            return

        combined = pd.concat(results, ignore_index=True)
        combined = combined[[
            "ticker",
            "period",
            "new_eps",
            "eps_delta_pct",
            "new_value",
            "current_price",
            "upside_pct",
            "signal",
        ]]

        st.subheader("Results")
        st.dataframe(combined, use_container_width=True)

        summary = {
            "Undervalued": int((combined["signal"] == "Undervalued").sum()),
            "Overpriced": int((combined["signal"] == "Overpriced").sum()),
            "Fairly valued": int((combined["signal"] == "Fairly valued").sum()),
            "Tickers analyzed": int(combined["ticker"].nunique()),
        }
        st.subheader("Summary")
        st.json(summary)

        if missing_prices:
            st.warning("Skipped tickers with no price data: " + ", ".join(missing_prices))


tabs = st.tabs(["Add EPS estimate", "Refresh prices", "Analysis"])
with tabs[0]:
    render_add_estimate_tab()
with tabs[1]:
    render_refresh_tab()
with tabs[2]:
    render_analysis_tab()
