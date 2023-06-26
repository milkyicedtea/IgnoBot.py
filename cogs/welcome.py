###################
#                 #
#     Welcome     #
#                 #
###################

import os

import discord
from discord.ext import commands
from discord import app_commands

from utils.dbhelper import DbHelper


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    welcome = app_commands.Group(name = 'welcome', description = 'Welcome related commands', guild_only = True)

    application_check = app_commands.checks.has_permissions

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        dbhelper = DbHelper()
        dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = member.guild.id
        guildname = member.guild.name

        cursor.execute(f'select channel_id from welcome where guildid = {guildid};')
        channel = discord.utils.get(member.guild.channels, id = cursor.fetchone()[0])
        default_message = 'Hey {} welcome to {}!'.format(member.mention, guildname)
        cursor.execute(f'select count(*) from welcome where guildid = {guildid};')
        if cursor.fetchone()[0] == 0:
            await channel.send(default_message)
        else:
            cursor.execute(f'select welcome_message from welcome where guildid = {guildid};')
            result = cursor.fetchone()
            custom_message = result[0]
            custom_message = custom_message.replace('%mention_user%', member)
            await channel.send(custom_message)
        dbhelper.close()

    @welcome.command(name = 'setup')
    @application_check(manage_guild = True)
    @app_commands.describe(message = 'The message that will be displayed when a member joins. Use %mention_user% to mention the joining user in the message. Leave blank for default.')
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = None):
        """Sets up the welcome channel and message"""
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()
        
        guildid = interaction.guild_id
        guildname = interaction.guild.name

        await interaction.response.defer(ephemeral = True)

        # check if the guild is in the welcome table
        cursor.execute(f'select count(*) from welcome where guildid = {guildid};')
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"insert into welcome(guildid) values({guildid});")          # add it if it isn't 
            mydb.commit()
            print(f'Added new guild {guildid} to the "welcome" table')

        # update welcome channel and message
        if not message:
            message = 'Hey %mention_user%! Welcome to {}!'.format(guildname)

        cursor.execute(f'update welcome set channel_id = {channel.id} where guildid = {guildid};')
        cursor.execute(f"update welcome set welcome_message = '{message}' where guildid = {guildid}")
        mydb.commit()
        await interaction.followup.send(f'The welcome channel has been set to: <#{channel.id}>.\n The current welcome message is: {message}') 

        dbhelper.close()

    @welcome.command(name = 'get-channel')
    @application_check(manage_guild = True)
    async def get_welcome_channel(self, interaction: discord.Interaction):
        """Returns the current channel for welcome messages"""
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = interaction.guild_id
        cursor.execute(f'select count(*) from welcome where guildid = {guildid};')
        if cursor.fetchone()[0] == 0:
            await interaction.response.send_message("This server hasn't configured custom welcome messages yet")

        else:
            cursor.execute(f'select channel_id from welcome where guildid = {guildid};')
            channel = discord.utils.get(interaction.guild.channels, id = cursor.fetchone()[0])
            await interaction.response.send_message(f'The configured welcome channel for this server is <#{channel.id}>')

    @welcome.command(name = 'get-message')
    @application_check(manage_guild = True)
    async def get_welcome_message(self, interaction: discord.Interaction):
        """Returns the current welcome message"""
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = interaction.guild_id
        cursor.execute(f'select count(*) from welcome where guildid = {guildid};')
        if cursor.fetchone()[0] == 0:
            await interaction.response.send_message("This server hasn't configured custom welcome messages yet")

        else:
            cursor.execute(f'select welcome_message from welcome where guildid = {guildid};')
            await interaction.response.send_message(f'The configured welcome message for this server is: {cursor.fetchone()[0]}')


async def setup(bot):
    await bot.add_cog(Welcome(bot))
