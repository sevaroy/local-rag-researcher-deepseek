# PowerShell 腳本 - 啟動 Docker 服務

# 切換到 docker 目錄並執行啟動腳本
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path "$scriptPath\docker"
& .\docker-start.ps1
