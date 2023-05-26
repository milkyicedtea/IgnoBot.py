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


    # Adds logs for deleted messages
    @logsGroup.command(name = 'channel', description = "Sets the default channel where logged events go. Leave empty to clear the channel")
    @application_check(view_audit_log = True, administrator = True)
    async def setLogChannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = interaction.guild_id
        guildraw = interaction.guild.name
        guildname = guildraw.replace("'", "")
        userid = interaction.user.id
        usernameraw = interaction.user.name
        username = usernameraw.replace("'", "")

        DbChecks.guildCheck(cursor, mydb, guildid, guildname)

        if channel is not None:
            channel_id = channel.id
            channel = self.bot.get_channel(channel_id)

            cursor.execute(f"update guildsettings set logchannel = {channel_id} where guildid = {guildid}")
            mydb.commit()
            await interaction.response.send_message(f"Your logs channel was updated to <#{channel_id}>.")
        else:
            cursor.execute(f"update guildsettings set logchannel = NULL where guildid = {guildid}")
            mydb.commit()
            await interaction.response.send_message(f"Your logs channel has been updated to default. (None)", ephemeral = True)
        dbhelper.close()


    # Toggles logs to enabled/disabled
    @logsGroup.command(name = "toggle", description = "Toggles logging to enabled/disabled")
    @application_check(view_audit_log = True, administrator = True)
    async def toggleLogs(self, interaction: discord.Interaction):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = interaction.guild_id
        guildraw = interaction.guild.name
        guildname = guildraw.replace("'", "")
        userid = interaction.user.id
        usernameraw = interaction.user.name
        username = usernameraw.replace("'", "")

        DbChecks.guildCheck(cursor, mydb, guildid, guildname)

        wantslogs = DbChecks.checkGuildLogs(cursor, mydb, guildid = message.guild.id)

        if not wantslogs:     # logs are off, switch on
            cursor.execute(f"update guildsettings set wantslogs = 'true' where guildid = {guildid}")
            mydb.commit()
            logchannel = DbChecks.checkLogChannel(cursor, mydb, guildid=guildid)
            if logchannel is not None:
                await interaction.response.send_message(f"Events logging has been turned on.\n"
                                                        f"Events will be logged in <#{logchannel}>.")
            else:
                await interaction.response.send_message(f"Events logging has been turned on, but no channel is set.\n"
                                                        f"Use ```/logs channel <channel>``` to set one.")
        else:
            cursor.execute(f"update guildsettings set wantslogs = 'false' where guildid = {guildid}")
            mydb.commit()
            await interaction.response.send_message("Events logging has been turned off.")
        dbhelper.close()


    # Listener for deleted messages logs
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        DbChecks.guildCheck(cursor, mydb, guildid = message.guild.id, guildname = message.guild.name)

        has_logs = DbChecks.checkGuildLogs(cursor, mydb, guildid = message.guild.id)

        if has_logs[0] is True:
            channel_id = int(str(has_logs[1]).replace("(", "").replace(")", "").replace(",", ""))
            channel = discord.utils.get(message.guild.channels, id = channel_id)

            embed = discord.Embed(color = discord.Colour.random())
            embed.set_author(name = message.author.name + "#" + message.author.discriminator, icon_url = message.author.display_avatar)
            embed.add_field(name = '', value = message.clean_content, inline = False)

            await channel.send(embed = embed)
        dbhelper.close()


async def setup(bot):
    await bot.add_cog(Logs(bot))
