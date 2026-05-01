@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title LyricAI Studio Launcher

echo ============================================
echo    LyricAI Studio - Application Launcher
echo ============================================
echo.

:: --- [1/3] Cleanup zombie processes ------------------------------------------
echo [1/3] Cleaning up existing processes...

:: kill by port 8888 (frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8888 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
:: kill by port 5678 (backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5678 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

:: kill by name (aggressive)
taskkill /F /IM python.exe /FI "WINDOWTITLE eq LyricAI_Frontend*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq LyricAI_Backend*" >nul 2>&1

echo [OK] Ports cleared.

:: --- [2/3] Check Dependencies and Start Backend ------------------------------
echo.
echo [2/3] Installing dependencies and starting backend...

cd /d "%~dp0"

:: Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        echo [*] .env not found. Creating from .env.example...
        copy .env.example .env >nul
    ) else (
        echo [!] Warning: .env and .env.example not found.
    )
)

echo [*] Checking requirements.txt...
pip install -qr requirements.txt
if errorlevel 1 (
    echo [!] Failed to install dependencies.
    pause
    exit /b 1
)

start "LyricAI_Backend" /min cmd /c "chcp 65001 >nul && uvicorn backend:app --host 0.0.0.0 --port 5678"

echo Waiting for Backend (3 sec)...
timeout /t 3 /nobreak >nul

:: --- [3/3] Starting Frontend -------------------------------------------------
echo.
echo [3/3] Starting Frontend (Python HTTP Server)...
start "LyricAI_Frontend" /min cmd /c "chcp 65001 >nul && python -m http.server 8888 --bind 127.0.0.1"

echo Waiting for Frontend (2 sec)...
timeout /t 2 /nobreak >nul

:: --- [Finished] Open browser -------------------------------------------------
echo Opening browser...
start "" "http://127.0.0.1:8080"

echo.
echo ============================================
echo    LyricAI Studio is running (Native Python)
echo.
echo    Editor:    http://127.0.0.1:8080
echo    Agent Pro: http://127.0.0.1:8080/agent.html
echo    Backend:   http://localhost:5678/docs
echo ============================================
pause
exit
