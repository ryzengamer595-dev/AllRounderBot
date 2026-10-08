import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable is missing!")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

class AllRounderBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        extensions = [
            "cogs.moderation",
            "cogs.utility",
            "cogs.fun",
            "cogs.server",
            "cogs.welcome",
            "cogs.tickets",
            "cogs.economy",
            "cogs.automod",
        ]
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"Loaded extension: {ext}")
            except Exception as e:
                print(f"Failed to load {ext}: {e}")

        synced = await self.tree.sync()
        print(f"Synced {len(synced)} slash commands.")

    async def on_ready(self):
        print(f"Logged in as {self.user} ({self.user.id})")
        print(f"Connected to {len(self.guilds)} server(s).")
        await self.change_presence(
            activity=discord.Game(name="/help • All-Rounder Bot")
        )

bot = AllRounderBot()
bot.run(TOKEN)
