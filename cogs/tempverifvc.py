# cogs/tempverifvc.py
# =====================================================================
import discord
from discord.ext import commands
import asyncio

# ⚙️ CONFIG
TRIGGER_VC_NAME = "GET VERIFIED"

# 🆔 IDs dyal les roles
VERIF_ROLE_ID = 1556373741510860890
CM_ROLE_ID    = 1549788949663322142

STAFF_ROLE_IDS = [
    VERIF_ROLE_ID,
    CM_ROLE_ID,
]

class TempVerifyVC(commands.Cog):
    """System dyal VC m'wa9at bash l-member yt-verifa"""

    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        guild = member.guild

        # 1. MEMBER DAKHEL L-TRIGGER
        if after.channel is not None and after.channel.name == TRIGGER_VC_NAME:

            existing_vc = None
            for ch_id, owner_id in self.temp_channels.items():
                if owner_id == member.id:
                    existing_vc = guild.get_channel(ch_id)
                    break

            if existing_vc:
                try:
                    await member.move_to(existing_vc)
                except discord.Forbidden:
                    pass
                return

            category = after.channel.category
            if category is None:
                category = discord.utils.get(guild.categories, name="🔐")
                if category is None:
                    try:
                        category = await guild.create_category("🔐")
                    except discord.Forbidden:
                        print(f"❌ Bot ma 3ndouch permission bash y-creyi Category f {guild.name}")
                        return

            # ─── Permissions ───
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(
                    view_channel=True,
                    connect=True,
                    speak=True,
                    send_messages=True,
                    read_message_history=True,
                ),
            }

            # Remover les doublons
            unique_staff_roles = list(dict.fromkeys(STAFF_ROLE_IDS))

            for role_id in unique_staff_roles:
                role = guild.get_role(role_id)
                if role is not None:
                    overwrites[role] = discord.PermissionOverwrite(
                        view_channel=True,
                        connect=True,
                        speak=True,
                        send_messages=True,
                        read_message_history=True,
                    )

            try:
                new_vc = await guild.create_voice_channel(
                    name=f"🔐 | {member.display_name}",
                    category=category,
                    overwrites=overwrites,
                    reason=f"Verification VC l {member.name}",
                )
                self.temp_channels[new_vc.id] = member.id
                await member.move_to(new_vc)
                print(f"✅ Tsayeb VC l {member.name}")

                # ─── Embed message ───
                try:
                    embed = discord.Embed(
                        title="🔐 Verification Required",
                        description=(
                            f"Welcome {member.mention},\n\n"
                            f"You have been moved to a temporary verification room. "
                            f"Please wait patiently, a staff member will be with you shortly to complete your verification.\n\n"
                            f"**Please do not leave this channel until you are verified.**"
                        ),
                        color=discord.Color.blue(),
                    )
                    
                    # ❌ HNA 7YEDT L-FIELD DYAL "AUTHORIZED STAFF"
                    
                    embed.set_footer(
                        text="Verification System",
                        icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None,
                    )

                    # L-ping kayb9a f l-content bach l-staff yt-notifaw
                    mentions = f"{member.mention} " + " ".join(f"<@&{rid}>" for rid in unique_staff_roles)
                    await new_vc.send(content=mentions.strip(), embed=embed)

                except discord.Forbidden:
                    print(f"⚠️ Ma 9dertch nsift message f VC dyal {member.name} (Missing Permissions).")
                except Exception as e:
                    print(f"⚠️ Erreur f sift dyal message f VC: {e}")

            except Exception as e:
                print(f"❌ Erreur f creation dyal VC: {e}")

        # 2. CLEANUP
        if before.channel is not None and before.channel.id in self.temp_channels:
            await asyncio.sleep(1.5)
            vc = guild.get_channel(before.channel.id)

            if vc and len(vc.members) == 0:
                try:
                    await vc.delete(reason="Verification VC empty")
                    self.temp_channels.pop(before.channel.id, None)
                    print(f"🗑️ Msa7 VC khawi: {before.channel.name}")
                except discord.Forbidden:
                    pass


async def setup(bot):
    await bot.add_cog(TempVerifyVC(bot))
