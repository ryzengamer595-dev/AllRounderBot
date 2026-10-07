import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="message", description="Send a custom message to a specific text channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def message_channel(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        try:
            embed = discord.Embed(
                description=message,
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"Sent by {interaction.user.display_name}")
            await channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Message successfully sent to {channel.mention}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to send message: {e}", ephemeral=True)

    @app_commands.command(name="message_all", description="Broadcast a message to ALL text channels in the server")
    @app_commands.checks.has_permissions(administrator=True)
    async def message_all_channels(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(ephemeral=True)
        sent_count = 0
        failed_count = 0

        embed = discord.Embed(
            title="📢 Server Announcement",
            description=message,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Broadcasted by {interaction.user.display_name}")

        for text_channel in interaction.guild.text_channels:
            try:
                if text_channel.permissions_for(interaction.guild.me).send_messages:
                    await text_channel.send(embed=embed)
                    sent_count += 1
            except Exception:
                failed_count += 1

        await interaction.followup.send(
            f"📢 Broadcast Complete!
✅ Sent to **{sent_count}** text channels.
❌ Failed in **{failed_count}** channels."
        )

    @app_commands.command(name="owner", description="Get information about the Bot Owner and Bot Details")
    async def owner_slash(self, interaction: discord.Interaction):
        bot_user = self.bot.user
        created_at = discord.utils.format_dt(bot_user.created_at, style="F")
        relative_created = discord.utils.format_dt(bot_user.created_at, style="R")

        embed = discord.Embed(
            title="👑 Bot Owner & Information",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=bot_user.display_avatar.url)
        embed.add_field(name="👤 Owner Name", value="**Akram**", inline=False)
        embed.add_field(name="🤖 Bot Name", value=f"{bot_user.name} ({bot_user.mention})", inline=False)
        embed.add_field(name="📅 Bot Creation Date", value=f"{created_at} ({relative_created})", inline=False)
        embed.set_footer(text=f"Bot ID: {bot_user.id}")

        await interaction.response.send_message(embed=embed)

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
        embed.add_field(name="📢 Announcements", value="`/message [channel] [text]`, `/message_all [text]`", inline=False)
        embed.add_field(name="👑 Owner & Info", value="`/owner`", inline=False)
        embed.add_field(name="🎵 Music", value="`/play`, `/queue`, `/autoplay`, `/mode247`, `/nowplaying`, `/skip`, `/stop`, `/join`, `/leave`", inline=False)
        embed.add_field(name="🛡️ Anti-Nuke & Moderation", value="`Auto Anti-Nuke Active`, `/clear`, `/kick`, `/ban`, `/timeout`", inline=False)
        embed.add_field(name="📊 Utility", value="`/ping`, `/serverinfo`, `/userinfo`, `/help`", inline=False)
        embed.add_field(name="🎮 Fun & Games", value="`/roll`, `/8ball`, `/coinflip`", inline=False)
        embed.add_field(name="⭐ Level & Economy", value="`/rank`, `/daily`, `/balance`", inline=False)
        embed.add_field(name="🎫 Support Tickets", value="`/setup_ticket`, `/close`", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
