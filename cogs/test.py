################
#              #
#     Test     #
#              #
################

import asyncio

import discord
from discord.ext import commands
from discord import app_commands

import linecache

import time

from Utils.db_checks import DbChecks
from Utils.database.database import PgDB 


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    test = app_commands.Group(name='test', description='Test group')

    application_check = app_commands.checks.has_permissions

    # bad slash command
    @test.command(name = 'bad')
    async def bad(self, interaction: discord.Interaction):
        await interaction.response.send_message('**Bad**', ephemeral = True) # noqa

    # beep command
    @test.command(name = 'beep')
    async def beep(self, interaction: discord.Interaction):
        await interaction.response.send_message('**Beep!**', ephemeral = True) # noqa

    # Embed test
    @test.command(name = 'embed')
    @application_check(administrator = True)
    async def embed_test(self, interaction: discord.Interaction):
        if not await self.bot.is_owner(interaction.user):
            # If the user is not the bot owner, deny the command
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False) # noqa
            return

        colorvalue = discord.Colour.random()
        embed_var = discord.Embed(title = 'Title', description = 'Desc', color = colorvalue)
        embed_var.add_field(name = "Field1", value = "hi", inline = False)
        embed_var.add_field(name = "Field2", value = "hi2", inline = False)
        await interaction.response.send_message(embed = embed_var) # noqa

    # Read test
    @test.command(name = 'read')
    @application_check(administrator = True)
    async def read_test(self, interaction: discord.Interaction):
        if not await self.bot.is_owner(interaction.user):
            # If the user is not the bot owner, deny the command
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False) # noqa
            return

        linecache.clearcache()
        title = linecache.getline('./data/welcome/welcome.ini', 2)
        color = linecache.getline('./data/welcome/welcome.ini', 4)
        description = linecache.getline('./data/welcome/welcome.ini', 6)
        await interaction.response.send_message(title + color + description) # noqa

    # asyncio.sleep() test
    @test.command(name = 'asynciosleep')
    @application_check(administrator = True)
    async def asynciosleep(self, interaction: discord.Interaction, amount_to_sleep: int, *, sentence: str):
        if not await self.bot.is_owner(interaction.user):
            # If the user is not the bot owner, deny the command
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False) # noqa
            return

        await interaction.response.send_message(f'Waiting {amount_to_sleep} seconds before sending your message.') # noqa
        await asyncio.sleep(amount_to_sleep)
        await interaction.followup.send(f'{sentence}')

    # time.sleep() test
    @test.command(name = 'timesleep')
    @application_check(administrator = True)
    async def timesleep(self, interaction: discord.Interaction, amount_to_sleep: int, *, sentence: str):
        if not await self.bot.is_owner(interaction.user):
            # If the user is not the bot owner, deny the command
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False) # noqa
            return

        await interaction.response.send_message(f'Waiting {amount_to_sleep} seconds before sending your message.') # noqa
        time.sleep(amount_to_sleep)
        await interaction.response.send_message(f'{sentence}') # noqa

    @test.command(name = 'getroletest')
    @application_check(administrator = True)
    async def getroletest(self, interaction: discord.Interaction, *, role_name: str):

        # If the user is not the bot owner, deny the command
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False) # noqa
            return

        print(discord.utils.get(interaction.guild.roles, name = role_name))

    @test.command(name = 'print-mention')
    @application_check(administrator = True)
    async def print_mention(self, interaction: discord.Interaction, member: discord.Member):
        if not await self.bot.is_owner(interaction.user):
            # If the user is not the bot owner, deny the command
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False) # noqa
            return

        await interaction.response.send_message(member.mention) # noqa
        print(member.mention)

    @test.command(name = 'fetchtest')
    @application_check(administrator = True)
    async def fetch_test(self, interaction: discord.Interaction):
        if not await self.bot.is_owner(interaction.user):
            # If the user is not the bot owner, deny the command
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False) # noqa
            return

        async with PgDB() as db:
            cursor = await db.get_cursor()

            await interaction.response.send_message( # noqa
                f"{DbChecks.check_guild_logs(cursor, guild = interaction.guild)}, "
                f"{DbChecks.get_log_channel(cursor, guild = interaction.guild)}"
            )

    @test.command(name = 'slashcommands')
    @application_check(administrator = True)
    async def slash_commands_get(self, interaction: discord.Interaction):
        if not await self.bot.is_owner(interaction.user):
            # If the user is not the bot owner, deny the command
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral = False) # noqa
            return

        for slash_command in self.bot.tree.walk_commands(guild = interaction.guild):
            print(slash_command.name)
        await interaction.response.send_message('slash commands are working.', ephemeral = True) # noqa


async def setup(bot):
    await bot.add_cog(Test(bot))
