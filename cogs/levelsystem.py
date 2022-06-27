########################
#                      #
#     Level System     #
#                      #
########################

import os

import discord
from discord.ext import commands

import random

from numpy import number
from utils.dbhelper import DbHelper

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, ctx):

        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        userid = ctx.author.id
        usernameraw = ctx.author.name
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
            level+= 1
        cursor.execute(f'update leveling set xpvalue = {xptodb} where guildid = {guildid} and userid = {userid};')
        cursor.execute(f'update leveling set levelvalue = {level} where guildid = {guildid} and userid = {userid};')
        mydb.commit()
        dbhelper.close()
        
    # level embed
    @commands.command(name = 'level', help = 'Shows your current level')
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
            print(member)

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

        print('here')
        # select number of role guild has
        cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}' and rolenames != NULL and reachlevels != NULL;")
        result = cursor.fetchone()
        print(result[0])
        if result[0] == 0:
            await ctx.send('This guild has no roles assigned to levels.') # say this and end

        elif result[0] != 0:
            cursor.execute(f"select rolenames from roles where guildid = {guildid} and guildname = '{guildname}';") # pulls role names from rolename column in that guild
            rolename = cursor.fetchall()
            cursor.execute(f"select rolelevels from roles where guildid = {guildid} and guildname = '{guildname}';") # pulls reachlevels from rolelevels column in that guild
            reachlevel = cursor.fetchall()
            embedVar = discord.Embed(title = 'Guild roles', color = discord.Colour.random())
            for x in range(len(rolename)):
                embedVar.add_field(name = f'{rolename[x]}', value = f'Reached at level {reachlevel[x]}') # REPLACE ROLENAME[X] WITH THE ROLE PING WITHOUT PINGING THAT ROLE IF POSSIBLE

            await ctx.send(embed = embedVar)
        dbhelper.close()

    # set roles to give for every levels
    @commands.command(name = 'setroles')
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
            await ctx.send('Your server already has the maximum number of roles (10). More roles will be added with future updates if needed.')
            print('exiting')
            return
        else:
            print('first else')
            cursor.execute(f"insert into roles(guildname, guildid, rolenames, reachlevels) values('{guildname}', {guildid}, '{role_name}', {reach_level});")
            print('insert exe')
            mydb.commit()

        # check if the role already exixts
        print(discord.utils.get(ctx.guild.roles, name = {role_name}))
        if str(discord.utils.get(ctx.guild.roles, name = {role_name})) == None:    # guild doesn't have role named like that
            print("guild doesn't have role")
            await ctx.guild.create_role(name = role_name)   # create role
            print('role just created')
        
        dbhelper.close()
        await ctx.send(f"The role **{role_name}** has been added to the guild! People will receive it when they reach level **{reach_level}**")

def setup(bot):
    bot.add_cog(LevelSystem(bot))