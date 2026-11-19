# cogs/i18n.py
import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from typing import Dict, Any

LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "locales")
TRANSLATIONS: Dict[str, Dict[str, Any]] = {}

def load_locales():
    global TRANSLATIONS
    for lang in ["en", "fr", "ar", "darija"]:
        path = os.path.join(LOCALES_DIR, f"{lang}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    TRANSLATIONS[lang] = json.load(f)
            except Exception:
                TRANSLATIONS[lang] = {}

load_locales()

def t(guild_id: int, key: str, default: str = "", **kwargs) -> str:
    from config_manager import get_guild_config
    conf = get_guild_config(guild_id)
    lang = conf.get("language", "darija")
    
    parts = key.split(".")
    val = TRANSLATIONS.get(lang, {})
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p)
        else:
            val = None
            break

    if not val:
        # Fallback to English
        val = TRANSLATIONS.get("en", {})
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                val = None
                break

    res = val or default or key
    try:
        return res.format(**kwargs) if kwargs else res
    except Exception:
        return res

class I18n(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="language", description="Changer la langue du bot pour ce serveur")
    @app_commands.describe(lang="Choisir la langue: en, fr, ar, ou darija")
    @app_commands.choices(lang=[
        app_commands.Choice(name="Darija (Moroccan Arabic)", value="darija"),
        app_commands.Choice(name="English (US)", value="en"),
        app_commands.Choice(name="Français (French)", value="fr"),
        app_commands.Choice(name="العربية (Arabic)", value="ar"),
    ])
    async def set_language(self, interaction: discord.Interaction, lang: app_commands.Choice[str]):
        if not interaction.guild:
            return await interaction.response.send_message("Commande utilisable uniquement sur un serveur.", ephemeral=True)
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("❌ Permission 'Gérer le serveur' requise.", ephemeral=True)

        from config_manager import set_guild_config
        conf = set_guild_config(interaction.guild.id, language=lang.value)
        msg = f"✅ La langue du serveur a été changée en **{lang.name}**."
        await interaction.response.send_message(msg)

async def setup(bot: commands.Bot):
    await bot.add_cog(I18n(bot))