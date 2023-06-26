################
#              #
#     Logs     #
#              #
################

import os

import discord
from discord.ext import commands
from discord import app_commands

from utils.dbchecks import DbChecks
from utils.dbhelper import DbHelper


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    logsGroup = app_commands.Group(name = 'log', description = 'Logging related commands')

    application_check = app_commands.checks.has_permissions

    @logsGroup.command(name = 'channel')
    @application_check(view_audit_log = True, administrator = True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """Sets the default channel where logged events go. Leave empty to clear the channel"""

        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild

        DbChecks.guild_check(cursor, mydb, guild)

        if channel is not None:

            cursor.execute(f"update guildsettings set logchannel = {channel.id} where guildid = {guild.id}")
            mydb.commit()
            await interaction.response.send_message(f"Your logs channel was updated to {channel.mention}.")
        else:
            cursor.execute(f"update guildsettings set logchannel = NULL where guildid = {guild.id}")
            mydb.commit()
            await interaction.response.send_message(f"Your logs channel has been updated to default. (None)", ephemeral = True)
        dbhelper.close()

    @logsGroup.command(name = "toggle")
    @application_check(view_audit_log = True, administrator = True)
    async def toggle_logs(self, interaction: discord.Interaction):
        """Toggles logging to enabled/disabled."""
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild

        DbChecks.guild_check(cursor, mydb, guild)

        wantslogs = DbChecks.check_guild_logs(cursor, guild)

        if not wantslogs:     # logs are off, switch on
            cursor.execute(f"update guildsettings set wantslogs = 'true' where guildid = {guild.id}")
            mydb.commit()
            logchannel = DbChecks.get_log_channel(cursor, guild)
            if logchannel is not None:
                await interaction.response.send_message(f"Events logging has been turned on.\n"
                                                        f"Events will be logged in {logchannel.mention}.")
            else:
                await interaction.response.send_message(f"Events logging has been turned on, but no channel is set.\n"
                                                        f"Use ```/logs channel <channel>``` to set one.")
        else:
            cursor.execute(f"update guildsettings set wantslogs = 'false' where guildid = {guild.id}")
            mydb.commit()
            await interaction.response.send_message("Events logging has been turned off.")
        dbhelper.close()

    # Listener for deleted messages logs
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        DbChecks.guild_check(cursor, mydb, guild = message.guild)

        has_logs = DbChecks.check_guild_logs(cursor, guild = message.guild)

        if has_logs:
            channel = DbChecks.get_log_channel(cursor, guild = message.guild)

            embed = discord.Embed(title = "Message deleted", color = discord.Colour.random())
            embed.set_author(name = message.author.name + "#" + message.author.discriminator, icon_url = message.author.display_avatar)
            embed.add_field(name = '', value = message.clean_content, inline = False)

            await channel.send(embed = embed)
        dbhelper.close()


async def setup(bot):
    await bot.add_cog(Logs(bot))
