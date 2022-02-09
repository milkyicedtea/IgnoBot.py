##################
#                #
#     Hentie     #
#                #
##################

import os

import discord
from discord.ext import commands
import base64
import utils.animeAPI

mydb = None
cursor = None

class Hentie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command(name = 'kayo', help = 'Get download links and useful information for the given anime')
    async def kayo(self, ctx, *, anime_name):
        print("ciao")

        print(anime_name)
        anime = utils.animeAPI.get_anime_info(query = anime_name)
        print('sto qui')
        print(anime)
        if anime is None:

            print('none')
            embed = discord.Embed(description = f"Coudn't find **{anime_name}**",
                            color = discord.Colour.random())
            return await ctx.send(embed = embed)
        print(anime.download)

        print(anime.download.encode('UTF-8'))
        base64_bytes = base64.b64encode(anime.download.encode('UTF-8'))
        print(base64_bytes)
        base64_string = base64_bytes.decode('UTF-8')
        print(base64_string)

        embed = discord.Embed(color = discord.Colour.random())
        embed.set_author(name = anime.title, icon_url = ctx.author.avatar_url)
        embed.add_field(name = 'Episodes', value = anime.episodes, inline = False)
        embed.add_field(name = 'Duration', value = anime.duration, inline = False)
        embed.add_field(name = 'Genres', value = anime.genres, inline = False)
        embed.add_field(name = 'Rating', value = anime.rating, inline = False)
        embed.add_field(name = 'Aired', value = anime.aired, inline = False)

        embed.add_field(name = "Link", 
                        value = f"Decode this using i.decode *string*\n{base64_string}", 
                        inline = False
                    )
        
        embed.set_image(url=anime.thumbnail)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Hentie(bot))