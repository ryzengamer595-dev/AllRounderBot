import discord
from discord.ext import commands

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bad_words = {"spamword", "badword"}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        content = message.content.lower()
        if any(word in content for word in self.bad_words):
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {message.author.mention}, please keep the chat clean.",
                    delete_after=5
                )
            except discord.HTTPException:
                pass

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
