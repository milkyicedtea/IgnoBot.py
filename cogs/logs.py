################
#              #
#     Logs     #
#              #
################

import discord
from discord.ext import commands
from discord import app_commands, RawMessageDeleteEvent

from Utils.db_checks import DbChecks
from Utils.database.database import PgDB 


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    logsGroup = app_commands.Group(name = 'log', description = 'Logging related commands')
    application_check = app_commands.checks.has_permissions

    @logsGroup.command(name = 'channel')
    @application_check(view_audit_log = True, administrator = True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """
        Sets the default channel where logged events go.
        Leave empty to clear the channel.
        """

        # Open the database connection
        async with PgDB() as db:

            # Get the database cursor
            cursor = await db.get_cursor()

            # Get the guild object from the interaction
            guild = interaction.guild

            # Check if the guild exists in the database
            await DbChecks.guild_check(db, guild)

            if channel:
                # Update the log channel in the database
                await cursor.execute(f"UPDATE guildsettings SET logchannel = {channel.id} WHERE guildid = {guild.id}")
                await db.commit()
                await interaction.response.send_message(f"Your logs channel was updated to {channel.mention}.") # noqa
            else:
                # Clear the log channel in the database
                await cursor.execute(f"UPDATE guildsettings SET logchannel = NULL WHERE guildid = {guild.id}")
                await db.commit()
                await interaction.response.send_message(f"Your logs channel has been updated to default. (None)", ephemeral=True) # noqa

            # Database connection closes automatically

    @logsGroup.command(name = "toggle")
    @application_check(view_audit_log = True, administrator = True)
    async def toggle_logs(self, interaction: discord.Interaction):
        """Toggles logging to enabled/disabled."""

        async with PgDB() as db:
            cursor = await db.get_cursor()

            guild = interaction.guild

            await DbChecks.guild_check(db, guild)

            wantslogs = DbChecks.check_guild_logs(cursor, guild)

            if not wantslogs:     # logs are off, switch on
                await cursor.execute(f"update guildsettings set wantslogs = 'true' where guildid = {guild.id}")
                await db.commit()
                logchannel = await DbChecks.get_log_channel(cursor, guild)
                if logchannel is not None:
                    await interaction.response.send_message(f"Events logging has been turned on.\n" # noqa
                                                            f"Events will be logged in {logchannel.mention}.")
                else:
                    await interaction.response.send_message(f"Events logging has been turned on, but no channel is set.\n" # noqa
                                                            f"Use ```/logs channel <channel>``` to set one.")
            else:
                await cursor.execute(f"update guildsettings set wantslogs = 'false' where guildid = {guild.id}")
                await db.commit()
                await interaction.response.send_message("Events logging has been turned off.") # noqa

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        """Listener for deleted messages logs"""
        guild = self.bot.get_guild(payload.guild_id)

        async with PgDB() as db:
            cursor = await db.get_cursor()

            await DbChecks.guild_check(db, guild = guild)

            has_logs = await DbChecks.check_guild_logs(cursor, guild = guild)

            if has_logs and payload.cached_message:
                message = payload.cached_message
                channel = await DbChecks.get_log_channel(cursor, guild = guild)

                embed = discord.Embed(title = "Message deleted", color = discord.Colour.red())
                embed.set_author(name = message.author.name + "#" + message.author.discriminator, icon_url = message.author.display_avatar)
                embed.add_field(name = '', value = message.clean_content, inline = False)

                await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        pass


async def setup(bot):
    await bot.add_cog(Logs(bot))
