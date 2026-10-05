# Casablanca Earnings Revision Engine

A small Python and Streamlit application for tracking EPS estimate revisions for stocks listed on the Casablanca Stock Exchange. It compares successive estimates for the same ticker and reporting period, converts each EPS revision into an implied fair-value change using a configurable P/E multiple, and compares that value with the latest stored share price.

> **Data note:** The values in `seed_estimates.py` are demonstration placeholders, not verified company EPS or investment research. Enter and verify real estimates before using the analysis. This project is for informational and educational purposes only and is not investment advice.

## Features

- Add and review EPS estimates in a Streamlit dashboard.
- Import historical price exports in CSV or Excel format.
- Normalize French-formatted prices and dates.
- Store prices and estimates in a local SQLite database.
- Calculate EPS revisions, implied values, price upside, and valuation signals.
- Configure the covered companies, P/E multiples, and valuation threshold in `config.py`.

## Companies

The configured universe is: ATW (Attijariwafa Bank), IAM (Maroc Telecom), BCP (Banque Centrale Populaire), BOA (Bank of Africa), CIH (CIH Bank), LHM (LafargeHolcim Maroc), CSR (Cosumar), TQM (TAQA Morocco), HPS, TGCC, AKT (Akdital), MNG (Managem), RIS (Risma), MUT (Mutandis), and CMT.

## Requirements

- Python 3.10 or newer
- Price exports from the Casablanca Stock Exchange or another source matching the expected column format

## Installation

From the project directory, create and activate a virtual environment, then install the dependencies.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the dashboard

```bash
streamlit run cre.py
```

The app creates `casablanca.db` in the project directory on first launch. Use the **Add EPS estimate** tab to enter an EPS value, its reporting period (for example, `FY2025`), its source, and the date recorded. The database stores estimates as an append-only history; record a newer value for the same ticker and period to create a revision.

Use the **Refresh prices** tab to import price exports, then use **Analysis** to calculate and view results. A ticker needs at least two estimates for the same period to produce a revision, and it needs stored price data to show upside and a signal.

## Import price data

Save one or more CSV or `.xlsx` export files in the ticker's folder:

```text
raw_data/<TICKER>/
```

For example, `raw_data/BCP/prices.csv`. The importer reads all CSV and Excel files in each ticker folder, combines them, and de-duplicates rows by date during cleaning. It expects these source columns:

- `Date`
- `Dernier` (closing price)
- `Ouv.` (open)
- `Plus Haut` (high)
- `Plus Bas` (low)
- `Vol.` (volume)

Dates and numeric values may use French formatting. Raw CSV/XLSX files are excluded from Git by `.gitignore` to avoid publishing potentially large or licensed exchange exports. Obtain the data from an authorized source and keep it locally, or deliberately change `.gitignore` if you have the right to redistribute it.

## Run the command-line pipeline

After entering EPS estimates and placing price exports in the ticker folders, run:

```bash
python Pipeline.py
```

The pipeline initializes the database, refreshes prices for all configured tickers, computes estimate revisions, and prints a ranked results table. A missing or invalid export for one ticker is reported without stopping ingestion for the others. The price refresh still requires an export folder and supported file for each ticker.

## Tests / data check

```bash
python test.py
```

This check imports and cleans the BCP price export, so it requires a valid supported file under `raw_data/BCP/`. It is a data-dependent smoke test, not a full automated unit-test suite.

## Project files

- `cre.py`: Streamlit dashboard entry point.
- `Pipeline.py`: command-line pipeline.
- `config.py`: ticker universe, database location, P/E multiples, and threshold.
- `storage.py`: SQLite schema and data access.
- `ingest.py`: reads local CSV and Excel exports.
- `clean.py`: normalizes export columns, dates, and numeric values.
- `engine.py`: calculates EPS revisions and implied values.
- `analytics.py`: ranks revisions and compares implied values with prices.
- `seed_estimates.py`: inserts demonstration EPS records; do not treat these as verified figures.
- `raw_data/`: local price exports (not committed by default).
- `casablanca.db`: generated local database (not committed).

## Configuration and calculations

- Implied value = EPS x configured P/E multiple.
- EPS percent change = (new EPS - previous EPS) / absolute(previous EPS) x 100.
- By default, the analysis threshold is 15%; adjust `THRESHOLD_PCT` in `config.py` or the dashboard slider.
- P/E multiples in `config.py` are assumptions and should be reviewed before interpreting results.

## GitHub publishing checklist

1. Review all source files and verify that any EPS values and sources you publish are accurate.
2. Keep exchange exports, `casablanca.db`, virtual environments, and machine-specific files out of the repository unless you intentionally want to publish them and have permission.
3. Choose and add a `LICENSE` if you want to specify reuse terms; no license is included by default.
4. Create an empty GitHub repository, then run these commands from the project folder after installing Git. Replace the URL with your repository's HTTPS URL:

	```bash
	git init
	git add .
	git commit -m "Prepare Casablanca EPS revision engine for GitHub"
	git branch -M main
	git remote add origin https://github.com/<USERNAME>/<REPOSITORY>.git
	git push -u origin main
	```

	You can use GitHub Desktop instead if you prefer a graphical workflow.
