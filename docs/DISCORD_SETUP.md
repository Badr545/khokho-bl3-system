# 🤖 Discord Developer Portal Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications).
2. Create New Application -> Name it "Khokho Bl3" (or your custom brand).
3. Under **Bot**:
   - Enable **Privileged Gateway Intents**:
     - Presence Intent: ON
     - Server Members Intent: ON
     - Message Content Intent: ON
   - Reset Token -> Paste into DISCORD_TOKEN in .env.
4. Under **OAuth2**:
   - Copy Client ID -> DISCORD_CLIENT_ID
   - Copy Client Secret -> DISCORD_CLIENT_SECRET
   - Add Redirect URI: http://localhost:3000/api/auth/callback/discord
"@, [System.Text.Encoding]::UTF8)

# 3. DEPLOYMENT.md
[System.IO.File]::WriteAllText("C:\Users\pc\Downloads\khokho bl3 V3\docs\DEPLOYMENT.md", @"
# 🚀 Deployment Guide (Docker & Production)

## One-Click Docker Compose
Deploy bot, web backend, frontend, Redis, and Lavalink simultaneously:
`ash
docker-compose up -d --build
`

## Manual Systemd Services (Ubuntu/Debian)
`ini
[Unit]
Description=Khokho Bl3 V3 Discord Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/khokho-bl3
ExecStart=/var/www/khokho-bl3/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
`
"@, [System.Text.Encoding]::UTF8)

# 4. CUSTOMIZATION.md
[System.IO.File]::WriteAllText("C:\Users\pc\Downloads\khokho bl3 V3\docs\CUSTOMIZATION.md", @"
# 🎨 White-Label & Customization Guide

## Rebranding the Bot
1. Update otconfig.py:
   - BOT_NAME = "YourBotName"
   - BOT_COLOR = 0x5865F2
   - BOT_FOOTER = "Powered by Your Brand"
2. Replace assets:
   - ssets/logo.png (Avatar)
   - ssets/banner.png (Dashboard Banner)
3. Update web/frontend/tailwind.config.js to customize dashboard color themes.