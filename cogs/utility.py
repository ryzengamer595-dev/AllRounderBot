import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel:
            embed = discord.Embed(
                title="👋 Welcome!",
                description=f"Welcome {member.mention} to **{member.guild.name}**!\nEnjoy your stay! ❤️",
                color=discord.Color.blurple()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping_slash(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: **{latency}ms**")

    @app_commands.command(name="serverinfo", description="Get server information")
    async def serverinfo_slash(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.blue())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="👑 Owner", value=str(guild.owner), inline=False)
        embed.add_field(name="👥 Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="💬 Channels", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="🆔 Server ID", value=str(guild.id), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Get user information")
    async def userinfo_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title="👤 User Information", color=discord.Color.blue())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Username", value=str(member), inline=False)
        embed.add_field(name="ID", value=str(member.id), inline=False)
        joined = discord.utils.format_dt(member.joined_at, style="F") if member.joined_at else "Unknown"
        embed.add_field(name="Joined Server", value=joined, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show all bot commands")
    async def help_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚡ All-Rounder Bot Commands (Slash Commands /)",
            description="Use slash `/` commands to interact with the bot:",
            color=discord.Color.gold()
        )
        embed.add_field(name="🛡️ Moderation", value="`/clear`, `/kick`, `/ban`, `/timeout`", inline=False)
        embed.add_field(name="📊 Utility", value="`/ping`, `/serverinfo`, `/userinfo`, `/help`", inline=False)
        embed.add_field(name="🎮 Fun & Games", value="`/roll`, `/8ball`, `/coinflip`", inline=False)
        embed.add_field(name="⭐ Level & Economy", value="`/rank`, `/daily`, `/balance`", inline=False)
        embed.add_field(name="🎫 Support Tickets", value="`/setup_ticket`, `/close`", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
