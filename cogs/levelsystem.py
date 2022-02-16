########################
#                      #
#     Level System     #
#                      #
########################

import os

import discord
from discord.ext import commands
import random
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
            if result[0] != 0:
                cursor.execute(f"select count(*) from guildinfo where guildname = '{guildname}';")
                result = cursor.fetchone()
            elif result[0] == 0:
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
        mydb = dbhelper.open()
        cursor = dbhelper.cursorget_cursor()

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

def setup(bot):
    bot.add_cog(LevelSystem(bot))