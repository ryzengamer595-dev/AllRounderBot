import discord
import random
from discord import app_commands
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Roll a 6-sided dice")
    async def roll_slash(self, interaction: discord.Interaction):
        result = random.randint(1, 6)
        await interaction.response.send_message(f"🎲 You rolled a **{result}**!")

    @app_commands.command(name="8ball", description="Ask Magic 8-Ball a question")
    async def eightball_slash(self, interaction: discord.Interaction, question: str):
        responses = [
            "Yes, definitely!", "Most likely.", "Ask again later.",
            "Cannot predict now.", "Don't count on it.", "My reply is no."
        ]
        await interaction.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {random.choice(responses)}")

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip_slash(self, interaction: discord.Interaction):
        outcome = random.choice(["Heads 🪙", "Tails 🪙"])
        await interaction.response.send_message(f"Result: **{outcome}**")

async def setup(bot):
    await bot.add_cog(Fun(bot))
