#################
#               #
#     Music     #
#               #
#################

import asyncio
import ctypes.util

from cogs.Cog_Utils.music_helper import YTDLPCMVolumeTransformer, MusicPlayer

import dotenv

import discord
from discord import app_commands
from discord.ext import commands

import platform

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


SPOTIPY_CLIENT_ID = dotenv.get_key('.env', 'SPOTIFY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = dotenv.get_key('.env', 'SPOTIFY_CLIENT_SECRET')

sp = spotipy.Spotify(client_credentials_manager = SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET))


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
        """Downloads songs in cunks of 10"""

        chunk_size = 10
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

        # extract track ID from URL
        track_id = track_url.split('/')[-1].split('?')[0]

        # get track info
        track_info = sp.track(track_id)

        if track_info:
            artist_name = track_info['artists'][0]['name']
            track_name = track_info['name']
            search_query = f"{track_name} {artist_name}"

            print(f"Search query: {search_query}")
            print("Creating source...")
            song = YTDLPCMVolumeTransformer.create_source(interaction, search_query)
            if song:
                print(f"Song created: {song.title}")
                self.music_player.add_song_to_queue(song)
                await interaction.followup.send(f'Added to the queue: **{song.title}**')
                print(f"Queue length: {len(self.music_player.queue)}")

                if not self.music_player.voice_client or not self.music_player.voice_client.is_connected():
                    print("Connecting to voice channel...")
                    channel = interaction.user.voice.channel
                    self.music_player.voice_client = await channel.connect()

                if not self.music_player.voice_client.is_playing():
                    print("Starting playback")
                    await self.music_player.start_playing()
                else:
                    print("Music is already playing")
            else:
                print("Failed to create song source")
                await interaction.followup.send("Couldn't create audio source for the track. Please try again.")

        else:
            await interaction.followup.send("Couldn't find the Spotify track. Please try again.")

    async def play_youtube_playlist(self, interaction: discord.Interaction, playlist_url: str):
        """Plays/Adds to the queue a YouTube playlist"""
        print(f"Processing YouTube playlist: {playlist_url}")

        playlist_info = YTDLPCMVolumeTransformer.extract_playlist_info(playlist_url)

        if 'entries' in playlist_info:
            entries = playlist_info['entries']
            print(f"Found {len(entries)} tracks in the YouTube playlist")

            if not entries:
                await interaction.followup.send('No tracks found in the YouTube playlist.')
                return

            await interaction.followup.send(f'**Found _{len(entries)}_ tracks from the YouTube playlist.**')

            for i, entry in enumerate(entries):
                if entry:
                    print(f"Processing track {i + 1}/{len(entries)}: {entry.get('title', 'Unknown title')}")

                    try:
                        song = YTDLPCMVolumeTransformer.create_source(interaction, entry['url'])
                        if song:
                            self.music_player.add_song_to_queue(song)
                            print(f"Added to queue: {song.title}")

                            if i == 0 and not self.music_player.voice_client.is_playing():
                                print("Starting playback of first track")
                                await self.music_player.start_playing()
                        else:
                            print(f"Failed to create source for: {entry.get('title', 'Unknown title')}")
                    except Exception as e:
                        print(f"Error processing track: {e}")

                # Add a small delay to avoid rate limiting
                await asyncio.sleep(1)

            await interaction.followup.send(f'Added {len(entries)} tracks from the YouTube playlist to the queue.')

        else:
            await interaction.followup.send('No tracks found in the YouTube playlist.')

    async def play_spotify_playlist(self, interaction: discord.Interaction, playlist_url: str):
        """Plays/Adds to the queue a Spotify playlist"""

        playlist_id = playlist_url.split('/')[-1].split('?')[0]

        try:
            results = sp.playlist_items(playlist_id)
            tracks = results['items']

            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])

            print(f"Found {len(tracks)} tracks in the Spotify playlist")

            if not tracks:
                await interaction.followup.send('No tracks found in the Spotify playlist.')
                return

            await interaction.followup.send(f'**Found _{len(tracks)}_ tracks from the Spotify playlist.**')

            for i, track_item in enumerate(tracks):
                track = track_item['track']
                if track['name'] and track['artists']:
                    search_query = f"{track['name']} {track['artists'][0]['name']}"
                    print(f"Processing track {i + 1}/{len(tracks)}: {search_query}")

                    song = YTDLPCMVolumeTransformer.create_source(interaction, search_query)
                    if song:
                        self.music_player.add_song_to_queue(song)
                        print(f"Added to queue: {song.title}")

                        if i == 0 and not self.music_player.voice_client.is_playing():
                            print("Starting playback of first track")
                            await self.music_player.start_playing()
                    else:
                        print(f"Failed to create source for: {search_query}")

                # Add a small delay to avoid rate limiting
                await asyncio.sleep(1)

            await interaction.followup.send(f'Added {len(tracks)} tracks from the Spotify playlist to the queue.')

        except Exception as e:
            print(f"Error processing Spotify playlist: {e}")
            await interaction.followup.send('An error occurred while processing the Spotify playlist.')

    async def play_spotify_album(self, interaction: discord.Interaction, album_url: str):
        album_id = album_url.split('/')[-1].split('?')[0]



    @app_commands.command(name = 'play')
    async def play(self, interaction: discord.Interaction, search: str):
        """The play command that redirects to other functions"""

        await interaction.response.defer()
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.followup.send('You are not connected to a voice channel.')
            return

        if not self.music_player.voice_client or not self.music_player.voice_client.is_connected():
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
        """Stops music playback, clears the queue, and disconnects the bot"""

        if self.music_player.voice_client and self.music_player.voice_client.is_connected():
            self.music_player.stop()
            await self.music_player.voice_client.disconnect()
            self.music_player.voice_client = None
            await interaction.response.send_message('Music playback stopped, queue cleared, and bot disconnected.')
        else:
            await interaction.response.send_message('The bot is not connected to a voice channel.', ephemeral = True)

    @app_commands.command(name = 'queue')
    async def show_queue(self, interaction: discord.Interaction):
        """Shows queue"""

        print("show_queue command executed")

        if not self.music_player.queue or not self.music_player:
            print('queue if')
            await interaction.response.send_message('The queue is empty.')
            return

        queue_message = '\n'.join(f'{index + 1}. {song.title}' for index, song in enumerate(self.music_player.queue))
        await interaction.response.send_message(f'Queue:\n{queue_message}')

    @app_commands.command(name = 'disconnect')
    async def disconnect(self, interaction: discord.Interaction):
        """Disconnects bot"""

        await self.music_player.disconnect()
        await interaction.response.send_message(f'Disconnected from {interaction.user.voice.channel.mention}.')

    @app_commands.command(name = 'pause')
    async def pause(self, interaction: discord.Interaction):
        """Pauses playback"""

        self.music_player.voice_client.pause()
        await interaction.response.send_message('Music has been paused.')

    @app_commands.command(name = 'resume')
    async def resume(self, interaction: discord.Interaction):
        """Resumes after pausing"""

        self.music_player.voice_client.resume()
        await interaction.response.send_message('Music has been resumed.')

    @app_commands.command(name = 'loop')
    async def loop(self, interaction: discord.Interaction):
        """Loops the current song"""

        self.music_player.loop = not self.music_player.loop
        loop_status = 'enabled' if self.music_player.loop else 'disabled'
        await interaction.response.send_message(f'Looping is now {loop_status}.')

    @app_commands.command(name = 'skip')
    async def skip(self, interaction: discord.Interaction):
        """Skips the current song"""

        if not self.music_player.voice_client:
            await interaction.response.send_message("I'm not connected to any voice channel.", ephemeral = True)
        elif not self.music_player.voice_client.is_playing():
            await interaction.response.send_message("There's no song playing to skip.", ephemeral = True)
        else:
            self.music_player.voice_client.stop()  # This will trigger the play_next_song method
            await interaction.response.send_message('Skipped the current song.')


async def setup(bot):
    await bot.add_cog(Music(bot))
