import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Play a song from YouTube (Search or URL)")
    async def play(self, interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ You must be in a Voice Channel to play music!", ephemeral=True)

        await interaction.response.defer()

        voice_channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if not vc:
            vc = await voice_channel.connect()

        try:
            player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
            vc.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"[{player.title}]({player.data.get('webpage_url', '')})",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Error playing music: {e}")

    @app_commands.command(name="skip", description="Skip the currently playing song")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped current song!")
        else:
            await interaction.response.send_message("❌ No song is currently playing.", ephemeral=True)

    @app_commands.command(name="stop", description="Stop music and leave voice channel")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("⏹️ Stopped playing and left voice channel.")
        else:
            await interaction.response.send_message("❌ I am not in a voice channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
