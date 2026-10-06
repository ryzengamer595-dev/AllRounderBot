# All-Rounder Discord Bot (Advanced Music, 24/7, Queue, Autoplay & Anti-Nuke)

Full-featured modular Discord Bot with Slash Commands (`/`).

## 🎵 Advanced Music Features:
- **Queue System**: `/queue` se next play hone wale gano ki list dekhein.
- **Autoplay Toggle**: `/autoplay` command se autoplay ON/OFF karein. Jab queue khatam hogi, bot pehle gana jaise related songs YouTube se dhund kar automatically play karega!
- **24/7 Mode**: `/mode247` command se 24/7 mode ON/OFF karein. On karne par bot gana khatam hone par bhi voice channel leave nahi karega.
- **Queue Control Commands**: `/nowplaying`, `/skip`, `/stop`, `/join`, `/leave`, `/play`.

## 🛡️ Other Modules:
- **Anti-Nuke / Anti-Raid**: Mass Channel Deletion & Ban protection.
- **Welcome Embed System**: Custom welcome banner format with thumbnails & links.
- **Moderation, Fun, Utility, Leveling, Support Tickets**.

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
