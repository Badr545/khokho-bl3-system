@echo off
title Khokho Bl3 V3 - Web Dashboard (Port 3000)
cd /d "%~dp0web\frontend"
node .\node_modules\next\dist\bin\next start --port 3000
pause