# All-Rounder Discord Bot (Music, Anti-Nuke, Custom Welcome & Slash Commands)

Full-featured modular Discord Bot with Slash Commands (`/`).

## Features Added:
- 🎵 **Music System (`yt-dlp` + FFmpeg)**:
  - `/play <search/URL>`: YouTube se music voice channel me play karega.
  - `/skip`: Current song skip karne ke liye.
  - `/stop`: Music stop karke voice channel leave karne ke liye.
- 🛡️ **Anti-Nuke / Anti-Raid System**:
  - Mass Channel Creation / Deletion Protection.
  - Mass Ban / Kick Protection.
  - Rogue Admins & Bots se Server Protection (Auto-Ban/Demote on malicious activity).
- 🖼️ **Fancy Embed Welcome System**:
  - Image wale screenshot jaisa fancy welcome embed format with thumbnail, member count & channel links.
- 🔄 **Auto-Push (`auto-push.ps1`)**:
  - GitHub pe auto-commit aur push ke liye.

## Setup Instructions:
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Make sure `ffmpeg` is installed on your system / hosting server (required for music playback).
3. Set your token in `.env`:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```
4. Enable **All Gateway Intents** (Message Content, Server Members, Presence) in Discord Developer Portal.
5. Run the bot:
   ```bash
   python bot.py
   ```
