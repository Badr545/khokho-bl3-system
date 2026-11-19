@echo off
title Khokho Bl3 V3 Commercial Suite - Manager
echo ===================================================
echo   Khokho Bl3 V3 - Commercial Suite Launcher
echo ===================================================
echo.
echo 1. Launch Discord Bot (app.py)
echo 2. Launch FastAPI Web Backend (Port 8000)
echo 3. Launch Next.js Frontend Dashboard (Port 3000)
echo 4. Launch ALL (Bot + Backend + Frontend in separate windows)
echo.
set /p opt="Choose an option (1-4): "

if "%opt%"=="1" (
    echo Starting Discord Bot...
    python app.py
    pause
)
if "%opt%"=="2" (
    echo Starting FastAPI Backend on http://localhost:8000...
    cd /d "%~dp0web\backend"
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    pause
)
if "%opt%"=="3" (
    echo Starting Next.js Dashboard on http://localhost:3000...
    cd /d "%~dp0web\frontend"
    node .\node_modules\next\dist\bin\next start --port 3000
    pause
)
if "%opt%"=="4" (
    echo Starting All Services in new windows...
    start "Khokho Bl3 Discord Bot" cmd /k "cd /d "%~dp0" && python app.py"
    start "Khokho Bl3 API Backend" cmd /k "cd /d "%~dp0web\backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    start "Khokho Bl3 Web Dashboard" cmd /k "cd /d "%~dp0web\frontend" && node .\node_modules\next\dist\bin\next start --port 3000"
    echo.
    echo [OK] All 3 services are launching in separate windows!
    echo - Website Dashboard: http://localhost:3000
    echo - REST API:          http://localhost:8000/api/v1/docs
    echo.
    pause
)