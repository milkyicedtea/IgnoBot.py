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

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Embed test
    @commands.command(name = 'embed-test', help = 'Embed test')
    @commands.has_permissions(manage_guild=True)
    async def embed_test(self, ctx):
        linecache.clearcache()
        title_read = linecache.getline('./data/welcome/welcome.ini', 2)
        color_read = linecache.getline('./data/welcome/welcome.ini', 4)
        description_read = linecache.getline('./data/welcome/welcome.ini', 6)
        embed=discord.Embed(
            title = "" + title_read ,
            description = "" + description_read,
            color = "" + discord.Color(color_read)
        )   
        await ctx.send(embed)

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

def setup(bot):
    bot.add_cog(Test(bot))