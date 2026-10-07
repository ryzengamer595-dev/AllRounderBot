# All-Rounder Discord Bot (Authenticated YouTube Music, Instant Sync & Anti-Nuke)

Full-featured modular Discord Bot with Slash Commands (`/`).

## 🎵 Authenticated YouTube Music:
- Includes valid `cookies.txt` authentication to completely bypass YouTube's cloud hosting IP blocks and bot verification errors.

## ⚡ Features & Commands:
- **Instant Guild Sync**: Instant `/` slash command registration across servers.
- **Music & Autoplay**: `/play`, `/queue`, `/autoplay`, `/mode247`, `/join`, `/leave`, `/skip`, `/stop`, `/nowplaying`.
- **Broadcast & Info**: `/message`, `/message_all`, `/owner` (Owner: Akram), `/help`, `/ping`, `/serverinfo`, `/userinfo`.
- **Security & Welcome**: Anti-Nuke protection & Custom Welcome embeds.

## Setup Instructions:
1. Dependencies install karein:
   ```bash
   pip install -U "discord.py[voice]" yt-dlp PyNaCl
   apt-get update && apt-get install -y ffmpeg libsodium-dev
   ```
2. Token set karein `.env` file me.
3. Run the bot:
   ```bash
   python bot.py
   ```
