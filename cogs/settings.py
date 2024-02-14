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

from Utils.dbchecks import DbChecks
from Utils.dbhelper import DbHelper as Database


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

        with Database() as db:
            cursor = db.get_cursor()

            guildid = interaction.guild_id
            cursor.execute(f'select count(*) from guildinfo where guildid = {guildid};')
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"insert into guildinfo(guildid) values({guildid});")
                db.commit()

            cursor.execute(f"select count(*) from guildsettings where guildid = {guildid};")
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"insert into guildsettings(guildid) values({guildid});")
                db.commit()

            # print(f'guildid is {guildid}')
            # print('prefix is {}'.format(prefix))
            cursor.execute(f"update guildsettings set prefix = '{prefix}' where guildid = {guildid};")
            print(cursor.rowcount)
            db.commit()
            await interaction.response.send_message(f"The bot's prefix is now set to {prefix}")


async def setup(bot):
    await bot.add_cog(Settings(bot))
