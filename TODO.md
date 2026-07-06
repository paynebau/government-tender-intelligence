# TODO: 政府標案情資查詢系統

更新日期：2026-07-06

## P0：MVP 基礎查詢

- [x] 建立 Streamlit app。
- [x] 載入跨年度標案資料。
- [x] 支援關鍵字搜尋。
- [x] 顯示查詢結果表格。
- [x] 顯示查無資料提示。
- [x] 顯示查詢摘要。
- [x] 支援金額千分位格式。
- [x] 支援年度新到舊、金額高到低、金額低到高排序。

## P1：SQLite 與資料匯入

- [x] 建立 CSV 匯入 SQLite 腳本。
- [x] 建立 PowerShell 匯入包裝腳本。
- [x] Streamlit app 改查 SQLite。
- [x] SQLite 缺失時退回讀取 CSV。
- [x] 補上資料缺漏與資料庫錯誤提示。
- [x] 建立欄位對照文件 `docs/FIELD_MAPPING.md`。

## P2：分析與報表

- [x] 加入年度篩選器。
- [x] 加入查詢結果 CSV 下載。
- [x] 查詢結果超過門檻時分頁顯示。
- [x] 加入年度趨勢圖。
- [x] 加入機關排行與得標廠商排行。
- [x] 加入單一機關分析。
- [x] 加入單一得標廠商分析。
- [x] 加入單筆標案明細。
- [x] 加入摘要報表 CSV 下載。
- [x] 加入固定格式機關分析報告 CSV 下載。

## P3：文件與維運

- [x] 建立 `README.md`。
- [x] 建立 `PROGRESS.md`。
- [x] 建立 `docs/VERSION_PLAN.md`。
- [x] 建立 `docs/DEPLOYMENT.md`。
- [x] 建立 `docs/API_EVALUATION.md`。
- [x] 建立 `.gitignore`。
- [x] 清理快取與 log 檔。
- [x] 重建可讀的 `PRD.md`。
- [x] 重建可讀的 `TODO.md`。

## P4：測試

- [x] 建立小型測試資料集。
- [x] 建立資料載入、搜尋、排序、金額格式化與摘要統計測試。
- [x] 建立 app 匯入 smoke test。
- [x] 保留 Python 語法檢查流程。

## P5：規則式智慧功能

- [x] 加入自然語言查詢解析。
- [x] 加入規則式文字洞察。
- [x] 加入相似標案推薦。
- [x] 加入異常提醒。
- [x] 完成外部 API 串接評估文件。

## P6：部署收尾

- [x] 建立 GitHub repository：`paynebau/government-tender-intelligence`。
- [x] 推送 `main` branch 到 GitHub。
- [x] 完成 Streamlit Community Cloud 部署規劃。
- [x] 完成 Streamlit / GitHub 連線問題整理。
- [ ] 在 Streamlit Community Cloud 建立 app，設定 repository、branch 與 main file path `app.py`。
- [ ] 驗證雲端 app 可正常啟動。
- [ ] 驗證雲端 app 是否能讀取必要資料。
- [ ] 確認 GitHub repository 要維持 private 或改為 public。
- [ ] 建立資料更新策略，包含 CSV 更新、SQLite 重建與部署後驗證。


## P7：登入保護

- [x] 建立登入頁面。
- [x] 登入頁需輸入帳號與密碼。
- [x] 登入成功後才顯示標案查詢頁。
- [x] 在查詢頁右上角提供登出按鈕。
- [x] 支援環境變數與 Streamlit secrets 設定帳密。

## P8：完整資料庫重跑

- [x] 支援 `完整資料庫/award_*_flat.csv` 匯入格式。
- [x] 使用完整資料庫重建 `database/tenders.sqlite`。
- [x] 完成 2020-2026 年資料 sanity check。
- [x] 重啟本機 Streamlit app。

## 下一步建議

1. 先完成 Streamlit Community Cloud app 建立與啟動驗證。
2. 若雲端無法使用本機 SQLite，改以 CSV 匯入或部署前重建 SQLite 的方式處理。
3. 決定資料檔是否適合放入 GitHub；若資料敏感或過大，需改用外部儲存或手動上傳流程。
4. 完成部署後，補一輪 README / PROGRESS 的部署狀態更新。
5. 下一階段再做金額區間、機關/廠商篩選與名稱別名對照表。




