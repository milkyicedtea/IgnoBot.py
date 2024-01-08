####################
#                  #
#     Database     #
#                  #
####################

from discord.ext import commands

from utils.dbhelper import DbHelper

import psycopg2


class DbEmergency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dbhelper = DbHelper()

    # THIS COMMAND CAN ONLY BE USED BY THE ACCOUNT THAT OWNS THE BOT DUE TO SECURITY/DATABASE SPAM PREVENTING
    @commands.command(name = 'add-guild')
    @commands.is_owner()
    @commands.guild_only()
    async def addguild(self, ctx):
        """Manually adds a guild (server) to the database."""

        try:

            mydb = self.dbhelper.open()
            cursor = self.dbhelper.get_cursor()

            guildid = ctx.message.guild.id
            guildraw = ctx.guild.name

            guildname = guildraw.replace("'", "")
            cursor.execute(f"select count(*) from guildinfo where guildid = {guildid} and guildname = '{guildname}';")
            if not cursor.fecthone()[0]:   # cursor.fetchone()[0] == 0
                cursor.execute(f'select count(*) from guildinfo where guildid = {guildid};')

                if cursor.fetchone()[0]:
                    cursor.execute(f"select count(*) from guildinfo where guildname = '{guildname}';")

                    if not cursor.fetchone()[0]:
                        cursor.execute(f"update guildinfo set guildname = '{guildname}' where guildid = {guildid};")
                        mydb.commit()
                        print(f'updated guild {guildid} with new name: {guildname}')
                    else:   
                        print(f'guild {guildid} with name {guildname} is already in the database')

                else:
                    cursor.execute(f"insert into guildinfo(guildid, guildname) values ({guildid}, '{guildname}');")
                    mydb.commit()
                    await ctx.send(f"Guild '{guildname}' with id {guildid} was added to the database")
            self.dbhelper.close()

        except psycopg2.Error as ag:
            print(f'Something went wrong in `add-guild` command: {ag}')


async def setup(bot):
    await bot.add_cog(DbEmergency(bot))
