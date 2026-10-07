import os
import asyncio
import ctypes.util
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

# Force load libopus for Railway / Cloud container
opus_named = ctypes.util.find_library('opus')
if opus_named:
    try:
        discord.opus.load_opus(opus_named)
        print(f"✅ Successfully loaded Opus library via find_library: {opus_named}")
    except Exception as e:
        print(f"⚠️ Failed to load Opus via find_library: {e}")

if not discord.opus.is_loaded():
    for lib in ["libopus.so.0", "libopus.so", "opus", "/usr/lib/x86_64-linux-gnu/libopus.so.0", "/usr/lib/libopus.so.0"]:
        try:
            discord.opus.load_opus(lib)
            print(f"✅ Successfully loaded Opus library from path: {lib}")
            break
        except Exception:
            pass

if discord.opus.is_loaded():
    print("🟢 Opus library status: LOADED")
else:
    print("🔴 Opus library status: NOT LOADED (Voice may fail)")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print("=" * 45)
    print(f"Bot Name : {bot.user}")
    print(f"Bot ID   : {bot.user.id}")
    print(f"Servers  : {len(bot.guilds)}")
    print("Status   : ONLINE")
    print("=" * 45)

    for guild in bot.guilds:
        try:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ Instantly synced {len(synced)} commands to guild: {guild.name} ({guild.id})")
        except Exception as e:
            print(f"⚠️ Failed to sync to guild {guild.name}: {e}")

    try:
        global_synced = await bot.tree.sync()
        print(f"🌐 Globally synced {len(global_synced)} Slash Commands.")
    except Exception as e:
        print(f"⚠️ Global sync error: {e}")

    activity = discord.Game(name="All-Rounder Bot | /help")
    await bot.change_presence(status=discord.Status.online, activity=activity)

async def load_extensions():
    cogs = [
        "cogs.moderation",
        "cogs.utility",
        "cogs.fun",
        "cogs.leveling",
        "cogs.tickets",
        "cogs.welcome",
        "cogs.antinuke",
        "cogs.music"
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"Loaded extension: {cog}")
        except Exception as e:
            print(f"Failed to load extension {cog}: {e}")

async def main():
    async with bot:
        await load_extensions()
        if not TOKEN or TOKEN == "your_bot_token_here":
            print("⚠️ WARNING: Please set DISCORD_TOKEN in .env file!")
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())