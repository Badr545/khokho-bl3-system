# Website and bot deployment

## How the integration works

- The Next.js frontend calls the FastAPI backend.
- The backend uses Discord OAuth to authenticate dashboard users and verify their server permissions.
- The backend and bot use the same private Redis instance for bot actions.
- The bot and backend share the persistent `data` directory for SQLite databases and guild configuration.

The included `docker-compose.yml` runs all services on one private Docker network, shares the data directory, and does not publish Redis. This is the recommended setup for the project.

## Wispbyte Website hosting

The Wispbyte **Website/File Manager** shown in the control panel hosts static files such as `index.html`. Uploading the source `web` folder there will not run Next.js, FastAPI, Redis, or the Discord bot. The current dashboard requires a Node.js server for Next.js and a Python server for FastAPI.

Use Wispbyte Website hosting only if your plan provides a way to run those server applications too. Otherwise, keep the bot and API on a host that supports Python and Redis, and deploy the Next.js app on a Node.js-capable host. A static-only website cannot provide the complete dashboard integration.

## Discord and environment configuration

1. Copy `.env.example` to `.env`; keep `.env` private and never upload it to the Website File Manager or GitHub.
2. Set `DISCORD_TOKEN`, `DISCORD_CLIENT_ID`, and `DISCORD_CLIENT_SECRET` from your Discord application.
3. Generate a unique session secret, for example:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Put the result in `NEXTAUTH_SECRET`. Do not reuse the example value.

4. Set `DISCORD_REDIRECT_URI` to the website's full callback URL, ending in `/login/callback`, and add that exact URL under OAuth2 Redirects in the Discord Developer Portal.
5. Set `NEXT_PUBLIC_API_URL` to the public API URL ending in `/api/v1`. It is embedded in the frontend at build time; rebuild the frontend after changing it.
6. Set `CORS_ORIGINS` to the exact website origin (scheme and hostname, no path), for example `https://bot.example.com`.
7. For HTTPS production, set `AUTH_COOKIE_SECURE=true`. If the website and API use different subdomains under the same domain, you can set `AUTH_COOKIE_DOMAIN=.example.com`. Prefer same-site subdomains; third-party cookie restrictions can break logins across unrelated domains.

For a single Docker host with a reverse proxy, the frontend, backend, and bot should still use the private Compose network. Only expose the web services through HTTPS; do not make Redis public. The frontend build needs the public `NEXT_PUBLIC_API_URL`, while server-side frontend requests use the internal API service URL.

## Start with Docker Compose

After completing `.env` and OAuth redirect settings:

```powershell
docker compose up -d --build
```

Check `http://localhost:3000` for the site and `http://localhost:8000/api/v1/status` for the API status. Sign in with Discord, invite the bot to a server, and make sure the bot has the channel permissions needed by the dashboard actions.

If bot, API, and Redis are hosted on separate machines, they need to share a reachable Redis service and the same persistent database/configuration storage. Do not expose an unauthenticated Redis port to the public internet.
