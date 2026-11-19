@echo off
title Khokho Bl3 V3 - REST API (Port 8000)
cd /d "%~dp0web\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause