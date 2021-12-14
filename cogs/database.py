####################
#                  #
#     Database     #
#                  #
####################

import os

import discord
from discord.ext import commands

import mariadb

mydb = None
cursor = None

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Add-guild command
    @commands.command(name = 'add-guild', help = "Adds the current guild to the bot's database")
    @commands.has_permissions(manage_guild = True)
    async def addguild(self, ctx):
        try:
            dbopen()
            guildid = ctx.message.guild.id
            guildname = ctx.message.guild.name
            sql = f"INSERT INTO guildinfo(guildid, guildname) VALUES ({guildid}, '{guildname}')"
            print(sql)
            cursor.execute(sql)
            # auto commit is disabled so i mydb.commit()
            mydb.commit()
            await ctx.send(f'Guild {guildname} with id {guildid} was added to the database')
            dbclose()

        except mariadb.Error as ag:
            print(f'Something went wrong: {ag}')

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
    bot.add_cog(Database(bot))