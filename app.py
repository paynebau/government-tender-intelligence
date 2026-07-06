import hmac
import os
from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "database" / "tenders.sqlite"
FULL_CSV_DIR = PROJECT_ROOT / "完整資料庫"
CSV_DIR = PROJECT_ROOT / "資料庫_CSV"
CSV_DIRS = [FULL_CSV_DIR, CSV_DIR]
TITLE = "\u653f\u5e9c\u6a19\u6848\u60c5\u8cc7\u67e5\u8a62\u7cfb\u7d71"
LOGIN_TITLE = "\u767b\u5165"
USERNAME_LABEL = "\u5e33\u865f"
PASSWORD_LABEL = "\u5bc6\u78bc"
LOGIN_BUTTON_LABEL = "\u767b\u5165"
LOGOUT_BUTTON_LABEL = "\u767b\u51fa"
LOGIN_ERROR_MESSAGE = "\u5e33\u865f\u6216\u5bc6\u78bc\u932f\u8aa4\u3002"
DEFAULT_AUTH_USERNAME = "admin"
DEFAULT_AUTH_PASSWORD = "admin123"
AUTH_SESSION_KEY = "authenticated"
SEARCH_LABEL = "\u641c\u5c0b / \u81ea\u7136\u8a9e\u8a00\u67e5\u8a62"
SEARCH_PLACEHOLDER = (
    "\u8f38\u5165\u6a5f\u95dc\u3001\u6a19\u6848\u540d\u7a31\u3001"
    "\u5f97\u6a19\u5ee0\u5546\u6216\u5354\u4f5c\u5ee0\u5546\uff1b\u4f8b\uff1a\u67e5\u4e2d\u83ef\u90f5\u653f\u8fd1\u4e94\u5e74\u6700\u5927 SI"
)
SORT_LABEL = "\u6392\u5e8f"
YEAR_FILTER_LABEL = "\u5e74\u5ea6\u7be9\u9078"
YEAR_FILTER_HELP = "\u672a\u9078\u53d6\u6642\u9810\u8a2d\u67e5\u8a62\u5168\u90e8\u5e74\u5ea6"
SORT_BY_YEAR = "\u5e74\u5ea6\uff08\u65b0\u5230\u820a\uff09"
SORT_BY_AMOUNT_DESC = "\u91d1\u984d\uff08\u9ad8\u5230\u4f4e\uff09"
SORT_BY_AMOUNT_ASC = "\u91d1\u984d\uff08\u4f4e\u5230\u9ad8\uff09"
NO_RESULT = "\u67e5\u7121\u76f8\u95dc\u6a19\u6848"
START_SEARCH = "\u8acb\u8f38\u5165\u95dc\u9375\u5b57\u958b\u59cb\u67e5\u8a62\u3002"
DOWNLOAD_LABEL = "\u4e0b\u8f09\u67e5\u8a62\u7d50\u679c CSV"
SUMMARY_DOWNLOAD_LABEL = "\u4e0b\u8f09\u6458\u8981\u5831\u8868 CSV"
AGENCY_REPORT_DOWNLOAD_LABEL = "\u4e0b\u8f09\u6a5f\u95dc\u5206\u6790\u5831\u544a CSV"
SUMMARY_COUNT = "\u672c\u6b21\u67e5\u5230\u5e7e\u7b46"
SUMMARY_TOTAL_AMOUNT = "\u7e3d\u91d1\u984d\u591a\u5c11"
YEAR_DISTRIBUTION = "\u5e74\u5ea6\u5206\u5e03\uff08\u5404\u5e74\u5e7e\u7b46\uff09"
TOP_AGENCIES = "\u51fa\u73fe\u6700\u591a\u7684\u524d 3 \u500b\u6a5f\u95dc"
TOP_SUPPLIERS = "\u51fa\u73fe\u6700\u591a\u7684\u524d 3 \u500b\u5f97\u6a19\u5ee0\u5546"
DATA_ERROR_TITLE = "\u8cc7\u6599\u8f09\u5165\u8b66\u793a"
DATA_EMPTY_MESSAGE = "\u76ee\u524d\u6c92\u6709\u53ef\u67e5\u8a62\u7684\u6a19\u6848\u8cc7\u6599\u3002"
DB_MISSING_MESSAGE = "\u627e\u4e0d\u5230 SQLite \u8cc7\u6599\u5eab\uff0c\u8acb\u5148\u57f7\u884c scripts/import_to_sqlite.ps1 \u532f\u5165\u8cc7\u6599\u3002"
RESULT_LIMIT_WARNING = "\u67e5\u8a62\u7d50\u679c\u8f03\u591a\uff0c\u8868\u683c\u5df2\u6539\u70ba\u5206\u9801\u986f\u793a\uff1bCSV \u4e0b\u8f09\u4ecd\u5305\u542b\u5168\u90e8\u7d50\u679c\u3002"
PAGE_LABEL = "\u9801\u78bc"
PAGE_SIZE_LABEL = "\u6bcf\u9801\u7b46\u6578"

SEARCH_COLUMNS = ["TenderOrgName", "TenderName", "BidderSuppName", "NotObtainSuppName"]
DISPLAY_COLUMNS = ["Year", "TenderOrgName", "TenderName", "TenderAwardPrice", "BidderSuppName", "NotObtainSuppName"]
RESULT_WARNING_THRESHOLD = 200
PAGE_SIZE_OPTIONS = [50, 100, 200]
TOP_N = 10
SIMILAR_TENDER_LIMIT = 5
ANOMALY_GROWTH_RATIO = 2.0
ANOMALY_CONCENTRATION_RATIO = 0.5
ANOMALY_MEDIAN_MULTIPLIER = 2.0

QUERY_SQL = """
SELECT
    year AS Year,
    tender_org_name AS TenderOrgName,
    tender_name AS TenderName,
    tender_award_price AS TenderAwardPrice,
    tender_award_price_number AS TenderAwardPriceNumber,
    bidder_supp_name AS BidderSuppName,
    not_obtain_supp_name AS NotObtainSuppName,
    tender_case_no AS TenderCaseNo,
    award_date AS AwardDate,
    procurement_type AS ProcurementType,
    procurement_attr AS ProcurementAttr,
    tender_award_way AS TenderAwardWay,
    source_file AS SourceFile,
    source_csv AS SourceCsv
FROM tenders
"""




def get_secret_value(section: str, key: str) -> str | None:
    try:
        section_values = st.secrets.get(section, {})
    except Exception:
        return None
    value = section_values.get(key) if hasattr(section_values, "get") else None
    return str(value) if value is not None else None


def get_auth_credentials() -> tuple[str, str]:
    username = (
        os.getenv("TENDER_APP_USERNAME")
        or get_secret_value("auth", "username")
        or DEFAULT_AUTH_USERNAME
    )
    password = (
        os.getenv("TENDER_APP_PASSWORD")
        or get_secret_value("auth", "password")
        or DEFAULT_AUTH_PASSWORD
    )
    return username, password


def validate_login(username: str, password: str, expected_username: str, expected_password: str) -> bool:
    username_matches = hmac.compare_digest(username, expected_username)
    password_matches = hmac.compare_digest(password, expected_password)
    return username_matches and password_matches


def show_login_page() -> bool:
    if st.session_state.get(AUTH_SESSION_KEY):
        return True

    st.title(TITLE)
    st.subheader(LOGIN_TITLE)
    username = st.text_input(USERNAME_LABEL)
    password = st.text_input(PASSWORD_LABEL, type="password")
    expected_username, expected_password = get_auth_credentials()

    if st.button(LOGIN_BUTTON_LABEL, type="primary"):
        if validate_login(username, password, expected_username, expected_password):
            st.session_state[AUTH_SESSION_KEY] = True
            st.rerun()
        else:
            st.error(LOGIN_ERROR_MESSAGE)

    return False


def show_app_header() -> None:
    title_column, logout_column = st.columns([5, 1])
    with title_column:
        st.title(TITLE)
    with logout_column:
        st.write("")
        if st.button(LOGOUT_BUTTON_LABEL, key="logout_button"):
            st.session_state[AUTH_SESSION_KEY] = False
            st.rerun()

@st.cache_data
def load_data(db_path: str) -> tuple[pd.DataFrame, list[str]]:
    path = Path(db_path)
    if not path.exists():
        data, errors, csv_dir = load_data_from_csv_dirs(CSV_DIRS)
        if data.empty:
            return data, [DB_MISSING_MESSAGE] + errors
        return data, [f"找不到 SQLite 資料庫，已改從 CSV 載入資料：{csv_dir.name}"] + errors

    try:
        with sqlite3.connect(path) as conn:
            table_exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'tenders'"
            ).fetchone()
            if not table_exists:
                return pd.DataFrame(), ["SQLite \u8cc7\u6599\u5eab\u7f3a\u5c11 tenders \u8cc7\u6599\u8868\u3002"]
            data = pd.read_sql_query(QUERY_SQL, conn)
    except sqlite3.Error as exc:
        return pd.DataFrame(), [f"SQLite \u8cc7\u6599\u5eab\u8b80\u53d6\u5931\u6557\uff1a{exc}"]

    if data.empty:
        return pd.DataFrame(), [DATA_EMPTY_MESSAGE]

    return data, []




def parse_amount(value: object) -> float:
    cleaned = "" if pd.isna(value) else str(value)
    cleaned = "".join(char for char in cleaned if char.isdigit() or char in ".-")
    if cleaned in {"", ".", "-", "-."}:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_year_from_csv(csv_path: Path) -> str | None:
    parts = csv_path.stem.split("_")
    if len(parts) >= 2 and parts[1].isdigit():
        return parts[1]
    return None


def load_data_from_csv_dirs(csv_dirs: list[Path]) -> tuple[pd.DataFrame, list[str], Path]:
    all_errors: list[str] = []
    for csv_dir in csv_dirs:
        data, errors = load_data_from_csv(csv_dir)
        if not data.empty:
            return data, errors, csv_dir
        all_errors.extend(errors)
    return pd.DataFrame(), all_errors, csv_dirs[0]

def load_data_from_csv(csv_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    if not csv_dir.exists():
        return pd.DataFrame(), [f"找不到 CSV 資料夾：{csv_dir}"]

    frames: list[pd.DataFrame] = []
    errors: list[str] = []
    csv_paths = sorted({*csv_dir.glob("*SourceData.csv"), *csv_dir.glob("award_*_flat.csv")})
    for csv_path in csv_paths:
        year = parse_year_from_csv(csv_path)
        if year is None:
            errors.append(f"{csv_path.name}: 無法從檔名解析年度")
            continue
        try:
            frame = pd.read_csv(csv_path, encoding="utf-8-sig")
        except Exception as exc:
            errors.append(f"{csv_path.name}: CSV 讀取失敗：{exc}")
            continue

        required = ["TenderOrgName", "TenderName", "TenderAwardPrice", "BidderSuppName", "NotObtainSuppName"]
        missing = [column for column in required if column not in frame.columns]
        if missing:
            errors.append(f"{csv_path.name}: 缺少欄位 {', '.join(missing)}")
            continue

        output = pd.DataFrame(index=frame.index)
        output["Year"] = year
        output["TenderOrgName"] = frame.get("TenderOrgName", "")
        output["TenderName"] = frame.get("TenderName", "")
        output["TenderAwardPrice"] = frame.get("TenderAwardPrice", "")
        output["TenderAwardPriceNumber"] = output["TenderAwardPrice"].map(parse_amount)
        output["BidderSuppName"] = frame.get("BidderSuppName", "")
        output["NotObtainSuppName"] = frame.get("NotObtainSuppName", "")
        output["TenderCaseNo"] = frame.get("TenderCaseNo", "")
        output["AwardDate"] = frame.get("AwardDate", "")
        output["ProcurementType"] = frame.get("ProcurementType", "")
        output["ProcurementAttr"] = frame.get("ProcurementAttr", "")
        output["TenderAwardWay"] = frame.get("TenderAwardWay", "")
        output["SourceFile"] = frame.get("SourceFile", "")
        output["SourceCsv"] = csv_path.name
        frames.append(output)

    if not frames:
        return pd.DataFrame(), errors or ["找不到可用的標案 CSV 資料。"]

    return pd.concat(frames, ignore_index=True), errors
def show_data_errors(errors: list[str], *, fatal: bool = False) -> None:
    if not errors:
        return

    if fatal:
        st.error(DATA_ERROR_TITLE)
    else:
        st.warning(DATA_ERROR_TITLE)
    for error in errors:
        st.caption(error)


def clean_series(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().replace("", pd.NA).dropna()


def format_amount(amount: float) -> str:
    return f"{int(amount):,}"


def show_summary(result: pd.DataFrame) -> None:
    total_amount = int(result["TenderAwardPriceNumber"].sum())
    count_column, amount_column = st.columns(2)
    count_column.metric(SUMMARY_COUNT, f"{len(result):,}")
    amount_column.metric(SUMMARY_TOTAL_AMOUNT, f"{total_amount:,}")

    year_counts = result["Year"].astype(str).value_counts().sort_index(ascending=False)
    top_agencies = clean_series(result["TenderOrgName"]).value_counts().head(3)
    top_suppliers = clean_series(result["BidderSuppName"]).value_counts().head(3)

    year_column, agency_column, supplier_column = st.columns(3)
    with year_column:
        st.markdown(f"**{YEAR_DISTRIBUTION}**")
        st.dataframe(
            year_counts.rename_axis("\u5e74\u5ea6").reset_index(name="\u7b46\u6578"),
            use_container_width=True,
            hide_index=True,
        )

    with agency_column:
        st.markdown(f"**{TOP_AGENCIES}**")
        st.dataframe(
            top_agencies.rename_axis("\u6a5f\u95dc").reset_index(name="\u7b46\u6578"),
            use_container_width=True,
            hide_index=True,
        )

    with supplier_column:
        st.markdown(f"**{TOP_SUPPLIERS}**")
        st.dataframe(
            top_suppliers.rename_axis("\u5f97\u6a19\u5ee0\u5546").reset_index(name="\u7b46\u6578"),
            use_container_width=True,
            hide_index=True,
        )


def build_download_csv(display_result: pd.DataFrame) -> bytes:
    return display_result.to_csv(index=False).encode("utf-8-sig")



def safe_filename(text: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in "-_" else "_" for char in text.strip())
    return cleaned.strip("_") or "report"


def build_summary_report(result: pd.DataFrame, keyword: str, selected_years: list[str]) -> pd.DataFrame:
    years = ", ".join(selected_years) if selected_years else "全部年度"
    rows: list[dict[str, object]] = [
        {"區段": "查詢條件", "項目": "關鍵字", "名稱": keyword, "筆數": "", "金額": ""},
        {"區段": "查詢條件", "項目": "年度", "名稱": years, "筆數": "", "金額": ""},
        {
            "區段": "總覽",
            "項目": "總計",
            "名稱": "",
            "筆數": len(result),
            "金額": int(result["TenderAwardPriceNumber"].sum()),
        },
    ]

    year_summary = build_year_trend(result)
    for row in year_summary.itertuples(index=False):
        rows.append({"區段": "年度分布", "項目": "年度", "名稱": row.Year, "筆數": row.筆數, "金額": int(row.總金額)})

    for ranking, section, name_column in [
        (build_ranking(result, "TenderOrgName", "機關"), "機關排行", "機關"),
        (build_ranking(result, "BidderSuppName", "得標廠商"), "得標廠商排行", "得標廠商"),
    ]:
        table = ranking.sort_values(["總金額", "筆數"], ascending=False).head(TOP_N)
        for row in table.itertuples(index=False):
            rows.append(
                {
                    "區段": section,
                    "項目": "依金額",
                    "名稱": getattr(row, name_column),
                    "筆數": row.筆數,
                    "金額": int(row.總金額),
                }
            )

    return pd.DataFrame(rows, columns=["區段", "項目", "名稱", "筆數", "金額"])


def build_agency_report(agency_data: pd.DataFrame, agency: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = [
        {
            "區段": "機關總覽",
            "年度": "",
            "機關": agency,
            "得標廠商": "",
            "標案名稱": "",
            "標案案號": "",
            "決標日期": "",
            "筆數": len(agency_data),
            "金額": int(agency_data["TenderAwardPriceNumber"].sum()),
        }
    ]

    si_summary = (
        agency_data.assign(得標廠商=clean_series(agency_data["BidderSuppName"]))
        .dropna(subset=["得標廠商"])
        .groupby(["Year", "得標廠商"])
        .agg(筆數=("TenderName", "size"), 金額=("TenderAwardPriceNumber", "sum"))
        .reset_index()
        .sort_values(["Year", "金額"], ascending=[False, False])
    )
    for row in si_summary.itertuples(index=False):
        rows.append(
            {
                "區段": "年度得標廠商彙總",
                "年度": row.Year,
                "機關": agency,
                "得標廠商": row.得標廠商,
                "標案名稱": "",
                "標案案號": "",
                "決標日期": "",
                "筆數": row.筆數,
                "金額": int(row.金額),
            }
        )

    detail_columns = [
        "Year",
        "TenderOrgName",
        "BidderSuppName",
        "TenderName",
        "TenderCaseNo",
        "AwardDate",
        "TenderAwardPriceNumber",
    ]
    details = agency_data[detail_columns].sort_values(["Year", "AwardDate", "TenderCaseNo"], ascending=[False, True, True])
    for row in details.itertuples(index=False):
        rows.append(
            {
                "區段": "標案明細",
                "年度": row.Year,
                "機關": row.TenderOrgName,
                "得標廠商": row.BidderSuppName,
                "標案名稱": row.TenderName,
                "標案案號": row.TenderCaseNo,
                "決標日期": row.AwardDate,
                "筆數": 1,
                "金額": int(row.TenderAwardPriceNumber),
            }
        )

    return pd.DataFrame(rows, columns=["區段", "年度", "機關", "得標廠商", "標案名稱", "標案案號", "決標日期", "筆數", "金額"])


def split_keyword(keyword: str) -> list[str]:
    return [part.strip() for part in keyword.replace("，", " ").replace(",", " ").split() if part.strip()]


def row_contains_token(data: pd.DataFrame, token: str) -> pd.Series:
    token_mask = pd.Series(False, index=data.index)
    for column in SEARCH_COLUMNS:
        token_mask = token_mask | data[column].fillna("").astype(str).str.contains(token, case=False, regex=False)
    return token_mask


def search_tenders(data: pd.DataFrame, keyword: str, selected_years: list[str]) -> pd.DataFrame:
    keyword = keyword.strip()
    if not keyword:
        return data.iloc[0:0].copy()

    tokens = split_keyword(keyword) or [keyword]
    mask = pd.Series(True, index=data.index)
    for token in tokens:
        mask = mask & row_contains_token(data, token)

    result = data.loc[mask].copy()
    if selected_years:
        result = result[result["Year"].astype(str).isin(selected_years)]
    return result


def sort_tenders(result: pd.DataFrame, sort_by: str) -> pd.DataFrame:
    if sort_by == SORT_BY_AMOUNT_DESC:
        return result.sort_values("TenderAwardPriceNumber", ascending=False)
    if sort_by == SORT_BY_AMOUNT_ASC:
        return result.sort_values("TenderAwardPriceNumber", ascending=True)
    return result.sort_values("Year", ascending=False)


def parse_natural_language_query(query: str, available_years: list[str]) -> tuple[str, list[str], str]:
    parsed = query.strip()
    years = [year for year in available_years if year in parsed]
    sort_by = SORT_BY_YEAR

    if "最大" in parsed or "最高" in parsed or "最多金額" in parsed:
        sort_by = SORT_BY_AMOUNT_DESC
    elif "最小" in parsed or "最低" in parsed:
        sort_by = SORT_BY_AMOUNT_ASC

    if "近五年" in parsed or "最近五年" in parsed:
        years = available_years[:5]
    elif "近三年" in parsed or "最近三年" in parsed:
        years = available_years[:3]

    stopwords = [
        "查詢", "查", "請幫我", "幫我", "近五年", "最近五年", "近三年", "最近三年",
        "最大", "最高", "最小", "最低", "金額", "標案", "得標", "決標", "有哪些", "多少",
    ]
    keyword = parsed
    for word in stopwords + years:
        keyword = keyword.replace(word, " ")
    keyword = " ".join(split_keyword(keyword))
    return keyword or parsed, years, sort_by


def build_text_insights(result: pd.DataFrame) -> list[str]:
    if result.empty:
        return []

    total_amount = int(result["TenderAwardPriceNumber"].sum())
    avg_amount = int(result["TenderAwardPriceNumber"].mean())
    max_row = result.sort_values("TenderAwardPriceNumber", ascending=False).iloc[0]
    year_summary = build_year_trend(result).sort_values("總金額", ascending=False)
    agency_ranking = build_ranking(result, "TenderOrgName", "機關").sort_values(["總金額", "筆數"], ascending=False)
    supplier_ranking = build_ranking(result, "BidderSuppName", "得標廠商").sort_values(["總金額", "筆數"], ascending=False)

    insights = [
        f"本次查詢共 {len(result):,} 筆，總金額 {format_amount(total_amount)}，平均每案 {format_amount(avg_amount)}。",
        f"最大金額標案為「{max_row['TenderName']}」，機關為「{max_row['TenderOrgName']}」，金額 {format_amount(max_row['TenderAwardPriceNumber'])}。",
    ]
    if not year_summary.empty:
        row = year_summary.iloc[0]
        insights.append(f"金額最高年度為 {row['Year']}，合計 {format_amount(row['總金額'])}。")
    if not agency_ranking.empty:
        row = agency_ranking.iloc[0]
        insights.append(f"金額最高機關為「{row['機關']}」，共 {int(row['筆數'])} 筆、{format_amount(row['總金額'])}。")
    if not supplier_ranking.empty:
        row = supplier_ranking.iloc[0]
        insights.append(f"金額最高得標廠商為「{row['得標廠商']}」，共 {int(row['筆數'])} 筆、{format_amount(row['總金額'])}。")
    return insights


def build_anomaly_alerts(result: pd.DataFrame) -> list[str]:
    if result.empty:
        return []

    alerts: list[str] = []
    trend = build_year_trend(result).sort_values("Year")
    previous_amount = None
    previous_year = None
    for row in trend.itertuples(index=False):
        amount = int(row.總金額)
        if previous_amount and previous_amount > 0 and amount >= previous_amount * ANOMALY_GROWTH_RATIO:
            alerts.append(
                f"{row.Year} 總金額較 {previous_year} 成長超過 {ANOMALY_GROWTH_RATIO:.0f} 倍：{format_amount(previous_amount)} -> {format_amount(amount)}。"
            )
        previous_amount = amount
        previous_year = row.Year

    total_amount = int(result["TenderAwardPriceNumber"].sum())
    supplier_ranking = build_ranking(result, "BidderSuppName", "得標廠商").sort_values("總金額", ascending=False)
    if total_amount > 0 and not supplier_ranking.empty:
        top_supplier = supplier_ranking.iloc[0]
        ratio = float(top_supplier["總金額"]) / total_amount
        if ratio >= ANOMALY_CONCENTRATION_RATIO and len(supplier_ranking) > 1:
            alerts.append(f"得標廠商「{top_supplier['得標廠商']}」金額占比 {ratio:.0%}，集中度偏高。")

    median_amount = float(result["TenderAwardPriceNumber"].median())
    if median_amount > 0:
        outliers = result[result["TenderAwardPriceNumber"] >= median_amount * ANOMALY_MEDIAN_MULTIPLIER]
        if not outliers.empty and len(result) >= 3:
            top = outliers.sort_values("TenderAwardPriceNumber", ascending=False).iloc[0]
            alerts.append(f"「{top['TenderName']}」金額為中位數 {ANOMALY_MEDIAN_MULTIPLIER:.0f} 倍以上，建議單獨檢視。")

    return alerts


def tender_similarity_score(source: pd.Series, target: pd.Series) -> int:
    score = 0
    if source.get("TenderOrgName", "") == target.get("TenderOrgName", ""):
        score += 3
    if source.get("BidderSuppName", "") == target.get("BidderSuppName", ""):
        score += 3

    source_tokens = set(split_keyword(str(source.get("TenderName", ""))))
    target_tokens = set(split_keyword(str(target.get("TenderName", ""))))
    score += len(source_tokens & target_tokens) * 2

    source_attr = str(source.get("ProcurementAttr", ""))
    if source_attr and source_attr == str(target.get("ProcurementAttr", "")):
        score += 1
    return score


def build_similar_tenders(all_data: pd.DataFrame, source: pd.Series, limit: int = SIMILAR_TENDER_LIMIT) -> pd.DataFrame:
    if all_data.empty:
        return pd.DataFrame()

    candidates = all_data.copy()
    source_case_no = str(source.get("TenderCaseNo", ""))
    if source_case_no:
        candidates = candidates[candidates["TenderCaseNo"].fillna("").astype(str) != source_case_no]
    if candidates.empty:
        return pd.DataFrame()

    candidates["SimilarityScore"] = candidates.apply(lambda row: tender_similarity_score(source, row), axis=1)
    candidates = candidates[candidates["SimilarityScore"] > 0]
    return candidates.sort_values(["SimilarityScore", "TenderAwardPriceNumber"], ascending=False).head(limit)


def rename_similar_for_display(result: pd.DataFrame) -> pd.DataFrame:
    if result.empty:
        return result
    display = rename_for_display(result.drop(columns=["SimilarityScore"], errors="ignore"))
    display.insert(0, "相似分數", result["SimilarityScore"].astype(int).tolist())
    return display

def rename_for_display(result: pd.DataFrame) -> pd.DataFrame:
    display_result = result.copy()
    display_result["TenderAwardPrice"] = display_result["TenderAwardPriceNumber"].map(format_amount)
    display_result = display_result.drop(columns=["TenderAwardPriceNumber"])
    return display_result.rename(
        columns={
            "Year": "\u5e74\u5ea6",
            "TenderOrgName": "\u6a5f\u95dc",
            "TenderName": "\u6a19\u6848\u540d\u7a31",
            "TenderAwardPrice": "\u91d1\u984d",
            "BidderSuppName": "\u5f97\u6a19\u5ee0\u5546",
            "NotObtainSuppName": "\u5354\u4f5c\u5ee0\u5546",
            "TenderCaseNo": "\u6a19\u6848\u6848\u865f",
            "AwardDate": "\u6c7a\u6a19\u65e5\u671f",
            "ProcurementType": "\u63a1\u8cfc\u985e\u578b",
            "ProcurementAttr": "\u63a1\u8cfc\u5c6c\u6027",
            "TenderAwardWay": "\u6c7a\u6a19\u65b9\u5f0f",
            "SourceFile": "\u539f\u59cb\u4f86\u6e90",
            "SourceCsv": "CSV \u4f86\u6e90",
        }
    )


def paginate_result(display_result: pd.DataFrame) -> pd.DataFrame:
    if len(display_result) <= RESULT_WARNING_THRESHOLD:
        return display_result

    st.warning(RESULT_LIMIT_WARNING)
    page_size_column, page_column = st.columns([1, 1])
    with page_size_column:
        page_size = st.selectbox(PAGE_SIZE_LABEL, PAGE_SIZE_OPTIONS, index=1)

    total_pages = max(1, (len(display_result) + page_size - 1) // page_size)
    with page_column:
        page = st.number_input(PAGE_LABEL, min_value=1, max_value=total_pages, value=1, step=1)

    start = (int(page) - 1) * page_size
    end = start + page_size
    st.caption(f"\u986f\u793a\u7b2c {start + 1:,} \u5230 {min(end, len(display_result)):,} \u7b46\uff0c\u5171 {len(display_result):,} \u7b46")
    return display_result.iloc[start:end]


def build_year_trend(result: pd.DataFrame) -> pd.DataFrame:
    trend = (
        result.groupby("Year", dropna=False)
        .agg(筆數=("TenderName", "size"), 總金額=("TenderAwardPriceNumber", "sum"))
        .reset_index()
        .sort_values("Year")
    )
    trend["總金額"] = trend["總金額"].astype(int)
    return trend


def build_ranking(result: pd.DataFrame, column: str, label: str) -> pd.DataFrame:
    ranking = (
        result.assign(_name=clean_series(result[column]))
        .dropna(subset=["_name"])
        .groupby("_name")
        .agg(筆數=("TenderName", "size"), 總金額=("TenderAwardPriceNumber", "sum"))
        .reset_index()
        .rename(columns={"_name": label})
    )
    ranking["總金額"] = ranking["總金額"].astype(int)
    return ranking


def show_trend_and_rankings(result: pd.DataFrame) -> None:
    st.markdown("**年度趨勢**")
    trend = build_year_trend(result)
    chart_data = trend.set_index("Year")[["筆數", "總金額"]]
    st.bar_chart(chart_data, use_container_width=True)
    trend_display = trend.copy()
    trend_display["總金額"] = trend_display["總金額"].map(format_amount)
    st.dataframe(trend_display.rename(columns={"Year": "年度"}), use_container_width=True, hide_index=True)

    agency_ranking = build_ranking(result, "TenderOrgName", "機關")
    supplier_ranking = build_ranking(result, "BidderSuppName", "得標廠商")
    ranking_tabs = st.tabs(["機關排行", "得標廠商排行"])
    with ranking_tabs[0]:
        show_ranking_table(agency_ranking, "機關")
    with ranking_tabs[1]:
        show_ranking_table(supplier_ranking, "得標廠商")


def show_ranking_table(ranking: pd.DataFrame, label: str) -> None:
    if ranking.empty:
        st.info("沒有可排行的資料。")
        return

    by_count, by_amount = st.columns(2)
    with by_count:
        st.markdown("**依筆數**")
        table = ranking.sort_values(["筆數", "總金額"], ascending=False).head(TOP_N).copy()
        table["總金額"] = table["總金額"].map(format_amount)
        st.dataframe(table, use_container_width=True, hide_index=True)
    with by_amount:
        st.markdown("**依金額**")
        table = ranking.sort_values(["總金額", "筆數"], ascending=False).head(TOP_N).copy()
        table["總金額"] = table["總金額"].map(format_amount)
        st.dataframe(table, use_container_width=True, hide_index=True)


def show_single_agency(result: pd.DataFrame) -> None:
    agencies = sorted(clean_series(result["TenderOrgName"]).unique())
    if not agencies:
        st.info("沒有可分析的機關資料。")
        return

    agency = st.selectbox("機關", agencies)
    agency_data = result[result["TenderOrgName"].fillna("").astype(str).str.strip() == agency]
    show_summary(agency_data)

    st.markdown("**歷年得標 SI 與金額分布**")
    pivot = (
        agency_data.assign(得標廠商=clean_series(agency_data["BidderSuppName"]))
        .dropna(subset=["得標廠商"])
        .groupby(["Year", "得標廠商"])
        .agg(筆數=("TenderName", "size"), 總金額=("TenderAwardPriceNumber", "sum"))
        .reset_index()
        .sort_values(["Year", "總金額"], ascending=[False, False])
    )
    pivot["總金額"] = pivot["總金額"].astype(int).map(format_amount)
    st.dataframe(pivot.rename(columns={"Year": "年度"}), use_container_width=True, hide_index=True)
    st.dataframe(rename_for_display(agency_data), use_container_width=True, hide_index=True)


def show_single_supplier(result: pd.DataFrame) -> None:
    suppliers = sorted(clean_series(result["BidderSuppName"]).unique())
    if not suppliers:
        st.info("沒有可分析的得標廠商資料。")
        return

    supplier = st.selectbox("得標廠商", suppliers)
    supplier_data = result[result["BidderSuppName"].fillna("").astype(str).str.strip() == supplier]
    show_summary(supplier_data)

    st.markdown("**服務過的機關與標案分布**")
    agency_summary = (
        supplier_data.assign(機關=clean_series(supplier_data["TenderOrgName"]))
        .dropna(subset=["機關"])
        .groupby("機關")
        .agg(筆數=("TenderName", "size"), 總金額=("TenderAwardPriceNumber", "sum"))
        .reset_index()
        .sort_values(["總金額", "筆數"], ascending=False)
    )
    agency_summary["總金額"] = agency_summary["總金額"].astype(int).map(format_amount)
    st.dataframe(agency_summary, use_container_width=True, hide_index=True)
    st.dataframe(rename_for_display(supplier_data), use_container_width=True, hide_index=True)


def show_tender_detail(result: pd.DataFrame) -> None:
    detail_result = result.reset_index(drop=True).copy()
    labels = detail_result.apply(
        lambda row: f"{row['Year']} | {row['TenderOrgName']} | {row['TenderName']}", axis=1
    ).tolist()
    selected_label = st.selectbox("標案", labels)
    row = detail_result.iloc[labels.index(selected_label)]

    st.markdown("**標案明細**")
    details = {
        "年度": row.get("Year", ""),
        "標案案號": row.get("TenderCaseNo", ""),
        "標案名稱": row.get("TenderName", ""),
        "機關": row.get("TenderOrgName", ""),
        "決標日期": row.get("AwardDate", ""),
        "金額": format_amount(row.get("TenderAwardPriceNumber", 0)),
        "得標廠商": row.get("BidderSuppName", ""),
        "協作廠商": row.get("NotObtainSuppName", ""),
        "採購類型": row.get("ProcurementType", ""),
        "採購屬性": row.get("ProcurementAttr", ""),
        "決標方式": row.get("TenderAwardWay", ""),
        "原始來源": row.get("SourceFile", ""),
        "CSV 來源": row.get("SourceCsv", ""),
    }
    detail_frame = pd.DataFrame(details.items(), columns=["欄位", "內容"])
    st.dataframe(detail_frame, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title=TITLE, layout="wide")
    if not show_login_page():
        st.stop()

    show_app_header()

    data, data_errors = load_data(str(DB_PATH))
    show_data_errors(data_errors, fatal=data.empty)

    if data.empty:
        st.info(DATA_EMPTY_MESSAGE)
        st.stop()

    missing_app_columns = [column for column in DISPLAY_COLUMNS + ["TenderAwardPriceNumber"] if column not in data.columns]
    if missing_app_columns:
        st.error("\u8cc7\u6599\u7f3a\u5c11\u67e5\u8a62\u6240\u9700\u6b04\u4f4d")
        st.caption(", ".join(missing_app_columns))
        st.stop()

    available_years = sorted(data["Year"].dropna().astype(str).unique(), reverse=True)

    query = st.text_input(SEARCH_LABEL, placeholder=SEARCH_PLACEHOLDER)
    parsed_keyword, suggested_years, suggested_sort_by = parse_natural_language_query(query, available_years)
    sort_options = [SORT_BY_YEAR, SORT_BY_AMOUNT_DESC, SORT_BY_AMOUNT_ASC]
    sort_index = sort_options.index(suggested_sort_by) if suggested_sort_by in sort_options else 0

    filter_column, sort_column = st.columns([2, 1])
    with filter_column:
        selected_years = st.multiselect(
            YEAR_FILTER_LABEL,
            available_years,
            default=suggested_years,
            help=YEAR_FILTER_HELP,
        )
    with sort_column:
        sort_by = st.selectbox(SORT_LABEL, sort_options, index=sort_index)

    if query:
        query = query.strip()
        if not query:
            st.caption(START_SEARCH)
            st.stop()

        keyword = parsed_keyword.strip()
        if keyword != query or suggested_years or suggested_sort_by != SORT_BY_YEAR:
            selected_year_text = ", ".join(selected_years) if selected_years else "全部年度"
            st.caption(f"解析條件：關鍵字「{keyword}」；年度：{selected_year_text}；排序：{sort_by}")

        result = sort_tenders(search_tenders(data, keyword, selected_years), sort_by)

        if result.empty:
            st.info(NO_RESULT)
        else:
            show_summary(result)
            st.caption(f"\u5171 {len(result)} \u7b46")
            (
                result_tab,
                insight_tab,
                analysis_tab,
                similar_tab,
                anomaly_tab,
                agency_tab,
                supplier_tab,
                detail_tab,
            ) = st.tabs(["查詢結果", "智慧摘要", "趨勢與排行", "相似標案", "異常提醒", "單一機關", "單一得標廠商", "標案明細"])
            display_result = rename_for_display(result)
            with result_tab:
                paged_result = paginate_result(display_result)
                st.dataframe(paged_result, use_container_width=True, hide_index=True)
                st.download_button(
                    DOWNLOAD_LABEL,
                    data=build_download_csv(display_result),
                    file_name=f"tender_search_results_{safe_filename(keyword)}.csv",
                    mime="text/csv",
                )
            with insight_tab:
                st.markdown("**規則式文字洞察**")
                for insight in build_text_insights(result):
                    st.write(f"- {insight}")
            with analysis_tab:
                show_trend_and_rankings(result)
            with similar_tab:
                detail_result = result.reset_index(drop=True).copy()
                labels = detail_result.apply(
                    lambda row: f"{row['Year']} | {row['TenderOrgName']} | {row['TenderName']}", axis=1
                ).tolist()
                selected_label = st.selectbox("參考標案", labels)
                source = detail_result.iloc[labels.index(selected_label)]
                similar = build_similar_tenders(data, source)
                if similar.empty:
                    st.info("沒有找到相似標案。")
                else:
                    st.dataframe(rename_similar_for_display(similar), use_container_width=True, hide_index=True)
            with anomaly_tab:
                alerts = build_anomaly_alerts(result)
                if alerts:
                    for alert in alerts:
                        st.warning(alert)
                else:
                    st.info("未偵測到明顯異常。")
            with agency_tab:
                show_single_agency(result)
            with supplier_tab:
                show_single_supplier(result)
            with detail_tab:
                show_tender_detail(result)
    else:
        st.caption(START_SEARCH)

if __name__ == "__main__":
    main()













