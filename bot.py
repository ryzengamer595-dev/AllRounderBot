import os
import traceback

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
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

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

        print("\n" + "=" * 60)
        print("           ALLROUNDER BOT - LOADING COGS")
        print("=" * 60)

        for extension in extensions:
            try:
                await self.load_extension(extension)
                print(f"✅ Loaded: {extension}")

            except Exception as error:
                print(f"❌ FAILED: {extension}")
                print(f"   Error: {error}")
                traceback.print_exc()

        print("=" * 60)
        print("              SYNCING SLASH COMMANDS")
        print("=" * 60)

        try:
            synced = await self.tree.sync()

            print(f"✅ Synced {len(synced)} slash command(s).")

            for command in synced:
                print(f"   /{command.name}")

        except Exception as error:
            print("❌ Slash command sync failed!")
            print(f"Error: {error}")
            traceback.print_exc()

        print("=" * 60)
        print()


    async def on_ready(self):

        print("=" * 60)
        print(f"🤖 Logged in as: {self.user}")
        print(f"🆔 Bot ID: {self.user.id}")
        print(f"🌐 Servers: {len(self.guilds)}")

        if self.guilds:
            print("📋 Connected servers:")

            for guild in self.guilds:
                print(f"   • {guild.name} ({guild.id})")

        print("=" * 60)

        await self.change_presence(
            activity=discord.Game(
                name="/help • All-Rounder Bot"
            )
        )


bot = AllRounderBot()

bot.run(TOKEN)