import os
import asyncio
import ctypes
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

# Comprehensive manual/auto loader for libopus on Linux containers
def load_opus_library():
    if discord.opus.is_loaded():
        return True
    
    # Check common system paths in lightweight containers
    paths = [
        "libopus.so.0",
        "libopus.so",
        "libopus-0.x86_64.dll",
        "/usr/lib/x86_64-linux-gnu/libopus.so.0",
        "/usr/lib/libopus.so.0",
        "/usr/lib/libopus.so",
        "/usr/local/lib/libopus.so.0",
        "/nix/store/*-opus-*/lib/libopus.so.0"
    ]
    
    for path in paths:
        try:
            if "*" in path:
                import glob
                matches = glob.glob(path)
                if matches:
                    discord.opus.load_opus(matches[0])
                    print(f"✅ Loaded Opus from glob: {matches[0]}")
                    return True
            else:
                discord.opus.load_opus(path)
                print(f"✅ Loaded Opus from path: {path}")
                return True
        except Exception:
            continue
            
    # Fallback to ctypes find_library
    try:
        opus_name = ctypes.util.find_library('opus')
        if opus_name:
            discord.opus.load_opus(opus_name)
            print(f"✅ Loaded Opus via ctypes: {opus_name}")
            return True
    except Exception:
        pass
        
    return False

if load_opus_library():
    print("🟢 Opus library status: LOADED")
else:
    print("🔴 Opus library status: NOT LOADED")