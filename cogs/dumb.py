#########################
#                       #
#     Dumb commands     #
#                       #
#########################

import os

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import bot

import random

from utils.APIs import duckAPI
from utils.APIs import catAPI

class Dumb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    test = app_commands.Group(name = 'test', description = 'Test group')
    fun = app_commands.Group(name = 'fun', description = 'fun misc group')
    animal = app_commands.Group(name = 'animal', description = 'Animal images/videos')

    application_check = app_commands.checks.has_permissions

    #new bad slash command
    @test.command(name = 'bad')
    async def bad(self, interaction: discord.Interaction):
        await interaction.response.send_message('**Bad**', ephemeral = True)

    # beep command
    @test.command(name = 'beep')
    async def beep(self, interaction: discord.Interaction):
        await interaction.response.send_message('**Beep!**', ephemeral = True)

    # Am i cool command
    @fun.command(name = 'am-i-cool')
    async def amicool(self, interaction: discord.Interaction):
        amicoolquotes = ['You are so cool, how do even you do that?', 'No, you are not cool at all.']
        response = random.choice(amicoolquotes)
        await interaction.response.send_message(response)

    # uwuduck command
    @fun.command(name = 'uwuduck')
    async def uwuduck(self, interaction: discord.Interaction):
        await interaction.response.send_message('<:uwuduck:916404134821904435>')

    # Dice simulation
    @fun.command(name = 'diceroll')
    async def roll(self, interaction: discord.Interaction, dices_to_roll: int, number_of_sides: int):
        if number_of_sides > 20 or number_of_sides <= 0:
            await interaction.response.send_message('The number must be in a range from 1 to 20', ephemeral = True)
            print(f'bad diceroll')
        else:
            dice = [
                str(random.choice(range(1, number_of_sides + 1)))
                for _ in range(dices_to_roll)
            ]
            await interaction.response.send_message(', '.join(dice))

    # anni?
    @fun.command(name = 'anni')
    async def anniqty(self, interaction: discord.Interaction):
        annirange = int(random.choice(range(-100,100+1)))
        if annirange <= 0:
            await interaction.response.send_message(f'Anni:{annirange}\nNon puoi farlo ha solo {annirange} anni')
        else:
            await interaction.response.send_message(f'{annirange}')

    # mof?
    @fun.command(name = 'mof')
    async def mof(self, interaction: discord.Interaction):
        mof_string = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        mof = random.choice(mof_string)
        await interaction.response.send_message(mof)

    # no u
    @fun.command(name = 'no-u')
    async def nou(self, interaction: discord.Interaction):
        nourange = ['no u', 'yes me']
        response = random.choice(nourange)
        await interaction.response.send_message(response)

    # bastardi chiamo da reggio emilia
    @commands.command(name = 'bastardi')
    @commands.is_owner()
    async def bastardi(self, ctx):
        response = '**Bastardi**, chiamo da Reggio Emilia, sono un assassino di **meridionali**. Vi ammazzo tutti *bastardi pezzi di merda*.'
        await ctx.send(response)

    # paytowin paytowin paytowin
    @commands.command(name = 'fennec')
    @commands.is_owner()
    async def fennec(self, ctx):
        paytowinrange = int(random.choice(range(1,5+1)))
        for x in range(paytowinrange):
            await ctx.send(f'pay to win')

    # anni anni anni anni
    @commands.command(name = 'annispam')
    @commands.is_owner()
    async def annispam(self, ctx):
        annispamrange = int(random.choice(range(1,5+1)))
        for x in range(annispamrange):
            await ctx.send('anni')

    # CRUNCH CRUNCH CRUNCH
    @commands.command(name = 'crunch')
    @commands.is_owner()
    async def crunch(self,ctx):
        guildidcompare = int(os.getenv('guild_id'))
        guild = ctx.guild.id
        if guild == guildidcompare:
            crunchspamrange = int(random.choice(range(1,5+1)))
            for x in range(crunchspamrange):
                await ctx.send('***crunch***')
        else:
            ctx.send('This command is only available in a cartain server!')

    # sexy
    # THIS WILL *NOT* RUN ON YOUR MACHINE. YOU ARE MISSING ENV FILES (and server..)
    @commands.command(name = 'sexy')
    @commands.is_owner()
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
            await ctx.send('This command is only available in a certain server!')

    # osu skins repo
    # @commands.command(name = 'osuskins', help = 'Brings up my osu skins repository')
    async def osuskins(self, ctx):
        await ctx.send('https://github.com/ignorance-uwu/Osu-Skins')

    @commands.command(name = 'shid')
    @commands.is_owner()
    async def shid(self, ctx):
        await ctx.send('omg bro')
        await ctx.send('https://pbs.twimg.com/media/E3jLAljVEAQz1f8?format=jpg&name=large')

    @commands.command(name = 'python')
    @commands.is_owner()
    async def pythonspam(self, ctx):
        pythonspamrange = int(random.choice(range(1,5+1)))
        for x in range(pythonspamrange):
            await ctx.send('***python***')

    @animal.command(name = 'duckimage', description = 'Sends you a cute duck image :3')
    async def duckimage(self, interaction: discord.Interaction):
        duck_image = await duckAPI.get_image()
        x = random.choice(range(len(duck_image)))
        await interaction.response.send_message(duck_image[x])

    @animal.command(name = 'duckvideo', description = 'Sends you a cute duck video :3')
    async def duckvideo(self, interaction: discord.Interaction):
        duck_video = await duckAPI.get_video()
        x = random.choice(range(len(duck_video)))
        await interaction.response.send_message(duck_video[x])

    @animal.command(name = 'catimage', description = 'Sends you a cute cat image :3')
    async def catimage(self, interaction: discord.Interaction):
        cat_image = await catAPI.get_image()
        x = random.choice(range(len(cat_image)))
        await interaction.response.send_message(cat_image[x])

    @animal.command(name = 'catvideo', description = 'Sends you a cute cat video :3')
    async def catvideo(self, interaction: discord.Interaction):
        cat_video = await catAPI.get_video()
        x = random.choice(range(len(cat_video)))
        await interaction.response.send_message(cat_video[x])

    # THIS WILL *NOT* RUN ON YOUR MACHINE. YOU ARE MISSING ENV FILES (and server..)
    @animal.command(name = 'cattos')
    async def cattos(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
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
            await interaction.response.send_message(cattos)
        else:
            await interaction.response.send_message("This command is only available in certain servers")

    # listeners
    @commands.Cog.listener()
    async def on_message(self, msg):
        
    # bastardi on message
        if msg.content == "pronto" or msg.content == "pronto?":
            response = '**Bastardi**, chiamo da Reggio Emilia, sono un assassino di **meridionali**. Vi ammazzo tutti *bastardi pezzi di merda*.'
            await msg.reply(response)

    # vado on message
        elif msg.content == 'vado' or msg.content == 'io vado' or msg.content == 'bella' or msg.content == 'a domani':
            response = 'ok a domani a domani a domani'
            await msg.reply(response)

    # bimbo dingo
        elif msg.content == 'rocket league' or msg.content == 'dingo':
            response = 'bimbo dingo'
            bimbodingospamrange = int(random.choice(range(1,5+1)))
            for x in range(bimbodingospamrange):
                await msg.reply(response)
        
    # sconosciuto
        elif msg.content == 'sconosciuto':
            response = random.choice(['Hai fatto incazzare la persona sbagliata. Non hai futuro.', 'Mi hai fregato la macchina! Sarai mangime per vermi, pezzo di merda.'])
            await msg.reply(response)

    # python bad
        elif msg.content == 'python?':
            response = 'bad'
            await msg.reply(response)

    # O RAZZIATORE???
        elif msg.content == 'o razziatore' or msg.content == 'razziatore' or msg.content == 'o razziatore?':
            await msg.reply('https://cdn.discordapp.com/attachments/933336707825295368/936916126594633779/Immagine_2022-01-27_221310.png')

    # Was für eine parade!
        elif msg.content == 'Was für eine parade!':
            await msg.reply('Danke!')

async def setup(bot):
    await bot.add_cog(Dumb(bot))