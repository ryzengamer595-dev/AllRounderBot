import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Delete messages.")
    @app_commands.describe(amount="Number of messages to delete")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction, amount: app_commands.Range[int, 1, 100]):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted `{len(deleted)}` messages.", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked {member.mention}. Reason: {reason}")

    @app_commands.command(name="ban", description="Ban a member.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 Banned **{member}**. Reason: {reason}")

    @app_commands.command(name="warn", description="Warn a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction, member: discord.Member, reason: str = "No reason provided"):
        await interaction.response.send_message(
            f"⚠️ {member.mention} has been warned.\n**Reason:** {reason}"
        )

    @app_commands.command(name="mute", description="Timeout a member.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction, member: discord.Member, minutes: app_commands.Range[int, 1, 10080] = 10):
        await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes), reason="Bot mute")
        await interaction.response.send_message(f"🔇 {member.mention} muted for `{minutes}` minutes.")

    @app_commands.command(name="lock", description="Lock the current channel.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔒 Channel locked.")

    @app_commands.command(name="unlock", description="Unlock the current channel.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = None
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔓 Channel unlocked.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
