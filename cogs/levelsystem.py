########################
#                      #
#     Level System     #
#                      #
########################

from dataclasses import dataclass
import os

import discord
from discord.ext import commands

import random

from utils.dbhelper import DbHelper

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # gives exp for every message
    @commands.Cog.listener()
    async def on_message(self, message):

        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = message.guild.id
        guildraw = message.guild.name
        guildname = guildraw.replace("'", "")
        userid = message.author.id
        usernameraw = message.author.name
        username = usernameraw.replace("'", "")

        # guild check and update
        cursor.execute(f"select count(*) from guildinfo where guildid = {guildid} and guildname = '{guildname}';")
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute(f'select count(*) from guildinfo where guildid = {guildid};')
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute(f"insert into guildinfo(guildid, guildname) values({guildid}, '{guildname}');")
                mydb.commit()
                if result[0] == 0:
                    cursor.execute(f"update guildinfo set guildname = '{guildname}' where guildid = {guildid};")
                    mydb.commit()
                    print(f'updated guild {guildid} with new name: {guildname}')
                else:
                    print(f'guild {guildid} with name {guildname} is already in the database')

        # user check and update
        cursor.execute(f"select count(*) from guildinfo where guildid = {guildid} and guildname = '{guildname}';")
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute(f'select count(*) from leveling where userid = {userid};')
            result = cursor.fetchone()
            if result[0] != 0:
                cursor.execute(f"select count(*) from leveling where username = '{username}';")
                result = cursor.fetchone()
                if result[0] == 0:
                    cursor.execute(f"update leveling set username = '{username}' where userid = {userid};")
                    mydb.commit()
                    print(f'updated user {userid} with new name: {username}')

        # search for user in the db
        cursor.execute(f'select count(*) from leveling where userid = {userid} and guildid = {guildid};')
        result = cursor.fetchone()

        if result[0] == 0:          # user is not in the db so we add him first and then give
            xptodb = 0
            leveltodb = 0
            cursor.execute(f"insert into leveling(guildid, userid, username, xpvalue, levelvalue) values({guildid}, {userid}, '{username}', 0, 0);")
            print(f'new user {username} added')
            mydb.commit()

        # xp giving
        xprange = random.choice(range(1, 20+1))
        cursor.execute(f'select xpvalue from leveling where userid = {userid} and guildid = {guildid};')            # getting xp
        result = cursor.fetchone()
        xpfromdb = result[0]
        xptodb = xpfromdb + xprange
        cursor.execute(f'select levelvalue from leveling where guildid = {guildid} and userid = {userid}')          # getting level
        result = cursor.fetchone()
        level = result[0]
        if level == 0:
            neededtolvl = 100
        else:
            neededtolvl = level * level * 100           # determines how much xp is needed to level up
        if xpfromdb >= neededtolvl:
            level += 1
        cursor.execute(f'update leveling set xpvalue = {xptodb} where guildid = {guildid} and userid = {userid};')
        cursor.execute(f'update leveling set levelvalue = {level} where guildid = {guildid} and userid = {userid};')
        mydb.commit()

        # implement giving role on message (kinda dumb way) (or?)
        user = message.author
        if not user.bot:    # checks if user is bot
            cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}';")
            result = cursor.fetchone()
            if result[0] > 0:
                cursor.execute(f"select rolenames from roles where guildid = {guildid} and guildname = '{guildname}';")
                rolenames = cursor.fetchmany(size = result[0])
                cursor.execute(f"select reachlevels from roles where guildid = {guildid} and guildname = '{guildname}';")
                reachlevels = cursor.fetchmany(size = result[0])
                for x in range(result[0]):
                    #print('dum')
                    reachlevel = int(str(reachlevels[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                    #print(f'level = {level}, reachlevel = {reachlevel}')
                    if level >= reachlevel:
                        # print('if')
                        index = x-1
                        role = discord.utils.get(message.guild.roles, name = str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                        # print(str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                        if role:
                            await message.author.add_roles(role)
                        else:
                            realrole = str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")
                            await message.channel.send(f"There was an error while assigning the role **{realrole}**. Please report this to our discord.")
            else:
                print('no roles')
        dbhelper.close()

    # show an embed with level
    @commands.command(name = 'level')
    async def level_embed(self, ctx, member: discord.Member = None):

        dbhelper = DbHelper()
        dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()
        
        # getting the right user id
        if member == None:
            userid = ctx.author.id
        else:
            userid = member.id

        # getting the right name to display
        if member == None:
            member = usernameraw
        else:
            member = member.display_name

        # search for user in the db
        cursor.execute(f'select count(*) from leveling where userid = {userid} and guildid = {guildid};')
        result = cursor.fetchone()
        print(f'userid exists = {result[0]}')

        if result[0] == 0:          # user is not in the database so we return an error message
            await ctx.send('Something went wrong while loading your xp stats.')
            print("Error while fetching someone's stats")

        # embed setup
        embedVar = discord.Embed(title = "Level and XP for {}".format(member), color = (colorValue))

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
    @commands.command()
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

        @dataclass
        class roles:
            rolename:str
            reachlevel:int

        # guild check and update
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}';")
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute(f'select count(*) from roles where guildid = {guildid};')
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute(f"insert into roles(guildid, guildname) values({guildid}, '{guildname}');")
                mydb.commit()
                if result[0] == 0:
                    cursor.execute(f"update roles set guildname = '{guildname}' where guildid = {guildid};")
                    mydb.commit()
                    print(f'updated guild {guildid} with new name: {guildname}')                    
                else:
                    print(f'guild {guildid} with name {guildname} is already in the database')

        # select number of role guild has
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}';")
        result = cursor.fetchone()
        print(result[0])
        if result[0] == 0:
            await ctx.send('This guild has no roles assigned to levels.') # say this and end

        elif result[0] != 0:
            cursor.execute(f"select rolenames from roles where guildid = {guildid} and guildname = '{guildname}';") # pulls role names from rolename column in that guild
            rolenamedb = cursor.fetchmany(size = result[0])

            cursor.execute(f"select reachlevels from roles where guildid = {guildid} and guildname = '{guildname}';") # pulls reachlevels from rolelevels column in that guild
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
    @commands.has_permissions(manage_roles = True)
    async def set_roles(self, ctx, reach_level: int, *, role_name:str):
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
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}';")
        number_of_roles = cursor.fetchone()
        print(number_of_roles)
        if number_of_roles[0] == 10 or number_of_roles[0] > 10:   # if it has more than 10 fuck off :kek:
            await ctx.send("Your server already has the maximum number of roles (10). More roles will be added with future updates if needed.\nIn the meantime you can remove the roles you don't need with the command ``removerole``")
            return

        # check if there role already exists in db
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}';")
        role_exists = cursor.fetchone()
        if role_exists[0] == 0:
            role_exists_db: bool = False
            print("Role doesn't exist in db")
        else:
            role_exists_db: bool = True
            print('Role already exists in db')

        print(f'role_exists_db = {role_exists_db}')

        if role_exists_db == False:
            cursor.execute(f"insert into roles(guildname, guildid, rolenames, reachlevels) values('{guildname}', {guildid}, '{role_name}', {reach_level});")
            mydb.commit()

        role = discord.utils.get(ctx.message.guild.roles, name = role_name)

        # check if there role already exists in guild
        if role:
            role_exists_guild: bool = True
            print("Role already exist in guild")
        else:
            role_exists_guild: bool = False
            print("Role doesn't exists in guild")

        if role_exists_guild == False:    # guild doesn't have role named like that
            print("guild doesn't have role")
            await ctx.guild.create_role(name = role_name, colour = colorValue)  # create role
            print("role just created")
        
        if role_exists_db and role_exists_guild:
            await ctx.send(f"The role **{role_name}** was already present and no changed were made")

        elif not role_exists_db or not role_exists_guild:
            await ctx.send(f"The role **{role_name}** has been added to the guild! People will receive it when they reach level **{reach_level}**")
        dbhelper.close()

    # remove role from guild
    @commands.command()
    @commands.has_permissions(manage_roles = True)
    async def removerole(self, ctx, *, role_name: str):
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
        dbhelper.close()

    # selfrole command
    @commands.command()
    async def selfrole(self, ctx, *, role_name: str):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")
        colorValue = discord.Colour.random()

        member: discord.Member = ctx.message.author

        exists_in_db: bool = False
        exists_in_guild: bool = False

        #check if role is present in db and guild
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames = '{role_name}'")
        result = cursor.fetchone()
        if result[0] > 0:
            exists_in_db = True
        else:
            print('role is not in db')

        role = discord.utils.get(ctx.message.guild.roles, name = role_name)

        if role:
            exists_in_guild = True
            print('role is in guild')
        else:
            print('role is not in guild')

        if exists_in_db and exists_in_guild:
            print('test')
            await member.add_roles(role)
            await ctx.send(f'The role **{role_name}** has been assigned to you')
        else:
            print('Something went wrong')
        dbhelper.close()

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))