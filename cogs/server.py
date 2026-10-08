import discord
from discord import app_commands
from discord.ext import commands

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Show server information.")
    async def serverinfo(self, interaction):
        g = interaction.guild
        embed = discord.Embed(title=f"🏠 {g.name}", color=discord.Color.blurple())
        embed.set_thumbnail(url=g.icon.url if g.icon else discord.Embed.Empty)
        owner = g.owner.mention if g.owner else "Unknown"
        embed.add_field(name="Owner", value=owner)
        embed.add_field(name="Members", value=str(g.member_count))
        embed.add_field(name="Channels", value=str(len(g.channels)))
        embed.add_field(name="Roles", value=str(len(g.roles)))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Show user information.")
    async def userinfo(self, interaction, user: discord.Member = None):
        user = user or interaction.user
        embed = discord.Embed(title=f"👤 {user}", color=user.color)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID", value=str(user.id))
        embed.add_field(name="Joined", value=discord.utils.format_dt(user.joined_at, "R") if user.joined_at else "Unknown")
        embed.add_field(name="Account", value=discord.utils.format_dt(user.created_at, "R"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="announce", description="Send an announcement in this channel.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def announce(self, interaction, message: str):
        embed = discord.Embed(title="📢 Announcement", description=message, color=discord.Color.orange())
        embed.set_footer(text=f"By {interaction.user}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Server(bot))
