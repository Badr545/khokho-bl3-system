# =====================================================================
# ─── ANNOUNCEMENTS — Premium Edition (All Raw Text + Forms)
# =====================================================================
import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import require_any_role, require_any_role_prefix
from botconfig import HELPER_ROLES, MODERATOR_ROLES, ADMIN_ROLES


ANNOUNCER_ROLES = HELPER_ROLES + MODERATOR_ROLES + ADMIN_ROLES


# ═══════════════════════════════════════════════════════════════════
# ─── MODALS (FORMS) - All Text with Titles & Categories
# ═══════════════════════════════════════════════════════════════════

class EventModal(discord.ui.Modal, title="🎉 Event Text Announcement"):
    ev_title = discord.ui.TextInput(
        label="Event Title", 
        placeholder="e.g., EPIC GIVEAWAY", 
        max_length=100
    )
    ev_time = discord.ui.TextInput(
        label="Event Time (Optional)", 
        placeholder="e.g., TODAY, 22:00", 
        required=False, 
        max_length=50
    )
    msg = discord.ui.TextInput(
        label="Message (Supports # and ||)", 
        style=discord.TextStyle.paragraph, 
        placeholder="Hna katkteb l-Event dyalek...", 
        max_length=4000
    )
    image_url = discord.ui.TextInput(
        label="Image URL (Optional)", 
        placeholder="e.g., https://i.pinimg.com/...", 
        required=False, 
        max_length=300
    )
    channel_id = discord.ui.TextInput(
        label="Channel ID (Optional)", 
        placeholder="e.g., 123456789", 
        required=False, 
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        target_channel = interaction.channel
        if self.channel_id.value:
            try:
                ch_id = int(self.channel_id.value.replace("<#", "").replace(">", ""))
                target_channel = interaction.guild.get_channel(ch_id) or interaction.channel
            except: pass

        # تنسيق النص الخام (Raw Text)
        content = f"# 🎉 {self.ev_title.value.upper()}\n\n"
        if self.ev_time.value:
            content += f"⏰ **Time:** {self.ev_time.value}\n\n"
            
        content += self.msg.value
        
        if self.image_url.value:
            content += f"\n{self.image_url.value}"

        await target_channel.send(content=content)
        await interaction.response.send_message(f"✅ Event sifted f {target_channel.mention}!", ephemeral=True)


class MeetingModal(discord.ui.Modal, title="📅 Meeting Text Announcement"):
    mt_title = discord.ui.TextInput(
        label="Meeting Title", 
        placeholder="e.g., STAFF MEETING", 
        max_length=100
    )
    mt_location = discord.ui.TextInput(
        label="Location (Optional)", 
        placeholder="e.g., VC GENERAL", 
        required=False, 
        max_length=100
    )
    msg = discord.ui.TextInput(
        label="Message / Agenda (Supports # and ||)", 
        style=discord.TextStyle.paragraph, 
        placeholder="Hna katkteb l-Meeting dyalek...", 
        max_length=4000
    )
    image_url = discord.ui.TextInput(
        label="Image URL (Optional)", 
        placeholder="e.g., https://i.pinimg.com/...", 
        required=False, 
        max_length=300
    )
    channel_id = discord.ui.TextInput(
        label="Channel ID (Optional)", 
        placeholder="e.g., 123456789", 
        required=False, 
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        target_channel = interaction.channel
        if self.channel_id.value:
            try:
                ch_id = int(self.channel_id.value.replace("<#", "").replace(">", ""))
                target_channel = interaction.guild.get_channel(ch_id) or interaction.channel
            except: pass

        # تنسيق النص الخام (Raw Text)
        content = f"# 📅 {self.mt_title.value.upper()}\n\n"
        if self.mt_location.value:
            content += f"📍 **Location:** {self.mt_location.value}\n\n"
            
        content += self.msg.value
        
        if self.image_url.value:
            content += f"\n{self.image_url.value}"

        await target_channel.send(content=content)
        await interaction.response.send_message(f"✅ Meeting sifted f {target_channel.mention}!", ephemeral=True)


class NewsModal(discord.ui.Modal, title="📰 News Text Announcement"):
    nw_title = discord.ui.TextInput(
        label="News Title", 
        placeholder="e.g., CLAN OF THE WEEK", 
        max_length=100
    )
    nw_category = discord.ui.TextInput(
        label="Category", 
        placeholder="e.g., Clan System Update", 
        required=False, 
        max_length=50
    )
    msg = discord.ui.TextInput(
        label="Message (Supports # and ||)", 
        style=discord.TextStyle.paragraph, 
        placeholder="Hna katkteb l-News dyalek...", 
        max_length=4000
    )
    image_url = discord.ui.TextInput(
        label="Image URL (Optional)", 
        placeholder="e.g., https://i.pinimg.com/...", 
        required=False, 
        max_length=300
    )
    channel_id = discord.ui.TextInput(
        label="Channel ID (Optional)", 
        placeholder="e.g., 123456789", 
        required=False, 
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        target_channel = interaction.channel
        if self.channel_id.value:
            try:
                ch_id = int(self.channel_id.value.replace("<#", "").replace(">", ""))
                target_channel = interaction.guild.get_channel(ch_id) or interaction.channel
            except: pass

        # تنسيق النص الخام (Raw Text)
        content = f"# 📰 {self.nw_title.value.upper()}\n\n"
        if self.nw_category.value:
            content += f"🏷️ **Category:** {self.nw_category.value}\n\n"
            
        content += self.msg.value
        
        if self.image_url.value:
            content += f"\n{self.image_url.value}"

        await target_channel.send(content=content)
        await interaction.response.send_message(f"✅ News sifted f {target_channel.mention}!", ephemeral=True)


# ═══════════════════════════════════════════════════════════════════
# ─── VIEWS (BUTTONS)
# ═══════════════════════════════════════════════════════════════════
class AnnouncementView(discord.ui.View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=180)
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Had l-menu machi dyalek!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🎉 Event", style=discord.ButtonStyle.primary)
    async def btn_event(self, it: discord.Interaction, b: discord.ui.Button):
        await it.response.send_modal(EventModal())

    @discord.ui.button(label="📅 Meeting", style=discord.ButtonStyle.success)
    async def btn_meeting(self, it: discord.Interaction, b: discord.ui.Button):
        await it.response.send_modal(MeetingModal())

    @discord.ui.button(label="📰 News", style=discord.ButtonStyle.secondary)
    async def btn_news(self, it: discord.Interaction, b: discord.ui.Button):
        await it.response.send_modal(NewsModal())


# ═══════════════════════════════════════════════════════════════════
# ─── COG
# ═══════════════════════════════════════════════════════════════════
class Announcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="announce", description="Sift announcement as Raw Text (Event / Meeting / News)")
    @require_any_role(*ANNOUNCER_ROLES)
    async def announce_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📢 Announcement System",
            description="Khtar l-type dyal l-announcement li bghiti tsayeb:",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=AnnouncementView(interaction.user), ephemeral=True)

    @commands.command(name="announce")
    @require_any_role_prefix(*ANNOUNCER_ROLES)
    async def announce_prefix(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📢 Announcement System",
            description="Khtar l-type dyal l-announcement li bghiti tsayeb:",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=AnnouncementView(ctx.author))

    @app_commands.command(name="embed", description="3mel embed custom (bach tsta3mel Embed 3adi)")
    @app_commands.describe(image_url="Rlien dyal tswira (Optionnel)")
    @require_any_role(*ANNOUNCER_ROLES)
    async def embed_slash(self, interaction: discord.Interaction, title: str, description: str, color: str = "#5865F2", image_url: str = None):
        try:
            embed_color = discord.Color(int(color.replace("#", ""), 16))
        except Exception:
            embed_color = discord.Color.blurple()
        em = discord.Embed(title=title, description=description, color=embed_color)
        
        if image_url:
            em.set_image(url=image_url)
            
        em.set_footer(text=f"Par {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        await interaction.channel.send(embed=em)
        await interaction.response.send_message("✅ Embed sift!", ephemeral=True)

    @commands.command(name="embed")
    @require_any_role_prefix(*ANNOUNCER_ROLES)
    async def embed_prefix(self, ctx: commands.Context, title: str, description: str, color: str = "#5865F2", image_url: str = None):
        """+embed <title> | <description> | [image_url]"""
        try:
            embed_color = discord.Color(int(color.replace("#", ""), 16))
        except Exception:
            embed_color = discord.Color.blurple()
        em = discord.Embed(title=title, description=description, color=embed_color)
        
        if image_url:
            em.set_image(url=image_url)
            
        em.set_footer(text=f"Par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(Announcements(bot))