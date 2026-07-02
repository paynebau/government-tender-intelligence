# AGENTS.md

本文件提供給後續協作的開發代理使用。進行任何修改前，請先閱讀 `PRD.md`、`PROGRESS.md`、`TODO.md`，並以目前程式碼行為為準。

## 專案概述

專案名稱：政府標案情資查詢系統

目標是建立一個可查詢政府標案資料的 Streamlit 網頁，讓使用者輸入關鍵字後，可跨年度查詢標案，並快速看到機關、標案名稱、得標廠商、協作廠商、金額與摘要統計。

## 重要檔案

- `app.py`：主要 Streamlit app。
- `requirements.txt`：Python 套件依賴。
- `run_app.ps1`：Windows 本機啟動腳本。
- `PRD.md`：產品需求文件。目前有編碼亂碼問題，解讀時需謹慎。
- `PROGRESS.md`：目前完成度與 PRD 對照。
- `TODO.md`：後續待辦與優先順序。
- `資料庫_CSV/`：CSV 資料來源。
- `scripts/query_agency_si.ps1`：指定機關查詢 SI 與金額的 PowerShell 腳本。
- `output/`：查詢輸出檔案。

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

## 資料來源與欄位

目前 app 直接讀取：

```text
資料庫_CSV/*SourceData.csv
```

主要欄位對照：

| 顯示名稱 | CSV 欄位 |
|---|---|
| 年度 | 從檔名 `award_YYYY...` 解析 |
| 機關 | `TenderOrgName` |
| 標案名稱 | `TenderName` |
| 金額 | `TenderAwardPrice` |
| 得標廠商 | `BidderSuppName` |
| 協作廠商 | `NotObtainSuppName` |

搜尋欄位：

- `TenderOrgName`
- `TenderName`
- `BidderSuppName`
- `NotObtainSuppName`

## 目前已實作功能

- Streamlit 查詢頁。
- `@st.cache_data` 快取 CSV 載入。
- 跨年度關鍵字搜尋。
- 查詢結果表格。
- 金額千分位顯示。
- 預設依年度新到舊排序。
- 可切換金額高到低、金額低到高排序。
- 查無資料顯示「查無相關標案」。
- 查詢摘要：筆數、總金額、年度分布、前 3 機關、前 3 得標廠商。

## 開發注意事項

- 優先維持 `app.py` 簡潔，避免過早拆過多抽象。
- 中文文字若在 Windows PowerShell 顯示亂碼，不一定代表檔案內容壞掉；但 `PRD.md` 目前確實疑似已有編碼問題。
- 新增功能前先更新或檢查 `TODO.md`，避免偏離 MVP。
- 不要刪除使用者資料、CSV 原始資料或既有輸出檔，除非使用者明確要求。
- 若要增加資料處理流程，優先做成可重跑腳本，避免只能手動操作。
- 大量資料查詢若變慢，下一步應優先導入 SQLite，而不是在 Streamlit 內堆疊複雜 pandas 邏輯。

## 驗證方式

修改 Python 後至少執行：

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m py_compile app.py
```

如需確認網頁：

```powershell
powershell -ExecutionPolicy Bypass -File .\run_app.ps1
```

然後打開 `http://localhost:8501` 測試搜尋。

## 近期優先事項

1. 修復或重建 `PRD.md` 編碼。
2. 加入查詢結果 CSV 下載按鈕。
3. 加入年度篩選器。
4. 補上 `README.md`。
5. 建立 SQLite 匯入流程。
