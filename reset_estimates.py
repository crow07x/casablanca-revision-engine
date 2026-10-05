import storage


ESTIMATES = {
    "ATW": [
        (44.00, "BMCE Capital Global Research (FY2024 actual)", "2025-01-15"),
        (49.48, "casabourse.ma, calc from FY2025 RNPG 10.64Bn / 215.14M shares", "2026-03-01"),
    ],
    "IAM": [
        (6.98, "Attijari CIB research (FY2024 recurring)", "2025-03-01"),
        (6.87, "Attijari CIB research (FY2025e recurring)", "2026-02-13"),
    ],
    "BCP": [
        (19.76, "estimated from reported +9% YoY profit growth", "2025-03-01"),
        (21.54, "investing.com, TTM EPS", "2026-03-30"),
    ],
    "BOA": [
        (8.70, "BOA Document de reference 2025 (AMMC)", "2025-03-01"),
        (9.90, "BOA Document de reference 2025 (AMMC)", "2026-03-31"),
    ],
    "CIH": [
        (22.64, "derived from FY2024 net income 875MDH / 38.64M shares", "2025-03-01"),
        (29.13, "investing.com, TTM EPS", "2026-03-17"),
    ],
    "LHM": [
        (78.30, "derived from FY2024 net income 1826MDH / 23.32M shares", "2025-03-01"),
        (89.79, "investing.com, TTM EPS", "2026-03-10"),
    ],
    "CSR": [
        (9.00, "derived from FY2024 net profit ~850MDH / 94.49M shares", "2025-06-26"),
        (7.45, "casabourse.ma, FY2025 (impacted by tax reassessment)", "2026-03-01"),
    ],
    "TQM": [
        (44.63, "casablanca-bourse.com, FY2024 official BPA", "2025-03-01"),
        (42.00, "TAQA Morocco FY2025 results release", "2026-03-24"),
    ],
    "HPS": [
        (10.20, "HPS Resultats Annuels 2025 official release (FY2024)", "2025-03-28"),
        (14.30, "HPS Resultats Annuels 2025 official release (FY2025)", "2026-03-25"),
    ],
    "TGCC": [
        (16.50, "TGCC resultats financiers release, FY2024", "2025-03-01"),
        (27.46, "casabourse.ma, FY2025 net income 952M / 34.67M shares", "2026-03-30"),
    ],
    "AKT": [
        (22.25, "derived from FY2024 RNPG 315MDH / 14.16M shares", "2025-03-01"),
        (35.31, "casabourse.ma, FY2025 net income 500M / 14.16M shares", "2026-03-01"),
    ],
    "MNG": [
        (5.23, "estimated from reported +384% YoY RNPG growth", "2025-03-01"),
        (25.30, "casabourse.ma, FY2025 net income 3.0Bn / 118.6M shares", "2026-03-26"),
    ],
    "RIS": [
        (12.82, "estimated from reported +47% YoY RNPG growth", "2025-03-01"),
        (18.82, "casabourse.ma, FY2025 net income 269.6M / 14.33M shares", "2026-03-01"),
    ],
    "MUT": [
        (17.19, "derived from FY2024 net income 159M / 9.247M shares", "2025-03-01"),
        (13.64, "casabourse.ma, FY2025 net income 126.16M / 9.247M shares", "2026-02-23"),
    ],
    "CMT": [
        (-7.21, "casablanca-bourse.com official BPA, FY2024 (loss year)", "2025-03-01"),
        (116.86, "casablanca-bourse.com official BPA, FY2025 (recovery)", "2026-03-27"),
    ],
}


if __name__ == "__main__":
    storage.init_db()
    deleted = storage.delete_estimates()

    for ticker, observations in ESTIMATES.items():
        for eps, source, date_recorded in observations:
            storage.add_estimate(ticker, "FY2025", eps, source, date_recorded)

    inserted = sum(len(observations) for observations in ESTIMATES.values())
    print(f"Deleted {deleted} existing estimate rows; inserted {inserted} replacement rows.")
