import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🏓 Pong! `{round(self.bot.latency * 1000)}ms`"
        )

    @app_commands.command(name="avatar", description="Show a user's avatar.")
    @app_commands.describe(user="User whose avatar you want")
    async def avatar(self, interaction, user: discord.User = None):
        user = user or interaction.user
        embed = discord.Embed(title=f"{user.display_name}'s Avatar")
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show all bot features.")
    async def help(self, interaction):
        embed = discord.Embed(
            title="🤖 All-Rounder Bot",
            description="Useful slash commands available on this server.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="🛡️ Moderation",
                        value="`/ban` `/kick` `/mute` `/warn` `/clear` `/lock` `/unlock`",
                        inline=False)
        embed.add_field(name="🎫 Server",
                        value="`/serverinfo` `/userinfo` `/announce` `/ticket`",
                        inline=False)
        embed.add_field(name="🎮 Fun",
                        value="`/8ball` `/coinflip` `/dice`",
                        inline=False)
        embed.add_field(name="💰 Economy",
                        value="`/balance` `/daily` `/leaderboard`",
                        inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))
