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


def test_validate_login_accepts_only_matching_credentials():
    assert app.validate_login("admin", "admin123", "admin", "admin123")
    assert not app.validate_login("admin", "wrong", "admin", "admin123")
    assert not app.validate_login("wrong", "admin123", "admin", "admin123")


def test_authenticated_header_replaces_sidebar_logout():
    assert callable(app.show_app_header)
    assert not hasattr(app, "show_logout_control")


def test_review_login_requires_backend_approval():
    users = {
        "approved_user": {"password": "pass123", "approved": True},
        "pending_user": {"password": "pass123", "approved": False},
    }

    assert app.review_login("approved_user", "pass123", users) == (True, "approved")
    assert app.review_login("approved_user", "wrong", users) == (False, "invalid_password")
    assert app.review_login("pending_user", "pass123", users) == (False, "not_approved")
    assert app.review_login("missing", "pass123", users) == (False, "unknown_user")


def test_write_login_audit_records_status_without_password(tmp_path, monkeypatch):
    audit_path = tmp_path / "login_audit.csv"
    monkeypatch.setattr(app, "AUTH_AUDIT_PATH", audit_path)

    app.write_login_audit("review_user", "not_approved")

    text = audit_path.read_text(encoding="utf-8-sig")
    assert "review_user" in text
    assert "not_approved" in text
    assert "password" not in text.lower()


def test_load_data_from_csv_accepts_full_database_flat_files(tmp_path):
    csv_path = tmp_path / "award_2026_flat.csv"
    csv_path.write_text(
        "TenderName,TenderOrgName,TenderAwardPrice,BidderSuppName,NotObtainSuppName\n"
        "完整資料測試案,測試機關,12345,測試廠商,協作廠商\n",
        encoding="utf-8-sig",
    )

    data, errors = app.load_data_from_csv(tmp_path)

    assert errors == []
    assert len(data) == 1
    assert data.iloc[0]["Year"] == "2026"
    assert data.iloc[0]["TenderName"] == "完整資料測試案"


def test_load_data_from_csv_dirs_prefers_full_database(tmp_path):
    full_dir = tmp_path / "完整資料庫"
    old_dir = tmp_path / "資料庫_CSV"
    full_dir.mkdir()
    old_dir.mkdir()
    (full_dir / "award_2026_flat.csv").write_text(
        "TenderName,TenderOrgName,TenderAwardPrice,BidderSuppName,NotObtainSuppName\n"
        "完整資料案,完整機關,100,完整廠商,完整協作\n",
        encoding="utf-8-sig",
    )
    (old_dir / "award_2025_SourceData.csv").write_text(
        "TenderName,TenderOrgName,TenderAwardPrice,BidderSuppName,NotObtainSuppName\n"
        "舊資料案,舊機關,50,舊廠商,舊協作\n",
        encoding="utf-8-sig",
    )

    data, errors, csv_dir = app.load_data_from_csv_dirs([full_dir, old_dir])

    assert errors == []
    assert csv_dir == full_dir
    assert len(data) == 1
    assert data.iloc[0]["TenderName"] == "完整資料案"


def test_load_data_falls_back_to_full_database_csv(tmp_path, monkeypatch):
    full_dir = tmp_path / "完整資料庫"
    old_dir = tmp_path / "資料庫_CSV"
    full_dir.mkdir()
    old_dir.mkdir()
    (full_dir / "award_2026_flat.csv").write_text(
        "TenderName,TenderOrgName,TenderAwardPrice,BidderSuppName,NotObtainSuppName\n"
        "完整 fallback 案,完整機關,100,完整廠商,完整協作\n",
        encoding="utf-8-sig",
    )
    (old_dir / "award_2025_SourceData.csv").write_text(
        "TenderName,TenderOrgName,TenderAwardPrice,BidderSuppName,NotObtainSuppName\n"
        "舊 fallback 案,舊機關,50,舊廠商,舊協作\n",
        encoding="utf-8-sig",
    )
    monkeypatch.setattr(app, "CSV_DIRS", [full_dir, old_dir])

    app.load_data.clear()
    data, errors = app.load_data(str(tmp_path / "missing.sqlite"))
    app.load_data.clear()

    assert len(data) == 1
    assert data.iloc[0]["TenderName"] == "完整 fallback 案"
    assert any("完整資料庫" in error for error in errors)



def test_password_hash_round_trip():
    stored = app.hash_password("secret-pass", "fixed-salt")

    assert stored.startswith(app.PASSWORD_HASH_PREFIX)
    assert app.verify_password("secret-pass", stored)
    assert not app.verify_password("wrong-pass", stored)


def test_register_user_creates_pending_hashed_account(tmp_path, monkeypatch):
    store_path = tmp_path / "auth_users.csv"
    monkeypatch.setattr(app, "AUTH_USER_STORE_PATH", store_path)

    created, message = app.register_user("new_user", "pass123", "pass123")
    users = app.load_registered_users()

    assert created
    assert "等待管理員審核" in message
    assert users["new_user"]["approved"] is False
    assert users["new_user"]["is_admin"] is False
    assert users["new_user"]["password"] != "pass123"
    assert app.verify_password("pass123", str(users["new_user"]["password"]))


def test_register_user_rejects_duplicate_and_mismatched_password(tmp_path, monkeypatch):
    store_path = tmp_path / "auth_users.csv"
    monkeypatch.setattr(app, "AUTH_USER_STORE_PATH", store_path)

    assert app.register_user("new_user", "pass123", "pass123")[0]
    duplicate_created, duplicate_message = app.register_user("new_user", "pass123", "pass123")
    mismatch_created, mismatch_message = app.register_user("other_user", "pass123", "pass456")

    assert not duplicate_created
    assert "已存在" in duplicate_message
    assert not mismatch_created
    assert "不一致" in mismatch_message


def test_update_registered_user_approves_and_grants_admin(tmp_path, monkeypatch):
    store_path = tmp_path / "auth_users.csv"
    monkeypatch.setattr(app, "AUTH_USER_STORE_PATH", store_path)
    app.register_user("review_user", "pass123", "pass123")

    assert app.update_registered_user("review_user", approved=True)
    assert app.update_registered_user("review_user", is_admin=True)
    users = app.load_registered_users()

    assert users["review_user"]["approved"] is True
    assert users["review_user"]["is_admin"] is True
    assert users["review_user"]["reviewed_at"]
