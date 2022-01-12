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
        username = ctx.author.name
        cursor.execute(f"select count(*) from guildinfo where guildid = {guildid} and guildname = '{guildname}';")
        result = cursor.fetchone()
        print(f'guild exists = {result[0]}')
        if result[0] == 0:
            cursor.execute(f"insert into guildinfo(guildid, guildname) values({guildid},'{guildname}');")
            mydb.commit()
        cursor.execute(f'select count(*) from leveling where userid = {userid} and guildid = {guildid};')
        result = cursor.fetchone()
        print(f'userid exists = {result[0]}')
        if result[0] == 0:
            xptodb = 0
            leveltodb = 0
            cursor.execute(f'insert into leveling(guildid, userid, xpvalue, levelvalue) values({guildid} ,{userid}, 0, 0);')
            print('new user added')
            mydb.commit()
        else:
            print(f'user {username} is already present in the db')
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
        guildname = ctx.guild.name
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