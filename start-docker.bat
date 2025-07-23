@echo off
REM Windows 批處理腳本 - 啟動 Docker 服務

REM 切換到 docker 目錄並執行啟動腳本
cd /d "%~dp0\docker" && docker-start.bat
