import sqlite3
from pathlib import Path

import pandas as pd

import app


SAMPLE_CSV = Path(__file__).parent / "fixtures" / "sample_tenders.csv"


def sample_data() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_CSV, dtype={"Year": str})


def create_test_db(path: Path, data: pd.DataFrame) -> None:
    rows = data.rename(
        columns={
            "Year": "year",
            "TenderOrgName": "tender_org_name",
            "TenderName": "tender_name",
            "TenderAwardPrice": "tender_award_price",
            "TenderAwardPriceNumber": "tender_award_price_number",
            "BidderSuppName": "bidder_supp_name",
            "NotObtainSuppName": "not_obtain_supp_name",
            "TenderCaseNo": "tender_case_no",
            "AwardDate": "award_date",
            "ProcurementType": "procurement_type",
            "ProcurementAttr": "procurement_attr",
            "TenderAwardWay": "tender_award_way",
            "SourceFile": "source_file",
            "SourceCsv": "source_csv",
        }
    )
    with sqlite3.connect(path) as conn:
        rows.to_sql("tenders", conn, index=False)


def test_load_data_reads_sqlite(tmp_path):
    db_path = tmp_path / "tenders.sqlite"
    create_test_db(db_path, sample_data())

    data, errors = app.load_data(str(db_path))

    assert errors == []
    assert len(data) == 3
    assert set(app.DISPLAY_COLUMNS).issubset(data.columns)


def test_search_tenders_matches_keyword_and_year_filter():
    data = sample_data()

    result = app.search_tenders(data, "測試機關A", ["2025"])

    assert len(result) == 1
    assert result.iloc[0]["TenderCaseNo"] == "A-2025-001"


def test_search_tenders_is_case_insensitive_and_literal():
    data = sample_data()

    result = app.search_tenders(data, "cloud.*", [])

    assert result.empty


def test_sort_tenders_by_amount_descending():
    data = sample_data()

    result = app.sort_tenders(data, app.SORT_BY_AMOUNT_DESC)

    assert result["TenderAwardPriceNumber"].tolist() == [2500000, 1200000, 800000]


def test_format_amount_uses_thousands_separator():
    assert app.format_amount(1200000) == "1,200,000"


def test_summary_builders_return_expected_totals():
    data = sample_data()

    trend = app.build_year_trend(data)
    ranking = app.build_ranking(data, "BidderSuppName", "得標廠商")
    report = app.build_summary_report(data, "資訊", ["2023", "2024", "2025"])

    assert trend["總金額"].sum() == 4500000
    assert ranking.loc[ranking["得標廠商"] == "甲資訊股份有限公司", "筆數"].iloc[0] == 2
    assert report.loc[report["區段"] == "總覽", "金額"].iloc[0] == 4500000


def test_search_tenders_supports_multiple_tokens():
    data = sample_data()

    result = app.search_tenders(data, "測試機關A 資安", [])

    assert len(result) == 1
    assert result.iloc[0]["TenderCaseNo"] == "A-2023-003"


def test_parse_natural_language_query_extracts_years_and_sort():
    keyword, years, sort_by = app.parse_natural_language_query(
        "查測試機關A近三年最大", ["2025", "2024", "2023", "2022"]
    )

    assert keyword == "測試機關A"
    assert years == ["2025", "2024", "2023"]
    assert sort_by == app.SORT_BY_AMOUNT_DESC


def test_build_text_insights_mentions_totals_and_largest_tender():
    insights = app.build_text_insights(sample_data())

    assert any("總金額 4,500,000" in insight for insight in insights)
    assert any("雲端平台建置案" in insight for insight in insights)


def test_build_anomaly_alerts_detects_growth_or_outlier():
    alerts = app.build_anomaly_alerts(sample_data())

    assert alerts
    assert any("成長" in alert or "中位數" in alert for alert in alerts)


def test_build_similar_tenders_excludes_source_and_scores_candidates():
    data = sample_data()
    source = data[data["TenderCaseNo"] == "A-2025-001"].iloc[0]

    similar = app.build_similar_tenders(data, source)

    assert not similar.empty
    assert "A-2025-001" not in similar["TenderCaseNo"].tolist()
    assert similar.iloc[0]["SimilarityScore"] > 0
