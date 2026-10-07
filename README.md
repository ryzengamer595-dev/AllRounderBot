# All-Rounder Discord Bot (Bypass YouTube Sign-in Bot Check, Multi-Client Player, Instant Sync & Anti-Nuke)

Full-featured modular Discord Bot with Slash Commands (`/`).

## 🛡️ YouTube Anti-Bot Bypass Included:
- Configured with `android`, `ios`, `mweb`, `tvhtml5` player clients to bypass Cloud Hosting IP blocks (`Sign in to confirm you're not a bot`).
- Optional `cookies.txt` support enabled (place exported YouTube `cookies.txt` in the root directory if needed).

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
