import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        channel = guild.system_channel or discord.utils.get(guild.text_channels, name="welcome") or discord.utils.get(guild.text_channels, name="entrance")

        if channel:
            embed = discord.Embed(
                title="Welcome!",
                description=(
                    f"**Welcome To {guild.name}**

"
                    f"**Enjoy Ur Stay Here**
"
                    f"┆ 📢 [ANNOUNCEMENT]
"
                    f"┆ ℹ️ [INFO]
"
                    f"┆ 📜 [RULES]

"
                    f"**User**
"
                    f"{member.mention} ({member.id})

"
                    f"**Member Count**
"
                    f"**{guild.member_count}**"
                ),
                color=discord.Color.from_rgb(46, 139, 87)
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            if guild.icon:
                embed.set_author(name=guild.name, icon_url=guild.icon.url)

            await channel.send(f"{member.mention}", embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
