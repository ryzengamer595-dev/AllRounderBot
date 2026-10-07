# All-Rounder Discord Bot (OAuth2 YouTube Authentication & Permanent Hosting Fix)

Full-featured modular Discord Bot with Slash Commands (`/`).

## 🔑 YouTube OAuth2 Setup (One-Time Authentication):
This bot uses YouTube OAuth2 authentication via `yt-dlp`. 

### First-Time Running Instructions:
1. Terminal par bot run karein:
   ```bash
   python bot.py
   ```
2. Terminal console par ek message aayega:
   `To authenticate, visit https://www.google.com/device and enter code: XXX-XXX-XXX`
3. Us link par jaakar code enter karein aur apne Google account se **Allow** karein.
4. Authorization ke baad token local cache (`yt-oauth2.cache`) me save ho jayega. Uske baad hosting par lifetime bina kisi cookie error ke songs play hongge!

## ⚡ Commands Included:
- **Music**: `/play`, `/queue`, `/autoplay`, `/mode247`, `/join`, `/leave`, `/skip`, `/stop`, `/nowplaying`.
- **Broadcast**: `/message`, `/message_all`.
- **Bot Info**: `/owner` (Owner: Akram), `/ping`, `/serverinfo`, `/userinfo`, `/help`.
- **Protection**: Anti-Nuke, Welcome Embeds, Moderation, Tickets, Fun & Leveling.
