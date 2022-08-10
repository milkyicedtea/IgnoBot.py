#################
#               #
#     Music     #
#               #
#################

import os

import discord
from discord.ext import commands

import asyncio
import youtube_dl

import ctypes
import ctypes.util

find_opus = ctypes.util.find_library('opus')
discord.opus.load_opus(find_opus)

youtube_dl.utils.bug_reports_message = lambda: ''

# YTDL settings
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

# FFMPEG settings
ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data

        self.title = data.get('title')
        self.url = ""

    # Not used but OwO
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_looping = False
        self.was_paused = False
        
        self.url:str

    # Cool function :sunglus:
    async def stream_music(self, ctx, url):
        self.was_paused = False
        ctx = ctx

        if not ctx.voice_client.is_connected:
            channel = ctx.message.author.voice.channel
            channel.connect()

        while ctx.voice_client.is_connected:
            print('heloooooooooo')
            print(ctx.voice_client.is_playing())
            if not ctx.voice_client.is_playing():
                voice = ctx.voice_client
                with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                    print('with')
                    info = ydl.extract_info(url, download=False)
                    print('info')
                    url2 = info['formats'][0]['url']
                    print('url2')

                    await voice.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options))
                    print('voice.play')
                    
        """
            if ctx.voice_client.is_playing() == False:
                if self.is_looping is False:
                    return
                else:
                    self.stream_music(ctx = ctx, url = self.url)
        """

    # Makes the bot join a channel
    @commands.command(name = 'join')
    async def join_channel(self, ctx, *, channel: discord.VoiceChannel = None):
        if channel == None:
            if ctx.message.author.voice.channel:   # both bools
                channel = ctx.message.author.voice.channel  # find member's vc
            elif not ctx.message.author.voice.channel:
                await ctx.send(f'You are not in a voice channel', mention_author=False)

        if channel is not None:
            print('channel is not none')
            #await ctx.voice_client.change_voice_state(channel)
            #await ctx.voice_client.connect()
            await channel.connect()
        else:
            print('channel is none')

    # Plays from local (disabled for now)
    # @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {query}')

    # Streams from a url without predownloading
    @commands.command()
    async def stream(self, ctx, *, url):

        self.url = url
        await self.stream_music(ctx = ctx, url = self.url)

    """
    @commands.command(name = 'volume')
    async def volume(self, ctx, volume:int):
        if ctx.voice_client is None:
            return await ctx.send('Not connected to a voice channel.')

        new_volume = float(volume / 100)
        ctx.voice_client.source.volume = discord.PCMVolumeTransformer(new_volume)
        await ctx.send(f"Changed volume to {volume}%")
    """
    
    @commands.command()
    async def pause(self, ctx):
        voice = ctx.voice_client
        if self.was_paused is False:
            self.was_paused = True
            voice.pause()
        else:
            await ctx.send(f'The player is already paused')

    @commands.command()
    async def resume(self, ctx):
        voice = ctx.voice_client
        if self.was_paused is True:
            voice.resume()
            self.was_paused = False
        else:
            await ctx.send(f'The player is not paused')

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send(f'Not connected to a voice channel.')

    """
    @commands.command()
    async def loop(self, ctx):
        if ctx.voice_client():
            print('if')
            self.is_looping = not self.is_looping
            print(f'self.is_looping: {self.is_looping}')
            await ctx.send(f'Looping the current song.')
        else:
            print('else')
            await ctx.send(f'Not connected to a voice channel.')
    """

    # @play.before_invoke   (Bruh)
    @stream.before_invoke
    @stop.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

def setup(bot):
    bot.add_cog(Music(bot))