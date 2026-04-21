####################
#                  #
#     Settings     #
#                  #
####################

import discord
from discord.ext import commands
from discord import app_commands

from Utils.database.database import PgDB 


def cooldown_checker(interaction: discord.Interaction) -> app_commands.Cooldown:
    return app_commands.Cooldown(1, 60)


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_enabled = {'set': False}

    prefix = app_commands.Group(name = 'prefix', description = "Commands related to guild's settings")

    application_check = app_commands.checks.has_permissions

    # Refactored and works, disabled in favor of slash commands in initialization function
    @cooldown_checker
    @prefix.command(name = "set")
    @application_check(administrator = True)
    async def setprefix(self, interaction: discord.Interaction, prefix: str = "i."):
        """Sets a custom prefix for chat commands."""

        if not self.command_enabled['set']:
            await interaction.response.send_message("""
                This command is currently disabled
            """, ephemeral = False)

        async with PgDB() as db:
            cursor = await db.get_cursor()
            guildid = interaction.guild_id

            await cursor.execute("""
                INSERT INTO guildsettings (guildid, prefix)
                VALUES (%s, %s)
                ON CONFLICT (guildid)
                DO UPDATE SET prefix = EXCLUDED.prefix;
            """, (guildid, prefix),)
            await db.commit()

            await interaction.response.send_message(f"The bot's prefix is now set to `{prefix}`.")


async def setup(bot):
    await bot.add_cog(Settings(bot))
