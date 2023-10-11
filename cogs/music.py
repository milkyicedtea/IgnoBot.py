#################
#               #
#     Music     #
#               #
#################

import os
import platform

import discord
from discord import app_commands
from discord.ext import commands

from builtins import bot

import yt_dlp

import asyncio
import ctypes.util


# print(platform.system())
if platform.system() != 'Windows':
    find_opus = ctypes.util.find_library('opus')
    discord.opus.load_opus(find_opus)

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
        self.bot = bot
        self.voice_client = None
        self.queue = []     # Inizialize an empty queue to store song
        self.loop = False

    def get_voice_client(self, guild: discord.Guild):
        return discord.utils.get(self.bot.voice_clients, guild = guild)

    def add_song_to_queue(self, song):
        self.queue.append(song)

    async def play_next_song(self):
        print('playing next song')
        if self.queue:
            song = self.queue.pop(0)
            self.current_song = song
            self.voice_client.play(song, after = self.play_next_song)
        elif self.loop:
            song = self.current_song
            self.voice_client.play(song, after = self.play_next_song)

    async def wait_for_song_end(self):
        while self.voice_client.is_playing() or self.voice_client.is_paused():
            await asyncio.sleep(1)

    async def start_playing(self):
        while self.queue:
            await self.play_next_song()


class Music(commands.Cog):
    def __init__(self, bot):
        self.music_player = MusicPlayer(bot)
        self.bot = bot

    @app_commands.command(name = 'play')
    async def play(self, interaction: discord.Interaction, search: str):
        await interaction.response.defer(thinking = False)
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.followup.send('You are not connected to a voice channel.')
            return
        elif not self.music_player.voice_client:
            channel = interaction.user.voice.channel
            self.music_player.voice_client = await channel.connect()

        print('creating source and song')
        song = YTDLPCMVolumeTransformer.create_source(interaction, search)
        self.music_player.add_song_to_queue(song)

        if not self.music_player.voice_client.is_playing():
            await self.music_player.start_playing()

        await interaction.followup.send(f'Added to the queue: **{song.title}**')

    @app_commands.command(name = 'stop')
    async def stop(self, interaction: discord.Interaction):
        if self.music_player.voice_client and self.music_player.voice_client.is_connected():
            self.music_player.voice_client.stop()
            await interaction.response.send_message('Music playback stopped.', ephemeral = True)
        else:
            await interaction.response.send_message('The bot is not connected to a voice channel.', ephemeral = True)

    @app_commands.command(name = 'queue')
    async def queue(self, interaction: discord.Interaction):
        queue_message = '\n'.join(f'{index + 1}. {song.title}' for index, song in enumerate(self.music_player.queue))
        if queue_message:
            await interaction.response.send_message(f'Queue:\n{queue_message}', ephemeral = True)
        else:
            await interaction.response.send_message('The queue is empty.', ephemeral = True)

    @app_commands.command(name = 'disconnect')
    async def disconnect(self, interaction: discord.Interaction):
        await self.music_player.disconnect()
        await interaction.response.send_message(f'Disconnected from {interaction.user.voice.channel.mention}.', ephemeral = True)

    @app_commands.command(name = 'pause')
    async def pause(self, interaction: discord.Interaction):
        self.music_player.voice_client.pause()
        await interaction.response.send_message('Music has been paused.', ephemeral = True)

    @app_commands.command(name = 'resume')
    async def resume(self, interaction: discord.Interaction):
        self.music_player.voice_client.resume()
        await interaction.response.send_message('Music has been resumed.', ephemeral = True)

    @app_commands.command(name = 'loop')
    async def loop(self, interaction: discord.Interaction):
        self.music_player.loop = not self.music_player.loop
        loop_status = 'enabled' if self.music_player.loop else 'disabled'
        await interaction.response.send_message(f'Looping is now {loop_status}.', ephemeral = True)

    @app_commands.command(name = 'skip')
    async def skip(self, interaction: discord.Interaction):
        if self.music_player.voice_client and self.music_player.voice_client.is_playing():
            self.music_player.voice_client.stop()
            await self.music_player.play_next_song()


async def setup(bot):
    await bot.add_cog(Music(bot))
