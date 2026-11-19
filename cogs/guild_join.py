# cogs/guild_join.py
# =====================================================================
# ─── GUILD JOIN — Auto role + Sync commands + Log l owner
# =====================================================================
import discord
from discord.ext import commands
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════
# ─── CONFIG (BEDDEL HADI!)
# ═══════════════════════════════════════════════════════════════════
import botconfig
BOT_OWNER_ID = botconfig.BOT_OWNER_ID
JOIN_LOG_CHANNEL_ID = botconfig.GUILD_JOIN_LOG_CHANNEL_ID
BOT_ADMIN_ROLE_NAME = "🤖 Bot Administrator"


class GuildJoin(commands.Cog):
    """Mnin bot ydkhol l server jdid → sayeb role + sync + log"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        print(f"\n🎉 Bot dakhel l server jdid: **{guild.name}** ({guild.id})")
        # ═══════════════════════════════════════════════════════════
        # ─── 0. Auto-Initialize Guild Configuration
        # ═══════════════════════════════════════════════════════════
        try:
            import config_manager
            is_new = config_manager.init_guild_if_missing(guild)
            if is_new:
                print(f"✅ Initialized default server configuration for {guild.name} ({guild.id})")
        except Exception as e:
            print(f"⚠️ Failed to init config for {guild.name}: {e}")

        # ═══════════════════════════════════════════════════════════
        # ─── 1. Sync slash commands
        # ═══════════════════════════════════════════════════════════
        synced_count = 0
        try:
            self.bot.tree.copy_global_to(guild=guild)
            synced = await self.bot.tree.sync(guild=guild)
            synced_count = len(synced)
            print(f"✅ Synced {synced_count} commands f {guild.name}")
        except Exception as e:
            print(f"❌ Sync error: {e}")

        # ═══════════════════════════════════════════════════════════
        # ─── 2. Sayeb Administrator role l rasso
        # ═══════════════════════════════════════════════════════════
        role_created = False
        role_error = None
        role = None

        try:
            # Jbed bot member
            bot_member = guild.get_member(self.bot.user.id)
            if bot_member is None:
                bot_member = await guild.fetch_member(self.bot.user.id)

            # Check Manage Roles permission
            if not bot_member.guild_permissions.manage_roles:
                role_error = "Ma 3ndich Manage Roles permission"
                print(f"⚠️ {role_error} f {guild.name}")
            else:
                # Check wach role deja kayn
                role = discord.utils.get(guild.roles, name=BOT_ADMIN_ROLE_NAME)

                if role is None:
                    # Sayeb role jdid
                    role = await guild.create_role(
                        name=BOT_ADMIN_ROLE_NAME,
                        permissions=discord.Permissions(administrator=True),
                        color=discord.Color.from_rgb(88, 101, 242),
                        reason="Bot auto-created Administrator role",
                        hoist=False,
                        mentionable=False,
                    )
                    print(f"✅ Created role '{BOT_ADMIN_ROLE_NAME}' f {guild.name}")

                # Assign role l bot
                try:
                    await bot_member.add_roles(role, reason="Auto-assign bot admin")
                    role_created = True
                    print(f"✅ Assigned role l bot f {guild.name}")
                except discord.Forbidden:
                    role_error = "Role dyal bot ta7t f hierarchy"
                    print(f"⚠️ {role_error} f {guild.name}")
                except Exception as e:
                    role_error = str(e)
                    print(f"❌ Assign error: {e}")

        except discord.Forbidden:
            role_error = "Ma 3ndich permission nsayeb role"
            print(f"⚠️ {role_error} f {guild.name}")
        except Exception as e:
            role_error = str(e)
            print(f"❌ Role error: {e}")

        # ═══════════════════════════════════════════════════════════
        # ─── 3. Log embed
        # ═══════════════════════════════════════════════════════════
        embed = discord.Embed(
            title="🎉 Bot Added to New Server",
            color=discord.Color.green() if role_created else discord.Color.orange(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="🏠 Server", value=f"{guild.name}\n`{guild.id}`", inline=True)
        embed.add_field(name="👥 Members", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="👑 Owner", value=f"<@{guild.owner_id}>\n`{guild.owner_id}`", inline=True)
        embed.add_field(name="📊 Channels", value=f"`{len(guild.channels)}`", inline=True)
        embed.add_field(name="🎭 Roles", value=f"`{len(guild.roles)}`", inline=True)
        embed.add_field(name="📅 Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="⚙️ Commands Synced", value=f"`{synced_count}`", inline=True)

        if role_created:
            embed.add_field(
                name="✅ Bot Role",
                value=f"Created + assigned `{BOT_ADMIN_ROLE_NAME}`",
                inline=False,
            )
        else:
            embed.add_field(
                name="⚠️ Bot Role",
                value=f"Failed: {role_error or 'Unknown'}",
                inline=False,
            )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_footer(
            text=f"Bot: {self.bot.user.name}",
            icon_url=self.bot.user.display_avatar.url if self.bot.user.display_avatar else None,
        )

        # ─── Send l log channel
        if JOIN_LOG_CHANNEL_ID:
            try:
                log_channel = self.bot.get_channel(JOIN_LOG_CHANNEL_ID)
                if log_channel is None:
                    log_channel = await self.bot.fetch_channel(JOIN_LOG_CHANNEL_ID)
                if log_channel:
                    await log_channel.send(embed=embed)
                    print(f"📨 Log sent l #{log_channel.name}")
            except Exception as e:
                print(f"❌ Log channel error: {e}")

        # ─── Send DM l owner
        if BOT_OWNER_ID:
            try:
                owner = await self.bot.fetch_user(BOT_OWNER_ID)
                if owner:
                    await owner.send(embed=embed)
                    print(f"📨 DM sent l owner")
            except discord.Forbidden:
                print("⚠️ Owner 3ndo DM msdoud")
            except Exception as e:
                print(f"❌ DM error: {e}")


async def setup(bot):
    await bot.add_cog(GuildJoin(bot))