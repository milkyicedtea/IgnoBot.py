import discord

import yt_dlp

import asyncio

import threading

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
        print('cs')
        try:
            print('try')
            info = cls.ytdl.extract_info(f'ytsearch:{search}', download = False)['entries'][0]
        except YTDLError as err:
            print(err)
            return interaction.followup.send('Something went wrong during the content search!', ephemeral = True)
        return cls(interaction, discord.FFmpegPCMAudio(info.get('url'), **cls.FFMPEG_OPTIONS), info)

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
        self.playback_thread = None
        self.bot = bot
        self.voice_client = None
        self.queue = asyncio.Queue()     # Inizialize an empty queue to store song
        self.loop = False
        self.current_song = None

        playback_thread = threading.Thread(target = self.start_playback_thread)
        playback_thread.daemon = True
        playback_thread.start()

    def after(self, error):
        if error:
            print(f"An error occurred: {error}")
        else:
            # Play the next song when the current one finishes
            self.play_next_song()

    async def play_music_thread(self):
        while True:
            song = await self.queue.get()
            self.current_song = song

            self.voice_client.play(song, after = lambda e: self.after(e))
            while self.voice_client.is_playing():
                await asyncio.sleep(1)

            self.queue.pop(0)

    def start_playback_thread(self):
        print('start_playback_thread')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.play_music_thread())

    def get_voice_client(self, guild: discord.Guild):
        return discord.utils.get(self.bot.voice_clients, guild = guild)

    async def disconnect(self):
        if self.voice_client and self.voice_client.is_connected():
            self.voice_client.stop()
            await self.voice_client.disconnect()
            self.voice_client = None
            self.queue.clear()

    async def stop(self):
        self.voice_client.stop()

    def add_song_to_queue(self, song):
        self.queue.append(song)

    async def play_next_song(self):
        print('playing next song')
        if not self.queue:
            return
        elif self.loop:
            print('self.loop')
            song = self.current_song
            self.voice_client.play(song, after = self.play_next_song)
        else:
            print('self.queue')
            print(f'playing next song')
            song = self.queue.pop(0)
            print(song.title)
            self.current_song = song
            self.voice_client.play(song, after = self.play_next_song)
            await self.wait_for_song_end()

    async def wait_for_song_end(self):
        while self.voice_client.is_playing() or self.voice_client.is_paused():
            await asyncio.sleep(1)

    async def start_playing(self):
        while self.queue:
            await self.play_next_song()
