import os
import asyncio
import ctypes.util
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

# Clean and reliable Opus loader for Nixpacks/Linux
def load_opus_library():
    if discord.opus.is_loaded():
        return True
    
    for lib in ["libopus.so.0", "libopus.so", "opus", "/usr/lib/x86_64-linux-gnu/libopus.so.0", "/nix/store/*-opus-*/lib/libopus.so.0"]:
        try:
            if "*" in lib:
                import glob
                matches = glob.glob(lib)
                if matches:
                    discord.opus.load_opus(matches[0])
                    return True
            else:
                discord.opus.load_opus(lib)
                return True
        except Exception:
            continue
            
    try:
        opus_name = ctypes.util.find_library('opus')
        if opus_name:
            discord.opus.load_opus(opus_name)
            return True
    except Exception:
        pass
        
    return False

if load_opus_library():
    print("🟢 Opus library status: LOADED")
else:
    print("🔴 Opus library status: NOT LOADED")