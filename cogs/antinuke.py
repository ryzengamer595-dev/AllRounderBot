import discord
from discord.ext import commands
import time

# Anti-Nuke Limits
CHANNEL_DELETE_LIMIT = 3
BAN_LIMIT = 3
TIME_WINDOW = 10 # Seconds

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_deletions = {}
        self.ban_actions = {}

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        async for entry in guild.audit_logs(action=discord.AuditLogAction.CHANNEL_DELETE, limit=1):
            user = entry.user
            if user.id == self.bot.user.id or user.id == guild.owner_id:
                return

            now = time.time()
            user_actions = self.channel_deletions.get(user.id, [])
            user_actions = [t for t in user_actions if now - t < TIME_WINDOW]
            user_actions.append(now)
            self.channel_deletions[user.id] = user_actions

            if len(user_actions) >= CHANNEL_DELETE_LIMIT:
                try:
                    await guild.ban(user, reason="[ANTI-NUKE] Mass Channel Deletion Detected!")
                    print(f"[ANTI-NUKE] Banned {user} for deleting multiple channels!")
                except Exception as e:
                    print(f"[ANTI-NUKE Error] Could not ban {user}: {e}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        async for entry in guild.audit_logs(action=discord.AuditLogAction.BAN, limit=1):
            executor = entry.user
            if executor.id == self.bot.user.id or executor.id == guild.owner_id:
                return

            now = time.time()
            user_bans = self.ban_actions.get(executor.id, [])
            user_bans = [t for t in user_bans if now - t < TIME_WINDOW]
            user_bans.append(now)
            self.ban_actions[executor.id] = user_bans

            if len(user_bans) >= BAN_LIMIT:
                try:
                    await guild.ban(executor, reason="[ANTI-NUKE] Mass Ban Triggered!")
                    print(f"[ANTI-NUKE] Banned rogue admin {executor}!")
                except Exception as e:
                    print(f"[ANTI-NUKE Error] Could not ban {executor}: {e}")

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
