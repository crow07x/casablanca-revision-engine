import pandas as pd


def rank_revisions(revisions_df):
    if revisions_df is None or revisions_df.empty:
        return revisions_df.copy() if revisions_df is not None else pd.DataFrame()

    ranked = revisions_df.copy()
    if "value_delta_pct" not in ranked.columns:
        raise ValueError("rank_revisions: missing value_delta_pct column")

    return ranked.sort_values("value_delta_pct", key=lambda s: s.abs(), ascending=False).reset_index(drop=True)


def upside_vs_price(revisions_df, prices_df, threshold=15.0):
    if revisions_df is None or revisions_df.empty:
        return revisions_df.copy() if revisions_df is not None else pd.DataFrame()
    if prices_df is None or prices_df.empty:
        result = revisions_df.copy()
        result["current_price"] = pd.NA
        result["upside_pct"] = pd.NA
        result["signal"] = "Fairly valued"
        return result

    if isinstance(prices_df.index, pd.DatetimeIndex):
        current_price = pd.to_numeric(prices_df["close"].iloc[-1], errors="coerce")
    else:
        current_price = pd.to_numeric(prices_df["close"].iloc[-1], errors="coerce")

    result = revisions_df.copy()
    result["current_price"] = current_price
    result["upside_pct"] = 0.0

    mask = result["current_price"].notna() & (result["current_price"] != 0)
    if mask.any():
        result.loc[mask, "upside_pct"] = (
            (result.loc[mask, "new_value"] - result.loc[mask, "current_price"]) /
            abs(result.loc[mask, "current_price"]) * 100.0
        )

    result["signal"] = "Fairly valued"
    result.loc[result["upside_pct"] > threshold, "signal"] = "Undervalued"
    result.loc[result["upside_pct"] < -threshold, "signal"] = "Overpriced"
    return result
