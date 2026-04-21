import asyncio

import discord

import yt_dlp

yt_dlp.utils.bug_reports_message = lambda: ''
ytdl_logs = False


class YTDLError(Exception):
    pass


class VoiceError(Exception):
    pass


class YTDLPCMVolumeTransformer(discord.PCMVolumeTransformer):
    # YTDL settings
    YTDL_OPTIONS = {
        'logtostderr': ytdl_logs,
        'format': 'm4a/bestaudio/best',
        'restrictfilenames': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio'
            # 'preferredcodec': 'm4a',
        }]
    }

    # FFMPEG settings
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    # Define custom YTDL options for playlist
    playlist_ytdl_options = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_flat': True,
        'skip_download': True  # This option skips the download step for playlists
    }

    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, interaction: discord.Interaction, audio_source: discord.FFmpegPCMAudio, info: dict):
        super().__init__(audio_source)
        self.audio_source = audio_source
        self.requester = interaction.user
        self.channel = interaction.channel
        self.info = info
        self.uploader: str = info.get('uploader')
        self.title: str = info.get('title')
        self.thumbnail = info.get('thumbnail')
        self.raw_duration: int = info.get('duration')
        self.str_duration: str = self.get_duration(int(info.get('duration')))
        self.url: str = info.get('webpage_url')
        self.stream_url: str = info.get('url')

    def __str__(self):
        return f"{self.title}, requested by {self.requester.mention}"

    @classmethod
    def create_source(cls, interaction: discord.Interaction, search: str):
        print(f"Creating source for: {search}")
        try:
            info = cls.ytdl.extract_info(f'ytsearch:{search}', download = False)['entries'][0]
            print(f"Source info extracted: {info.get('title')}")
            return cls(interaction, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), info)
        except Exception as e:
            print(f"Error creating source: {e}")
            return None

    @classmethod
    def extract_playlist_info(cls, playlist_url):
        """Extract video information from a YouTube playlist"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'extract_flat': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(playlist_url, download = False)
                return info
            except Exception as e:
                print(f"Error extracting playlist info: {e}")
                return None

    @staticmethod
    def get_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        duration = []
        if days > 0:
            duration.append(f'{days} days')
        if hours > 0:
            duration.append(f'{hours} hours')
        if minutes > 0:
            duration.append(f'{minutes} minutes')
        if seconds > 0:
            duration.append(f'{seconds} seconds')
        return ', '.join(duration)


class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.queue = []
        self.loop = False
        self.current_song = None
        self.should_play_next = True

    async def skip(self):
        if self.queue:
            # Stop the current song and play the next one
            self.voice_client.stop()
        else:
            await self.voice_client.disconnect()

    async def play_next_song(self):
        if not self.should_play_next:
            print("Playback stopped")
            return

        if self.queue and self.voice_client and self.voice_client.is_connected():
            try:
                song = self.queue.pop(0)
                print(f"Playing: {song.title}")
                self.current_song = song
                self.voice_client.play(song, after=self.on_playback_complete)
                print("Playback started")
            except Exception as e:
                print(f"Error playing next song: {e}")
                await self.play_next_song()
        else:
            print(f"Cannot play next song. Queue: {len(self.queue)}, Voice client connected: {self.voice_client and self.voice_client.is_connected()}")

    async def start_playing(self):
        print(f"Starting to play. Queue length: {len(self.queue)}")
        while self.queue:
            print(f"Playing next song. Remaining in queue: {len(self.queue)}")
            await self.play_next_song()
        print("Finished playing all songs in queue")

    async def async_task_after_playback(self):
        await self.play_next_song()

    def on_playback_complete(self, error):
        if error:
            print(f"An error occurred during playback: {error}")
        else:
            print("Playback completed successfully")
        if self.should_play_next:
            asyncio.run_coroutine_threadsafe(self.play_next_song(), self.bot.loop)
        else:
            print("Playback complete and stopped")

    def add_song_to_queue(self, song):
        self.queue.append(song)

    async def disconnect(self):
        if self.voice_client and self.voice_client.is_connected():
            self.voice_client.stop()
            await self.voice_client.disconnect()
            self.voice_client = None
            self.queue.clear()

    def get_voice_client(self, guild: discord.Guild):
        return discord.utils.get(self.bot.voice_clients, guild = guild)

    def stop(self):
        self.should_play_next = False
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        self.queue.clear()

