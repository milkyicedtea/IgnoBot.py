########################
#                      #
#     Level System     #
#                      #
########################

import os
from typing import ContextManager

import discord
from discord.ext import commands
import mariadb
import random

mydb = None
cursor = None

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, ctx):
        dbopen()
        global mydb
        global cursor
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
            print(f'Guildid search result is: {result}')
            if result[0] != 0:
                cursor.execute(f"select count(*) from guildinfo where guildname = '{guildname}';")
                result = cursor.fetchone()
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
            print(f'Guildid search result is: {result}')
            if result[0] != 0:
                cursor.execute(f"select count(*) from leveling where username = '{username}';")
                result = cursor.fetchone()
                if result[0] == 0:
                    cursor.execute(f"update leveling set username = '{username}' where userid = {userid};")
                    mydb.commit()
                    print(f'updated user {userid} with new name: {username}')
                else:
                    print(f'user {userid} with name {usernameraw} is already in the database')

        # search for user in the db
        cursor.execute(f'select count(*) from leveling where userid = {userid} and guildid = {guildid};')
        result = cursor.fetchone()
        print(f'userid exists = {result[0]}')

        if result[0] == 0:          # user is not in the db so we add him first and then give
            xptodb = 0
            leveltodb = 0
            cursor.execute(f"insert into leveling(guildid, userid, username, xpvalue, levelvalue) values({guildid} ,{userid}, '{username}', 0, 0);")
            print(f'new user {username} added')
            mydb.commit()
        elif userid == 913424314290815007:            # user is a bot so no xp for him
            print(f'The user ({username}) is a bot! No xp for bots')
            dbclose()
            return
        else:           # user is already in the the db so no changes to be made
            print(f'user {username} is already present in the db')

        # xp giving
        xprange = random.choice(range(1, 20+1))
        print(f'generated xp is = {xprange}')
        cursor.execute(f'select xpvalue from leveling where userid = {userid} and guildid = {guildid};')
        result = cursor.fetchone()
        xpfromdb = result[0]
        print(f'xpfromdb is = {result[0]}')
        xptodb = xpfromdb + xprange
        print(f'xptodb is = {xptodb}')
        # cursor.execute(f"insert into leveling set xpvalue = {xpfromdb} where userid = {userid} and guildid = {guildid};")
        # leveltodb = xpfromdb ** (1/5)
        cursor.execute(f"update leveling set xpvalue = {xptodb} where guildid = {guildid} and userid = {userid};")
        mydb.commit()
        dbclose()
        
    @commands.command(name = 'level', help = 'Shows your current level')
    async def level(self, ctx):
        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        userid = ctx.author.id
        levelfromdb = cursor.execute(f'select from leveling(levelvalue) where userid = {userid} and guildid = {guildid};')
        xpfromdb = cursor.execute(f'select from leveling(xpvalue) where userid = {userid} and guildid = {guildid};')

# db open/close
def dbopen():
    global mydb
    global cursor
    try:
        mydb = mariadb.connect(host = "localhost", user = "root", password = os.getenv('mariadb'), database = 'ignobot')
        print("Connected to the database")
    except mariadb.Error as e:
        print(f'Error connecting to the platform (mydb): {e}')

    # getting the cursor
    try:
        cursor = mydb.cursor()
    except mariadb.Error as c:
        print(f'Error connecting to the platform (cursor): {c}')

def dbclose():
    global mydb
    global cursor
    try:
        cursor.close()
        mydb.close()
        print(f'Database closed')
    except mariadb.Error as ce:
        print(f'Error while closing the database: {ce}')   


def setup(bot):
    bot.add_cog(LevelSystem(bot))