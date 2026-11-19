# cogs/modmail.py
import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from datetime import datetime
from cogs.premium import is_premium, premium_required

MODMAIL_FILE = "data/modmail.json"

class Modmail(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._ensure()

    def _ensure(self):
        if not os.path.exists(MODMAIL_FILE):
            with open(MODMAIL_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self):
        try:
            with open(MODMAIL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, data):
        with open(MODMAIL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    modmail_group = app_commands.Group(name="modmail", description="Système de support privé Modmail")

    @modmail_group.command(name="setup", description="Configurer la catégorie pour les tickets Modmail")
    @app_commands.describe(category="La catégorie où les canaux modmail seront créés")
    async def setup_modmail(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("❌ Permission 'Gérer le serveur' requise.", ephemeral=True)

        data = self._load()
        data[str(interaction.guild_id)] = {"category_id": category.id}
        self._save(data)
        await interaction.response.send_message(f"✅ Catégorie Modmail configurée sur: **{category.name}**")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        # If user DMs the bot
        if isinstance(message.channel, discord.DMChannel):
            data = self._load()
            if not data:
                return
            # Find the primary guild or first configured
            guild_id_str = list(data.keys())[0]
            conf = data.get(guild_id_str, {})
            cat_id = conf.get("category_id")
            if not cat_id:
                return

            guild = self.bot.get_guild(int(guild_id_str))
            if not guild:
                return

            # Check if thread channel already exists
            ch_name = f"modmail-{message.author.id}"
            existing = discord.utils.get(guild.text_channels, name=ch_name)
            if not existing:
                cat = guild.get_channel(cat_id)
                if not cat or not isinstance(cat, discord.CategoryChannel):
                    return
                existing = await guild.create_text_channel(
                    name=ch_name,
                    category=cat,
                    topic=f"Modmail Thread pour {message.author} ({message.author.id})"
                )
                init_embed = discord.Embed(
                    title="📬 Nouveau Ticket Modmail",
                    description=f"**Utilisateur:** {message.author.mention} ({message.author.id})\nRépondez avec +reply <message>",
                    color=discord.Color.blue()
                )
                await existing.send(embed=init_embed)
                await message.channel.send("✅ Votre message a été transmis à l'équipe du staff.")

            # Forward message
            embed = discord.Embed(description=message.content, color=discord.Color.light_grey())
            embed.set_author(name=f"{message.author}", icon_url=message.author.display_avatar.url)
            await existing.send(embed=embed)

    @commands.command(name="reply")
    @commands.has_permissions(manage_messages=True)
    async def reply_modmail(self, ctx: commands.Context, *, response: str):
        """Répondre à un ticket modmail depuis son canal dédié"""
        if not ctx.channel.name.startswith("modmail-"):
            return await ctx.send("❌ Cette commande ne peut être utilisée que dans un canal Modmail.")
        user_id_str = ctx.channel.name.split("-")[1]
        try:
            target_user = await self.bot.fetch_user(int(user_id_str))
            embed = discord.Embed(
                title=f"🛡️ Réponse du Staff ({ctx.guild.name})",
                description=response,
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Répondu par {ctx.author.display_name}")
            await target_user.send(embed=embed)
            await ctx.send(f"✅ Réponse transmise avec succès à {target_user.mention}.")
        except Exception as e:
            await ctx.send(f"❌ Impossible d'envoyer le message: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Modmail(bot))