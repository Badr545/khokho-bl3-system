# 🔧 Troubleshooting Guide

- **Error: Intents Missing**: Verify you enabled Message Content Intent and Server Members Intent in Discord portal.
- **Error: Lavalink Connection Refused**: Ensure Lavalink is running on port 2333 with password matching .env.
- **Error: Redis Connection Failed**: Bot falls back safely to in-memory mode when Redis is offline.