##################
#                #
#     Hentie     #
#                #
##################

import os

import discord
from discord import app_commands
from discord.ext import commands

import base64
import random
import cogs.rule34 as rule34
import asyncio

from utils.APIs.animeAPI import get_anime_info

class Hentie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    anime = app_commands.Group(name = 'anime', description = 'Anime group')

    application_check = app_commands.checks.has_permissions

    @anime.command(name = 'search')
    async def kayo(self, interaction: discord.Interaction, *, anime_name: str):
        anime = get_anime_info(query = anime_name)
        # print(anime)
        if anime is None:
            print('anime is none')
            embed = discord.Embed(description = f"**An error occurred**", color = discord.Colour.random())
            embed.add_field(name = 'Error description:', value = f"Couldn't find the requested anime")
            return await interaction.response.send_message(embed = embed)
        
        # print('anime is not none')
        
        base64_bytes = base64.b64encode(anime.download.encode('UTF-8'))
        base64_string = base64_bytes.decode('UTF-8')
        # print('anime.download encoded')

        '''
        print(anime.episodes)
        print(anime.title)
        print(anime.genres)
        print(anime.rating)
        print(anime.aired)
        print(base64_string)
        '''

        '''
        print(type(anime.episodes))
        print(type(anime.title))
        print(type(anime.genres))
        print(type(anime.rating))
        print(type(anime.aired))
        print(type(base64_string))
        '''

        embed = discord.Embed(color = discord.Colour.random())
        # print('author')
        embed.set_author(name = str(anime.title), icon_url = interaction.user.avatar)
        # print('episodes')
        embed.add_field(name = 'Episodes', value = str(anime.episodes), inline = False)
        # print('duration')
        embed.add_field(name = 'Duration', value = str(anime.duration), inline = False)
        # print('genres')
        embed.add_field(name = 'Genres', value = str(anime.genres), inline = False)
        # print('rating')
        embed.add_field(name = 'Rating', value = str(anime.rating), inline = False)
        # print('aired')
        embed.add_field(name = 'Aired', value = str(anime.aired), inline = False)
        # print('link')
        embed.add_field(name = 'Link', value = f"Decode this using i.decode *string*\n```{base64_string}```", inline = False)

        embed.set_image(url = anime.thumbnail)
        await interaction.response.send_message(embed = embed, ephemeral = True)

    # actual hentie command OwO (don't try at home)
    @app_commands.command(name = 'hentai', nsfw = True)    # channel must be marked as 18+
    async def hentai(self, interaction: discord.Interaction, tag: str = 'vanilla', number_to_send: int = 1):
        print('hentie')
        await interaction.response.defer()

        # print('checking how many to fetch')
        if number_to_send > 20:
            number_to_send = 20

        Rule34 = rule34.Rule34()

        print('getting images')
        images = await Rule34.getImages(tag)
        print('done')

        """
        print(images)
        print(images[0].file_url)
        print(len(images))
        print(number_to_send)
        print(tag)
        """

        if images is not None:
            # print('images is not none')
            for x in range(number_to_send):

                """
                embed = discord.Embed(color = discord.Colour.random())
                embed.add_field(name = 'Tag', value = tag)
                embed.set_image(url = f"|| {images[random.randint(0, int(len(images)))].file_url} ||")
                await ctx.send(embed = embed)
                """

                await interaction.followup.send(f'|| {images[random.randint(0, int(len(images)))].file_url} ||')
                #print(images[0].file_url)
                await asyncio.sleep(1)

        else:
            embed = discord.Embed(description = f"**An error occurred**", color = discord.Colour.random())
            embed.add_field(name = 'Error description:', value = f"Couldn't find any images related to tag ``{tag}`` or tag is invalid. Maybe try another?")
            await interaction.followup.send(embed = embed, ephemeral = True)

async def setup(bot):
    await bot.add_cog(Hentie(bot))