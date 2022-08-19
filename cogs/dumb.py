#########################
#                       #
#     Dumb commands     #
#                       #
#########################

import os

import discord
from discord.ext import commands
import random

from discord.ext.commands import bot
from utils.APIs import duckAPI
from utils.APIs import catAPI

class Dumb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # beep command
    @commands.command()
    async def beep(self, ctx):
        response = '**Beep!**'
        await ctx.send(response)

    # bad command
    @commands.command()
    async def bad(self, ctx):
        response = '**Bad**'
        await ctx.send(response)

    # Am i cool command
    @commands.command(name = 'am-i-cool')
    async def amicool(self, ctx):
        amicoolquotes = ['You are so cool, how do even you do that?', 'No, you are not cool at all.']
        response = random.choice(amicoolquotes)
        await ctx.send(response)

    # uwuduck command
    @commands.command()
    async def uwuduck(self, ctx):
        await ctx.send('<:uwuduck:916404134821904435>')

    # anni?
    @commands.command(name = 'anni', aliases = ['anni?'])
    async def anniqty(self, ctx):
        annirange = int(random.choice(range(-100,100+1)))
        if annirange <= 0:
            await ctx.send(f'Anni:{annirange}\nNon puoi farlo ha solo {annirange} anni')
        else:
            await ctx.send(f'{annirange}')

    # mof?
    @commands.command()
    async def mof(self, ctx):
        mof_string = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        mof = random.choice(mof_string)
        await ctx.send(mof)

    # no u
    @commands.command(name = 'no-u')
    async def nou(self, ctx):
        nourange = ['no u', 'yes me']
        response = random.choice(nourange)
        await ctx.send(response)

    # bastardi chiamo da reggio emilia
    @commands.command(name = 'pronto', aliases = ['pronto?'])
    async def bastardi(self, ctx):
        response = '**Bastardi**, chiamo da Reggio Emilia, sono un assassino di **meridionali**. Vi ammazzo tutti *bastardi pezzi di merda*.'
        await ctx.send(response)

    # paytowin paytowin paytowin
    @commands.command()
    async def fennec(self, ctx):
        paytowinrange = int(random.choice(range(1,5+1)))
        for x in range(paytowinrange):
            await ctx.send(f'pay to win')

    # anni anni anni anni
    @commands.command()
    async def annispam(self, ctx):
        annispamrange = int(random.choice(range(1,5+1)))
        for x in range(annispamrange):
            await ctx.send('anni')

    # CRUNCH CRUNCH CRUNCH
    @commands.command()
    async def silvio(self,ctx):
        crunchspamrange = int(random.choice(range(1,5+1)))
        for x in range(crunchspamrange):
            await ctx.send('***crunch***')

    # sexy
    @commands.command()
    async def sexy(self, ctx):
        guildidcompare = int(os.getenv('guild_id'))
        guild = ctx.guild.id
        # remember this is on stored on the .env and server ffs
        if guild == guildidcompare:
            sexy = os.getenv(random.choice(['scono0', 
                                            'scono1',
                                            'scono2',
                                            'scono3',
                                            'scono4',
                                            'scono5',
                                            'scono6',
                                            'scono7',
                                            'scono8',
                                            'scono9',
                                            'scono10',
                                            'scono11',
                                            'scono12',
                                            'scono13',
                                            'scono14',
                                            'scono15',
                                            'scono16',
                                            'scono17',
                                            'scono18',
                                            'scono19',
                                            'livio0']))
            await ctx.send(sexy)
            catturato = os.getenv('livio0')
            if catturato == sexy:
                await ctx.send('CATTURATO IN 16K UHD 1298037HZ HDR69420+ 87BIT')
        else:
            print('bad')

    # osu skins repo
    # @commands.command(name = 'osuskins', help = 'Brings up my osu skins repository')
    async def osuskins(self, ctx):
        await ctx.send('https://github.com/ignorance-uwu/Osu-Skins')

    @commands.command()
    async def shid(self, ctx):
        await ctx.send('omg bro')
        await ctx.send('https://pbs.twimg.com/media/E3jLAljVEAQz1f8?format=jpg&name=large')

    @commands.command(name = 'python')
    async def pythonspam(self, ctx):
        pythonspamrange = int(random.choice(range(1,5+1)))
        for x in range(pythonspamrange):
            await ctx.send('***python***')

    @commands.command()
    async def duckimage(self, ctx):
        duck_image = await duckAPI.get_image()
        x = random.choice(range(len(duck_image)))
        await ctx.send(duck_image[x])

    @commands.command()
    async def duckvideo(self, ctx):
        duck_video = await duckAPI.get_video()
        x = random.choice(range(len(duck_video)))
        await ctx.send(duck_video[x])

    @commands.command()
    async def catimage(self, ctx):
        cat_image = await catAPI.get_image()
        x = random.choice(range(len(cat_image)))
        await ctx.send(cat_image[x])

    @commands.command()
    async def catvideo(self, ctx):
        cat_video = await catAPI.get_video()
        x = random.choice(range(len(cat_video)))
        await ctx.send(cat_video[x])

    @commands.command()
    async def cattos(self, ctx):
        guild_id = ctx.guild.id
        if guild_id == int(os.getenv('guild_id')) or guild_id == int(os.getenv('private_guild')) or guild_id == int(os.getenv('varg_guild')) or guild_id == int(os.getenv('extra_guild')):
            cattos = os.getenv(random.choice([  'catto0',
                                                'catto1',
                                                'catto2',
                                                'catto3',
                                                'catto4',
                                                'catto5',
                                                'catto6',
                                                'catto7',
                                                'catto8',
                                                'catto9',
                                                'catto10',
                                                'catto11',
                                                'catto12',
                                                'catto13',
                                                'catto14',
                                                'catto15',
                                                'catto16',
                                                'catto17',
                                                'catto18',
                                                'catto19']))
            await ctx.send(cattos)

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
            response = 'bimbo dingo'
            bimbodingospamrange = int(random.choice(range(1,5+1)))
            for x in range(bimbodingospamrange):
                await msg.reply(response)
        
    # sconosciuto
        if msg.content == 'sconosciuto':
            response = random.choice(['Hai fatto incazzare la persona sbagliata. Non hai futuro.', 'Mi hai fregato la macchina! Sarai mangime per vermi, pezzo di merda.'])
            await msg.reply(response)

    # python bad
        if msg.content == 'python?':
            response = 'bad'
            await msg.reply(response)

    # O RAZZIATORE???
        if msg.content == 'o razziatore' or msg.content == 'razziatore' or msg.content == 'o razziatore?':
            await msg.reply('https://cdn.discordapp.com/attachments/933336707825295368/936916126594633779/Immagine_2022-01-27_221310.png')

    # Was für eine parade!
        if msg.content == 'Was für eine parade!':
            await msg.reply('Danke!')

def setup(bot):
    bot.add_cog(Dumb(bot))