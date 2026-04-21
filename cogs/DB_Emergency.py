####################
#                  #
#     Database     #
#                  #
####################

import discord
from discord import app_commands
from discord.ext import commands

import psycopg

from Utils.database.database import PgDB


class DbEmergency(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # THIS COMMAND CAN ONLY BE USED BY THE ACCOUNT THAT OWNS THE BOT DUE TO SECURITY/DATABASE SPAM PREVENTING
    @app_commands.command(name = 'add-guild')
    @app_commands.checks.has_permissions(administrator = True)
    async def addguild(self, interaction: discord.Interaction):
        """Manually adds a guild (server) to the database."""

        if not await self.bot.is_owner(interaction.user):
            # If the user is not the bot owner, deny the command
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False) # noqa
            return

        try:
            async with PgDB() as db:
                cursor = await db.get_cursor()

                guildid = interaction.guild.id
                guildraw = interaction.guild.name
                guildname = guildraw.replace("'", "")

                await cursor.execute("""
                    insert into guildinfo(guildid, guildname)
                    values(%s, %s)
                    on conflict (guildid) 
                    do update set guildname = EXCLUDED.guildname
                """, (guildid, guildname))
                await db.commit()

                await interaction.response.send_message( # noqa
                    f"Guild '{guildname}' with id {guildid} was added or updated in the database."
                )

        except psycopg.Error as ag:
            print(f'Something went wrong in `add-guild` command: {ag}')
            await interaction.response.send_message( # noqa
                f"An error occurred: {ag}",
                ephemeral = True
            )

    @addguild.error
    async def addguild_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message( # noqa
            "Not allowed!"
        )

    # @app_commands.command(name = 'users-sync')
    # @app_commands.checks.has_permissions(administrator = True)
    # async def users_sync(self, interaction: discord.Interaction):
    #     """Manually syncs users from leveling table to user table. (from old database structure)"""
    #     if not await self.bot.is_owner(interaction.user):
    #         await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False)
    #         return
    #
    #     try:
    #         async with PgDB() as db:
    #             cursor = await db.get_cursor()
    #
    #             await cursor.execute("""
    #                 select userid
    #                 from leveling
    #             """)
    #
    #             result_dict = {userid: username for userid, username in await cursor.fetchall()}
    #             print(result_dict)
    #
    #             await cursor.executemany("""
    #                 insert into users(userid, username)
    #                 values(%s, %s)
    #             """, [(userid, username) for userid, username in result_dict.items()])
    #
    #             await db.commit()
    #
    #             await interaction.response.send_message("""
    #                 Users synced.
    #             """, ephemeral = True)
    #
    #     except psycopg.Error as ag:
    #         print(f'Something went wrong in `users-sync` command: {ag}')
    #         await interaction.response.send_message(f"An error occurred: {ag}", ephemeral = True)


async def setup(bot):
    await bot.add_cog(DbEmergency(bot))
