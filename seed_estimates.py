from config import UNIVERSE
from storage import add_estimate

# One earlier estimate and one later estimate per ticker.
# BCP is left alone because it already has real historical data in the DB.
ESTIMATES = {
    "ATW": [("2025-01-15", 17.20), ("2025-06-10", 18.90)],
    "IAM": [("2025-01-15", 12.10), ("2025-06-10", 13.40)],
    "BOA": [("2025-01-15", 5.40), ("2025-06-10", 6.10)],
    "CIH": [("2025-01-15", 1.90), ("2025-06-10", 2.20)],
    "LHM": [("2025-01-15", 34.00), ("2025-06-10", 36.50)],
    "CSR": [("2025-01-15", 21.40), ("2025-06-10", 23.80)],
    "TQM": [("2025-01-15", 4.30), ("2025-06-10", 4.90)],
    "HPS": [("2025-01-15", 9.80), ("2025-06-10", 11.20)],
    "TGCC": [("2025-01-15", 8.10), ("2025-06-10", 9.30)],
    "AKT": [("2025-01-15", 6.20), ("2025-06-10", 7.10)],
    "MNG": [("2025-01-15", 12.80), ("2025-06-10", 14.30)],
    "RIS": [("2025-01-15", 3.60), ("2025-06-10", 4.10)],
    "MUT": [("2025-01-15", 15.40), ("2025-06-10", 17.20)],
    "CMT": [("2025-01-15", 11.60), ("2025-06-10", 12.90)],
}

for ticker in UNIVERSE:
    if ticker == "BCP":
        continue
    if ticker not in ESTIMATES:
        continue
    for date_recorded, eps in ESTIMATES[ticker]:
        source = "my research" if date_recorded < "2025-06-01" else "broker update"
        add_estimate(ticker, "FY2025", eps, source, date_recorded)

print(f"Seeded FY2025 EPS estimates for {len(ESTIMATES)} tickers.")
