import time
import discord
import aiosqlite
from discord import app_commands
from discord.ext import commands

DB = "bot.db"

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure(self, guild_id, user_id):
        async with aiosqlite.connect(DB) as db:
            await db.execute(
                "INSERT OR IGNORE INTO economy(guild_id,user_id,balance,last_daily) VALUES(?,?,0,0)",
                (guild_id, user_id)
            )
            await db.commit()

    @app_commands.command(name="balance", description="Check your balance.")
    async def balance(self, interaction):
        await self.ensure(interaction.guild.id, interaction.user.id)
        async with aiosqlite.connect(DB) as db:
            cur = await db.execute("SELECT balance FROM economy WHERE guild_id=? AND user_id=?",
                                   (interaction.guild.id, interaction.user.id))
            row = await cur.fetchone()
        await interaction.response.send_message(f"💰 Balance: **{row[0]} coins**")

    @app_commands.command(name="daily", description="Claim your daily coins.")
    async def daily(self, interaction):
        await self.ensure(interaction.guild.id, interaction.user.id)
        now = int(time.time())
        async with aiosqlite.connect(DB) as db:
            cur = await db.execute("SELECT last_daily FROM economy WHERE guild_id=? AND user_id=?",
                                   (interaction.guild.id, interaction.user.id))
            row = await cur.fetchone()
            if now - row[0] < 86400:
                remaining = 86400 - (now - row[0])
                return await interaction.response.send_message(
                    f"⏳ Daily already claimed. Try again in `{remaining//3600}h {(remaining%3600)//60}m`."
                )
            await db.execute(
                "UPDATE economy SET balance=balance+500,last_daily=? WHERE guild_id=? AND user_id=?",
                (now, interaction.guild.id, interaction.user.id)
            )
            await db.commit()
        await interaction.response.send_message("🎁 You received **500 coins**!")

    @app_commands.command(name="leaderboard", description="Show the server economy leaderboard.")
    async def leaderboard(self, interaction):
        async with aiosqlite.connect(DB) as db:
            cur = await db.execute(
                "SELECT user_id,balance FROM economy WHERE guild_id=? ORDER BY balance DESC LIMIT 10",
                (interaction.guild.id,)
            )
            rows = await cur.fetchall()
        if not rows:
            return await interaction.response.send_message("No economy data yet.")
        lines = [f"**{i}.** <@{uid}> — `{bal}` coins" for i, (uid, bal) in enumerate(rows, 1)]
        await interaction.response.send_message("🏆 **Economy Leaderboard**\n" + "\n".join(lines))

async def setup(bot):
    await bot.add_cog(Economy(bot))
