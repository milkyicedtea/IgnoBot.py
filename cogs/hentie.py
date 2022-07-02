##################
#                #
#     Hentie     #
#                #
##################

import os
from unicodedata import numeric

import discord
from discord.ext import commands

import base64
import random

from numpy import number

from utils.APIs.animeAPI import get_anime_info

from utils.APIs import hentieAPI

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

        embed.set_image(url=anime.thumbnail)
        await ctx.send(embed=embed)

    # actual hentie command OwO (don't try at home)
    @commands.command(name = 'hentai')
    @commands.is_nsfw()
    async def hentai(self, ctx, number_to_send: int = None):
        if number_to_send == None:
            number_to_send = 1
        hen_image = await hentieAPI.get_image()
        for x in range(number_to_send):
            embedVar = discord.Embed(title = x+1, color = discord.Colour.darker_grey())
            embedVar.set_image(url = hen_image[random.choice(range(len(hen_image)))])
            await ctx.send(embed = embedVar)

def setup(bot):
    bot.add_cog(Hentie(bot))