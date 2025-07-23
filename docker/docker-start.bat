@echo off
REM Windows 批處理腳本 - 啟動 Docker 服務

REM 切換到腳本所在目錄
cd /d "%~dp0"

echo [36m🐳 啟動 Docker Compose 服務...[0m

REM 確保 Ollama 模型已下載
echo [33m📥 確保 Ollama 模型已下載...[0m
docker run --rm -v ollama_data:/root/.ollama ollama/ollama pull deepseek-r1:7b

REM 啟動所有服務
echo [32m🚀 啟動所有服務...[0m
docker-compose up -d

REM 顯示服務資訊
echo.
echo [32m✅ 服務已啟動[0m
echo [35m📱 Streamlit Web 介面: http://localhost:8501[0m
echo [35m🤖 LINE Bot API: http://localhost:8000[0m
echo [35m🧠 Ollama API: http://localhost:11434[0m

echo.
echo [33m📋 查看日誌:[0m
echo   Streamlit: docker-compose logs -f streamlit
echo   LINE Bot: docker-compose logs -f linebot
echo   Ollama: docker-compose logs -f ollama

echo.
echo [31m🛑 停止服務: docker-compose down[0m

REM 等待用戶按任意鍵繼續
echo.
pause
