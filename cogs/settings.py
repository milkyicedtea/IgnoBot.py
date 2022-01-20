####################
#                  #
#     Settings     #
#                  #
####################

import os

import discord
from discord.ext import commands
import random
import psycopg2

mydb = None
cursor = None

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'setprefix', help = 'Sets the prefix for the bot in the current server')
    async def setprefix(self, ctx, *, prefix: None):
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
            elif result[0] == 0:
                cursor.execute(f"insert into guildinfo(guildid, guildname) values({guildid}, '{guildname}');")
                mydb.commit()
                if result[0] == 0:
                    cursor.execute(f"update guildinfo set guildname = '{guildname}' where guildid = {guildid};")
                    mydb.commit()
                    print(f'updated guild {guildid} with new name: {guildname}')
                else:
                    print(f'guild {guildid} with name {guildname} is already in the database')

        cursor.execute(f"select prefix from guildsettings where guildid = {guildid}")
        result = cursor.fetchone()
        







# db open/close
def dbopen():
    global mydb
    global cursor
    try:
        mydb = psycopg2.connect(host = os.getenv('dbhost'), user = os.getenv('dbuser'), password = os.getenv('dbpw'), database = os.getenv('db_db'), port = os.getenv('dbport'))
        print("Connected to the database")
    except psycopg2.Error as e:
        print(f'Error connecting to the platform (mydb): {e}')

    # getting the cursor
    try:
        cursor = mydb.cursor()
    except psycopg2.Error as c:
        print(f'Error connecting to the platform (cursor): {c}')

def dbclose():
    global mydb
    global cursor
    try:
        cursor.close()
        mydb.close()
        print(f'Database closed')
    except psycopg2.Error as ce:
        print(f'Error while closing the database: {ce}')   

def setup(bot):
    bot.add_cog(Settings(bot))