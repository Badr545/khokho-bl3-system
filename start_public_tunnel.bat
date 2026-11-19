@echo off
title Khokho Bl3 V3 - Cloudflare Public HTTPS Tunnel
echo ========================================================
echo   Khokho Bl3 V3 - Free Global HTTPS Tunnel (Cloudflare)
echo ========================================================
echo.
echo Launching public tunnel for http://localhost:3000...
echo Anyone in the world with the link will be able to access your site!
echo.
cloudflared.exe tunnel --url http://localhost:3000
pause