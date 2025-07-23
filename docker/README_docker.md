# 🐳 Docker 版本 RAG 研究助手使用指南

本文件說明如何使用 Docker Compose 來運行本地 RAG 研究助手的所有服務。

## 📋 前置需求

- [Docker](https://www.docker.com/get-started) 和 [Docker Compose](https://docs.docker.com/compose/install/)
- 確保已設定好 `.env` 檔案中的必要環境變數

## 🚀 快速開始

### 1. 使用啟動腳本

最簡單的方式是使用提供的啟動腳本：

```bash
./docker-start.sh
```

這個腳本會：
- 確保 Ollama 模型已下載
- 啟動所有 Docker 服務
- 顯示各服務的存取網址

### 2. 手動啟動

如果你想手動控制服務，可以使用以下命令：

```bash
# 下載 Ollama 模型（首次使用時）
docker run --rm -v ollama_data:/root/.ollama ollama/ollama pull deepseek-r1:7b

# 啟動所有服務
docker-compose up -d

# 查看所有服務的日誌
docker-compose logs -f
```

## 🔧 服務說明

Docker Compose 會啟動以下三個服務：

1. **Streamlit Web 介面** (http://localhost:8501)
   - 提供網頁使用者介面
   - 基於 `app.py`

2. **LINE Bot API** (http://localhost:8000)
   - 處理 LINE 訊息
   - 基於 `main.py`

3. **Ollama** (http://localhost:11434)
   - 本地運行 DeepSeek R1 模型
   - 提供 API 給其他服務使用

## 🛠️ 常用命令

```bash
# 啟動所有服務
docker-compose up -d

# 停止所有服務
docker-compose down

# 查看特定服務的日誌
docker-compose logs -f streamlit
docker-compose logs -f linebot
docker-compose logs -f ollama

# 重新建構並啟動服務（程式碼變更後）
docker-compose up -d --build
```

## ⚙️ 環境變數配置

所有服務都會使用專案根目錄中的 `.env` 檔案。你可以在這裡設定：

- Ollama 模型配置 (`OLLAMA_MODEL`, `USE_OLLAMA`)
- 外部 LLM 配置 (`EXTERNAL_LLM_MODEL`, `OPENROUTER_API_KEY`)
- LINE Bot 憑證 (`LINE_CHANNEL_SECRET`, `LINE_CHANNEL_ACCESS_TOKEN`)
- 其他服務配置

## 🔄 切換 Ollama 模型

如果要使用不同的 Ollama 模型：

1. 修改 `.env` 檔案中的 `OLLAMA_MODEL` 變數
2. 確保該模型已下載：
   ```bash
   docker run --rm -v ollama_data:/root/.ollama ollama/ollama pull <新模型名稱>
   ```
3. 重新啟動服務：
   ```bash
   docker-compose restart
   ```

## 📁 資料持久化

- Ollama 模型資料存儲在名為 `ollama_data` 的 Docker volume 中
- 專案檔案通過 volume 映射到容器內的 `/app` 目錄

## 🔍 疑難排解

如果遇到問題：

1. 確認所有容器都在運行：
   ```bash
   docker-compose ps
   ```

2. 檢查容器日誌：
   ```bash
   docker-compose logs -f
   ```

3. 重新建構並啟動服務：
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```
