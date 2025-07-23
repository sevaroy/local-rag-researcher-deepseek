#!/bin/bash

# 切換到腳本所在目錄
cd "$(dirname "$0")"

# 啟動所有 Docker 服務
echo "🐳 啟動 Docker Compose 服務..."

# 確保 Ollama 模型已下載
echo "📥 確保 Ollama 模型已下載..."
docker run --rm -v ollama_data:/root/.ollama ollama/ollama pull deepseek-r1:7b

# 啟動所有服務
echo "🚀 啟動所有服務..."
docker-compose up -d

echo "✅ 服務已啟動"
echo "📱 Streamlit Web 介面: http://localhost:8501"
echo "🤖 LINE Bot API: http://localhost:8000"
echo "🧠 Ollama API: http://localhost:11434"

echo ""
echo "📋 查看日誌:"
echo "  Streamlit: docker-compose logs -f streamlit"
echo "  LINE Bot: docker-compose logs -f linebot"
echo "  Ollama: docker-compose logs -f ollama"
echo ""
echo "🛑 停止服務: docker-compose down"
