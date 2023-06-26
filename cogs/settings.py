####################
#                  #
#     Settings     #
#                  #
####################

import os
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

from utils.dbchecks import DbChecks
from utils.dbhelper import DbHelper


def cooldown_checker(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    return app_commands.Cooldown(1, 60)


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    prefix = app_commands.Group(name = 'prefix', description = "Commands related to guild's settings")

    application_check = app_commands.checks.has_permissions

    # won't be used as much as almost all the commands will be replaced with application commands
    @prefix.command(name = 'set')
    @application_check(administrator = True)
    # @app_commands.checks.dynamic_cooldown(cooldown_checker)
    async def setprefix(self, interaction: discord.Interaction, prefix: str = 'i.'):
        """Sets a custom prefix for chat commands. There are little to no chat commands now."""
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

        # print(f'guildid is {guildid}')
        # print('prefix is {}'.format(prefix))
        cursor.execute(f"update guildsettings set prefix = '{prefix}' where guildid = {guildid};")
        print(cursor.rowcount)
        mydb.commit()
        await interaction.response.send_message(f"The bot's prefix is now set to {prefix}")
        dbhelper.close()


async def setup(bot):
    await bot.add_cog(Settings(bot))
