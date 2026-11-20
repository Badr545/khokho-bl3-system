# 🤖 Khokho Bl3 V3 — Commercial SaaS Edition

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![discord.py](https://img.shields.io/badge/discord.py-2.4+-5865F2?style=for-the-badge&logo=discord)
![Next.js](https://img.shields.io/badge/Next.js-14_App_Router-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)
![SQLite WAL](https://img.shields.io/badge/SQLite-WAL_Engine-003B57?style=for-the-badge&logo=sqlite)
![Redis](https://img.shields.io/badge/Redis-Pub%2FSub_Sync-DC382D?style=for-the-badge&logo=redis)
![License](https://img.shields.io/badge/License-Commercial-green?style=for-the-badge)

**The Enterprise-Grade Discord Bot & Web Dashboard Suite.**
*Built to directly outcompete MEE6, Dyno, Carl-bot, and ProBot in performance, features, and commercial monetization.*

[🌐 Live Demo](#) • [📖 Documentation](docs/INSTALLATION.md) • [💎 Pricing Plans](docs/PREMIUM.md) • [🚀 Deploy](docs/WEB_DEPLOYMENT.md)

</div>

---

## ⚡ What is Khokho Bl3 V3?
**Khokho Bl3 V3** is a production-hardened Discord bot and web platform featuring **69+ modules** and **170+ commands**. Designed for commercial SaaS deployments, white-label agencies, and server networks, it delivers:
- **Web Dashboard**: High-performance Next.js 14 App Router console with Discord OAuth2.
- **REST API & Microservices**: FastAPI backend with JWT security, Rate Limiting, and CORS.
- **Real-Time Bot Bridge**: Redis Pub/Sub synchronizing web changes to Discord within milliseconds.
- **Zero-Corruption Dual Database**: Bot state in data/bot.db and commercial features in data/features.db (both SQLite WAL mode).
- **Turnkey Monetization**: Integrated Stripe Checkout, recurring subscriptions, and offline cryptographic license key generator (KHOKHO-XXXX-XXXX-XXXX).

---

## 💎 Tier Comparison

| Feature | Free Tier | Basic SaaS (/mo) | Pro SaaS (/mo) | Ultra / White-Label (/mo) |
|---|:---:|:---:|:---:|:---:|
| **Core Modules (51 Cogs)** | ✅ | ✅ | ✅ | ✅ |
| **Tickets & HTML Transcripts**| 1 Active | Unlimited | Unlimited | Unlimited |
| **Concurrent Giveaways** | 1 | 5 | Unlimited | Unlimited |
| **Custom Commands** | 3 | 10 | 50 | Unlimited |
| **Economy Daily Commands** | 100 / day | 500 / day | Unlimited | Unlimited |
| **Music Audio Filters (8D/Bass)**| ❌ | ❌ | ✅ | ✅ |
| **REST API Developer Access**| ❌ | ❌ | ✅ | ✅ |
| **No Bot Branding** | ❌ | ✅ | ✅ | ✅ |
| **Custom Bot Name & Avatar** | ❌ | ❌ | ❌ | ✅ |
| **Custom Dashboard Domain** | ❌ | ❌ | ❌ | ✅ |
| **24/7 Dedicated Voice Room** | ❌ | ❌ | ❌ | ✅ |

---

## 📦 Architecture Overview

`	ext
khokho_bl3_V3/
├── app.py                      # Main Discord gateway entry point
├── botconfig.py                # Environment & permissions loader
├── config_manager.py           # Per-server guild isolation engine
├── data_manager.py             # SQLite ORM & cache layer
│
├── web/
│   ├── backend/                # FastAPI REST API (JWT + Discord OAuth2)
│   │   ├── app/ (routers, models, schemas, auth, bot_bridge)
│   │   ├── requirements.txt & Dockerfile
│   └── frontend/               # Next.js 14 App Router + TailwindCSS
│       ├── app/ (landing, status, login, dashboard, servers, premium)
│       ├── package.json & Dockerfile
│
├── database/                   # Database engine & migrations
│   ├── engine.py & schema.py   # bot.db engine (WAL mode)
│   └── features_schema.py      # features.db (separate SQLite engine)
│
├── cogs/                       # 69+ Modular Bot Cogs
│   ├── Core: admin, economy, gambling (19 games), levels, voice...
│   ├── Commercial: web_bridge, premium, premium_sync, i18n
│   ├── Community: modmail, suggestions, applications, starboard, counting...
│   └── Security & Audio: antinuke, ai_automod, music, social_notif
│
├── docs/                       # Complete production documentation (7 guides)
├── scripts/generate_keys.py    # Commercial CLI license key generator
├── docker-compose.yml          # Production container orchestration
└── pterodactyl/                # Game panel / VPS one-click egg
`

---

## 🚀 Quick Start (Docker)

1. Copy `.env.example` to `.env` and configure the Discord bot token, OAuth client credentials, redirect URL, and a unique `NEXTAUTH_SECRET`. See [Discord setup](docs/DISCORD_SETUP.md) and [web deployment](docs/WEB_DEPLOYMENT.md).
2. Start the entire cluster:

   ```powershell
   docker compose up -d --build
   ```

3. Access services:
   - **Web Dashboard**: http://localhost:3000
   - **REST API Docs**: http://localhost:8000/api/v1/docs
   - **Status Page**: http://localhost:3000/status

---

## 🔑 Generating Commercial Licenses
Sell subscriptions or white-label instances without Stripe:
`ash
python scripts/generate_keys.py --tier pro --days 30 --count 3
`
Output:
`	ext
  🎟️ KHOKHO-7A4B-8E21-CC09 [PRO - 30 Days]
  🎟️ KHOKHO-12FD-59A0-BB14 [PRO - 30 Days]
`
Users redeem keys inside Discord using /premium activate <KEY> or directly from the Web Dashboard.

---

## 📄 License
This software is provided under a **Commercial SaaS & Distribution License**. See [LICENSE.md](LICENSE.md) for full terms and conditions.