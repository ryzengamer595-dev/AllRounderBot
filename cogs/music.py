import os
import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import collections
import urllib.request
import tarfile
import shutil

# Automatic Static FFmpeg Setup for Railway / Cloud
FFMPEG_PATH = "ffmpeg"
if not shutil.which("ffmpeg"):
    local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg_bin", "ffmpeg")
    if os.path.exists(local_ffmpeg):
        FFMPEG_PATH = local_ffmpeg
    else:
        try:
            print("📥 Downloading static FFmpeg binary for cloud environment...")
            os.makedirs("ffmpeg_bin", exist_ok=True)
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
            tar_path = "ffmpeg.tar.xz"
            urllib.request.urlretrieve(url, tar_path)
            with tarfile.open(tar_path, "r:xz") as tar:
                for member in tar.getmembers():
                    if member.name.endswith("bin/ffmpeg"):
                        member.name = os.path.basename(member.name)
                        tar.extract(member, "ffmpeg_bin")
                        break
            os.remove(tar_path)
            FFMPEG_PATH = os.path.join(os.getcwd(), "ffmpeg_bin", "ffmpeg")
            os.chmod(FFMPEG_PATH, 0o755)
            print("✅ FFmpeg successfully setup locally!")
        except Exception as e:
            print(f"⚠️ Could not auto-download ffmpeg: {e}")

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
    'default_search': 'scsearch',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
    'executable': FFMPEG_PATH
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.webpage_url = data.get('webpage_url', '')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data and data['entries']:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

class GuildMusicState:
    def __init__(self):
        self.queue = collections.deque()
        self.current = None
        self.last_played_title = None
        self.autoplay = True
        self.is_247 = False
        self.text_channel = None

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states = {}

    def get_state(self, guild_id):
        if guild_id not in self.states:
            self.states[guild_id] = GuildMusicState()
        return self.states[guild_id]

    async def play_next(self, guild, interaction=None):
        state = self.get_state(guild.id)
        vc = guild.voice_client

        if not vc or not vc.is_connected():
            return

        if len(state.queue) > 0:
            song_info, requester = state.queue.popleft()
            try:
                player = await YTDLSource.from_url(song_info.get('webpage_url') or song_info.get('title'), loop=self.bot.loop, stream=True)
                state.current = player
                state.last_played_title = player.title

                def after_playing(error):
                    if error:
                        print(f"Player error: {error}")
                    coro = self.play_next(guild)
                    fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
                    try:
                        fut.result()
                    except Exception as ex:
                        print(f"Error in after_playing coro: {ex}")

                vc.play(player, after=after_playing)

                if state.text_channel:
                    embed = discord.Embed(
                        title="🎵 Now Playing",
                        description=f"[{player.title}]({player.webpage_url})",
                        color=discord.Color.green()
                    )
                    embed.set_footer(text=f"Requested by {requester.display_name}")
                    await state.text_channel.send(embed=embed)
            except Exception as e:
                if state.text_channel:
                    await state.text_channel.send(f"❌ Error playing song: {e}")
                await self.play_next(guild)

        elif state.autoplay and state.last_played_title:
            try:
                clean_title = state.last_played_title.replace("Official Video", "").replace("MV", "").replace("Song", "")
                search_query = f"scsearch5:{clean_title} audio"
                data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False))
                entries = data.get('entries', [])
                
                next_song = None
                if len(entries) > 1:
                    next_song = entries[1]
                elif len(entries) == 1:
                    next_song = entries[0]

                if next_song:
                    state.queue.append((next_song, self.bot.user))
                    if state.text_channel:
                        embed = discord.Embed(
                            title="📻 Smart Autoplay",
                            description=f"Found similar track:\\n👉 [{next_song.get('title')}]({next_song.get('webpage_url')})",
                            color=discord.Color.purple()
                        )
                        await state.text_channel.send(embed=embed)
                    await self.play_next(guild)
                else:
                    state.current = None
                    if not state.is_247:
                        await vc.disconnect()
            except Exception as e:
                print(f"Autoplay error: {e}")
                state.current = None
                if not state.is_247:
                    await vc.disconnect()
        else:
            state.current = None
            if not state.is_247:
                if state.text_channel:
                    await state.text_channel.send("⏹️ Queue is empty. Leaving voice channel (Use `/mode247` to stay connected).")
                await vc.disconnect()

    @app_commands.command(name="join", description="Join your current Voice Channel")
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ You must be in a Voice Channel first!", ephemeral=True)

        voice_channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc:
            if vc.channel.id == voice_channel.id:
                return await interaction.response.send_message(f"👌 Already connected to {voice_channel.mention}!", ephemeral=True)
            await vc.move_to(voice_channel)
            return await interaction.response.send_message(f"🚚 Moved to {voice_channel.mention}!")

        await voice_channel.connect()
        await interaction.response.send_message(f"🔊 Joined {voice_channel.mention}!")

    @app_commands.command(name="leave", description="Leave the Voice Channel")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            state = self.get_state(interaction.guild_id)
            state.queue.clear()
            state.current = None
            await interaction.response.send_message("👋 Left the voice channel.")
        else:
            await interaction.response.send_message("❌ I am not in any voice channel.", ephemeral=True)

    @app_commands.command(name="play", description="Play any song from SoundCloud (Instant & Unblocked)")
    async def play(self, interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ You must be in a Voice Channel to play music!", ephemeral=True)

        await interaction.response.defer()

        guild = interaction.guild
        voice_channel = interaction.user.voice.channel