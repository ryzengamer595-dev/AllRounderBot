import discord
from discord import app_commands
from discord.ext import commands

user_xp = {}
user_balance = {}

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        user_id = message.author.id
        user_xp[user_id] = user_xp.get(user_id, 0) + 10

    @app_commands.command(name="rank", description="Check your or another member's rank & XP")
    async def rank_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        xp = user_xp.get(member.id, 0)
        level = xp // 100
        await interaction.response.send_message(f"🌟 **{member.display_name}** is Level **{level}** ({xp} XP)")

    @app_commands.command(name="daily", description="Claim your daily coin reward")
    async def daily_slash(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_balance[user_id] = user_balance.get(user_id, 0) + 100
        await interaction.response.send_message("💰 You claimed your daily reward of **100 coins**!")

    @app_commands.command(name="balance", description="Check your coin balance")
    async def balance_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        coins = user_balance.get(member.id, 0)
        await interaction.response.send_message(f"👛 **{member.display_name}** has **{coins} coins**.")

async def setup(bot):
    await bot.add_cog(Leveling(bot))
