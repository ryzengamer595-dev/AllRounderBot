# All-Rounder Discord Bot (Music with /join, Anti-Nuke, Custom Welcome & Slash Commands)

Full-featured modular Discord Bot with Slash Commands (`/`).

## Features Added:
- 🎵 **Music System (`yt-dlp` + FFmpeg)**:
  - `/join`: Voice Channel me manual join karne ke liye.
  - `/leave`: Voice Channel se leave karne ke liye.
  - `/play <search/URL>`: YouTube se music play karne ke liye (Auto-joins voice channel).
  - `/skip`: Current song skip karne ke liye.
  - `/stop`: Music stop karke disconnect hone ke liye.
- 🛡️ **Anti-Nuke / Anti-Raid System**:
  - Mass Channel Creation / Deletion Protection.
  - Mass Ban / Kick Protection.
- 🖼️ **Fancy Embed Welcome System**:
  - Custom welcome embed format with thumbnail, member count & channel links.
- 🔄 **Auto-Push (`auto-push.ps1`)**:
  - GitHub pe auto-commit aur push.

## Setup Instructions:
1. Container/System par dependencies install karein:
   ```bash
   pip install -r requirements.txt
   apt-get update && apt-get install -y ffmpeg
   ```
2. Set token in `.env`:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```
3. Run the bot:
   ```bash
   python bot.py
   ```
