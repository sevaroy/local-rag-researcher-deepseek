# PowerShell 腳本 - 在 Windows 環境下啟動 Docker 服務

# 切換到腳本所在目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptPath

# 顯示歡迎訊息
Write-Host "🐳 啟動 Docker Compose 服務..." -ForegroundColor Cyan

# 確保 Ollama 模型已下載
Write-Host "📥 確保 Ollama 模型已下載..." -ForegroundColor Yellow
docker run --rm -v ollama_data:/root/.ollama ollama/ollama pull deepseek-r1:7b

# 啟動所有服務
Write-Host "🚀 啟動所有服務..." -ForegroundColor Green
docker-compose up -d

# 顯示服務資訊
Write-Host "`n✅ 服務已啟動" -ForegroundColor Green
Write-Host "📱 Streamlit Web 介面: http://localhost:8501" -ForegroundColor Magenta
Write-Host "🤖 LINE Bot API: http://localhost:8000" -ForegroundColor Magenta
Write-Host "🧠 Ollama API: http://localhost:11434" -ForegroundColor Magenta

Write-Host "`n📋 查看日誌:" -ForegroundColor Yellow
Write-Host "  Streamlit: docker-compose logs -f streamlit" -ForegroundColor Gray
Write-Host "  LINE Bot: docker-compose logs -f linebot" -ForegroundColor Gray
Write-Host "  Ollama: docker-compose logs -f ollama" -ForegroundColor Gray

Write-Host "`n🛑 停止服務: docker-compose down" -ForegroundColor Red

# 等待用戶按任意鍵繼續
Write-Host "`n按任意鍵繼續..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
