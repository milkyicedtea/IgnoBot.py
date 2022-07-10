##################
#                #
#     Hentie     #
#                #
##################

import os

import discord
from discord.ext import commands

import base64
import random
import rule34
import asyncio

from utils.APIs.animeAPI import get_anime_info

mydb = None
cursor = None

class Hentie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command(name = 'kayo', help = 'Get download links and useful information for the given anime')
    async def kayo(self, ctx, *, anime_name):
        anime = get_anime_info(query = anime_name)
        if anime is None:
            embed = discord.Embed(description = f"Coudn't find **{anime_name}**",
                            color = discord.Colour.random())
            return await ctx.send(embed = embed)
        
        base64_bytes = base64.b64encode(anime.download.encode('UTF-8'))
        base64_string = base64_bytes.decode('UTF-8')

        embed = discord.Embed(color = discord.Colour.random())
        embed.set_author(name = anime.title, icon_url = ctx.author.avatar_url)
        embed.add_field(name = 'Episodes', value = anime.episodes, inline = False)
        embed.add_field(name = 'Duration', value = anime.duration, inline = False)
        embed.add_field(name = 'Genres', value = anime.genres, inline = False)
        embed.add_field(name = 'Rating', value = anime.rating, inline = False)
        embed.add_field(name = 'Aired', value = anime.aired, inline = False)
        embed.add_field(name = "Link", value = f"Decode this using i.decode *string*\n{base64_string}", inline = False)

        embed.set_image(url = anime.thumbnail)
        await ctx.send(embed = embed)

    # actual hentie command OwO (don't try at home)
    @commands.command(name = 'hentai')
    @commands.is_nsfw()     # channel must be marked as 18+
    async def hentai(self, ctx, number_to_send: int = None, tag: str = None):
        if number_to_send == None:
            number_to_send = 5

        if number_to_send > 20:
            number_to_send = 20

        if tag == None:
            tag = 'vanilla'

        Rule34 = rule34.Rule34()

        images = await Rule34.getImages(tag)

        for x in range(number_to_send):
            await ctx.send(f'|| {images[random.choice(range(len(images)))].file_url} ||')
            print(images[0].file_url)
            asyncio.sleep(1)

def setup(bot):
    bot.add_cog(Hentie(bot))