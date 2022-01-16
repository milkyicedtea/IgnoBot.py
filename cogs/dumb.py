#########################
#                       #
#     Dumb commands     #
#                       #
#########################

import os
from typing import AsyncContextManager

import discord
from discord import client
from discord.ext import commands
import random

from discord.ext.commands import bot

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

    # anni?
    @commands.command(name = 'anni', aliases = ['anni?'], help = 'Dice quanti sono gli anni')
    async def anniqty(self, ctx):
        annirange = int(random.choice(range(-100,100+1)))
        if annirange <= 0:
            await ctx.send(f'Anni:{annirange}\nNon puoi farlo ha solo {annirange} anni')
        else:
            await ctx.send(f'{annirange}')

    # mof?
    @commands.command(name = 'mof', help = 'mof')
    async def mof(self, ctx):
        mof_string = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        mof = random.choice(mof_string)
        await ctx.send(mof)

    # no u
    @commands.command(name = 'no-u', help = 'No u')
    async def nou(self, ctx):
        nourange = ['no u', 'yes me']
        response = random.choice(nourange)
        await ctx.send(response)

    # bastardi chiamo da reggio emilia
    @commands.command(name = 'pronto', aliases = ['pronto?'], help = 'Bastardi chiamo da Reggio Emilia')
    async def bastardi(self, ctx):
        response = '**Bastardi**, chiamo da Reggio Emilia, sono un assassino di **meridionali**. Vi ammazzo tutti *bastardi pezzi di merda*.'
        await ctx.send(response)

    # paytowin paytowin paytowin
    @commands.command(name = 'fennec', help = 'paytowin paytowin paytowin..')
    async def fennec(self, ctx):
        x = 0
        paytowinrange = int(random.choice(range(1,5+1)))
        while x < paytowinrange:
            await ctx.send(f'pay to win')
            x += 1

    # anni anni anni anni
    @commands.command(name = 'annispam', help = 'anni anni anni anni anni..')
    async def annispam(self, ctx):
        x = 0
        annispamrange = int(random.choice(range(1,5+1)))
        while x < annispamrange:
            await ctx.send('anni')
            x += 1

    # CRUNCH CRUNCH CRUNCH
    @commands.command(name = 'silvio', help = '*crunch crunch crunch*')
    async def silvio(self,ctx):
        x = 0
        crunchspamrange = int(random.choice(range(1,5+1)))
        while x < crunchspamrange:
            await ctx.send('***crunch***')
            x += 1

    # sexy
    @commands.command(name = 'sexy', help = 'SCONOSCIUTO SEXY A 2 METRI DA TE')
    async def sexy(self, ctx):
        await ctx.send('https://ibb.co/KjmR0Hq')

    # osu skins repo
    @commands.command(name = 'osuskins', help = 'Brings up my osu skins repository')
    async def osuskins(self, ctx):
        await ctx.send('https://github.com/ignorance-uwu/Osu-Skins')

    @commands.command(name = 'shid', help = 'i just shidded and farded +HDDT')
    async def shid(self, msg):
        await msg.reply('https://ibb.co/K7Bjd8Q')



    # listeners
    @commands.Cog.listener()
    async def on_message(self, msg):
        
    # bastardi on message
        if msg.content == "pronto" or msg.content == "pronto?":
            response = '**Bastardi**, chiamo da Reggio Emilia, sono un assassino di **meridionali**. Vi ammazzo tutti *bastardi pezzi di merda*.'
            await msg.reply(response)

    # vado on message
        if msg.content == 'vado' or msg.content == 'io vado' or msg.content == 'bella' or msg.content == 'a domani':
            response = 'ok a domani a domani a domani'
            await msg.reply(response)

    # bimbo dingo
        if msg.content == 'rocket league' or msg.content == 'dingo':
            x = 0
            response = 'bimbo dingo'
            bimbodingospamrange = int(random.choice(range(1,5+1)))
            while x < bimbodingospamrange:
                await msg.reply(response)
                x += 1
        
        if msg.content == 'sconosciuto':
            response = random.choice(['Hai fatto incazzare la persona sbagliata. Non hai futuro.', 'Mi hai fregato la macchina! Sarai mangime per vermi, pezzo di merda.'])
            await msg.reply(response)


def setup(bot):
    bot.add_cog(Dumb(bot))