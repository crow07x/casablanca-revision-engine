from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "casablanca.db"
START_DATE = "2020-01-01"

UNIVERSE = {
	"ATW": "Attijariwafa",
	"IAM": "Maroc Telecom",
	"BCP": "BCP",
	"BOA": "BOA",
	"CIH": "CIH",
	"LHM": "LafargeHolcim",
	"CSR": "COSUMAR",
	"TQM": "TAQA Morocco",
	"HPS": "HPS",
	"TGCC": "TGCC",
	"AKT": "Akdital",
	"MNG": "Managem",
	"RIS": "Risma",
	"MUT": "Mutandis",
	"CMT": "CMT",
}

DEFAULT_PE = {
	"ATW": 12.0,
	"IAM": 15.0,
	"BCP": 10.0,
	"BOA": 12.0,
	"CIH": 12.0,
	"LHM": 18.0,
	"CSR": 17.0,
	"TQM": 18.0,
	"HPS": 20.0,
	"TGCC": 22.0,
	"AKT": 24.0,
	"MNG": 14.0,
	"RIS": 18.0,
	"MUT": 16.0,
	"CMT": 12.0,
}

THRESHOLD_PCT = 15.0

assert not set(UNIVERSE) - set(DEFAULT_PE)
assert not set(DEFAULT_PE) - set(UNIVERSE)
