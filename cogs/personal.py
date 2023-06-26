################################
#                              #
#     Personal commands :3     #
#                              #
################################
import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands

import random
import dotenv

from builtins import guildList


# RUNNING THIS COG ON YOUR MACHINE MAY PREVENT COMPILING DUE TO A LACK OF ENVIRONMENT KEYS.
# IT IS NOT ESSENTIAL AND DOES NOT CONTAIN ANY IMPORTANT COMMANDS, SO FEEL FREE TO DELETE OR DISABLE IT AS NEEDED.
# PLEASE DO NOT REQUEST ANY OTHESE KEYS. SHOULD YOU DO SO, YOUR REQUEST WILL BE DISREGARDED

class Personal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    kodama_guild: int = int(dotenv.get_key(".env", "kodama_guild"))
    chill_ignorance: int = int(dotenv.get_key(".env", "chill_ignorance"))
    # ducks_hideout: int = int(dotenv.get_key(".env", "ducks_hideout"))
    ichiban_kuji_guild: int = int(dotenv.get_key(".env", "ichiban_kuji_guild"))

    guildList: list[int] = [kodama_guild, chill_ignorance, ichiban_kuji_guild]

    personal = app_commands.Group(name = 'personal', description = 'These commands only work in a certain guild.', guild_ids = [kodama_guild, chill_ignorance, ichiban_kuji_guild])

    # anni?
    @personal.command(name = 'anni', description = 'Anni?')
    async def anniqty(self, interaction: discord.Interaction):
        annirange = int(random.choice(range(-100, 100+1)))
        if annirange <= 0:
            await interaction.response.send_message(f'Anni:{annirange}\nNon puoi farlo ha solo {annirange} anni')
        else:
            await interaction.response.send_message(f'{annirange}')

    # mof?
    @personal.command(name = 'mof', description = 'mof?')
    async def mof(self, interaction: discord.Interaction):
        mof_string = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        mof = random.choice(mof_string)
        await interaction.response.send_message(mof)

    # no u
    @personal.command(name = 'no-u', description = 'no u.')
    async def nou(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(["no u", "yes me"]))

    # bastardi chiamo da reggio emilia
    @personal.command(name = 'bastardi')
    async def bastardi(self, interaction: discord.Interaction):
        await interaction.response.send_message('**Bastardi**, chiamo da Reggio Emilia, sono un assassino di **meridionali**. Vi ammazzo tutti *bastardi pezzi di merda*.')

    # sexy
    # THIS WILL *NOT* RUN ON YOUR MACHINE (or server). YOU ARE MISSING ENV FILES
    @personal.command(name = 'sexy')
    async def sexy(self, interaction: discord.Interaction):
        guildidcompare = discord.Object(id = dotenv.get_key('.env', 'kodama_guild'))
        guild = interaction.guild
        # remember this is on stored on the .env and server ffs
        if guild.id == guildidcompare.id:
            sexy = dotenv.get_key('.env', random.choice([
                                'scono0',
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
            await interaction.response.send_message(sexy, ephemeral = True, delete_after = 5)
            catturato = dotenv.get_key('.env', 'livio0')
            if catturato == sexy:
                await interaction.followup.send('CATTURATO IN 16K UHD 1298037HZ HDR69420+ 96BITS', delete_after = 5)

    @personal.command(name = 'shid')
    async def shid(self, interaction: discord.Interaction):
        embed = discord.Embed(title = "omg bro :shit:", url = "https://milkyicedtea.epizy.com/Ignobot", color = discord.Colour.from_str('#7b5804'))
        embed.set_image(url = 'https://pbs.twimg.com/media/E3jLAljVEAQz1f8.jpg')
        await interaction.response.send_message(embed = embed, ephemeral = True)

    # listeners
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild.id in guildList:
            # bastardi on message
            if message.content.lower() in ['pronto', 'pronto?']:
                response = '**Bastardi**, chiamo da Reggio Emilia, sono un assassino di **meridionali**. Vi ammazzo tutti *bastardi pezzi di merda*.'
                await message.reply(response)

            # vado on message
            elif message.content.lower() in ['vado', 'io vado', 'bella', 'a domani', 'mani']:
                response = 'k grazie mani'
                await message.reply(response)

            # bimbo dingo
            elif message.content.lower() in ['rocket league', 'dingo']:
                response = 'bimbo dingo'
                bimbodingospamrange = int(random.choice(range(1, 5 + 1)))
                for x in range(bimbodingospamrange):
                    await message.reply(response)

            # sconosciuto
            elif message.content.lower() == 'sconosciuto':
                response = random.choice(['Hai fatto incazzare la persona sbagliata. Non hai futuro.',
                                          'Mi hai fregato la macchina! Sarai mangime per vermi, pezzo di merda.'])
                await message.reply(response)

            # python bad
            elif message.content.lower() == 'python?':
                response = 'bad'
                await message.reply(response)

            # O RAZZIATORE???
            elif message.content.lower() in ['o razziatore', 'razziatore', 'o razziatore?']:
                await message.reply('https://cdn.discordapp.com/attachments/933336707825295368/936916126594633779/Immagine_2022-01-27_221310.png')

            # Was für eine parade!
            elif message.content == 'Was für eine parade!':
                await message.reply('Danke!')


async def setup(bot):
    await bot.add_cog(Personal(bot))
