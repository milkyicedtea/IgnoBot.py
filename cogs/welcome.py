###################
#                 #
#     Welcome     #
#                 #
###################

import discord
from discord.ext import commands
from discord import app_commands

from Utils.database.database import PgDB


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    welcome = app_commands.Group(name = 'welcome', description = 'Welcome related commands', guild_only = True)

    application_check = app_commands.checks.has_permissions

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Triggers when a member joins to send a welcome message"""

        async with PgDB() as db:
            cursor = await db.get_cursor()

            guildid = member.guild.id
            guildname = member.guild.name

            await cursor.execute("""
                select channel_id, welcome_message
                from welcome 
                where guildid = %s
            """, (guildid,))
            result = await cursor.fetchone()

            if result:
                channel_id, welcome_message = result
                channel = discord.utils.get(member.guild.channels, id = channel_id)
                if not channel:
                    return  # exit if channel no longer exists

                # replace placeholders in custom message
                welcome_message = welcome_message.replace("%member_user%", member.mention)
            else:
                # default message
                channel = member.guild.system_channel
                welcome_message = f"Hey {member.mention} welcome to {guildname}!"

            if channel:
                await channel.send(welcome_message)

    @welcome.command(name = 'setup')
    @application_check(manage_guild = True)
    @app_commands.describe(message = 'The message that will be displayed when a member joins. Use %mention_user% to mention the joining user in the message. Leave blank for default.')
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = None):
        """Sets up the welcome channel and message"""

        async with PgDB() as db:
            cursor = await db.get_cursor()

            guild = interaction.guild
            guildname = interaction.guild.name

            await interaction.response.defer(ephemeral = True) # noqa

            if not message:
                message = f"Hey %mention_user%! Welcome to {guildname}!"

            await cursor.execute("""
                insert into welcome(guildid, channel_id, welcome_message)
                values(%s, %s, %s)
                on conflict(guildid)
                do update set channel_id = EXCLUDED.channel_id, welcome_message = EXCLUDED.welcome_message
            """, (guild.id, channel.id, message))
            await db.commit()

            await interaction.followup.send(f"""
                The welcome channel has been set to: <#{channel.id}>.\n
                The current welcome message is: {message}
            """)

    @welcome.command(name = 'get-channel')
    @application_check(manage_guild = True)
    async def get_welcome_channel(self, interaction: discord.Interaction):
        """Returns the current channel for welcome messages"""

        async with PgDB() as db:
            cursor = await db.get_cursor()

            guild = interaction.guild
            await cursor.execute("""
                select channel_id
                from welcome
                where guildid = %s
            """, (guild.id,))
            result = await cursor.fetchone()

            if result:
                channel = discord.utils.get(interaction.guild.channels, id = result[0])
                if channel:
                    await interaction.response.send_message( # noqa
                        f"The configured welcome channel for this server <#{channel.id}>."
                    )
                else:
                    await interaction.response.send_message( # noqa
                        "The configured channel not longer exists."
                    )
            else:
                await interaction.response.send_message( # noqa
                    "This server hasn't configured custom welcome messages yet."
                )

    @welcome.command(name = 'get-message')
    @application_check(manage_guild = True)
    async def get_welcome_message(self, interaction: discord.Interaction):
        """Returns the current welcome message"""

        async with PgDB() as db:
            cursor = await db.get_cursor()

            guild = interaction.guild
            await cursor.execute("""
                SELECT welcome_message
                FROM welcome
                WHERE guildid = %s
            """, (guild.id,))
            result = await cursor.fetchone()

            if result:
                await interaction.response.send_message( # noqa
                    f"The configured welcome message for this server is: {result[0]}"
                )
            else:
                await interaction.response.send_message( # noqa
                    "This server hasn't configured custom welcome messages yet."
                )


async def setup(bot):
    await bot.add_cog(Welcome(bot))
