# utils/confirm.py
# ═══════════════════════════════════════════════════════════════════
# ─── SHARED CONFIRM VIEW (لجميع الأوامر الحساسة)
# ═══════════════════════════════════════════════════════════════════
import discord
from discord.ext import commands


class ConfirmView(discord.ui.View):
    """View dyal confirm/cancel — kaystakhdem f kol command sensible."""

    def __init__(self, author: discord.Member, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.author = author
        self.value: bool | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Had l-menu machi dyalek!", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, it: discord.Interaction, btn: discord.ui.Button):
        self.value = True
        for c in self.children:
            c.disabled = True
        await it.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, it: discord.Interaction, btn: discord.ui.Button):
        self.value = False
        for c in self.children:
            c.disabled = True
        await it.response.edit_message(view=self)
        self.stop()


async def confirm_action(ctx: commands.Context, title: str, description: str) -> bool:
    """Helper: يبعث embed dyal confirm w yrje3 True/False."""
    embed = discord.Embed(
        title=f"⚠️ {title}",
        description=description,
        color=discord.Color.orange(),
    )
    embed.set_footer(text="Time out: 60 seconds")

    view = ConfirmView(ctx.author)
    msg = await ctx.send(embed=embed, view=view)
    await view.wait()

    if not view.value:
        try:
            await msg.edit(
                embed=discord.Embed(
                    description="❌ **Action cancelled.**",
                    color=discord.Color.red(),
                ),
                view=None,
            )
        except Exception:
            pass
        return False

    try:
        await msg.delete()
    except Exception:
        pass
    return True


async def confirm_interaction(
    interaction: discord.Interaction, title: str, description: str
) -> bool:
    """Helper l slash commands."""
    embed = discord.Embed(
        title=f"⚠️ {title}",
        description=description,
        color=discord.Color.orange(),
    )
    embed.set_footer(text="Time out: 60 seconds")

    view = ConfirmView(interaction.user)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    msg = await interaction.original_response()
    await view.wait()

    if not view.value:
        try:
            await msg.edit(
                embed=discord.Embed(
                    description="❌ **Action cancelled.**",
                    color=discord.Color.red(),
                ),
                view=None,
            )
        except Exception:
            pass
        return False

    try:
        await msg.delete()
    except Exception:
        pass
    return True