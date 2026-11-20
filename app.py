import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext.commands.view import StringView
from utils.context import EmbedContext
from config_manager import get_guild_config
load_dotenv()

# ═══════════════════════════════════════════════════════════════════
# ─── INTENTS
# ═══════════════════════════════════════════════════════════════════
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.presences = True


async def get_prefix(bot, message):
    prefix = get_guild_config(message.guild)["prefix"] if message.guild else "&"
    return commands.when_mentioned_or(prefix, "+", "-")(bot, message)


# ═══════════════════════════════════════════════════════════════════
# ─── BOT
# ═══════════════════════════════════════════════════════════════════
bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None,
    context_class=EmbedContext,
)

# ═══════════════════════════════════════════════════════════════════
# ─── PREFIX RULES
# ═══════════════════════════════════════════════════════════════════
ADMIN_PREFIX_COMMANDS = {
    "kick", "ban", "unban", "warn", "warnings", "clearwarns",
    "slowmode", "lock", "unlock", "ms7", "clear", "purge",
    "giverole", "removerole", "massrole","striprole", "addrole", "delrole",
    "jail", "rta7", "unjail", "timeout", "untimeout", "mute", "unmute",
    "case", "cases", "warns", "history",
    "announce", "embed", "say", "echo",
    "cm",
    "botjoin", "botleave", "voice247",
    "addmod", "removemod", "listroles", "checkperm",
    "setgame", "delgame", "listgames",
    "setserver", "fixroles", "setcolors", "setperms",
    "temprole","verify", "vform", "vb", "vg", "vcheck", "vinfo", "vlist", "unverify", "unvb",
    "move", "aji",
    # 👇 Clan Manager Commands
    "createclan", "deleteclan", "resetpoints", "renameclan", "updaterole", 
    "giveclan", "forceaddmember", "clearcoleaders", "clan-of-the-week", "update-limits",
    "removeclan-of-the-week", "removecotw", "delcotw","serverstats", "ss", "stats","allcmds",
    "duproles", "finddups", "rolesdup", "cleandroles", "removedups", "dupdell", "rolesinfo", "rhier", "setup",
    "activity", "stats_user", "activity_top", "atop", "topactive",
}

# 👇 Zidna myperms hna
DUAL_PREFIX_COMMANDS = {"help", "cmds", "myperms"} 

# ─── COGS ───
COGS = [
    "cogs.basic", "cogs.admin", "cogs.announcements", "cogs.roles",
    "cogs.help", "cogs.roleconfig", "cogs.channelmanager",
    "cogs.economy", "cogs.shop", "cogs.bir",
    "cogs.gambling", "cogs.games", "cogs.gamerequests",
    "cogs.levels", "cogs.rankcard", "cogs.leaderboard",
    "cogs.info", "cogs.utility", "cogs.logs",# "cogs.stats",
    "cogs.welcome", "cogs.voice", "cogs.tempvoice", "cogs.temproles",
    "cogs.automod", "cogs.antiraid", "cogs.tickets", "cogs.tempban", "cogs.transcripts",
    "cogs.giveaway", "cogs.reactionroles", "cogs.selfroles", "cogs.social", "cogs.scheduled",
    "cogs.embedbuilder", "cogs.auto_responses", "cogs.backup_restore",
    "cogs.tournaments", "cogs.heist", "cogs.server_setup", "cogs.moderation_cases", "cogs.status_rotation",
    "cogs.verification", "cogs.tempverifvc", "cogs.clans", "cogs.serverstats","cogs.permsmanager", 
    "cogs.sysinfo", "cogs.guild_join", "cogs.activity", "cogs.adventure", "cogs.setup",
    # ─── COMMERCIAL SUITE & EXTENSION COGS ───
    "cogs.web_bridge", "cogs.premium", "cogs.premium_sync",
    "cogs.modmail", "cogs.suggestions", "cogs.applications", "cogs.antinuke",
    "cogs.starboard", "cogs.birthday", "cogs.afk", "cogs.counting",
    "cogs.autopublish", "cogs.sticky", "cogs.bump", "cogs.ai_automod",
    "cogs.custom_commands", "cogs.context_menus", "cogs.cloud_backup", "cogs.i18n",
    "cogs.music", "cogs.social_notif",
]

# ═══════════════════════════════════════════════════════════════════
# ─── GLOBAL PREFIX CHECK
# ═══════════════════════════════════════════════════════════════════
@bot.check
async def global_prefix_check(ctx: commands.Context) -> bool:
    if ctx.command is None or ctx.guild is None: return True
    root = ctx.command.root_parent if ctx.command.root_parent else ctx.command
    cmd_name = root.name.lower()

    if cmd_name in DUAL_PREFIX_COMMANDS: return True

    is_admin = cmd_name in ADMIN_PREFIX_COMMANDS

    if is_admin and ctx.prefix not in ("+", "-"):
        raise commands.CheckFailure(f"__WRONG_PREFIX_ADMIN__{cmd_name}")
    if (not is_admin) and ctx.prefix in ("+", "-"):
        raise commands.CheckFailure(f"__WRONG_PREFIX_PUBLIC__{cmd_name}")

    return True

# ═══════════════════════════════════════════════════════════════════
# ─── SETUP HOOK
# ═══════════════════════════════════════════════════════════════════
@bot.event
async def setup_hook():
    print("🔧 Setup hook — kanloadi cogs...")
    loaded, failed = set(), []
    for cog in COGS:
        if cog in loaded: continue
        try:
            await bot.load_extension(cog)
            loaded.add(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            failed.append(cog)
            print(f"❌ Failed {cog}: {e}")

    if failed: print(f"⚠️ Failed: {', '.join(failed)}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# ═══════════════════════════════════════════════════════════════════
# ─── READY
# ═══════════════════════════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"\n🔥 Ready: {bot.user} ({bot.user.id})")
    print(f"🏠 Guilds: {len(bot.guilds)}\n")

    import botconfig
    for guild in bot.guilds:
        for rid in botconfig.ADMIN_ROLES + botconfig.MODERATOR_ROLES + \
                   botconfig.HELPER_ROLES + botconfig.STAFF_ROLES:
            if isinstance(rid, int):
                role = guild.get_role(rid)
                if role:
                    botconfig.ROLE_NAME_TO_ID[role.name] = rid
    print(f"🗺️ ROLE_NAME_TO_ID: {len(botconfig.ROLE_NAME_TO_ID)} entries")

# ═══════════════════════════════════════════════════════════════════
# ─── NO PREFIX LISTENER (Kay9bel Arguments / Mentions)
# ═══════════════════════════════════════════════════════════════════
@bot.listen("on_message")
async def no_prefix_listener(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    content = message.content.strip()
    if not content:
        return

    parts = content.split(maxsplit=1)
    cmd_word = parts[0].lower()
    args_str = parts[1] if len(parts) > 1 else ""

    target_cmd = None
    if cmd_word in ("u", "ra"):
        target_cmd = bot.get_command("userinfo")
    elif cmd_word in ("r", "rcard"):
        target_cmd = bot.get_command("rcard")
    elif cmd_word == "a":
        target_cmd = bot.get_command("avatar")
    elif cmd_word == "b":
        target_cmd = bot.get_command("banner")

    if target_cmd:
        ctx = await bot.get_context(message)
        ctx.command = target_cmd
        ctx.view = StringView(args_str)
        try:
            await bot.invoke(ctx)
        except Exception as e:
            print(f"❌ Error no-prefix {cmd_word}: {e}")

# ═══════════════════════════════════════════════════════════════════
# ─── PREFIX ERRORS
# ═══════════════════════════════════════════════════════════════════
@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound): return

    if isinstance(error, commands.CheckFailure):
        err_str = str(error)
        if err_str.startswith("__WRONG_PREFIX_ADMIN__"):
            try: await ctx.send("❌ Had command khedma ghir b prefix `+`!", delete_after=8)
            except Exception: pass
            return 
        if err_str.startswith("__WRONG_PREFIX_PUBLIC__"):
            try: await ctx.send("❌ Had command khedma ghir b prefix `&`!", delete_after=8)
            except Exception: pass
            return 
        
        try: await ctx.send(err_str, delete_after=8)
        except Exception: pass
        return 

    if isinstance(error, commands.MissingPermissions):
        try: await ctx.send("❌ Ma 3ndkch les permissions dyal Discord l had command!", delete_after=8)
        except Exception: pass
        return 

    if isinstance(error, commands.MissingRequiredArgument):
        try:
            await ctx.send(f"⚠️ {ctx.author.mention} — Khass: `{error.param.name}`", delete_after=8)
            await ctx.message.delete(delay=8)
        except Exception: pass
        return

    if isinstance(error, commands.CommandOnCooldown):
        try: await ctx.send(f"⏰ 3awed mn ba3d `{error.retry_after:.1f}s`!", delete_after=5)
        except Exception: pass
        return

    if isinstance(error, commands.CommandInvokeError):
        print(f"❌ Invoke error [{ctx.command}]: {error.original}")
        try: await ctx.send(f"❌ {ctx.author.mention} — Chi haja ghalt f command.", delete_after=8)
        except Exception: pass
        return

    print(f"❌ Command error [{ctx.command}]: {error}")

# ═══════════════════════════════════════════════════════════════════
# ─── SLASH ERRORS
# ═══════════════════════════════════════════════════════════════════
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        msg = "🚫 **You don't have permission to use this command!**"
        try:
            if interaction.response.is_done(): await interaction.followup.send(msg, ephemeral=True)
            else: await interaction.response.send_message(msg, ephemeral=True)
        except Exception: pass
        return
    print(f"❌ Slash error [{interaction.command}]: {error}")

# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════
# ─── DASHBOARD SLASH COMMAND
# ═══════════════════════════════════════════════════════════════════
@bot.tree.command(name="dashboard", description="Recevez le lien d'accès direct au Web Dashboard")
async def dashboard_slash_cmd(interaction: discord.Interaction):
    dash_url = os.getenv("NEXTAUTH_URL", "http://localhost:3000/dashboard/servers")
    embed = discord.Embed(
        title="🌐 Khokho Bl3 V3 — Web Dashboard",
        description=f"Gérez votre serveur en temps réel via notre console web:\n[**Accéder au Dashboard**]({dash_url})",
        color=discord.Color.from_rgb(88, 101, 242)
    )
    embed.add_field(name="🔑 Connexion", value="Connectez-vous avec votre compte Discord", inline=True)
    embed.add_field(name="⚙️ Permissions", value="Gérer le serveur requis", inline=True)
    embed.set_footer(text="Khokho Bl3 V3 SaaS Edition")
    
    try:
        await interaction.user.send(embed=embed)
        await interaction.response.send_message("📬 Le lien du dashboard vous a été envoyé en message privé !", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ─── MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN ma kaynch f .env!")
        sys.exit(1)
    bot.run(token)
