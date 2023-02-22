########################
#                      #
#     Level System     #
#                      #
########################

import os

import discord
from discord.ext import commands

import random
import asyncio

from utils.dbhelper import DbHelper
from utils.dbchecks import DbChecks

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        DbChecks.checkUser(cursor, mydb, guildid, guildname, username, userid, user)

        # xp giving
        DbChecks.giveXp(cursor, mydb, guildid, guildname, username, userid, user)

        # implement giving role on message (kinda dumb way) (or?)
        await DbChecks.roleOnMessage(cursor, mydb, guildid, guildname, username, userid, user, message)

        dbhelper.close()

    # show an embed with level
    @commands.command(name = 'level')
    async def level_embed(self, ctx, member: discord.Member = None):

        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()
        user = ctx.message.author
        
        # getting the right user id
        if member == None:
            userid = ctx.author.id
        else:
            userid = member.id

        # getting the right name to display
        if member == None:
            member = ctx.author
        else:
            if member.bot is True:
                embedVar = discord.Embed(title = "No levels for bots :P", color = (colorValue))
                await ctx.reply(embed = embedVar, mention_author = False)
                return
        

        # search for user in the db
        DbChecks.checkUser(cursor, mydb, guildid, guildname, member.name, member.id, member)

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
        await ctx.reply(embed = embedVar, mention_author = False)
        dbhelper.close()

    

    # show a list of all the roles in the guild
    @commands.command(name = 'roles')
    async def roles(self, ctx):
       
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        userid = ctx.author.id
        usernameraw = ctx.author.name
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
            await ctx.send('This guild has no roles assigned to levels.') # say this and end

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

            await ctx.send(embed = embedVar)
        dbhelper.close()

    # set roles to give for every levels
    @commands.command(name = 'setrole')
    @commands.has_guild_permissions(manage_roles = True)
    async def set_roles(self, ctx ,reach_level: int, *, role_name:str):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()

        # check how many role the guild has
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and is_selfrole = 'false';")
        number_of_roles = cursor.fetchone()
        #print(number_of_roles)
        if number_of_roles[0] == 10 or number_of_roles[0] > 10:   # if it has more than 10 fuck off :kek:
            await ctx.send("Your server already has the maximum number of roles (10). More roles will be added with future updates if needed.\nIn the meantime you can remove the roles you don't need with the command ``unsetrole``")
            return

        # check if there role already exists in db
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}' and is_selfrole = 'false';")
        role_exists = cursor.fetchone()
        if role_exists[0] == 0:
            role_exists_db: bool = False
            #print("Role doesn't exist in db")
        else:
            role_exists_db: bool = True
            #print('Role already exists in db')

        #print(f'role_exists_db = {role_exists_db}')

        if role_exists_db == False:
            cursor.execute(f"insert into roles(guildname, guildid, rolenames, reachlevels, is_selfrole) values('{guildname}', {guildid}, '{role_name}', {reach_level}, 'false');")
            mydb.commit()

        role = discord.utils.get(ctx.message.guild.roles, name = role_name)

        # check if there role already exists in guild
        if role:
            role_exists_guild: bool = True
            #print("Role already exist in guild")
        else:
            role_exists_guild: bool = False
            #print("Role doesn't exists in guild")

        if role_exists_guild == False:    # guild doesn't have role named like that
            #print("guild doesn't have role")
            await ctx.guild.create_role(name = role_name, colour = colorValue)  # create role
            #print("role just created")
        
        if role_exists_db and role_exists_guild:
            await ctx.send(f"The role **{role_name}** was already present and no changes were made")

        elif not role_exists_db or not role_exists_guild:
            await ctx.send(f"The role **{role_name}** has been added to the guild! People will receive it when they reach level **{reach_level}**")
        dbhelper.close()

    @commands.command()
    @commands.has_guild_permissions(manage_roles = True)
    async def unsetrole(self, ctx, *, role_name: str):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()

        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}';")
        result = cursor.fetchone()
        if result[0] > 0:
            cursor.execute(f"delete from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}';")
            mydb.commit()
        
        await ctx.send(f"The role **{role_name}** will no more be assigned")

    # remove role from guild
    """@commands.command()
    @commands.has_guild_permissions(manage_roles = True)
    async def deleterole(self, ctx, *, role_name: str):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()

        delfromdb: bool = False
        delfromserver: bool = False

        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}';")
        result = cursor.fetchone()
        if result[0] > 0:
            cursor.execute(f"delete from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}';")
            mydb.commit()
            delfromdb: bool = True
        elif result[0] == 0:
            delfromdb: bool = True

        role = discord.utils.get(ctx.message.guild.roles, name = role_name)

        if role:
            await role.delete()
            delfromserver: bool = True

        if delfromdb and delfromserver:
            await ctx.send(f'The role **{role_name}** got deleted from existance >:)')
        else:
            await ctx.send(f"The role **{role_name}** couldn't be deleted due to an error. If this continues to happen please refer this to our discord server")
        dbhelper.close()"""

    # selfrole command
    @commands.command()
    async def selfrole(self, ctx, action, *, role_name: str = None):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()

        exists_in_db: bool = False
        exists_in_guild: bool = False

        if action == "list":
            #print('list')
            embed = discord.Embed(title = "\U0001f9fe Selfroles list", color = colorValue)
            embed.add_field(name = "", value = "**These are the available selfroles in the server.**", inline = False)
            embed.set_author(name = "", icon_url = ctx.guild.icon)

            cursor.execute(f"select rolenames from roles where guildid = {guildid} and guildname = '{guildname}' and is_selfrole = 'true';")
            fetch = cursor.fetchall()
            #print(fetch)

            for x in range(len(fetch)):
                fetch[x] = str(fetch[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")
                role = discord.utils.get(ctx.guild.roles, name = fetch[x])
                embed.add_field(name = "", value = f"{x+1}: **<@&{role.id}>**", inline = False)

            embed.set_footer(text = "Use the command `selfrole give` to give yourself the role")
            
            await ctx.send(embed = embed)


        elif action == "remove":
            # print('remove')
            if role_name is None:
                await ctx.reply(f'No role specified', delete_after = 5, mention_author = False)
                await asyncio.sleep(5)
                await ctx.message.delete()

            else:
                # print(ctx.message.author.guild_permissions.manage_roles)
                if ctx.message.author.guild_permissions.manage_roles:
                    # print('has perms')
                    cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}' and is_selfrole = 'true';")
                    if cursor.fetchone()[0] == 0:
                        await ctx.reply(f"An error occured: the role was not previously added as a selfrole!", delete_after = 5, mention_author = False)
                        await asyncio.sleep(5)
                        await ctx.message.delete()

                    else:
                        cursor.execute(f"delete from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}' and is_selfrole = 'true';")
                        mydb.commit()
                        # print(ctx.guild.members)
                        for member in ctx.guild.members:
                            # print(member)
                            role = discord.utils.get(ctx.guild.roles, name = role_name)
                            # print(role)
                            # print(member.roles)
                            # print(len(member.roles))
                            for x in range(len(member.roles) - 1):
                                if member.roles[x].name == role_name:
                                    await member.remove_roles(role)
                            
                        await ctx.send(f'The role **{role_name}** was removed from every user and is no longer self-assignable')
                else:
                    # print('no perms??')
                    raise commands.MissingPermissions()

        elif action == "add":
            # print('add')
            if not ctx.message.author.guild_permissions.manage_roles:
                raise commands.MissingPermissions
                
            else:
                if role_name is not None:
                    role = discord.utils.get(ctx.guild.roles, name = role_name)
                    # print(role_name)
                    # print(role)
                    if discord.utils.get(ctx.guild.roles, name = role_name):
                        cursor.execute(f"select count(*) from roles where guildid = {guildid} and rolenames = '{role_name}' and is_selfrole = 'true'")
                        if cursor.fetchone()[0] == 0:
                            cursor.execute(f"insert into roles(guildid, guildname, rolenames, is_selfrole) values({guildid}, '{guildname}', '{role_name}', 'true')")
                            mydb.commit()
                            await ctx.reply(f"The role **{role_name}** is now self-assignable!", mention_author = False)
                        else:
                            await ctx.reply(f"The role **{role_name}** is already self-assignable!", delete_after = 5, mention_author = False)
                            await asyncio.sleep(5)
                            await ctx.message.delete()
                    else:
                        await ctx.reply(f"This role doesn't exist!", delete_after = 5, mention_author = False)
                        await asyncio.sleep(5)
                        await ctx.message.delete()
                else:
                    await ctx.reply(f'No role specified', delete_after = 5, mention_author = False)
                    await asyncio.sleep(5)
                    await ctx.message.delete()

        elif action == "give":
            # print('give')
            if role_name is None:
                await ctx.reply(f'No role specified', delete_after = 5, mention_author = False)
                await asyncio.sleep(5)
                await ctx.message.delete()

            else:
                #check if role is present in db and guild
                role = discord.utils.get(ctx.guild.roles, name = role_name)
                if role:
                    exists_in_guild = True
                else:
                    await ctx.reply('The role specified does not exist.', delete_after = 5, mention_author = False)
                    await asyncio.sleep(5)
                    await ctx.message.delete()

                
                cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}';")
                result = cursor.fetchone()
                if result[0] > 0:
                    exists_in_db = True
                else:
                    await ctx.reply('The role specified was not added to selfroles.', delete_after = 5, mention_author = False)
                    await asyncio.sleep(5)
                    await ctx.message.delete()

                if exists_in_db and exists_in_guild:
                    await ctx.message.author.add_roles(role)
                    await ctx.reply(f"The role **{role_name}** has been assigned to you", mention_author = False)

        elif action == "leave":
            # print('leave')
            if role_name is None:
                await ctx.reply(f'No role specified', delete_after = 5, mention_author = False)
                await asyncio.sleep(5)
                await ctx.message.delete()

            else:
                #check if role is present in db and guild
                role = discord.utils.get(ctx.guild.roles, name = role_name)
                if role:
                    exists_in_guild = True
                else:
                    await ctx.reply('The role specified does not exist.', delete_after = 5, mention_author = False)
                    await asyncio.sleep(5)
                    await ctx.message.delete()

                cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}';")
                result = cursor.fetchone()
                if result[0] > 0:
                    exists_in_db = True
                else:
                    await ctx.reply('The role specified was not added to selfroles.', delete_after = 5, mention_author = False)
                    await asyncio.sleep(5)
                    await ctx.message.delete()

                if exists_in_db and exists_in_guild:
                    await ctx.message.author.remove_roles(role)
                    await ctx.reply(f"The role **{role_name}** has been removed from your current roles", mention_author = False)


        else:
            await ctx.send(f'The action specified was not valid: try with `give` or `leave`')

        dbhelper.close()

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))