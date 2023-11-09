#################
#               #
#     Music     #
#               #
#################
import os
import platform
import dotenv
import threading

import discord
from discord import app_commands
from discord.ext import commands

import yt_dlp

import spotipy
from spotipy import SpotifyOAuth

import asyncio
import ctypes.util

from cogs.utils.music_helper import YTDLPCMVolumeTransformer, MusicPlayer


SPOTIPY_CLIENT_ID = dotenv.get_key('.env', 'spotify_client_id')
SPOTIPY_CLIENT_SECRET = dotenv.get_key('.env', 'spotify_client_secret')
SPOTIPY_REDIRECT_URI = dotenv.get_key('.env', 'spotify_redirect_uri')

sp = spotipy.Spotify(auth_manager = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI))


# print(platform.system())
if platform.system() != 'Windows':
    find_opus = ctypes.util.find_library('opus')
    discord.opus.load_opus(find_opus)


class Music(commands.Cog):
    def __init__(self, bot):
        self.downloading = False
        self.music_player = MusicPlayer(bot)
        self.bot = bot

    async def download_and_enqueue_songs(self, interaction,  entries):
        chunk_size = 10
        # links_list = [entry['url'] for entry in entries[1:]]
        for i in range(0, len(entries), chunk_size):
            chunk = entries[1:][i:i + chunk_size]
            print(chunk)
            links_list = [entry['url'] for entry in chunk]
            print(len(links_list), links_list)
            for link in links_list:
                song = YTDLPCMVolumeTransformer.create_source(interaction, link)
                self.music_player.add_song_to_queue(song)
                await asyncio.sleep(5)
        print('finished downloading the playlist')

    async def play_youtube_search(self, interaction: discord.Interaction, search: str):
        """Generic request searches from YouTube."""
        song = YTDLPCMVolumeTransformer.create_source(interaction, search)
        self.music_player.add_song_to_queue(song)
        await interaction.followup.send(f'Added to queue: **{song.title}**')

        if not self.music_player.voice_client.is_playing():
            await self.music_player.start_playing()

    async def play_individual_youtube_video(self, interaction: discord.Interaction, video_url: str):
        """Plays/Adds to the queue a single YouTube video"""
        song = YTDLPCMVolumeTransformer.create_source(interaction, video_url)
        self.music_player.add_song_to_queue(song)
        await interaction.followup.send(f'Added to the queue: **{song.title}**')

        if not self.music_player.voice_client.is_playing():
            await self.music_player.start_playing()

    async def play_individual_spotify_track(self, interaction: discord.Interaction, track_url: str):
        """Plays/Adds to the queue a single Spotify track"""
        song = YTDLPCMVolumeTransformer.create_source(interaction, track_url)
        self.music_player.add_song_to_queue(song)
        await interaction.followup.send(f'Added to the queue: **{song.title}**')

        if not self.music_player.voice_client.is_playing():
            await self.music_player.start_playing()

    async def play_youtube_playlist(self, interaction: discord.Interaction, playlist_url: str):
        """Plays/Adds to the queue a YouTube playlist"""

        # # Define custom YTDL options for playlist
        # playlist_ytdl_options = {
        #     'format': 'bestaudio/best',
        #     'quiet': True,
        #     'extract_flat': True,
        #     'skip_download': True  # This option skips the download step for playlists
        # }

        channel = interaction.channel

        playlist_info = YTDLPCMVolumeTransformer.extract_playlist_info(playlist_url)

        if 'entries' in playlist_info:
            entries = playlist_info['entries']
            print(type(entries[0]))
            print(type(entries))
            print(len(entries))
            if not entries:
                await interaction.followup.send('No tracks found in the YouTube playlist.')
                return

            await interaction.followup.send(f'**Found _{len(entries)}_ tracks from the YouTube playlist.**')

            first_entry = entries[0]
            print(type(entries))
            first_song_url = first_entry['url']
            first_song = YTDLPCMVolumeTransformer.create_source(interaction, first_song_url)
            self.music_player.add_song_to_queue(first_song)

            if not self.music_player.voice_client.is_playing():
                await self.music_player.start_playing()
                await channel.send(f'Started playing the first track from the YouTube playlist.')

            await asyncio.create_task(self.download_and_enqueue_songs(interaction, entries))

        else:
            await interaction.followup.send('No tracks found in the YouTube playlist.')

    async def play_spotify_playlist(self, interaction: discord.Interaction, playlist_url: str):
        """Plays/Adds to the queue a Spotify playlist"""
        playlist_id = playlist_url.split('/')[-1]
        tracks = sp.playlist_items(playlist_id)

        if tracks and tracks['items']:
            for track in tracks['items']:
                track_url = track['track']['external_urls']['spotify']
                print(track_url)
                song = YTDLPCMVolumeTransformer.create_source(interaction, track_url)
                self.music_player.add_song_to_queue(song)

                if not self.music_player.voice_client.is_playing():
                    await self.music_player.start_playing()

            await interaction.followup.send(f'Added {len(tracks["items"])} from the Spotify playlist to the queue.')

        else:
            await interaction.followup.send('No tracks found in the Spotify playlist.')

    @app_commands.command(name = 'play')
    async def play(self, interaction: discord.Interaction, search: str):
        await interaction.response.defer()
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.followup.send('You are not connected to a voice channel.')
            return
        elif not self.music_player.voice_client:
            channel = interaction.user.voice.channel
            self.music_player.voice_client = await channel.connect()

        if search.startswith('https://open.spotify.com/playlist/'):
            # Spotify playlist
            print('Spotify playlist')
            await self.play_spotify_playlist(interaction, search)
        elif search.startswith('https://www.youtube.com/playlist?'):
            # YouTube playlist
            print('YouTube playlist')
            await self.play_youtube_playlist(interaction, search)
        elif search.startswith('https://open.spotify.com/track/'):
            # Individual Spotify track
            print('Spotify track')
            await self.play_individual_spotify_track(interaction, search)
        elif search.startswith('https://www.youtube.com/watch?'):
            # Individual YouTube video
            print('YouTube video')
            await self.play_individual_youtube_video(interaction, search)
        else:
            # Generic search (YouTube)
            print('Generic search (YouTube)')
            await self.play_youtube_search(interaction, search)

    @app_commands.command(name = 'stop')
    async def stop(self, interaction: discord.Interaction):
        if self.music_player.voice_client and self.music_player.voice_client.is_connected():
            self.music_player.voice_client.stop()
            await interaction.response.send_message('Music playback stopped.')
        else:
            await interaction.response.send_message('The bot is not connected to a voice channel.', ephemeral = True)

    @app_commands.command(name = 'queue')
    async def show_queue(self, interaction: discord.Interaction):
        print("show_queue command executed")

        if not self.music_player.queue:
            print('queue if')
            await interaction.response.send_message('The queue is empty.')
            return

        queue_message = '\n'.join(f'{index + 1}. {song.title}' for index, song in enumerate(self.music_player.queue))
        await interaction.response.send_message(f'Queue:\n{queue_message}')

    @app_commands.command(name = 'disconnect')
    async def disconnect(self, interaction: discord.Interaction):
        await self.music_player.disconnect()
        await interaction.response.send_message(f'Disconnected from {interaction.user.voice.channel.mention}.')

    @app_commands.command(name = 'pause')
    async def pause(self, interaction: discord.Interaction):
        self.music_player.voice_client.pause()
        await interaction.response.send_message('Music has been paused.')

    @app_commands.command(name = 'resume')
    async def resume(self, interaction: discord.Interaction):
        self.music_player.voice_client.resume()
        await interaction.response.send_message('Music has been resumed.')

    @app_commands.command(name = 'loop')
    async def loop(self, interaction: discord.Interaction):
        self.music_player.loop = not self.music_player.loop
        loop_status = 'enabled' if self.music_player.loop else 'disabled'
        await interaction.response.send_message(f'Looping is now {loop_status}.')

    @app_commands.command(name = 'skip')
    async def skip(self, interaction: discord.Interaction):
        if not self.music_player.voice_client:
            await interaction.followup.send("I'm not connected to any voice channel.")
        elif not self.music_player.queue:
            await interaction.followup.send('There are no songs to skip.')
        elif self.music_player.voice_client.is_playing():
            await self.music_player.skip()
            await interaction.response.send_message('Song has been skipped.')
        else:
            await interaction.response.send_message('The bot is not connected to a voice channel or is not playing anything', ephemeral = True)


async def setup(bot):
    await bot.add_cog(Music(bot))
