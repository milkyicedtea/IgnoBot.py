####################
#                  #
#     Settings     #
#                  #
####################

import os

import discord
from discord.ext import commands
import psycopg2

mydb = None
cursor = None

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'setprefix', help = 'Sets the prefix for the bot in the current server')
    async def setprefix(self, ctx, prefix:str = None):
        global mydb
        global cursor
        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")

        dbopen()

        if prefix == None:
            print('prefix is none')
            prefix = 'i.'

        cursor.execute(f'select count(*) from guildinfo where guildid = {guildid};')
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute(f"insert into guildinfo(guildid) values({guildid});")
            mydb.commit()

        cursor.execute(f"select count(*) from guildsettings where guildid = {guildid};")
        result = cursor.fetchone()
        if result[0] == 0:
            cursor.execute(f"insert into guildsettings(guildid) values({guildid});")
            mydb.commit()

        print(f'guildid is {guildid}')
        print('prefix is {}'.format(prefix))
        cursor.execute(f"update guildsettings set prefix = '{prefix}' where guildid = {guildid};")
        print(cursor.rowcount)
        mydb.commit()
        await ctx.send(f"The bot's prefix is now set to {prefix}")
        dbclose()

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