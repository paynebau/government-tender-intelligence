# TODO: 政府標案情資查詢系統

更新日期：2026-07-02

## P0：先讓 MVP 穩定可用

- [x] 在 Streamlit app 加入「下載查詢結果 CSV」按鈕。
- [x] 加入年度篩選器，讓使用者可選 2021-2025 或指定年度。
- [x] 加入查詢結果筆數過多時的提示與分頁/限制顯示策略。
- [x] 將目前查詢欄位與顯示欄位整理成明確欄位對照表。
- [x] 加入基本錯誤處理：找不到 `資料庫_CSV`、CSV 欄位缺漏、資料為空時要顯示友善訊息。

## P1：資料層與查詢能力

- [x] 建立可重跑的 CSV 匯入流程，從 `資料庫_CSV/*SourceData.csv` 匯入並清洗成標準格式。
- [x] 導入 SQLite，將 CSV 資料匯入資料庫。
- [x] 調整 Streamlit app，改為查詢 SQLite，而不是每次直接讀 CSV。
- [x] 建立資料表 schema，至少包含年度、機關、標案名稱、案號、得標日期、金額、得標廠商、協作廠商。
- [x] 增加資料更新腳本，讓新年度 CSV 可一鍵匯入。
- [x] 建立廠商名稱標準化規則，例如處理中英文括號與空白差異。

## P2：分析與視覺化

- [x] 加入年度趨勢圖：每年筆數與總金額。
- [x] 加入得標廠商排行：依筆數與依金額。
- [x] 加入機關排行：依筆數與依金額。
- [x] 加入單一機關頁面，顯示該機關歷年 SI 與金額分布。
- [x] 加入單一得標廠商頁面，顯示該廠商服務過的機關與標案。
- [x] 加入標案明細展開區，顯示案號、日期、採購類型、決標方式等欄位。

## P3：報表與專案管理

- [x] 在網頁提供查詢結果匯出 CSV。
- [x] 在網頁提供摘要報表匯出。
- [x] 產出固定格式的機關分析報告，例如指定機關 2021-2025 得標 SI 與金額。
- [x] 將 `scripts/query_agency_si.ps1` 的輸出格式與 Streamlit 查詢結果格式統一。
- [x] 補上 `README.md`，說明安裝、啟動、資料放置與常見問題。
- [x] 規劃版本節點：MVP、v1.1、v1.2、v2.0。

## P4：品質與部署

- [x] 建立測試資料集，避免每次都用完整 CSV 測試。
- [x] 加入單元測試：資料載入、搜尋、排序、金額格式化、摘要統計。
- [x] 加入 smoke test，確認 `app.py` 可啟動。
- [x] 清理不應納入版本管理的檔案，例如 `__pycache__`、log 檔。
- [x] 建立 `.gitignore`。
- [x] 規劃部署方式：本機使用、內網主機、或雲端部署。

## P5：AI 與進階功能

- [x] 評估是否加入自然語言查詢，例如「查中華郵政近五年最大 SI」。
- [x] 加入 AI 摘要，針對查詢結果產生文字洞察。
- [x] 加入相似標案推薦。
- [x] 加入異常值提醒，例如金額暴增、特定廠商集中度過高。
- [x] 評估串接政府採購公開資料 API 或 g0v/PCC 相關資料源。


## P6：上線與維運

- [x] 建立 GitHub repository：`paynebau/government-tender-intelligence`。
- [x] 推送 `main` branch 到 GitHub。
- [x] 完成 Streamlit Community Cloud 帳號註冊與登入。
- [x] 完成 Streamlit / GitHub 授權流程。
- [ ] 在 Streamlit Community Cloud 建立 app，綁定 repository、branch 與 `app.py`。
- [ ] 完成首次雲端部署並記錄正式網址。
- [ ] 部署後測試搜尋、年度篩選、智慧摘要、相似標案與異常提醒。
- [ ] 決定 GitHub repo 維持 private 或改為 public。
- [ ] 建立資料更新與重新部署流程。

## 近期建議執行順序

1. 在 Streamlit Community Cloud 建立 app：repo `paynebau/government-tender-intelligence`、branch `main`、main file `app.py`。
2. 完成首次雲端部署並把正式網址記錄回 `README.md`、`PROGRESS.md` 與本 TODO。
3. 部署後測試主要查詢流程與 P5 分頁功能。
4. 決定 GitHub repo 維持 private 或改為 public。
5. 建立後續資料更新與重新部署流程。
