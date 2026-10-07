import os
import asyncio
import ctypes
import urllib.request
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

# Auto-download and load libopus if missing on cloud containers
def ensure_opus_loaded():
    if discord.opus.is_loaded():
        return True
    
    # Try common local or system paths first
    paths = [
        "libopus.so.0",
        "libopus.so",
        "/usr/lib/x86_64-linux-gnu/libopus.so.0",
        "/usr/lib/libopus.so.0",
        os.path.join(os.getcwd(), "libopus.so.0")
    ]
    
    for path in paths:
        try:
            discord.opus.load_opus(path)
            if discord.opus.is_loaded():
                print(f"✅ Loaded Opus from path: {path}")
                return True
        except Exception:
            continue
            
    # If not found, download a precompiled libopus.so.0 binary directly into the workspace
    try:
        print("📥 Downloading static libopus library for cloud environment...")
        lib_path = os.path.join(os.getcwd(), "libopus.so.0")
        if not os.path.exists(lib_path):
            url = "https://github.com/ToTheMax/discord-opus-binaries/raw/master/rpi/libopus.so.0" # or a reliable linux binary mirror
            # Using an alternate direct link or standard Debian shared object
            urllib.request.urlretrieve("https://raw.githubusercontent.com/Anankkj/opus-binaries/main/libopus.so.0", lib_path)
        
        discord.opus.load_opus(lib_path)
        if discord.opus.is_loaded():
            print("✅ Successfully downloaded and loaded libopus.so.0 locally!")
            return True
    except Exception as e:
        print(f"⚠️ Failed to auto-download libopus: {e}")
        
    return False

if ensure_opus_loaded():
    print("🟢 Opus library status: LOADED")
else:
    print("🔴 Opus library status: NOT LOADED")

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