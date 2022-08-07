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

youtube_dl.utils.bug_reports_message = lambda: ''

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

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {query}')

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        """if ctx.message.author.voice.channel:   # both bools
                channel = ctx.message.author.voice.channel  # find member's vc
        elif not ctx.message.author.voice.channel:
            await ctx.send(f'You are not in a voice channel', mention_author=False)

        if channel is not None:
            print('channel is not none')
            #await ctx.voice_client.change_voice_state(channel)
            #await ctx.voice_client.connect()
            await channel.connect()
            print('channel.connect()')"""

        if not ctx.voice_client.is_connected:
            channel = ctx.message.author.voice.channel
            channel.connect()


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

                voice.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options))
                print('voice.play')

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
        voice.pause()

    @commands.command()
    async def resume(self, ctx):
        voice = ctx.voice_client
        await voice.resume()

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.reply(f'Not connected to a voice channel.', mention_author = False)

    @play.before_invoke
    @stream.before_invoke
    @pause.before_invoke
    @resume.before_invoke
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