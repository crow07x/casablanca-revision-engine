from pathlib import Path

import pandas as pd

from config import BASE_DIR, UNIVERSE

RAW_DATA_DIR = BASE_DIR / "raw_data"
SUPPORTED_SUFFIXES = {".csv", ".xlsx"}


def get_prices(ticker):
    if ticker not in UNIVERSE:
        raise ValueError(f"Unknown ticker '{ticker}'. Add it to config.UNIVERSE first.")

    ticker_dir = RAW_DATA_DIR / ticker
    if not ticker_dir.is_dir():
        raise FileNotFoundError(
            f"Raw-data folder for {ticker} was not found: {ticker_dir}"
        )

    files = sorted(
        path
        for path in ticker_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if not files:
        raise FileNotFoundError(
            f"No .xlsx or .csv exports found for {ticker} in {ticker_dir}"
        )

    frames = []
    for file_path in files:
        try:
            if file_path.suffix.lower() == ".csv":
                frame = pd.read_csv(
                    file_path, sep=None, engine="python", encoding="utf-8-sig"
                )
            else:
                frame = pd.read_excel(file_path)
        except Exception as exc:
            raise ValueError(f"Could not read export file {file_path}: {exc}") from exc

        if not frame.empty:
            frames.append(frame)

    if not frames:
        raise ValueError(f"All exports for {ticker} are empty: {ticker_dir}")

    return pd.concat(frames, ignore_index=True, sort=False)