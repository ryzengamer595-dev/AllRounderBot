import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import collections

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
    'default_search': 'ytsearch',
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
        self.webpage_url = data.get('webpage_url', '')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
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
                player = await YTDLSource.from_url(song_info['webpage_url'] or song_info['title'], loop=self.bot.loop, stream=True)
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
                # Search similar songs based on last played song's title
                clean_title = state.last_played_title.replace("Official Video", "").replace("MV", "").replace("Song", "")
                search_query = f"ytsearch5:{clean_title} similar song"
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
                            description=f"Found similar song based on **{state.last_played_title}**:
👉 [{next_song.get('title')}]({next_song.get('webpage_url')})",
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

    @app_commands.command(name="play", description="Play a song or add to queue from YouTube")
    async def play(self, interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ You must be in a Voice Channel to play music!", ephemeral=True)

        await interaction.response.defer()

        guild = interaction.guild
        voice_channel = interaction.user.voice.channel
        vc = guild.voice_client
        state = self.get_state(guild.id)
        state.text_channel = interaction.channel

        if not vc or not vc.is_connected():
            try:
                vc = await voice_channel.connect()
            except Exception as e:
                return await interaction.followup.send(f"❌ Could not connect to Voice Channel: {e}")

        try:
            loop = self.bot.loop
            search_query = query if query.startswith("http") else f"ytsearch:{query}"
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False))

            if 'entries' in data and data['entries']:
                song_info = data['entries'][0]
            else:
                song_info = data

            if vc.is_playing() or vc.is_paused():
                state.queue.append((song_info, interaction.user))
                embed = discord.Embed(
                    title="📝 Added to Queue",
                    description=f"[{song_info.get('title')}]({song_info.get('webpage_url', '')})",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Position in Queue", value=str(len(state.queue)))
                embed.set_footer(text=f"Requested by {interaction.user.display_name}")
                await interaction.followup.send(embed=embed)
            else:
                state.queue.append((song_info, interaction.user))
                await interaction.followup.send("🔎 Fetching track details and starting playback...")
                await self.play_next(guild, interaction)

        except Exception as e:
            await interaction.followup.send(f"❌ Error fetching song details: {e}")

    @app_commands.command(name="queue", description="Show the current music queue")
    async def queue_cmd(self, interaction: discord.Interaction):
        state = self.get_state(interaction.guild_id)
        embed = discord.Embed(title="🎶 Music Queue", color=discord.Color.gold())

        if state.current:
            embed.add_field(name="▶️ Currently Playing", value=f"[{state.current.title}]({state.current.webpage_url})", inline=False)
        else:
            embed.add_field(name="▶️ Currently Playing", value="Nothing playing right now.", inline=False)

        if len(state.queue) == 0:
            embed.add_field(name="📑 Up Next", value="No songs in queue.", inline=False)
        else:
            queue_list = ""
            for idx, (song, requester) in enumerate(state.queue, start=1):
                queue_list += f"`{idx}.` [{song.get('title')}]({song.get('webpage_url', '')}) | Req by {requester.mention}\n"
                if idx >= 10:
                    queue_list += f"*...and {len(state.queue) - 10} more songs*"
                    break
            embed.add_field(name="📑 Up Next", value=queue_list, inline=False)

        embed.set_footer(text=f"24/7 Mode: {'ON 🟢' if state.is_247 else 'OFF 🔴'} | Autoplay: {'ON 🟢' if state.autoplay else 'OFF 🔴'}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="autoplay", description="Enable or Disable YouTube Smart Autoplay")
    async def autoplay_cmd(self, interaction: discord.Interaction):
        state = self.get_state(interaction.guild_id)
        state.autoplay = not state.autoplay
        status = "ENABLED 🟢" if state.autoplay else "DISABLED 🔴"
        await interaction.response.send_message(f"📻 **Smart Autoplay** has been **{status}**!")

    @app_commands.command(name="mode247", description="Enable or Disable 24/7 Voice Channel Mode")
    async def mode247_cmd(self, interaction: discord.Interaction):
        state = self.get_state(interaction.guild_id)
        state.is_247 = not state.is_247
        status = "ENABLED 🟢" if state.is_247 else "DISABLED 🔴"
        await interaction.response.send_message(f"🔋 **24/7 Mode** has been **{status}**!")

    @app_commands.command(name="nowplaying", description="Show details of current playing track")
    async def nowplaying(self, interaction: discord.Interaction):
        state = self.get_state(interaction.guild_id)
        if state.current:
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"[{state.current.title}]({state.current.webpage_url})",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ No song is currently playing.", ephemeral=True)

    @app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped current track!")
        else:
            await interaction.response.send_message("❌ No track is currently playing.", ephemeral=True)

    @app_commands.command(name="stop", description="Stop music and clear queue")
    async def stop(self, interaction: discord.Interaction):
        state = self.get_state(interaction.guild_id)
        state.queue.clear()
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
            if not state.is_247:
                await vc.disconnect()
            await interaction.response.send_message("⏹️ Stopped playback and cleared queue!")
        else:
            await interaction.response.send_message("❌ Bot is not connected to a voice channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
