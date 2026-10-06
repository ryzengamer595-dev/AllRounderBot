# All-Rounder Discord Bot (Advanced Music, 24/7, Queue, Autoplay & Owner Info)

Full-featured modular Discord Bot with Slash Commands (`/`).

## 👑 Owner & Bot Info:
- `/owner`: Displays Bot Owner (Akram) and Bot Creation Date with custom embed.

## 🎵 Advanced Music Features:
- **Queue System**: `/queue`
- **Autoplay Toggle**: `/autoplay`
- **24/7 Mode**: `/mode247`
- **Queue Control Commands**: `/nowplaying`, `/skip`, `/stop`, `/join`, `/leave`, `/play`.

## Setup Instructions:
1. Container/System par dependencies install karein:
   ```bash
   pip install -U "discord.py[voice]" yt-dlp PyNaCl
   apt-get update && apt-get install -y ffmpeg libsodium-dev
   ```
2. Set token in `.env`:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```
3. Run the bot:
   ```bash
   python bot.py
   ```
