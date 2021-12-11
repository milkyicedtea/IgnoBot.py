#########################
#                       #
#     Dumb commands     #
#                       #
#########################

import os

import discord
from discord.ext import commands
import random

class Dumb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # beep command
    @commands.command(name = 'beep', help = 'Literally just says beep.')
    async def beep(self, ctx):
        response = '**Beep!**'
        await ctx.send(response)

    # bad command
    @commands.command(name = 'bad', help = 'Literally just says bad.')
    async def bad(self, ctx):
        response = '**Bad**'
        await ctx.send(response)

    # Am i cool command
    @commands.command(name = 'am-i-cool', help = 'Find out if you are cool.')
    async def amicool(self, ctx):
        amicoolquotes = ['You are so cool, how do even you do that?', 'No, you are not cool at all.']
        response = random.choice(amicoolquotes)
        await ctx.send(response)

    # uwuduck command
    @commands.command(name = 'uwuduck', help = 'uwuduck')
    async def uwuduck(self, ctx):
        await ctx.send('<:uwuduck:916404134821904435>')

    # anni anni anni anni anni anni
    @commands.command(name = 'anni', aliases = ['anni?'], help = 'anni anni anni anni anni')
    async def anni(self, ctx):
        annirange = str(random.choice(range(0,100+1)))
        if annirange == 0:
            await ctx.send(f'Anni:{annirange}\nNon puoi farlo ha solo {annirange} anni')
        else:
            await ctx.send(f'{annirange}')

    @commands.command(name = 'mof', help = 'mof')
    async def mof(self, ctx):
        mof_string = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        mof = random.choice(mof_string)
        await ctx.send(mof)

def setup(bot):
    bot.add_cog(Dumb(bot))