################
#              #
#     Test     #
#              #
################

import os

import discord
from discord.ext import commands
import linecache
import random
import asyncio
import time
import http.client

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Embed test
    @commands.command(name = 'embed-test', help = 'Embed test')
    @commands.has_permissions(manage_guild=True)
    async def embed_test(self, ctx):
        colorvalue = discord.Colour.random()
        print(f'colorvalue is: {colorvalue}')
        embedVar = discord.Embed(title = 'Title', description = 'Desc', color = (colorvalue))
        embedVar.add_field(name = "Field1", value = "hi", inline = False)
        embedVar.add_field(name = "Field2", value = "hi2", inline = False)
        await ctx.send(embed = embedVar)

    # Read test
    @commands.command(name = 'read-test', help = 'Used to test file reading functionality (Requires the user to have manage_guild or administrator permission)')
    @commands.has_permissions(manage_guild=True)
    async def read_test(self, ctx):
        linecache.clearcache()
        title = linecache.getline('./data/welcome/welcome.ini', 2)
        color = linecache.getline('./data/welcome/welcome.ini', 4)
        description = linecache.getline('./data/welcome/welcome.ini', 6)
        await ctx.send(title + color + description)

    # Dice simulation
    @commands.command(name = 'diceroll', help = 'Simulates rolling dice.')
    async def roll(self, ctx, dices_to_roll: int, number_of_sides: int):
        if number_of_sides > 20 or number_of_sides <= 0:
            await ctx.send('The number must be in a range from 1 to 20')
            print(f'bad diceroll')
        else:
            dice = [
                str(random.choice(range(1, number_of_sides + 1)))
                for _ in range(dices_to_roll)
            ]
            await ctx.send(', '.join(dice))

    # asyncio.sleep() test
    @commands.command(name = 'asynciosleep', help = 'Asyncio.sleep test')
    async def asynciosleep(self, ctx, amount_to_sleep: int, *, sentence: str):
        await ctx.send(f'Waiting {amount_to_sleep} seconds before sending your message.')
        await asyncio.sleep(amount_to_sleep)
        await ctx.send(f'{sentence}')

    # time.sleep() test
    @commands.command(name = 'timesleep', help = 'Time.sleep test')
    @commands.has_guild_permissions(manage_guild = True)
    async def timesleep(self, ctx, amount_to_sleep: int, *, sentence: str):
        await ctx.send(f'Waiting {amount_to_sleep} seconds before sending your message.')
        time.sleep(amount_to_sleep)
        await ctx.send(f'{sentence}')

    # anime api test
    @commands.command(name = 'animetest', help = 'Anime api test')
    async def animetest(self,ctx):
        conn = http.client.HTTPSConnection("jikan1.p.rapidapi.com")

        headers = {
            'x-rapidapi-host': "jikan1.p.rapidapi.com",
            'x-rapidapi-key': "79e506351bmsh051e1172c44a0b6p1de664jsn579a9893d633"
            }

        conn.request("GET", "/meta/requests/anime/today", headers=headers)

        res = conn.getresponse()
        data = res.read()

        print(data)
        print(data.decode("utf-8"))

def setup(bot):
    bot.add_cog(Test(bot))