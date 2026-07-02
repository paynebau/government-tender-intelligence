# 欄位對照表

本文件整理目前 Streamlit 查詢頁、SQLite 資料表與原始 CSV 欄位的對照。資料匯入流程由 `scripts/import_to_sqlite.py` 建立 `database/tenders.sqlite`。

## 查詢欄位

| 查詢用途 | Streamlit 欄位 | SQLite 欄位 | CSV 欄位 |
|---|---|---|---|
| 機關 | `TenderOrgName` | `tender_org_name` | `TenderOrgName` |
| 標案名稱 | `TenderName` | `tender_name` | `TenderName` |
| 得標廠商 | `BidderSuppName` | `bidder_supp_name` | `BidderSuppName` |
| 協作廠商 | `NotObtainSuppName` | `not_obtain_supp_name` | `NotObtainSuppName` |

## 查詢結果顯示欄位

| 顯示名稱 | Streamlit 欄位 | SQLite 欄位 | CSV 欄位 |
|---|---|---|---|
| 年度 | `Year` | `year` | 從檔名 `award_YYYY...` 解析 |
| 機關 | `TenderOrgName` | `tender_org_name` | `TenderOrgName` |
| 標案名稱 | `TenderName` | `tender_name` | `TenderName` |
| 金額 | `TenderAwardPrice` | `tender_award_price` | `TenderAwardPrice` |
| 得標廠商 | `BidderSuppName` | `bidder_supp_name` | `BidderSuppName` |
| 協作廠商 | `NotObtainSuppName` | `not_obtain_supp_name` | `NotObtainSuppName` |
| 標案案號 | `TenderCaseNo` | `tender_case_no` | `TenderCaseNo` |
| 決標日期 | `AwardDate` | `award_date` | `AwardDate` |
| 採購類型 | `ProcurementType` | `procurement_type` | `ProcurementType` |
| 採購屬性 | `ProcurementAttr` | `procurement_attr` | `ProcurementAttr` |
| 決標方式 | `TenderAwardWay` | `tender_award_way` | `TenderAwardWay` |
| 原始來源 | `SourceFile` | `source_file` | `SourceFile` |
| CSV 來源 | `SourceCsv` | `source_csv` | 匯入時記錄來源檔名 |

## 標準化與數值欄位

| 用途 | SQLite 欄位 | 規則 |
|---|---|---|
| 金額排序與加總 | `tender_award_price_number` | 從 `TenderAwardPrice` 移除非數字字元後轉為數值；無法解析時為 0 |
| 機關名稱標準化 | `tender_org_name_normalized` | 去除空白，將全形括號轉半形括號 |
| 得標廠商標準化 | `bidder_supp_name_normalized` | 去除空白，將全形括號轉半形括號 |
| 協作廠商標準化 | `not_obtain_supp_name_normalized` | 去除空白，將全形括號轉半形括號 |

## 必要欄位

匯入時每個 `*SourceData.csv` 至少需要以下欄位，否則該檔會被跳過並列入警示：

- `TenderName`
- `TenderOrgName`
- `TenderAwardPrice`
- `BidderSuppName`
- `NotObtainSuppName`
