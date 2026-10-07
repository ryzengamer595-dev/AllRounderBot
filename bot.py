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

# Self-healing Opus loader
def setup_opus():
    if discord.opus.is_loaded():
        return True
        
    local_opus = os.path.join(os.getcwd(), "libopus.so.0")
    if not os.path.exists(local_opus):
        try:
            print("📥 Downloading libopus.so.0 binary for container...")
            url = "https://github.com/eugeneware/discord-opus-binaries/raw/master/linux/x64/libopus.so"
            urllib.request.urlretrieve(url, local_opus)
        except Exception as e:
            print(f"⚠️ Could not download libopus: {e}")
            
    paths = [
        local_opus,
        "libopus.so.0",
        "libopus.so",
        "/usr/lib/x86_64-linux-gnu/libopus.so.0",
        "/usr/lib/libopus.so.0"
    ]
    
    for path in paths:
        if os.path.exists(path) or "libopus" in path:
            try:
                discord.opus.load_opus(path)
                if discord.opus.is_loaded():
                    print(f"🟢 Opus library status: LOADED from {path}")
                    return True
            except Exception:
                continue
                
    return False

setup_opus()

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
            return
            
        # Safe startup loop to handle temporary network/rate-limit blocks smoothly
        while True:
            try:
                print("Connecting to Discord...")
                await bot.start(TOKEN)
                break
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    print("⚠️ Hit Cloudflare Rate Limit (429/1015). Waiting 60 seconds before retrying...")
                    await asyncio.sleep(60)
                else:
                    print(f"HTTP Exception encountered: {e}")
                    await asyncio.sleep(10)
            except Exception as e:
                print(f"Connection error: {e}. Retrying in 15 seconds...")
                await asyncio.sleep(15)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")