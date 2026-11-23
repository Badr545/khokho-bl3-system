"""Staff application panel, persistent submissions, approval and rejection."""
import json
import discord
from discord import app_commands
from discord.ext import commands

import config_manager
from database.features_schema import execute_feat, commit_feat, query_feat_one, query_feat_all


class StaffApplyModal(discord.ui.Modal, title="Apply for Staff"):
    name_field = discord.ui.TextInput(label="Name", required=True, max_length=100)
    age_field = discord.ui.TextInput(label="Age", required=True, max_length=3)
    timezone_field = discord.ui.TextInput(label="Timezone", required=True, max_length=50)
    experience_field = discord.ui.TextInput(label="Moderation experience", required=True, style=discord.TextStyle.paragraph, max_length=1000)
    motivation_field = discord.ui.TextInput(label="Why should we approve you?", required=True, style=discord.TextStyle.paragraph, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        existing = query_feat_one(
            "SELECT id FROM staff_applications WHERE guild_id=? AND user_id=? AND status='pending'",
            (interaction.guild.id, interaction.user.id),
        )
        if existing:
            return await interaction.response.send_message("You already have a pending staff application.", ephemeral=True)

        answers = {
            "name": self.name_field.value,
            "age": self.age_field.value,
            "timezone": self.timezone_field.value,
            "experience": self.experience_field.value,
            "motivation": self.motivation_field.value,
        }
        execute_feat(
            "INSERT INTO staff_applications (guild_id,user_id,answers_json,status) VALUES (?,?,?, 'pending')",
            (interaction.guild.id, interaction.user.id, json.dumps(answers)),
        )
        commit_feat()
        application = query_feat_one(
            "SELECT id FROM staff_applications WHERE guild_id=? AND user_id=? AND status='pending'",
            (interaction.guild.id, interaction.user.id),
        )
        channel = config_manager.get_channel(interaction.guild, "staff_applications_channel")
        if channel is None:
            channel = discord.utils.get(interaction.guild.text_channels, name="staff-applications")
        if channel is None:
            execute_feat(
                "UPDATE staff_applications SET status='cancelled', updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (application["id"],),
            )
            commit_feat()
            return await interaction.response.send_message("No applications channel is configured. Ask an administrator to run `/setup`.", ephemeral=True)

        embed = discord.Embed(title=f"Staff Application #{application['id']}", color=discord.Color.orange(), timestamp=discord.utils.utcnow())
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        for label, value in (("Name", answers["name"]), ("Age", answers["age"]), ("Timezone", answers["timezone"]), ("Experience", answers["experience"]), ("Motivation", answers["motivation"])):
            embed.add_field(name=label, value=value[:1024], inline=False)
        embed.set_footer(text=f"Applicant ID: {interaction.user.id}")

        try:
            message = await channel.send(embed=embed, view=ApplicationReviewView(application["id"]))
            execute_feat(
                "UPDATE staff_applications SET message_id=?, channel_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (message.id, channel.id, application["id"]),
            )
            commit_feat()
        except discord.Forbidden:
            execute_feat(
                "UPDATE staff_applications SET status='cancelled', updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (application["id"],),
            )
            commit_feat()
            return await interaction.response.send_message("I cannot post applications in the configured channel.", ephemeral=True)
        await interaction.response.send_message("✅ Your staff application was submitted.", ephemeral=True)


class RejectionModal(discord.ui.Modal, title="Reject Staff Application"):
    reason = discord.ui.TextInput(label="Rejection reason", required=True, style=discord.TextStyle.paragraph, max_length=1000)

    def __init__(self, application_id: int):
        super().__init__()
        self.application_id = application_id

    async def on_submit(self, interaction: discord.Interaction):
        row = query_feat_one("SELECT * FROM staff_applications WHERE id=? AND guild_id=? AND status='pending'", (self.application_id, interaction.guild.id))
        if not row:
            return await interaction.response.send_message("This application is no longer pending.", ephemeral=True)
        member = interaction.guild.get_member(row["user_id"])
        if member:
            try:
                await member.send(f"Your staff application was **REJECTED**.\nReason: {self.reason.value}")
            except discord.Forbidden:
                pass
        execute_feat(
            "UPDATE staff_applications SET status='rejected', reviewer_id=?, rejection_reason=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (interaction.user.id, self.reason.value, self.application_id),
        )
        commit_feat()
        await interaction.response.send_message("Application rejected.", ephemeral=True)


class ApplicationReviewView(discord.ui.View):
    def __init__(self, application_id: int):
        super().__init__(timeout=None)
        self.application_id = application_id
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                action = "approve" if child.label == "Approve" else "reject"
                child.custom_id = f"staff-app:{action}:{application_id}"

    def is_staff(self, interaction: discord.Interaction) -> bool:
        member = interaction.user
        if not isinstance(member, discord.Member):
            return False
        if member.guild_permissions.administrator or member.guild_permissions.manage_roles:
            return True
        staff_role = config_manager.get_role(interaction.guild, "staff_role")
        verification_staff = config_manager.get_role(interaction.guild, "verification_staff_role")
        return bool((staff_role and staff_role in member.roles) or (verification_staff and verification_staff in member.roles))

    @discord.ui.button(label="Approve", emoji="✅", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_staff(interaction):
            return await interaction.response.send_message("Only staff can approve applications.", ephemeral=True)
        row = query_feat_one("SELECT * FROM staff_applications WHERE id=? AND guild_id=? AND status='pending'", (self.application_id, interaction.guild.id))
        if not row:
            return await interaction.response.send_message("This application is no longer pending.", ephemeral=True)
        member = interaction.guild.get_member(row["user_id"])
        staff_role = config_manager.get_role(interaction.guild, "staff_role")
        if member is None or staff_role is None:
            return await interaction.response.send_message("Applicant or Staff role could not be found.", ephemeral=True)
        try:
            await member.add_roles(staff_role, reason=f"Staff application #{self.application_id} approved")
            await member.send("Your staff application was **APPROVED**.")
        except discord.Forbidden:
            pass
        except discord.HTTPException as exc:
            return await interaction.response.send_message(f"Role update failed: {exc.text}", ephemeral=True)
        execute_feat(
            "UPDATE staff_applications SET status='approved', reviewer_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (interaction.user.id, self.application_id),
        )
        commit_feat()
        await interaction.response.send_message("Application approved.", ephemeral=True)

    @discord.ui.button(label="Reject", emoji="❌", style=discord.ButtonStyle.danger, custom_id="staff-app:reject")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_staff(interaction):
            return await interaction.response.send_message("Only staff can reject applications.", ephemeral=True)
        row = query_feat_one("SELECT id FROM staff_applications WHERE id=? AND guild_id=? AND status='pending'", (self.application_id, interaction.guild.id))
        if not row:
            return await interaction.response.send_message("This application is no longer pending.", ephemeral=True)
        await interaction.response.send_modal(RejectionModal(self.application_id))


class Applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._restored = False

    async def cog_load(self):
        if self._restored:
            return
        self._restored = True
        for row in query_feat_all(
            "SELECT id FROM staff_applications WHERE status='pending' AND message_id IS NOT NULL"
        ):
            self.bot.add_view(ApplicationReviewView(row["id"]))
        self.bot.add_view(StaffApplicationPanelView())

    @app_commands.command(name="applystaff-setup", description="Create or repost the staff application panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def applystaff_setup(self, interaction: discord.Interaction):
        category = config_manager.get_category(interaction.guild, "staff_category")
        applications_channel = config_manager.get_channel(interaction.guild, "staff_applications_channel")
        panel_channel = config_manager.get_channel(interaction.guild, "staff_application_panel_channel")
        if category is None:
            category = discord.utils.get(interaction.guild.categories, name="Staff")
        if applications_channel is None:
            try:
                applications_channel = await interaction.guild.create_text_channel("staff-applications", category=category, reason="Staff application setup")
                config_manager.set_channel(interaction.guild.id, "staff_applications_channel", applications_channel.id)
            except discord.Forbidden:
                return await interaction.response.send_message("I lack permission to create the applications channel.", ephemeral=True)
        if panel_channel is None:
            try:
                panel_channel = await interaction.guild.create_text_channel("apply-for-staff", category=category, reason="Staff application setup")
                config_manager.set_channel(interaction.guild.id, "staff_application_panel_channel", panel_channel.id)
            except discord.Forbidden:
                return await interaction.response.send_message("I lack permission to create the panel channel.", ephemeral=True)

        embed = discord.Embed(title="Apply for Staff", description="Press the button below to submit a staff application.", color=discord.Color.gold())
        view = StaffApplicationPanelView()
        try:
            message = await panel_channel.send(embed=embed, view=view)
            execute_feat(
                "INSERT INTO staff_application_panels (guild_id,channel_id,message_id) "
                "VALUES (?,?,?) ON CONFLICT(guild_id) DO UPDATE SET channel_id=excluded.channel_id,message_id=excluded.message_id",
                (interaction.guild.id, panel_channel.id, message.id),
            )
            commit_feat()
        except discord.Forbidden:
            return await interaction.response.send_message("I cannot post in the panel channel.", ephemeral=True)
        await interaction.response.send_message(f"✅ Staff application panel posted in {panel_channel.mention}.", ephemeral=True)


class StaffApplicationPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apply for Staff", emoji="📝", style=discord.ButtonStyle.primary, custom_id="staff-app:apply")
    async def apply(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffApplyModal())


async def setup(bot: commands.Bot):
    await bot.add_cog(Applications(bot))
