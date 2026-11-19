# 🛠️ Installation Guide — Khokho Bl3 V3 Commercial

## Prerequisites
- Python 3.10+ (Recommended Python 3.11 or 3.12)
- Node.js 18+ and npm
- Redis server
- Lavalink v4+ (Optional for High-Fidelity Music)

## 1. Setup Bot Environment
`ash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
pip install -r web/backend/requirements.txt
`

## 2. Setup Web Frontend
`ash
cd web/frontend
npm install
npm run build
`

## 3. Configure .env
Copy .env.example to .env and fill in your Discord Bot Token, OAuth2 credentials, and Stripe secret keys.