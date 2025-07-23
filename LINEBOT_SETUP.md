# LINE Bot RAG 研究助手 設定指南

## 概述

本專案成功實現了一個 FastAPI LINE Bot，整合了現有的 RAG 研究助手系統。用戶可以透過 LINE 聊天介面使用 AI 研究助手功能。

## 已實現功能

### ✅ 完成的核心功能

1. **專案結構** - 建立了完整的模組化架構
2. **資料模型** - 實現了 UserSession、UserConfig、ResearchQuery 等核心模型
3. **LINE Webhook 處理** - 支援簽名驗證和事件路由
4. **訊息路由** - 處理文字訊息、文件上傳和互動按鈕
5. **RAG 研究整合** - 與現有的研究系統完全整合
6. **會話管理** - 支援用戶會話狀態和上下文保持
7. **文件處理** - 支援 PDF、圖片、文字文件上傳和向量化
8. **用戶設定** - 可配置研究參數和報告格式
9. **LINE 訊息模板** - 提供豐富的互動式介面
10. **錯誤處理和日誌** - 完整的錯誤處理和監控機制

### 🔧 技術架構

```
FastAPI LineBot
├── 資料模型層 (models/)
│   ├── UserSession - 用戶會話管理
│   ├── UserConfig - 用戶配置
│   └── ResearchQuery - 研究查詢
├── 服務層 (services/)
│   ├── LineBotHandler - Webhook 處理
│   ├── MessageRouter - 訊息路由
│   ├── ResearchService - RAG 研究整合
│   ├── SessionManager - 會話管理
│   ├── FileHandler - 文件處理
│   └── ConfigurationService - 設定管理
└── 工具層 (utils/)
    ├── MessageTemplates - LINE 訊息模板
    └── ErrorResponse - 錯誤回應

整合現有 RAG 系統:
├── src/assistant/graph.py - 研究圖表
├── src/assistant/vector_db.py - 向量資料庫
└── src/assistant/utils.py - 文件處理工具
```

## 設定步驟

### 1. 環境準備

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. LINE Bot 設定

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 和 Messaging API Channel
3. 取得以下憑證：
   - Channel Secret
   - Channel Access Token

### 3. 環境變數設定

複製並修改 `.env.example` 為 `.env`：

```bash
cp .env.example .env
```

設定以下環境變數：

```env
# LINE Bot 設定
LINE_CHANNEL_SECRET="你的_channel_secret"
LINE_CHANNEL_ACCESS_TOKEN="你的_channel_access_token"

# RAG 系統設定
OPENROUTER_API_KEY="你的_openrouter_api_key"
TAVILY_API_KEY="你的_tavily_api_key"
LANGCHAIN_API_KEY="你的_langchain_api_key"
```

### 4. 啟動服務

#### 簡化版測試 (推薦先試用)

```bash
source venv/bin/activate
python3 simple_linebot.py
```

#### 完整版服務

```bash
source venv/bin/activate
python3 main.py
```

服務會在 `http://localhost:8000` 啟動

### 5. LINE Bot Webhook 設定

在 LINE Developers Console 中設定 Webhook URL：
- 本地測試: 使用 ngrok 等工具建立隧道
- 生產環境: `https://你的域名.com/webhook`

## 使用指南

### 支援的指令

| 指令 | 功能 |
|------|------|
| `hi`, `hello`, `你好` | 歡迎訊息 |
| `說明`, `help`, `幫助` | 使用說明 |
| `設定`, `config`, `配置` | 開啟設定選單 |
| `清除`, `clear`, `重置` | 清除對話記錄 |
| `狀態`, `status` | 查看研究狀態 |
| 其他文字 | 進行研究查詢 |

### 支援的文件格式

- PDF 文件 (.pdf)
- 圖片檔案 (.jpg, .png, .gif)
- 文字檔案 (.txt)

### 設定選項

- **最大查詢數量**: 1, 3, 5 (預設: 3)
- **網路搜尋**: 啟用/停用 (預設: 停用)
- **報告格式**: 標準報告/財務報告 (預設: 標準報告)

## 部署建議

### Cloudflare Workers (如規格設計)

1. 安裝 Wrangler CLI
2. 建立 `wrangler.toml` 配置
3. 設定環境變數和 KV 儲存
4. 部署: `wrangler publish`

### 其他雲端平台

- **Heroku**: 支援 Python/FastAPI
- **Railway**: 簡單的部署流程
- **Google Cloud Run**: 容器化部署
- **AWS Lambda**: 無伺服器部署

## 開發說明

### 測試

```bash
# 測試基本功能
curl http://localhost:8000/

# 測試健康檢查
curl http://localhost:8000/health
```

### 擴展功能

1. **新增訊息類型**: 修改 `MessageRouter.handle_message_event()`
2. **自訂研究參數**: 更新 `UserConfig` 模型
3. **新增報告格式**: 在 `report_structures/` 目錄添加新模板
4. **客製化回應**: 修改 `MessageTemplates` 類別

## 故障排除

### 常見問題

1. **導入錯誤**: 確保虛擬環境已啟動且依賴已安裝
2. **簽名驗證失敗**: 檢查 Channel Secret 是否正確
3. **API 呼叫失敗**: 確認 Channel Access Token 有效
4. **文件處理失敗**: 檢查文件格式和大小限制

### 日誌監控

日誌會輸出到控制台，包含：
- 請求處理狀態
- 錯誤訊息和堆疊追蹤
- 用戶互動記錄
- 系統效能指標

## 授權

本專案基於現有的 RAG 研究助手系統擴展，遵循相同的授權條款。