####################
#                  #
#     Settings     #
#                  #
####################

import os

import discord
from discord.ext import commands
from utils.dbhelper import DbHelper

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'setprefix', help = 'Sets the prefix for the bot in the current server')
    async def setprefix(self, ctx, prefix:str = None):
        guildid = ctx.guild.id

        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

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
        dbhelper.close()

def setup(bot):
    bot.add_cog(Settings(bot))