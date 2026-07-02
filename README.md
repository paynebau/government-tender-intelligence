# 政府標案情資查詢系統

這是一個 Streamlit 查詢工具，用來跨年度搜尋政府標案資料。資料會先由 `資料庫_CSV/*SourceData.csv` 匯入 SQLite，使用者可輸入機關、標案名稱、得標廠商或協作廠商關鍵字，查看查詢結果、摘要統計，並下載結果 CSV。


## 匯入資料

首次啟動或 CSV 更新後，先執行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\import_to_sqlite.ps1
```

預設會重建：

```text
database/tenders.sqlite
```

若需要指定來源或資料庫位置，可直接使用 Python 腳本：

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" .\scripts\import_to_sqlite.py --csv-dir .\資料庫_CSV --db .\database\tenders.sqlite
```
## 啟動方式

在 PowerShell 執行：

```powershell
cd D:\職能學院\政府標案情資查詢系統
powershell -ExecutionPolicy Bypass -File .\run_app.ps1
```

啟動後開啟：

```text
http://localhost:8501
```

## 資料來源

目前匯入來源：

```text
資料庫_CSV/*SourceData.csv
```

年度從檔名解析，例如 `award_2025_..._SourceData.csv` 會解析為 `2025`。完整欄位對照請見 `docs/FIELD_MAPPING.md`。

## 主要欄位

| 顯示名稱 | CSV 欄位 |
|---|---|
| 年度 | 檔名中的年度 |
| 機關 | `TenderOrgName` |
| 標案名稱 | `TenderName` |
| 金額 | `TenderAwardPrice` |
| 得標廠商 | `BidderSuppName` |
| 協作廠商 | `NotObtainSuppName` |

## 目前功能

- 跨年度關鍵字搜尋。
- 自然語言查詢解析，例如「查中華郵政近五年最大 SI」。
- 年度篩選。
- 查詢結果過多時分頁顯示。
- 依年度新到舊、金額高到低、金額低到高排序。
- 查詢結果表格。
- 查詢結果 CSV 下載。
- 金額千分位顯示。
- 查無資料提示。
- SQLite 匯入流程與資料庫查詢。
- 摘要統計：筆數、總金額、年度分布、前 3 機關、前 3 得標廠商。
- 年度趨勢圖：每年筆數與總金額。
- 機關排行與得標廠商排行：依筆數與依金額。
- 單一機關分析：歷年 SI 與金額分布。
- 單一得標廠商分析：服務過的機關與標案。
- 單筆標案明細：案號、日期、採購類型、決標方式與來源。
- 規則式文字洞察、相似標案推薦與異常提醒。

## 驗證方式

修改 Python 後至少執行：

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m py_compile app.py
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pytest
```

## 後續方向

1. 擴充自然語言解析規則，例如金額區間、機關/廠商指定語句。
2. 規劃更細的機關、廠商、金額區間篩選。
3. 建立外部資料源下載樣本與欄位 mapping 測試。
4. 評估登入、權限控管與資料版本記錄。




## 部署規劃

本機、內網主機與雲端部署建議請見 docs/DEPLOYMENT.md。


## 外部資料源評估

政府採購公開資料 API 與 g0v/PCC 相關資料源評估請見 docs/API_EVALUATION.md。


