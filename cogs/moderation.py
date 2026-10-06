import discord
from discord import app_commands
from discord.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash Command: /clear
    @app_commands.command(name="clear", description="Purge messages in channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_slash(self, interaction: discord.Interaction, amount: int = 10):
        if amount < 1:
            return await interaction.response.send_message("❌ Amount must be at least 1.", ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Deleted **{len(deleted)}** messages.", ephemeral=True)

    # Slash Command: /kick
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member == interaction.user:
            return await interaction.response.send_message("❌ You cannot kick yourself.", ephemeral=True)
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 **{member}** has been kicked. Reason: **{reason}**")

    # Slash Command: /ban
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member == interaction.user:
            return await interaction.response.send_message("❌ You cannot ban yourself.", ephemeral=True)
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 **{member}** has been banned. Reason: **{reason}**")

    # Slash Command: /timeout
    @app_commands.command(name="timeout", description="Timeout/Mute a member")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, minutes: int = 10, reason: str = "No reason provided"):
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await interaction.response.send_message(f"🔇 **{member}** timed out for {minutes} minutes. Reason: **{reason}**")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
