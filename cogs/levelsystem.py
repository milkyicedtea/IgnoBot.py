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

        # guild check and update
        DbChecks.guildCheck(cursor, mydb, guild.id, guild.name)

        # guilsettings check and update
        DbChecks.settingsCheck(cursor, mydb, guild.id)

        # user check and update
        DbChecks.userCheck(cursor, mydb, guild, user)

        # xp giving
        DbChecks.giveXp(cursor, mydb, guildid, guildname, username, userid, user)

        # implement giving role on message (kinda dumb way) (or?)
        await DbChecks.roleOnMessage(cursor, mydb, guildid, guildname, username, userid, user, message)

        dbhelper.close()

    # show an embed with level
    @levelGroup.command(name = 'show')
    async def level_embed(self, interaction: discord.Interaction, member: discord.Member = None):

        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        user = interaction.user
        colorValue = discord.Colour.random()
        
        # getting the right user id and display name
        if member is None:
            member = interaction.user.id, interaction.user

        if member.bot is True:
            embedVar = discord.Embed(title = "No levels for bots :P", color = colorValue)
            await interaction.response.send_message(embed = embedVar)
            return

        # search for user in the db
        DbChecks.userCheck(cursor, mydb, guild.id, guild.name, member.name, member.id, member)

        # embed setup
        embedVar = discord.Embed(title = "Level and XP for {}".format(member.display_name), color = colorValue)

        # fetch xpvalue
        cursor.execute(f'select xpvalue from leveling where guildid = {guild.id} and userid = {member.id};')
        embedVar.add_field(name = "Text XP", value = f"XP: {cursor.fetchone()[0]}", inline = False)

        # fetch levelvalue
        cursor.execute(f'select levelvalue from leveling where guildid = {guild.id} and userid = {member.id};')
        embedVar.add_field(name = "Level", value = f"Level: {cursor.fetchone()[0]}", inline = False)
        await interaction.response.send_message(embed = embedVar)
        dbhelper.close()

    # show a list of all the roles in the guild
    @levelGroup.command(name = 'roles')
    async def roles(self, interaction: discord.Interaction):

        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        user = interaction.user

        rolename: str
        reachlevel: int

        # guild check and update
        DbChecks.guildCheck(cursor, mydb, guild.id, guild.name)

        # select number of role guild has
        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and guildname = '{guild.name}' "
                       f"and reachlevels is not NULL "
                       f"and is_selfrole = 'false';")
        result = cursor.fetchone()
        print(result[0])
        if result[0] == 0:
            await interaction.response.send_message('This guild has no roles assigned to levels.')  # say this and end

        elif result[0] != 0:
            cursor.execute(f"select rolenames from roles where guildid = {guild.id} "
                           f"and guildname = '{guild.name}'  "
                           f"and reachlevels is not NULL "
                           f"and is_selfrole = 'false';")  # pulls role names from rolename column in that guild
            roleListDb: list = list(itertools.chain(*cursor.fetchmany(size = result[0])))
            roleList: list[discord.Role]
            for role in roleListDb:
                roleList.append(discord.utils.get(interaction.guild.roles, name = roleListDb[role]))

            cursor.execute(f"select reachlevels from roles where guildid = {guild.id} "
                           f"and guildname = '{guild.name}' "
                           f"and rolenames is not NULL "
                           f"and is_selfrole = 'false';")  # pulls reachlevels from rolelevels column in that guild
            reachLevelList = list(itertools.chain(*cursor.fetchmany(size = result[0])))

            embed = discord.Embed(title = 'Guild roles', color = discord.Colour.random())

            # TO TEST
            for role, level in roleList, reachLevelList:
                embed.add_field(name = f'<@&{role.id}>', value = f'Reached at level {int(level)}')  # REPLACE ROLENAME[X] WITH THE ROLE PING WITHOUT PINGING THAT ROLE IF POSSIBLE

            await interaction.response.send_message(embed = embed)
        dbhelper.close()

    # set roles to give for every levels
    @levelGroup.command(name = 'setrole')
    @application_check(manage_roles = True)
    async def set_roles(self, interaction: discord.Interaction, role: discord.Role, level: int):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        user = interaction.user
        colorValue = discord.Colour.random()

        # check how many role the guild has
        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and guildname = '{guild.name}' and is_selfrole = 'false';")
        if cursor.fetchone()[0] >= 10:   # tf are you doing with more than 10 leveled roles :kek:
            await interaction.response.send_message("Your server already has the maximum number of roles (10). "
                                                    "More roles will be added with future updates if needed."
                                                    "\nIn the meantime you can remove the roles you don't need "
                                                    "with the command ``unsetrole``", ephemeral = True)
        
        else:
            # check if the role already exists in db
            cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                           f"and guildname = '{guild.name}' and rolenames = '{role.name}' "
                           f"and is_selfrole = 'false';")
            if cursor.fetchone()[0] == 0:
                role_exists_db: bool = False
                cursor.execute(f"insert into roles(guildname, guildid, rolenames, reachlevels, is_selfrole) "
                               f"values('{guild.name}', {guild.id}, '{role.name}', {level}, 'false');")
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
    async def unsetrole(self, interaction: discord.Interaction, role: discord.Role):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        user = interaction.user
        colorValue = discord.Colour.random()

        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and guildname = '{guild.name}' and rolenames = '{role.name}';")

        if cursor.fetchone()[0] > 0:
            cursor.execute(f"delete from roles where guildid = {guild.id} "
                           f"and guildname = '{guild.name}' and rolenames = '{role.name}';")
            mydb.commit()
        
        await interaction.response.send_message(f"The role **<@&{role.id}>** will no more be assigned. You can use"
                                                f"```/role delete <role>``` to delete it if necessary.")
        dbhelper.close()

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))