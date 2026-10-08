import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = next((c for c in member.guild.text_channels if "welcome" in c.name.lower()), None)
        if channel:
            embed = discord.Embed(
                title="👋 Welcome!",
                description=f"Welcome {member.mention} to **{member.guild.name}**!",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
