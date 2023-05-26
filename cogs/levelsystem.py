########################
#                      #
#     Level System     #
#                      #
########################

import os

import discord
from discord.ext import commands
from discord import app_commands

from utils.dbchecks import DbChecks
from utils.dbhelper import DbHelper

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    levelGroup = app_commands.Group(name = 'level', description = 'Levels related commands')

    application_check = app_commands.checks.has_permissions

    # gives exp for every message
    @commands.Cog.listener()
    async def on_message(self, message):
        #print('message')
        
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        #print(f'message.guild.name {message.guild.name}')
        #print(f'message.author.name {message.author.name}')

        guildid = message.guild.id
        guildraw = message.guild.name
        guildname = guildraw.replace("'", "")
        userid = message.author.id
        usernameraw = message.author.name
        username = usernameraw.replace("'", "")
        user = message.author

        # guild check and update
        DbChecks.guildCheck(cursor, mydb, guildid, guildname)

        # guilsettings check and update
        DbChecks.settingsCheck(cursor, mydb, guildid)

        # user check and update
        DbChecks.userCheck(cursor, mydb, guildid, guildname, username, userid, user)

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

        guildid = interaction.guild_id
        guildraw = interaction.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = interaction.user.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()
        user = interaction.user
        
        # getting the right user id and display name
        if member is None:
            userid = interaction.user.id
            member = interaction.user
        else:
            userid = member.id
            if member.bot is True:
                embedVar = discord.Embed(title = "No levels for bots :P", color = (colorValue))
                await interaction.response.send_message(embed = embedVar)
                return

        # search for user in the db
        DbChecks.userCheck(cursor, mydb, guildid, guildname, member.name, member.id, member)

        # embed setup
        embedVar = discord.Embed(title = "Level and XP for {}".format(member.display_name), color = (colorValue))

        # fetch xpvalue
        cursor.execute(f'select xpvalue from leveling where guildid = {guildid} and userid = {userid};')
        result = cursor.fetchone()
        xpfromdb = result[0]
        embedVar.add_field(name = "Text XP", value = "XP: {}".format(xpfromdb), inline = False)

        # fetch levelvalue
        cursor.execute(f'select levelvalue from leveling where guildid = {guildid} and userid = {userid};')
        result = cursor.fetchone()
        levelfromdb = result[0]
        embedVar.add_field(name = "Level", value = "Level: {}".format(levelfromdb), inline = False)
        await interaction.response.send_message(embed = embedVar)
        dbhelper.close()

    # show a list of all the roles in the guild
    @levelGroup.command(name = 'roles')
    async def roles(self, interaction: discord.Interaction):
       
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = interaction.guild_id
        guildraw = interaction.guild.name
        guildname = guildraw.replace("'", "")
        userid = interaction.user.id
        usernameraw = interaction.user.name
        username = usernameraw.replace("'", "")
    
        rolename:str
        reachlevel:int

        # guild check and update
        DbChecks.guildCheck(cursor, mydb, guildid, guildname)

        # select number of role guild has
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and reachlevels is not NULL and is_selfrole = 'false';")
        result = cursor.fetchone()
        print(result[0])
        if result[0] == 0:
            await interaction.response.send_message('This guild has no roles assigned to levels.') # say this and end

        elif result[0] != 0:
            cursor.execute(f"select rolenames from roles where guildid = {guildid} and guildname = '{guildname}'  and reachlevels is not NULL and is_selfrole = 'false';") # pulls role names from rolename column in that guild
            rolenamedb = cursor.fetchmany(size = result[0])

            cursor.execute(f"select reachlevels from roles where guildid = {guildid} and guildname = '{guildname}'; and rolenames is not NULL and is_selfrole = 'false';") # pulls reachlevels from rolelevels column in that guild
            reachleveldb = cursor.fetchmany(size = result[0])

            embedVar = discord.Embed(title = 'Guild roles', color = discord.Colour.random())
            for x in range(result[0]):
                rolename = str(rolenamedb[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")
                reachlevel = str(reachleveldb[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")
                embedVar.add_field(name = f'{rolename}', value = f'Reached at level {reachlevel}') # REPLACE ROLENAME[X] WITH THE ROLE PING WITHOUT PINGING THAT ROLE IF POSSIBLE

            await interaction.response.send_message(embed = embedVar)
        dbhelper.close()

    # set roles to give for every levels
    @levelGroup.command(name = 'setrole')
    @application_check(manage_roles = True)
    async def set_roles(self, interaction: discord.Interaction, reach_level: int, *, role_name:str):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = interaction.guild_id
        guildraw = interaction.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = interaction.user.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()

        # check how many role the guild has
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and is_selfrole = 'false';")
        if cursor.fetchone()[0] >= 10:   # if it has more than 10 fuck off :kek:
            await interaction.response.send_message("Your server already has the maximum number of roles (10). More roles will be added with future updates if needed.\nIn the meantime you can remove the roles you don't need with the command ``unsetrole``", ephemeral = True)
        
        else:
            # check if the role already exists in db
            cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}' and is_selfrole = 'false';")
            role_exists = cursor.fetchone()
            if role_exists[0] == 0:
                role_exists_db: bool = False
                cursor.execute(f"insert into roles(guildname, guildid, rolenames, reachlevels, is_selfrole) values('{guildname}', {guildid}, '{role_name}', {reach_level}, 'false');")
                mydb.commit()
                #print("Role doesn't exist in db")
            else:
                role_exists_db: bool = True
                #print('Role already exists in db')

            # check if the role already exists in guild
            role = discord.utils.get(interaction.guild.roles, name = role_name)
            if role:
                role_exists_guild: bool = True
                #print("Role already exist in guild")
            else:
                role_exists_guild: bool = False
                await interaction.guild.create_role(name = role_name, colour = colorValue)  # create role
                #print("Role doesn't exists in guild")
            
            if role_exists_db and role_exists_guild:
                await interaction.response.send_message(f"The role **{role_name}** was already present and no changes were made", ephemeral = True)

            elif not role_exists_db or not role_exists_guild:
                await interaction.response.send_message(f"The role **{role_name}** has been added to the guild! People will receive it when they reach level **{reach_level}**", ephemeral = True)
            dbhelper.close()

    @levelGroup.command(name = 'unsetrole')
    @application_check(manage_roles = True)
    async def unsetrole(self, interaction: discord.Interaction, *, role_name: str):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = interaction.guild_id
        guildraw = interaction.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = interaction.user.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()

        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}';")
        result = cursor.fetchone()
        if result[0] > 0:
            cursor.execute(f"delete from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}';")
            mydb.commit()
        
        await interaction.response.send_message(f"The role **{role_name}** will no more be assigned")

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))