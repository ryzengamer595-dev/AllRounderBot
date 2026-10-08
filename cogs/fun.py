import random
import discord
from discord import app_commands
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="coinflip", description="Flip a coin.")
    async def coinflip(self, interaction):
        await interaction.response.send_message(f"🪙 **{random.choice(['Heads', 'Tails'])}**")

    @app_commands.command(name="dice", description="Roll a dice.")
    async def dice(self, interaction):
        await interaction.response.send_message(f"🎲 You rolled **{random.randint(1, 6)}**")

    @app_commands.command(name="8ball", description="Ask the magic 8-ball.")
    @app_commands.describe(question="Your question")
    async def eightball(self, interaction, question: str):
        answers = ["Yes.", "No.", "Maybe.", "Definitely!", "Ask again later.", "Probably."]
        await interaction.response.send_message(
            f"🎱 **Question:** {question}\n**Answer:** {random.choice(answers)}"
        )

async def setup(bot):
    await bot.add_cog(Fun(bot))
