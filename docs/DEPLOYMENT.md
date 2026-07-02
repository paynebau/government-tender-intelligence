# 部署規劃

更新日期：2026-07-02

## 方案一：本機使用

適合單人或小團隊在 Windows 電腦上查詢。

1. 安裝 Python 3.12。
2. 執行 `pip install -r requirements.txt`。
3. 將 CSV 放在 `資料庫_CSV/`。
4. 執行 `powershell -ExecutionPolicy Bypass -File .\scripts\import_to_sqlite.ps1` 重建 SQLite。
5. 執行 `powershell -ExecutionPolicy Bypass -File .\run_app.ps1`。
6. 開啟 `http://localhost:8501`。

## 方案二：內網主機

適合多人在同一個內網環境查詢，建議作為近期優先部署方式。

1. 準備 Windows 或 Linux 內網主機。
2. 建立固定專案目錄與 Python 虛擬環境。
3. 由排程或人工更新 `資料庫_CSV/`，再執行匯入腳本。
4. 用 Streamlit 啟動服務，指定內網可連線的 host 與 port，例如 `streamlit run app.py --server.address 0.0.0.0 --server.port 8501`。
5. 由防火牆限制只允許內網來源連線。
6. 若需要長期服務，使用 Windows 工作排程、NSSM、systemd 或容器管理程序維持常駐。

## 方案三：雲端部署

適合跨地點使用，但需要先處理資料權限與存取控管。

1. 將應用部署到 VM、容器平台或 Streamlit Community Cloud 類型服務。
2. 不建議直接提交完整 SQLite 或原始 CSV 到公開版本庫。
3. 使用私有儲存空間保存 CSV 與 SQLite，部署時再掛載或下載。
4. 加上 HTTPS、帳號權限與連線來源限制。
5. 建立資料更新流程，避免手動覆蓋造成版本不一致。

## 建議

MVP 階段先採本機使用；若有多人共用需求，下一步採內網主機。雲端部署等資料權限、登入機制與更新流程明確後再評估。
