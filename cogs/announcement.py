import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Announcement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="massdm", description="Server ke sabhi members ko DM bhejo (Admin Only)")
    @app_commands.default_permissions(administrator=True)
    async def massdm(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        success = 0
        failed = 0
        
        await interaction.guild.chunk()
        
        for member in interaction.guild.members:
            if member.bot:
                continue
            try:
                await member.send(f"📢 **Announcement from {interaction.guild.name}:**\n\n{message}")
                success += 1
                await asyncio.sleep(0.5)
            except Exception:
                failed += 1
                
        await interaction.followup.send(f"✅ Mass DM Complete!\nSuccessfully Sent: `{success}`\nFailed (DMs Closed): `{failed}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Announcement(bot))