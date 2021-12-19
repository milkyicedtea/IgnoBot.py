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
        guildname = ctx.guild.name
        userid = ctx.author.id
        primaryguildexist = cursor.execute(f"select count(*) from guildinfo where guildid = {guildid} and guildname = '{guildname}';")
        if primaryguildexist == 0:
            cursor.execute(f'insert into guildinfo(guildname, guildid) values({guildname}, {guildid};')
            cursor.execute(f'insert into guildinfo(guildname, guildid) values({guildname}, {guildid};')
            mydb.commit()
        xpsearch = cursor.execute(f'select count(*) from leveling where userid = {userid} and guildid = {guildid};')
        print(xpsearch)
        if xpsearch == 0:
            xpvalue = 0
            levelvalue = 0
            cursor.execute(f'insert into leveling(userid, guilid, xpvalue, levelvalue) values({userid}, {guildid}, {xpvalue}, {levelvalue});')
            mydb.commit()
        else:
            xprange = random.choice(range(1, 20+1))
            xpfromdb = cursor.execute(f'select xpvalue from leveling where userid = {userid} and guildid = {guildid};')
            print(xpfromdb)
            xpfromdb += xprange
            cursor.execute(f'insert into leveling(xpvalue) where userid = {userid} and guildid = {guildid} values({xpfromdb});')
            leveltodb = xpfromdb ** (1/5)
            cursor.execute(f'insert into leveling(levelvalue) where userid = {userid} and guildid = {guildid} values({leveltodb});')
        dbclose()
        
    @commands.command(name = 'level', help = 'Shows your current level')
    async def level(self, ctx):
        guildid = ctx.guild.id
        guildname = ctx.guild.name
        userid = ctx.author.id
        levelfromdb = cursor.execute(f'select from leveling(levelvalue) where userid = {userid} and guildid = {guildid};')
        xpfromdb = cursor.execute(f'select from leveling(xpvalue) where userid = {userid} and guildid = {guildid};')
        

    # memorizzazione dati....
    # SELECT xp, level FROM xpvalue, levelvalue
    #   WHERE guildid == ctx.guild.id memberid == ctx.message.author.id
    

    #anig - server1 - p+v
    #anig - server2 - b+v

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