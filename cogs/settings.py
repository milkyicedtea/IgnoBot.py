####################
#                  #
#     Settings     #
#                  #
####################

import os

import discord
from discord.ext import commands
from discord import app_commands

from utils.dbchecks import DbChecks
from utils.dbhelper import DbHelper


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    prefix = app_commands.Group(name = 'prefix', description = "Commands related to guild's settings")

    application_check = app_commands.checks.has_permissions

    #won't be used as much as almost all the commands will be replace with application commands
    @prefix.command(name = 'set')
    @application_check(administrator = True)
    async def setprefix(self, interaction: discord.Interaction, prefix:str = 'i.'):
        guildid = interaction.guild_id

        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        cursor.execute(f'select count(*) from guildinfo where guildid = {guildid};')
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"insert into guildinfo(guildid) values({guildid});")
            mydb.commit()

        cursor.execute(f"select count(*) from guildsettings where guildid = {guildid};")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"insert into guildsettings(guildid) values({guildid});")
            mydb.commit()

        #print(f'guildid is {guildid}')
        #print('prefix is {}'.format(prefix))
        cursor.execute(f"update guildsettings set prefix = '{prefix}' where guildid = {guildid};")
        print(cursor.rowcount)
        mydb.commit()
        await interaction.response.send_message(f"The bot's prefix is now set to {prefix}")
        dbhelper.close()

async def setup(bot):
    await bot.add_cog(Settings(bot))