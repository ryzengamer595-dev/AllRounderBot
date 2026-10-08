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
        print("       ALLROUNDER BOT - LOADING EXTENSIONS")
        print("=" * 60)

        for extension in extensions:
            try:
                await self.load_extension(extension)
                print(f"✅ Loaded: {extension}")

            except Exception as error:
                print(f"❌ Failed: {extension}")
                print(f"   {error}")
                traceback.print_exc()

        print("=" * 60)
        print("       SYNCING SLASH COMMANDS")
        print("=" * 60)

        # Global sync
        try:
            global_commands = await self.tree.sync()

            print(
                f"🌍 Global commands synced: "
                f"{len(global_commands)}"
            )

        except Exception as error:
            print("❌ Global sync failed:")
            print(error)

        # Guild sync
        #
        # This makes slash commands appear much faster
        # in servers where the bot is already installed.
        #
        for guild in self.guilds:
            try:
                guild_commands = await self.tree.sync(
                    guild=guild
                )

                print(
                    f"✅ Guild synced: "
                    f"{guild.name} "
                    f"({guild.id}) "
                    f"→ {len(guild_commands)} commands"
                )

            except Exception as error:
                print(
                    f"❌ Guild sync failed: "
                    f"{guild.name}"
                )
                print(error)

        print("=" * 60)


    async def on_ready(self):

        print("\n" + "=" * 60)
        print(f"🤖 Logged in as: {self.user}")
        print(f"🆔 Bot ID: {self.user.id}")
        print(f"🌐 Servers: {len(self.guilds)}")
        print("=" * 60)

        for guild in self.guilds:
            print(
                f"📌 {guild.name} "
                f"({guild.id})"
            )

        await self.change_presence(
            activity=discord.Game(
                name="/help • All-Rounder Bot"
            )
        )


bot = AllRounderBot()

bot.run(TOKEN)