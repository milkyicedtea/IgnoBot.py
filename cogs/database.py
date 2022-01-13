####################
#                  #
#     Database     #
#                  #
####################

import os

import discord
from discord import guild
from discord.ext import commands

import mariadb

mydb = None
cursor = None

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Add-guild command
    @commands.command(name = 'add-guild', help = "ONLY USE THIS COMMANDS IF SOMETHING BREAKS **PLEASE**.")
    @commands.has_permissions(manage_guild = True)
    async def addguild(self, ctx):
        try:
            dbopen()
            guildid = ctx.message.guild.id
            guildraw = ctx.guild.name
            guildname = guildraw.replace("'", "")
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
                elif result[0] == 0:
                    cursor.execute(f"insert into guildinfo(guildid, guildname) values ({guildid}, '{guildname}');")
                    # auto commit is disabled so i mydb.commit()
                    mydb.commit()
                    await ctx.send(f"Guild '{guildname}' with id {guildid} was added to the database")
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