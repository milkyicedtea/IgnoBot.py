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

import asyncio
import yt_dlp

import ctypes.util

print(platform.system())
if platform.system() != 'Windows':
    find_opus = ctypes.util.find_library('opus')
    discord.opus.load_opus(find_opus)

yt_dlp.utils.bug_reports_message = lambda: ''

# YTDL settings
ytdl_format_options = {
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
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    'options': '-vn'
}


class Music(commands.Cog):
    def __init__(self, bot):
        self.voice = None
        self.bot = bot

    application_check = app_commands.checks.has_permissions

    @app_commands.command(name = 'play')
    async def play(self, interaction: discord.Interaction, search: str):
        print(search)
        print(type(search))
        try:
            channel = interaction.user.voice.channel
        except AttributeError:
            return await interaction.response.send_message('You are not in a voice channel!', ephemeral = True)

        if self.voice:
            voice = self.voice
        else:
            voice = await channel.connect()
            self.voice = voice
        print(f'self.voice is {self.voice}')
        print(f'voice is {voice}')

        with yt_dlp.YoutubeDL(ytdl_format_options) as ytdl:
            try:
                print('try')
                info = ytdl.extract_info(f'ytsearch:{search}', download = False)['entries'][0]
            except:
                print('except')
                return interaction.response.send_message('Something went wrong during the content search!', ephemeral = True)

            stream = info['url']
            print(stream)
            url = info['webpage_url']
            song_duration = info['duration']
            print(f'songDuration is {song_duration} seconds')
            song_name = info['title']
            print(f'songName is {song_name}')

            try:
                if not voice.is_playing():
                    voice.play(discord.PCMVolumeTransformer((discord.FFmpegPCMAudio(stream, **ffmpeg_options))))
                    print('play started')
                else:
                    while voice.is_playing():
                        await asyncio.sleep(1)
                    voice.play(discord.PCMVolumeTransformer((discord.FFmpegPCMAudio(stream, **ffmpeg_options))))
                await interaction.response.send_message(f'Playing {song_name} in {voice.channel.mention}', ephemeral = True)
            except Exception as exx:
                print(exx)
                await interaction.response.send_message('Something went wrong while trying to play your search!', ephemeral = True)

    @app_commands.command(name = 'printpl')
    @application_check(manage_guild = True)
    async def printpl(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.playlist, ephemeral = True)

    # Makes the bot join a channel (disabled because unnecessary)
    @app_commands.command(name = 'join')
    async def join_channel(self, interaction: discord.Interaction):
        try:
            channel = interaction.user.voice.channel
        except AttributeError:
            return await interaction.response.send_message('You are not in a voice channel!', ephemeral = True)

        self.voice = await channel.connect()
        await interaction.response.send_message(f'Connected to {channel.mention}')

    """
    @commands.command(name = 'volume')
    async def volume(self, ctx, volume:int):
        if ctx.voice_client is None:
            return await ctx.send('Not connected to a voice channel.')

        new_volume = float(volume / 100)
        ctx.voice_client.source.volume = discord.PCMVolumeTransformer(new_volume)
        await ctx.send(f"Changed volume to {volume}%")
    """

    @app_commands.command(name = 'pause')
    async def pause(self, interaction: discord.Interaction):
        voice: discord.VoiceClient = self.voice or None
        if voice:
            if voice.is_playing():
                voice.pause()
                await interaction.response.send_message('Paused music playback.', ephemeral = True)
            else:
                await interaction.response.send_message('Nothing is being played.', ephemeral = True)
        else:
            await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)

    @app_commands.command(name = 'resume')
    async def resume(self, interaction: discord.Interaction):
        voice: discord.VoiceClient = self.voice or None
        if voice:
            if voice.is_paused():
                voice.resume()
                await interaction.response.send_message('Resumed music playback.', ephemeral = True)
            else:
                await interaction.response.send_message('The player is not paused.', ephemeral = True)
        else:
            await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)

    @app_commands.command(name = 'stop')
    async def stop(self, interaction: discord.Interaction):
        voice: discord.VoiceClient = self.voice or None
        if voice:
            await voice.disconnect()
            self.voice = None
            await interaction.response.send_message(f'Disconnected from {voice.channel.mention}', ephemeral = True)
        else:
            await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)

    @app_commands.command(name = 'skip')
    async def skip(self, interaction: discord.Interaction):
        voice: discord.VoiceClient = self.voice or None
        if voice:
            ...
        else:
            await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)

    @app_commands.command(name = 'loop')
    async def loop(self, interaction: discord.Interaction):
        voice: discord.VoiceClient = self.voice or None
        if voice:
            voice.loop.create_task()
            await interaction.response.send_message('Looped the current playback', ephemeral = True)
        else:
            await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)

    @app_commands.command(name = 'volume')
    async def volume(self, interaction: discord.Interaction, volume: int):
        voice: discord.VoiceClient = self.voice or None
        if voice:
            try:
                voice.volume = volume / 100
                await interaction.response.send_message(f'Volume set to {volume/100}%', ephemeral = True)
            except Exception as exx:
                print(exx)
                await interaction.response.send_message('Something went wrong while trying to change the volume!', ephemeral = True)
        else:
            await interaction.response.send_message('Not connected to any voice channel.', ephemeral = True)


async def setup(bot):
    await bot.add_cog(Music(bot))