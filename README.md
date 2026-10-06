# All-Rounder Discord Bot (Slash Commands & Auto Push)

Full-featured modular Discord Bot with Slash Commands (`/`) built using `discord.py` (Cogs architecture).

## Features
- ⚡ **Slash Commands (`/`)**: All commands work with `/` as well as prefix `!`.
- 🔄 **Auto-Push (`auto-push.ps1`)**: Automatically syncs code changes to GitHub.
- 🛡️ **Moderation**: `/clear`, `/kick`, `/ban`, `/timeout`
- 📊 **Utility**: `/serverinfo`, `/userinfo`, `/ping`, `/help` + Welcome System
- 🎮 **Fun**: `/roll`, `/8ball`, `/coinflip`
- ⭐ **Leveling & Economy**: `/rank`, `/daily`, `/balance`
- 🎫 **Tickets**: `/setup_ticket`, `/close` (Interactive Support Tickets)

## Setup Instructions
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Enable **All Gateway Intents** (Message Content, Server Members, Presence) in the Discord Developer Portal under your Bot settings.
3. Put your bot token in `.env`:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```
5. To enable auto-push to GitHub, open PowerShell in VS Code and run:
   ```powershell
   .\auto-push.ps1
   ```
