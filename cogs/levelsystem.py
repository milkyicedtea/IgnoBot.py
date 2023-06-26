########################
#                      #
#     Level System     #
#                      #
########################

import os

import discord
from discord.ext import commands
from discord import app_commands

import itertools

from utils.dbchecks import DbChecks
from utils.dbhelper import DbHelper

from cogs.utils.selfrole_helper import SelfroleHelper

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    levelGroup = app_commands.Group(name = 'level', description = 'Levels related commands')

    application_check = app_commands.checks.has_permissions

    # gives exp for every message
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # print('message')
        
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        # print(f'message.guild.name {message.guild.name}')
        # print(f'message.author.name {message.author.name}')

        guild = message.guild
        user = message.author

        # xp giving
        DbChecks.give_xp(cursor, mydb, guild, user)

        # implement giving role on message (kinda dumb way) (or?)
        await DbChecks.role_on_message(cursor, guild, user, message)

        dbhelper.close()

    @levelGroup.command(name = 'show')
    async def level_embed(self, interaction: discord.Interaction, user: discord.Member = None):
        """Shows your level."""
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        colorValue = discord.Colour.random()
        
        # getting the right user id and display name
        if user is None:
            user = interaction.user

        if user.bot is True:
            embedVar = discord.Embed(title = "No levels for bots :P", color = colorValue)
            await interaction.response.send_message(embed = embedVar)
            return

        # search for user in the db
        DbChecks.user_check(cursor, mydb, guild, user)

        # embed setup
        embedVar = discord.Embed(title = "Level and XP for {}".format(user.display_name), color = colorValue)

        # fetch xpvalue
        cursor.execute(f'select xpvalue from leveling where guildid = {guild.id} and userid = {user.id};')
        embedVar.add_field(name = "Text XP", value = f"XP: {cursor.fetchone()[0]}", inline = False)

        # fetch levelvalue
        cursor.execute(f'select levelvalue from leveling where guildid = {guild.id} and userid = {user.id};')
        embedVar.add_field(name = "Level", value = f"Level: {cursor.fetchone()[0]}", inline = False)
        await interaction.response.send_message(embed = embedVar)
        dbhelper.close()


    @levelGroup.command(name = 'roles')
    async def roles(self, interaction: discord.Interaction):
        """Shows a list of all the level roles in the server."""
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild

        # guild check and update
        DbChecks.guild_check(cursor, mydb, guild)
        guildname = guild.name.replace("'", "")

        # select number of role guild has
        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and guildname = '{guildname}' "
                       f"and reachlevels is not NULL "
                       f"and is_selfrole = 'false';")
        if cursor.fetchone()[0] == 0:
            await interaction.response.send_message('This guild has no roles assigned to levels.')  # say this and end

        else:
            cursor.execute(f"select rolenames from roles where guildid = {guild.id} "
                           f"and guildname = '{guildname}'  "
                           f"and reachlevels is not NULL "
                           f"and is_selfrole = 'false';")  # pulls role names from rolename column in that guild
            roleListDb: list = list(itertools.chain(*cursor.fetchall()))
            roleList: list[discord.Role] = []
            for role in roleListDb:
                roleList.append(discord.utils.get(interaction.guild.roles, name = str(role)))

            cursor.execute(f"select reachlevels from roles where guildid = {guild.id} "
                           f"and guildname = '{guildname}' "
                           f"and rolenames is not NULL "
                           f"and is_selfrole = 'false';")  # pulls reachlevels from rolelevels column in that guild
            reachLevelList = list(itertools.chain(*cursor.fetchall()))

            embed = discord.Embed(title = 'Guild roles', color = discord.Colour.random())

            for role, level in zip(roleList, reachLevelList):
                embed.add_field(name = '', value = f'**{role.mention}**\nReached at level {level}', inline = False)

            await interaction.response.send_message(embed = embed)
        dbhelper.close()

    @levelGroup.command(name = 'setrole')
    @application_check(manage_roles = True)
    async def set_roles(self, interaction: discord.Interaction, role: discord.Role, level: int):
        """Sets a role to be given when x level is reached."""
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        guildname = guild.name.replace("'", "")

        # check how many role the guild has
        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and guildname = '{guildname}' and is_selfrole = 'false';")
        if cursor.fetchone()[0] >= 10:   # tf are you doing with more than 10 leveled roles :kek:
            await interaction.response.send_message("Your server already has the maximum number of roles (10). "
                                                    "More roles will be added with future updates if needed."
                                                    "\nIn the meantime you can remove the roles you don't need "
                                                    "with the command ``unsetrole``", ephemeral = True)
        
        else:
            # check if the role already exists in db
            cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                           f"and guildname = '{guildname}' and rolenames = '{role.name}' "
                           f"and is_selfrole = 'false';")
            if cursor.fetchone()[0] == 0:
                role_exists_db: bool = False
                cursor.execute(f"insert into roles(guildname, guildid, rolenames, reachlevels, is_selfrole) "
                               f"values('{guildname}', {guild.id}, '{role.name}', {level}, 'false');")
                mydb.commit()
                # print("Role doesn't exist in db")
            else:
                role_exists_db: bool = True
                # print('Role already exists in db')

            if role_exists_db:
                await interaction.response.send_message(f"The role **{role.mention}** was already present and no changes were made", ephemeral = True)

            elif not role_exists_db:
                await interaction.response.send_message(f"The role **{role.mention}** has been added to the guild! People will receive it when they reach level **{level}**", ephemeral = True)
        dbhelper.close()

    @levelGroup.command(name = 'unsetrole')
    @application_check(manage_roles = True)
    @app_commands.describe(role = "The role that will be unset", remove = "Type 'yes' to remove the role from every user. Else, type 'no' or leave blank.")
    async def unsetrole(self, interaction: discord.Interaction, role: discord.Role, remove: str = None):
        """Unsets a role from being given when reaching x level and removes it from every user if needed."""
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        guildname = guild.name.replace("'", "")

        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and guildname = '{guildname}' and rolenames = '{role.name}';")

        if cursor.fetchone()[0] > 0:
            cursor.execute(f"delete from roles where guildid = {guild.id} "
                           f"and guildname = '{guildname}' and rolenames = '{role.name}';")
            mydb.commit()
        
        await interaction.response.send_message(f"The role **<@&{role.id}>** will no more be assigned. You can use"
                                                f"```/role delete <role>``` to delete it if necessary.", ephemeral = True)
        if remove or remove == 'yes':
            SelfroleHelper.remove_role(interaction, role)

        dbhelper.close()


async def setup(bot):
    await bot.add_cog(LevelSystem(bot))
