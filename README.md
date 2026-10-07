# All-Rounder Discord Bot (Music with Smart Autoplay, /message, /message_all & Anti-Nuke)

Full-featured modular Discord Bot with Slash Commands (`/`).

## 🎵 Advanced Music Features:
- **Smart Autoplay (`/autoplay`)**: Jab queue finish ho jayegi, bot automatically pehle song ke title aur artist ke basis par YouTube se similar recommended songs search karke play karega.
- **Queue System**: `/queue`
- **24/7 Mode**: `/mode247`
- **Control Commands**: `/nowplaying`, `/skip`, `/stop`, `/join`, `/leave`, `/play`.

## 📢 New Broadcast Commands:
- `/message channel:<#channel> message:<text>`: Bot dwara kisi specific channel me message bhejne ke liye (Admins only).
- `/message_all message:<text>`: Server ke saare text channels me message broadcast karne ke liye (Admins only).
- `/owner`: Bot owner details (Akram) & creation date.

## Setup Instructions:
1. Dependencies install karein:
   ```bash
   pip install -U "discord.py[voice]" yt-dlp PyNaCl
   apt-get update && apt-get install -y ffmpeg libsodium-dev
   ```
2. Token set karein `.env` me:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```
3. Run the bot:
   ```bash
   python bot.py
   ```
