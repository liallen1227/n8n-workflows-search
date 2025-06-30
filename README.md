# n8n Workflow Search Tool with Gemini

本專案是一套結合 **n8n workflow 自動收集機制** 與 **Gemini 語意搜尋引擎** 的自動化查詢工具。透過 Selenium 自動爬取 n8n 上的 workflow 範例，儲存至 MySQL 資料庫，並可輸入關鍵字（如「郵件」）查詢相關自動化流程。

---

## 專案功能

- 使用 Selenium 爬取 n8n 官方 workflow
- 儲存資料至 MySQL 資料庫
- 整合 Gemini 語意搜尋 API 進行關鍵字查詢
- 可搭配 Docker 部署、虛擬環境管理 (`.venv`)

---

## 專案結構

    n8n-list/
    ├── src/
    │ ├── e01_list_search2.py # Step 1：收集 workflow 列表
    │ ├── e02_get_all_workflow.py # Step 2：爬取所有 workflow 詳情
    │ ├── t03_insert_mysql.py # Step 3：寫入 MySQL 資料庫
    │ └── search_workflow.py # 關鍵字搜尋主程式
    ├── data/
    │ ├── n8n_workflows_all.py # 所有成功爬取 workflow 資料
    │ ├── n8n_workflows_fail.py # 爬取失敗列表
    │ └── n8n_workflows_final.py # 清理與彙總後的結果
    └── requirements.txt # Python 套件依賴

安裝依賴
- pip install -r requirements.txt

建立資料庫（MySQL）
- docker run -d `
    --name mysql `
    -e MYSQL_ROOT_PASSWORD=password `
    -p 3306:3306 `
    mysql:8.0

執行完整流程
## Step 1: 收集 workflow 列表
- python src/e01_list_search2.py

## Step 2: 逐一爬取詳細內容
- python src/e02_get_all_workflow.py

## Step 3: 寫入 MySQL 資料庫
- python src/t03_insert_mysql.py

查詢關鍵字（Gemini 語意搜尋）
- python src/search_workflow.py

輸入關鍵字：郵件
搜尋結果：
1. 發送 Gmail 郵件通知
2. 自動整理郵件附件並上傳至雲端
3. 根據表單內容自動產生郵件回覆
