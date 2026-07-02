from __future__ import annotations

import argparse
import re
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_DIR = PROJECT_ROOT / "資料庫_CSV"
DEFAULT_DB_PATH = PROJECT_ROOT / "database" / "tenders.sqlite"

CSV_REQUIRED_COLUMNS = [
    "TenderName",
    "TenderOrgName",
    "TenderAwardPrice",
    "BidderSuppName",
    "NotObtainSuppName",
]

COLUMN_MAP = {
    "SourceFile": "source_file",
    "RangeStartDate": "range_start_date",
    "RangeEndDate": "range_end_date",
    "AwardDate": "award_date",
    "AwardNoticeDate": "award_notice_date",
    "TenderCaseNo": "tender_case_no",
    "TenderName": "tender_name",
    "TenderOrgName": "tender_org_name",
    "TenderOrgAddr": "tender_org_addr",
    "ContactPerson": "contact_person",
    "TenderTel": "tender_tel",
    "ProcurementType": "procurement_type",
    "ProcurementAttr": "procurement_attr",
    "TenderAwardWay": "tender_award_way",
    "TenderAwardPrice": "tender_award_price",
    "BidderSuppName": "bidder_supp_name",
    "BidderSuppAddr": "bidder_supp_addr",
    "NotObtainSuppName": "not_obtain_supp_name",
}

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS tenders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year TEXT NOT NULL,
    source_csv TEXT NOT NULL,
    source_file TEXT,
    range_start_date TEXT,
    range_end_date TEXT,
    award_date TEXT,
    award_notice_date TEXT,
    tender_case_no TEXT,
    tender_name TEXT,
    tender_org_name TEXT,
    tender_org_name_normalized TEXT,
    tender_org_addr TEXT,
    contact_person TEXT,
    tender_tel TEXT,
    procurement_type TEXT,
    procurement_attr TEXT,
    tender_award_way TEXT,
    tender_award_price TEXT,
    tender_award_price_number REAL NOT NULL DEFAULT 0,
    bidder_supp_name TEXT,
    bidder_supp_name_normalized TEXT,
    bidder_supp_addr TEXT,
    not_obtain_supp_name TEXT,
    not_obtain_supp_name_normalized TEXT,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

INDEX_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_tenders_year ON tenders(year)",
    "CREATE INDEX IF NOT EXISTS idx_tenders_amount ON tenders(tender_award_price_number)",
    "CREATE INDEX IF NOT EXISTS idx_tenders_org ON tenders(tender_org_name)",
    "CREATE INDEX IF NOT EXISTS idx_tenders_bidder ON tenders(bidder_supp_name)",
    "CREATE INDEX IF NOT EXISTS idx_tenders_case_no ON tenders(tender_case_no)",
]


def normalize_name(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = text.replace("（", "(").replace("）", ")")
    text = re.sub(r"\s+", "", text)
    return text.strip()


def parse_amount(value: object) -> float:
    if pd.isna(value):
        return 0.0
    cleaned = re.sub(r"[^0-9.-]", "", str(value))
    if cleaned in {"", ".", "-", "-."}:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_year(csv_path: Path) -> str | None:
    parts = csv_path.stem.split("_")
    if len(parts) < 2 or not parts[1].isdigit():
        return None
    return parts[1]


def load_csv(csv_path: Path) -> tuple[pd.DataFrame | None, str | None]:
    year = parse_year(csv_path)
    if year is None:
        return None, f"{csv_path.name}: cannot parse year from file name"

    try:
        frame = pd.read_csv(csv_path, encoding="utf-8-sig")
    except Exception as exc:
        return None, f"{csv_path.name}: failed to read CSV ({exc})"

    missing = [column for column in CSV_REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        return None, f"{csv_path.name}: missing columns {', '.join(missing)}"

    if frame.empty:
        return None, f"{csv_path.name}: empty CSV"

    output = pd.DataFrame(index=frame.index)
    output["year"] = year
    output["source_csv"] = csv_path.name
    for source_column, db_column in COLUMN_MAP.items():
        output[db_column] = frame[source_column] if source_column in frame.columns else ""

    output["tender_award_price_number"] = output["tender_award_price"].map(parse_amount)
    output["tender_org_name_normalized"] = output["tender_org_name"].map(normalize_name)
    output["bidder_supp_name_normalized"] = output["bidder_supp_name"].map(normalize_name)
    output["not_obtain_supp_name_normalized"] = output["not_obtain_supp_name"].map(normalize_name)
    return output, None


def import_csvs(csv_dir: Path, db_path: Path, rebuild: bool = True) -> tuple[int, list[str]]:
    errors: list[str] = []
    frames: list[pd.DataFrame] = []

    if not csv_dir.exists() or not csv_dir.is_dir():
        raise FileNotFoundError(f"CSV directory not found: {csv_dir}")

    csv_paths = sorted(csv_dir.glob("*SourceData.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No *SourceData.csv files found in: {csv_dir}")

    for csv_path in csv_paths:
        frame, error = load_csv(csv_path)
        if error:
            errors.append(error)
            continue
        if frame is not None:
            frames.append(frame)

    if not frames:
        raise RuntimeError("No usable CSV rows were loaded")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(CREATE_SQL)
        if rebuild:
            conn.execute("DELETE FROM tenders")
            conn.execute("DELETE FROM sqlite_sequence WHERE name = 'tenders'")

        data = pd.concat(frames, ignore_index=True)
        data.to_sql("tenders", conn, if_exists="append", index=False)
        for sql in INDEX_SQL:
            conn.execute(sql)
        conn.commit()

    return int(sum(len(frame) for frame in frames)), errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Import tender SourceData CSV files into SQLite.")
    parser.add_argument("--csv-dir", type=Path, default=DEFAULT_CSV_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--append", action="store_true", help="Append rows instead of rebuilding the tenders table.")
    args = parser.parse_args()

    row_count, errors = import_csvs(args.csv_dir, args.db, rebuild=not args.append)
    print(f"Imported {row_count} rows into {args.db}")
    if errors:
        print("Warnings:")
        for error in errors:
            print(f"- {error}")


if __name__ == "__main__":
    main()


