###################
#                 #
#     Welcome     #
#                 #
###################

import os

import discord
from discord.ext import commands
import psycopg2
from utils.dbhelper import DbHelper

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        dbhelper = DbHelper()

        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = member.guild.id
        guildname = member.guild.name
        cursor.execute(f'select channel_id from welcome where guildid = {guildid};')
        result = cursor.fetchone()
        channel_id:int = result[0]
        channel = self.bot.get_channel(id = channel_id)
        member = member.mention
        default_message = 'Hey {} welcome to {}!'.format(member, guildname)
        cursor.execute(f'select count(*) from welcome where guildid = {guildid};')
        result = cursor.fetchone()
        if result[0] == 0:
            await channel.send(default_message)
        else:
            cursor.execute(f'select welcome_message from welcome where guildid = {guildid};')
            result = cursor.fetchone()
            custom_message = result[0]
            custom_message = custom_message.replace('%mention_user%', member)
            await channel.send(custom_message)
        dbhelper.close()

    @commands.command(name = 'set-welcome-channel', aliases = ['setwelcomechannel', 'welcomechannel', 'welcome-channel'], help = 'Use this to set the channel in which the bot will send the welcome message. The welcome message will not be sent if this is not configured')
    async def set_welcome_channel(self, ctx, welcome_channel = None):
        dbhelper = DbHelper()

        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()
        if welcome_channel == None:
            await ctx.send('You must specify a channel (Link or id)')
        else:
            guildid = ctx.guild.id
            dbhelper.open()
            welcome_channel1 = welcome_channel.replace("<", "")
            welcome_channel2 = welcome_channel1.replace(">", "")
            channel_id = welcome_channel2.replace("#", "")

            # check if the guild is in the welcome table
            cursor.execute(f'select count(*) from welcome where guildid = {guildid};')
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute(f"insert into welcome(guildid) values({guildid});")          # add it if it isn't 
                mydb.commit()
                print(f'Added new guild {guildid} to the "welcome" table')

            # continue by updating the channel id with the selected channel
            cursor.execute(f'update welcome set channel_id = {channel_id} where guildid = {guildid};')
            mydb.commit()
            await ctx.send(f'The welcome channel has been set to: {welcome_channel}')
            dbhelper.close()


    @commands.command(name = 'set-welcome', help = 'Used to set your welcome message when a user joins. Use "default" to set your welcome message to default. Use %mention_user% to mention the joining user.')
    @commands.has_permissions(manage_guild = True)
    async def set_welcome(self, ctx,* , message = None):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildname = ctx.guild.name
        guildid = ctx.guild.id
        if message == 'default':
            message = 'Hey %mention_user%! Welcome to {}!'.format(guildname)

        await ctx.send(f'Your welcome message currently is: {message}')
        # update the welcome_message column in the table
        dbhelper.open()
        cursor.execute(f"update welcome set welcome_message = '{message}' where guildid = {guildid};")
        mydb.commit()
        print('Welcome message updated')
        dbhelper.close()       

def setup(bot):
    bot.add_cog(Welcome(bot))