########################
#                      #
#     Level System     #
#                      #
########################
from typing import Literal

from cogs.Cog_Utils.selfrole_helper import SelfroleHelper

import discord
from discord.ext import commands
from discord import app_commands

import itertools

from Utils.db_checks import DbChecks
from Utils.database.database import PgDB 


class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    levelGroup = app_commands.Group(name = 'level', description = 'Levels related commands')

    application_check = app_commands.checks.has_permissions

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Gives exp for every message."""
        if message.author.bot:  # also skip bots here
            return

        # print('message')
        async with PgDB() as db:
            cursor = await db.get_cursor()

            guild = message.guild
            user = message.author

            # give xp
            await DbChecks.give_xp(db, guild, user)

            # implement role on message
            await DbChecks.role_on_message(cursor, guild, user, message)

    @levelGroup.command(name = 'show')
    async def level_embed(self, interaction: discord.Interaction, user: discord.Member = None):
        """Shows your level."""

        async with PgDB() as db:
            cursor = await db.get_cursor()

            guild = interaction.guild
            user = user or interaction.user

            if user.bot:
                embed = discord.Embed(title = "No levels for bots :P", color = discord.Color.from_str('#AF0606'))
                await interaction.response.send_message(embed = embed) # noqa
                return

            # search for user in the db
            await DbChecks.user_check(db, guild, user)

            # embed setup
            # TODO: get last role color instead of random
            embed = discord.Embed(title = f"Level and XP for {user.display_name}", color = user.roles[-1].color)

            # fetch xpvalue and levelvalue
            await cursor.execute("""
                select xp_value, level_value
                from leveling 
                where guild_id = %s and user_id = %s
            """, (guild.id, user.id))

            xp, level = await cursor.fetchone()
            embed.add_field(name = "Text XP", value = f"XP: {xp}", inline = False)
            embed.add_field(name = "Level", value = f"Level: {level}", inline = False)

            await db.commit()

            await interaction.response.send_message(embed = embed) # noqa

    @levelGroup.command(name = 'roles')
    async def roles(self, interaction: discord.Interaction):
        """Shows a list of all the level roles in the server."""

        async with PgDB() as db:
            cursor = await db.get_cursor()

            guild = interaction.guild

            # guild check and update
            await DbChecks.guild_check(db, guild)

            # select number of role guild has
            await cursor.execute("""
                select count(*)
                from roles
                where guild_id = %s and reach_level is not null and is_selfrole = %s
            """, (guild.id, False))
            if (await cursor.fetchone())[0] == 0:
                await interaction.response.send_message('This guild has no roles assigned to levels.') # noqa
                return

            await cursor.execute("""
                select role_id, reach_level from roles 
                where guild_id = %s and reach_level is not NULL and is_selfrole = %s
            """, (guild.id, False))

            await db.commit()

            role_list_db = await cursor.fetchall()
            role_list_db.sort(key = lambda x: x[1])
            role_list_db = list(itertools.chain(*role_list_db))

            role_list = [
                (discord.utils.get(guild.roles, id = role_id), level)
                for role_id, level in zip(role_list_db[::2], role_list_db[1::2])
            ]

            # TODO: select a different color for this embed
            embed = discord.Embed(title = f'Roles for {guild.name}', color = discord.Color.random())

            for role, level in role_list:
                embed.add_field(name = '', value = f'**{role.mention}**\nReached at level {level}', inline = False)

            await interaction.response.send_message(embed = embed) # noqa

    @levelGroup.command(name = 'setrole')
    @application_check(manage_roles = True)
    async def set_roles(self, interaction: discord.Interaction, role: discord.Role, level: int):
        """Sets a role to be given when x level is reached."""

        async with PgDB() as db:
            cursor = await db.get_cursor()

            guild = interaction.guild

            # check if there are already 10 roles assigned
            await cursor.execute("""
                select count(*)
                from roles
                where guild_id = %s and is_selfrole = %s;
            """, (guild.id, False))

            if (await cursor.fetchone())[0] >= 10:  # tf are you doing with more than 10 leveled roles :kek:
                await interaction.response.send_message( # noqa
                    "Your server already has the maximum number of roles (10)."
                    "More roles will be added with future updates if needed."
                    "\nIn the meantime you can remove the roles you don't need with the command ``unsetrole``",
                    ephemeral = True
                )
                return

            # check if the role already exists
            await cursor.execute("""
                select count(*)
                from roles
                where guild_id = %s and role_id = %s and is_selfrole = %s
            """, (guild.id, role.id, False))

            if (await cursor.fetchone())[0] == 0:
                await cursor.execute("""
                    insert into roles(role_id, guild_id, reach_level, is_selfrole)
                    values(%s, %s, %s, %s)
                """, (role.id, guild.id, level, False))
                await db.commit()
                await interaction.response.send_message( # noqa
                    f"The role **{role.mention}** has been added to the guild!"
                    f"People will receive it when they reach level **{level}**.",
                ephemeral = True)
            else:
                await interaction.response.send_message( # noqa
                    f"The role **{role.mention}** was already set and no changes were made",
                    ephemeral = True)

    @levelGroup.command(name = 'unsetrole')
    @application_check(manage_roles = True)
    @app_commands.describe(role = "The role that will be unset", remove = "Type 'yes' to remove the role from every user. Else, type 'no' or leave blank.")
    async def unsetrole(
        self, interaction: discord.Interaction,
        role: discord.Role,
        remove: Literal['yes', 'no'] = 'no'
    ):
        """Unsets a role from being given when reaching x level and removes it from every user if needed."""

        async with PgDB() as db:
            cursor = await db.get_cursor()

            guild = interaction.guild

            await cursor.execute("""
                select count(*)
                from roles
                where guild_id = %s and role_id = %s
            """, (guild.id, role.id))

            if (await cursor.fetchone())[0] > 0:
                await cursor.execute("""
                    delete from roles 
                    where guild_id = %s and role_id = %s
                """, (guild.id, role.id))
                await db.commit()

            await interaction.response.send_message( # noqa
                f"The role **<@&{role.id}>** will no more be assigned."
                "You can use ```/role delete <role>``` to delete it if necessary.",
                ephemeral = True
            )

            if remove == 'yes':
                await SelfroleHelper.remove_role(interaction, role)


async def setup(bot):
    await bot.add_cog(LevelSystem(bot))
