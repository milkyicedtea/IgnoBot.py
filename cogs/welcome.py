########################
#                      #
#     Level System     #
#                      #
########################

import os

import discord
from discord.ext import commands
import random
import psycopg2

mydb = None
cursor = None

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'set-welcome', help = 'Used to set your welcome message when a user joins')
    @commands.has_permissions(manage_guild = True)
    async def set_welcome(self, ctx, message:str, ):
        await ctx.send('This command is currently WIP')










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
    bot.add_cog(Welcome(bot))