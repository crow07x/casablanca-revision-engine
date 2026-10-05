import pandas as pd


def fair_value(eps, multiple):
    return float(eps) * float(multiple)


def percent_change(old, new):
    if old == 0:
        return 0.0
    return (float(new) - float(old)) / abs(float(old)) * 100.0


def build_revisions(estimates_df, default_pe):
    if estimates_df is None or estimates_df.empty:
        return pd.DataFrame(
            columns=[
                "ticker",
                "period",
                "prev_eps",
                "new_eps",
                "eps_delta_pct",
                "prev_value",
                "new_value",
                "value_delta_pct",
            ]
        )

    work = estimates_df.copy()
    if "date_recorded" in work.columns:
        work["date_recorded"] = pd.to_datetime(work["date_recorded"], errors="coerce")
    if "id" in work.columns:
        work = work.sort_values(["ticker", "period", "date_recorded", "id"], kind="stable")
    else:
        work = work.sort_values(["ticker", "period", "date_recorded"], kind="stable")

    rows = []
    for (ticker, period), group in work.groupby(["ticker", "period"], sort=False):
        if len(group) < 2:
            continue

        previous = group.iloc[-2]
        latest = group.iloc[-1]
        pe = float(default_pe.get(ticker, default_pe.get(ticker.upper(), 15.0)))

        prev_value = fair_value(previous["eps"], pe)
        new_value = fair_value(latest["eps"], pe)

        rows.append(
            {
                "ticker": ticker,
                "period": period,
                "prev_eps": float(previous["eps"]),
                "new_eps": float(latest["eps"]),
                "eps_delta_pct": percent_change(previous["eps"], latest["eps"]),
                "prev_value": prev_value,
                "new_value": new_value,
                "value_delta_pct": percent_change(prev_value, new_value),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "ticker",
                "period",
                "prev_eps",
                "new_eps",
                "eps_delta_pct",
                "prev_value",
                "new_value",
                "value_delta_pct",
            ]
        )

    return pd.DataFrame(rows).sort_values(["ticker", "period"], kind="stable").reset_index(drop=True)
