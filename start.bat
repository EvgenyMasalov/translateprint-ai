@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title LyricAI Studio Launcher

echo ============================================
echo    LyricAI Studio - Application Launcher
echo ============================================
echo.

:: --- [0/3] Cleanup zombie processes ------------------------------------------
echo [0/3] Cleaning up existing processes on port 8080...

:: kill by port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

:: kill by name (aggressive)
taskkill /F /IM python.exe /FI "WINDOWTITLE eq LyricAI_Frontend*" >nul 2>&1

echo [OK] Port 8080 cleared.

:: --- [1/3] Check Docker and start n8n ----------------------------------------
echo.
echo [1/3] Checking Docker and n8n...

docker info >nul 2>&1
if errorlevel 1 (
    echo [!] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

docker start n8n >nul 2>&1
if errorlevel 1 (
    echo [!] n8n container not found.
    echo [!] Please create it first: docker run -d --name n8n -p 5678:5678 n8nio/n8n
    pause
    exit /b 1
)

:: Wait for n8n to be ready
echo Waiting for n8n to be ready...
set /a attempts=0
:WAIT_N8N
set /a attempts+=1
if %attempts% GTR 30 (
    echo [!] n8n timeout. Continuing anyway...
    goto START_FRONTEND
)
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://localhost:5678/' -UseBasicParsing).StatusCode -eq 200 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto WAIT_N8N
)
echo [OK] n8n is ready!

:: --- [2/3] Starting Frontend -------------------------------------------------
:START_FRONTEND
echo.
echo [2/3] Starting Frontend (Python HTTP Server)...
cd /d "%~dp0"
start "LyricAI_Frontend" /min cmd /c "chcp 65001 >nul && python -m http.server 8080 --bind 127.0.0.1"

echo Waiting for Frontend (3 sec)...
timeout /t 3 /nobreak >nul

:: --- [3/3] Open browser ------------------------------------------------------
echo [3/3] Opening browser...
start "" "http://127.0.0.1:8080/editor.html"

echo.
echo ============================================
echo    LyricAI Studio is running!
echo.
echo    Editor:    http://127.0.0.1:8080/editor.html
echo    Agent Pro: http://127.0.0.1:8080/agent_pro.html
echo    n8n:       http://localhost:5678
echo ============================================
pause
exit
