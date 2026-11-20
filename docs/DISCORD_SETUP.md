# Discord application setup

1. Create or select the bot application in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Under **Bot**, copy the bot token to `DISCORD_TOKEN`. Enable the privileged gateway intents the bot uses: Server Members, Message Content, and Presence.
3. Under **OAuth2**, copy the application ID to `DISCORD_CLIENT_ID` and the client secret to `DISCORD_CLIENT_SECRET`.
4. Add the exact value of `DISCORD_REDIRECT_URI` to the application's OAuth2 redirect URLs. For local development, use:

   `http://localhost:3000/login/callback`

5. On the dashboard login page, users authorize the `identify` and `guilds` scopes. The bot must also be invited to each Discord server the dashboard should manage.

Never put the bot token, OAuth client secret, or `NEXTAUTH_SECRET` in frontend code or public website files.
