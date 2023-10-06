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
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
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


class YTDLFFmpegPCMAudio(discord.FFmpegPCMAudio):
    # YTDL settings
    YTDL_OPTIONS = {
        'logtostderr': True,
        'format': 'm4a/bestaudio/best',
        'restrictfilenames': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }

    # FFMPEG settings
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, interaction: discord.Interaction, info: dict, audio_source: str):
        super().__init__(audio_source, **self.FFMPEG_OPTIONS)

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
        return cls(interaction, info, info.get('url'))

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
        self.queue = asyncio.Queue()
        self.playing = False

    async def play_music(self):
        while True:
            song = await self.queue.get()
            self.voice_client.play(song, after = lambda e: self.bot.loop.call_soon_threadsafe(self.queue.task_done))
            await self.queue.join()

    async def join_voice_channel(self, interaction: discord.Interaction):
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message('You are not connected to a voice channel.')
            return False

        # if self.voice_client is not None and self.voice_client.is_playing():
        #     await interaction.response.send_message('I am already playing music.')
        #     return False

        channel = interaction.user.voice.channel
        self.voice_client = await channel.connect()
        return True

    def add_song_to_queue(self, song):
        self.queue.put_nowait(song)

    def stop_music(self):
        if self.voice_client is not None and self.voice_client.is_playing():
            self.voice_client.stop()

    async def disconnect(self):
        if self.voice_client is not None and self.voice_client.is_connected():
            await self.voice_client.disconnect()


class Music(commands.Cog):
    def __init__(self, bot):
        self.music_player = MusicPlayer(bot)
        self.bot = bot

    @app_commands.command(name = 'play')
    async def play(self, interaction: discord.Interaction, search: str):
        await interaction.response.defer(ephemeral = True, thinking = False)
        if not await self.music_player.join_voice_channel(interaction):
            return

        song = YTDLPCMVolumeTransformer.create_source(interaction, search)
        self.music_player.add_song_to_queue(song)

        if not self.music_player.playing:
            self.music_player.playing = True
            bot.loop.create_task(self.music_player.play_music())
            await interaction.followup.send(f'Now playing: **{song.title}** in {interaction.user.voice.channel.mention}', ephemeral = True)

    @app_commands.command(name = 'stop')
    async def stop(self, interaction: discord.Interaction):
        self.music_player.stop_music()
        await interaction.response.send_message('Music has been stopped.', ephemeral = True)

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

    @app_commands.command(name = 'queue')
    async def queue(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed = self.music_player.now_playing_embed())

    @app_commands.command(name = 'loop')
    async def loop(self, interaction: discord.Interaction):
        self.music_player.voice_client.loop = not self.music_player.voice_client.loop
        await interaction.response.send_message(f'Looping: {self.music_player.voice_client.loop}', ephemeral = True)







# class Music(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.voice_client = None
#         self.queue = asyncio.Queue()
#         self.playing = False
#
#     application_check = app_commands.checks.has_permissions
#
#     @app_commands.command(name = 'play')
#     async def play(self, interaction: discord.Interaction, search: str):
#         if interaction.user.voice:
#             channel = interaction.user.voice.channel
#             await interaction.response.defer(ephemeral = True, thinking = False)
#         else:
#             return await interaction.response.send_message('You are not in a voice channel!', ephemeral = True)
#
#         if self.voice:
#             voice = self.voice
#         else:
#             voice = await channel.connect()
#             self.voice = voice
#
#         source = YTDLFFmpegPCMAudio.create_source(interaction, search)
#
#         if not (self.last_song == source):
#             self.last_song = source
#
#         try:
#             """if self.loop:
#                 print('self.loop if')
#                 while self.loop:
#                     if not self.voice.is_playing():
#                         print('trying to play')
#                         try:
#                             self.voice.play(discord.PCMVolumeTransformer(self.last_song))
#                             await asyncio.sleep(source.raw_duration)
#                         except Exception as exx:
#                             print(exx)
#                         print(self.last_song)
#                         await interaction.followup.send(f'Playing {source.title} in {voice.channel.mention}', ephemeral = True)
#                     else:
#                         await asyncio.sleep(5)
#
#             else:
#                 if self.voice.is_playing():
#                     self.voice.source.cleanup(); self.voice.stop()
#                     await asyncio.sleep(1)
#                     self.voice.play(discord.PCMVolumeTransformer(source))
#                     print(self.voice.is_playing())
#                 else:
#                     self.voice.play(discord.PCMVolumeTransformer(source))
#                 await interaction.followup.send(f'Playing {source.title} in {voice.channel.mention}', ephemeral = True)"""
#
#             if self.voice.is_playing():
#                 self.voice.source.cleanup(); self.voice.stop()
#                 await asyncio.sleep(1)
#                 self.voice.play(discord.PCMVolumeTransformer(source))
#                 print(self.voice.is_playing())
#             else:
#                 self.voice.play(discord.PCMVolumeTransformer(source))
#             await interaction.followup.send(f'Playing {source.title} in {voice.channel.mention}', ephemeral = True)
#
#         except VoiceError as err:
#             print(err)
#             await interaction.followup.send('Something went wrong while trying to play your search!', ephemeral = True)
#         except TypeError as err:
#             print(err)
#             await interaction.followup.send('Something went wrong while trying to play your search!', ephemeral = True)
#         except Exception as err:
#             print(err)
#             await interaction.followup.send('Something went wrong while trying to play your search!', ephemeral = True)
#
#         """source = YTDLPCMVolumeTransformer.create_source(interaction, search)
#         song = Song(source)
#
#         # print(source.stream_url)
#         print(self.voice)
#         print(voice)
#
#         try:
#             self.voice.play(discord.PCMVolumeTransformer(song.source.audio_source))
#             # self.voice.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source.stream_url, **YTDLSource.FFMPEG_OPTIONS)))
#             # await asyncio.sleep(10)
#             print(self.voice.is_playing())
#             await interaction.followup.send(f'Playing {song.title} in {voice.channel.mention}', ephemeral = True)
#         except VoiceError as err:
#             print(err)
#             await interaction.followup.send('Something went wrong while trying to play your search!', ephemeral = True)
#         except TypeError as err:
#             print(err)
#             await interaction.followup.send('Something went wrong while trying to play your search!', ephemeral = True)
#         except Exception as err:
#             print(err)"""
#
#     @app_commands.command(name = 'loop')
#     async def loop(self, interaction: discord.Interaction):
#         try:
#             print(self.loop)
#             self.loop = not self.loop
#             if self.loop:
#                 await interaction.response.send_message('Songs loop enabled')
#             else:
#                 await interaction.response.send_message('Songs loop disabled')
#         except Exception as exx:
#             print(exx)
#
#     @app_commands.command(name = 'printqueue')
#     async def queue(self, interaction: discord.Interaction):
#         for song in self.voice.queue.songs:
#             print(song.source.title)
#
#     @app_commands.command(name = 'printstream')
#     @application_check(administrator = True)
#     async def printstream(self, interaction: discord.Interaction, search: str):
#         await interaction.response.defer(ephemeral = True)
#         stream = YTDLPCMVolumeTransformer.create_source(interaction, search)
#
#         print(stream.requester,
#               stream.channel,
#               stream.uploader,
#               stream.title,
#               stream.thumbnail,
#               stream.raw_duration,
#               stream.str_duration,
#               stream.url,
#               stream.stream_url)
#
#         await interaction.followup.send('got it', ephemeral = True)
#
#     """@app_commands.command(name = 'printinfo')
#     @application_check(manage_guild = True)
#     async def printinfo(self, interaction: discord.Interaction, search: str):
#         with yt_dlp.YoutubeDL(ytdl_format_options) as ytdl:
#             info = ytdl.extract_info(f'ytsearch:{search}', download = False)['entries'][0]
#         print(info['url'], info['duration'], info['title'], info['webpage_url'], info['uploader'], sep = '\n')
#         await interaction.response.send_message('alr', ephemeral = True)"""
#
#     @app_commands.command(name = 'join')
#     async def join_channel(self, interaction: discord.Interaction):
#         """Makes the bot join a channel"""
#         try:
#             channel = interaction.user.voice.channel
#         except AttributeError:
#             return await interaction.response.send_message('You are not in a voice channel!', ephemeral = True)
#
#         self.voice = await channel.connect()
#         await interaction.response.send_message(f'Connected to {channel.mention}')
#
#     """
#     @commands.command(name = 'volume')
#     async def volume(self, ctx, volume:int):
#         if ctx.voice_client is None:
#             return await ctx.send('Not connected to a voice channel.')
#
#         new_volume = float(volume / 100)
#         ctx.voice_client.source.volume = discord.PCMVolumeTransformer(new_volume)
#         await ctx.send(f"Changed volume to {volume}%")
#     """
#
#     @app_commands.command(name = 'pause')
#     async def pause(self, interaction: discord.Interaction):
#         """Pauses the current player"""
#         voice: discord.VoiceClient = self.voice or None
#         if voice:
#             if voice.is_playing():
#                 voice.pause()
#                 await interaction.response.send_message('Paused music playback.', ephemeral = True)
#             else:
#                 await interaction.response.send_message('Nothing is being played.', ephemeral = True)
#         else:
#             await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)
#
#     @app_commands.command(name = 'resume')
#     async def resume(self, interaction: discord.Interaction):
#         """Resumes the current player"""
#         voice: discord.VoiceClient = self.voice or None
#         if voice:
#             if voice.is_paused():
#                 voice.resume()
#                 await interaction.response.send_message('Resumed music playback.', ephemeral = True)
#             else:
#                 await interaction.response.send_message('The player is not paused.', ephemeral = True)
#         else:
#             await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)
#
#     @app_commands.command(name = 'stop')
#     async def stop(self, interaction: discord.Interaction):
#         voice: discord.VoiceClient = self.voice or None
#         if voice:
#             voice.stop()
#             await voice.disconnect()
#             self.voice = None
#             await interaction.response.send_message(f'Disconnected from {voice.channel.mention}', ephemeral = True)
#         else:
#             await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)
#
#     @app_commands.command(name = 'skip')
#     async def skip(self, interaction: discord.Interaction):
#         voice: discord.VoiceClient = self.voice or None
#         if voice:
#             ...
#         else:
#             await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)
#
#     @app_commands.command(name = 'volume')
#     async def volume(self, interaction: discord.Interaction, volume: int):
#         voice: discord.VoiceClient = self.voice or None
#         if voice:
#             try:
#                 voice.volume = volume / 100
#                 await interaction.response.send_message(f'Volume set to {volume / 100}%', ephemeral = True)
#             except Exception as exx:
#                 print(exx)
#                 await interaction.response.send_message('Something went wrong while trying to change the volume!', ephemeral = True)
#         else:
#             await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)


async def setup(bot):
    await bot.add_cog(Music(bot))
