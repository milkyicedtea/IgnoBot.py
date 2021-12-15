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
import math

mydb = None
cursor = None

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, ctx, member = discord.member):
        dbopen()
        guildid = ctx.guild.id
        guildname = ctx.guild.name
        userid = ctx.author.id
        primaryguildexist = print(f'select count(*) from guildinfo where guildid = {guildid} and guildname = {guildname}')
        if primaryguildexist == 0:
            print(f'insert into guildinfo(guildname, guildid) values({guildname}, {guildid}')
        xpsearch = print(f'select count(*) from leveling where userid = {userid} and guildid = {guildid}')
        if xpsearch == 0:
            xpvalue = 0
            levelvalue = 0
            print(f'insert into leveling(userid, guilid, xpvalue, levelvalue) values({userid}, {guildid}, {xpvalue}, {levelvalue})')
        else:
            xprange = random.choice(range(1, 20+1))
            xpvaluefromdb = print(f'select * from leveling(xpvalue) where userid = {userid} and guildid = {guildid}')
            print(f'{xpvaluefromdb}')
            xpvaluefromdb += xprange
            print(f'insert into leveling(xpvalue) where userid = {userid} and guildid = {guildid} values({xpvaluefromdb})')
            levelvaluetodb = xpvaluefromdb ** (1/5)
            print(f'insert into leveling(levelvalue) where userid = {userid} and guildid = {guildid} values({levelvaluetodb})')
        dbclose()
        
    @commands.command(name = 'level', help = 'Shows your current level')
    async def level(self, ctx, member = discord.member):
        guildid = ctx.guild.id
        guildname = ctx.guild.name
        userid = ctx.author.id
        levelfromdb = print(f'select from leveling(levelvalue) where userid = {userid} and guildid = {guildid}')
        

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