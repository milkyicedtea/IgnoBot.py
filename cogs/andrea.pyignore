#####################
#                   #
#     Andrea :D     #
#                   #
#####################

import os

import discord
from discord import app_commands
from discord.ext import commands

import dotenv
import asyncio
import datetime

from builtins import guildList

# RUNNING THIS COG ON YOUR MACHINE MAY PREVENT COMPILING DUE TO A LACK OF ENVIRONMENT KEYS.
# IT IS NOT ESSENTIAL AND DOES NOT CONTAIN ANY IMPORTANT COMMANDS, SO FEEL FREE TO DELETE OR DISABLE IT AS NEEDED.
# PLEASE DO NOT REQUEST ANY OTHESE KEYS. SHOULD YOU DO SO, YOUR REQUEST WILL BE DISREGARDED


class AndreaClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    andreaGroup = app_commands.Group(name = 'andrea', description = 'Questi comandi fanno qualcosa ad Andrea :3', guild_ids = guildList)

    andrea_id = int(dotenv.get_key('.env', 'id_andrea'))
    # andrea_id = int   # for test purposes, you can manually an id.

    @andreaGroup.command(name = 'muta')
    async def andrea_mute(self, interaction: discord.Interaction):
        """Muta andrea per 20 secondi:3"""
        andrea: discord.Member = discord.utils.get(interaction.guild.members, id = self.andrea_id)
        await interaction.response.send_message(f"{andrea.mention} e' stato mutato per 20 secondi :3", ephemeral = True, delete_after = 10)
        if not andrea.voice.mute:
            await andrea.edit(mute = True)
            await asyncio.sleep(20)
            await andrea.edit(mute = False)

    @andreaGroup.command(name = 'timeout')
    async def andrea_timout(self, interaction: discord.Interaction):
        """Mette in timout andrea per 20 secondi :3"""
        andrea: discord.Member = discord.utils.get(interaction.guild.members, id = self.andrea_id)
        await interaction.response.send_message(f"{andrea.mention} e' stato messo in timeout per 20 secondi :3", ephemeral = True, delete_after = 10)
        if not andrea.is_timed_out():
            time = discord.utils.utcnow() + datetime.timedelta(seconds = 20)
            await andrea.edit(timed_out_until = time)
        else:
            interaction.response.send_message(f"{andrea.mention} e' gia' in timeout xD", ephemeral = True, delete_after = 10)

    @andreaGroup.command(name = 'ghost')
    async def andrea_ghost(self, interaction: discord.Interaction):
        """Pinga andrea 3 volte cancella subito i messaggi :3"""
        andrea: discord.Member = discord.utils.get(interaction.guild.members, id = self.andrea_id)
        await interaction.response.send_message(f"Mandato ghostino a {andrea.mention} :3", ephemeral = True, delete_after = 10)
        for x in range(3):
            message = await interaction.channel.send(andrea.mention)
            await message.delete()

    @andreaGroup.command(name = 'vkick')
    async def andrea_vkick(self, interaction: discord.Interaction):
        """Espelle andrea dal canale vocale :3"""
        andrea: discord.Member = discord.utils.get(interaction.guild.members, id = self.andrea_id)
        if andrea.voice is not None:
            await interaction.response.send_message(f"{andrea.mention} e' stato espulso dal canale :3", ephemeral = True, delete_after = 10)
            await andrea.edit(voice_channel = None)
        else:
            await interaction.response.send_message(f"{andrea.mention} non e' in un canale vocale :(", ephemeral = True, delete_after = 10)

    # Manda un dm ad andrea, inutile perche' puo' vedere da chi e' stato mandato.
    """@andreaGroup.command(name = 'messaggio')
    async def andrea_messaggio(self, interaction: discord.Interaction, message: str):
        andrea: discord.Member = discord.utils.get(interaction.guild.members, id = self.andrea_id)
        try:
            await andrea.send(message)
        except:
            await interaction.response.send_message(f"C'e stato un errore mentre mandavo il messaggio ad {andrea.mention} :(", ephemeral = True, delete_after = 10)
        else:
            await interaction.response.send_message(f"Mandato messaggino a {andrea.mention} :3", ephemeral = True, delete_after = 10)"""


async def setup(bot):
    await bot.add_cog(AndreaClass(bot))
