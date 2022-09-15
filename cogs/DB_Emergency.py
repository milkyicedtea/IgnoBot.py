####################
#                  #
#     Database     #
#                  #
####################

import os

import discord
from discord.ext import commands
from utils.dbhelper import DbHelper

import psycopg2

class DB_Emergency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Add-guild command
    @commands.command(name = 'add-guild', help = "ONLY USE THIS COMMANDS IF SOMETHING BREAKS **PLEASE**.")
    @commands.has_permissions(manage_guild = True)
    async def addguild(self, ctx):
        try:
            dbhelper = DbHelper()

            mydb = dbhelper.open()
            cursor = dbhelper.get_cursor()

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
            dbhelper.close()

        except psycopg2.Error as ag:
            print(f'Something went wrong: {ag}')

async def setup(bot):
    await bot.add_cog(DB_Emergency(bot))