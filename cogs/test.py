################
#              #
#     Test     #
#              #
################

import os

import discord
from discord.ext import commands
from discord import app_commands

import linecache
import random
import asyncio
import time


from utils.dbchecks import DbChecks
from utils.dbhelper import DbHelper


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    test = app_commands.Group(name='test', description='Test group')

    application_check = app_commands.checks.has_permissions

    # bad slash command
    @test.command(name = 'bad')
    async def bad(self, interaction: discord.Interaction):
        await interaction.response.send_message('**Bad**', ephemeral = True)


    # beep command
    @test.command(name = 'beep')
    async def beep(self, interaction: discord.Interaction):
        await interaction.response.send_message('**Beep!**', ephemeral = True)


    # Embed test
    @commands.command(name = 'embed-test')
    @commands.has_guild_permissions(manage_guild = True)
    @commands.is_owner()
    async def embed_test(self, ctx: discord.ext.commands.Context):
        colorvalue = discord.Colour.random()
        embedVar = discord.Embed(title = 'Title', description = 'Desc', color = colorvalue)
        embedVar.add_field(name = "Field1", value = "hi", inline = False)
        embedVar.add_field(name = "Field2", value = "hi2", inline = False)
        await ctx.send(embed = embedVar)


    # Read test
    @commands.command(name = 'read-test')
    @commands.has_guild_permissions(manage_guild = True)
    @commands.is_owner()
    async def read_test(self, ctx: discord.ext.commands.Context):
        linecache.clearcache()
        title = linecache.getline('./data/welcome/welcome.ini', 2)
        color = linecache.getline('./data/welcome/welcome.ini', 4)
        description = linecache.getline('./data/welcome/welcome.ini', 6)
        await ctx.send(title + color + description)


    # asyncio.sleep() test
    @commands.command(name = 'asynciosleep')
    @commands.has_guild_permissions(manage_guild = True)
    @commands.is_owner()
    async def asynciosleep(self, ctx: discord.ext.commands.Context, amount_to_sleep: int, *, sentence: str):
        await ctx.send(f'Waiting {amount_to_sleep} seconds before sending your message.')
        await asyncio.sleep(amount_to_sleep)
        await ctx.send(f'{sentence}')


    # time.sleep() test
    @commands.command(name = 'timesleep')
    @commands.has_guild_permissions(manage_guild = True)
    @commands.is_owner()
    async def timesleep(self, ctx: discord.ext.commands.Context, amount_to_sleep: int, *, sentence: str):
        await ctx.send(f'Waiting {amount_to_sleep} seconds before sending your message.')
        time.sleep(amount_to_sleep)
        await ctx.send(f'{sentence}')


    @commands.command(name = 'getroletest')
    @commands.has_guild_permissions(manage_guild = True)
    async def getroletest(self, ctx: discord.ext.commands.Context, *, role_name):
        print(discord.utils.get(ctx.guild.roles, name = role_name))


    @commands.command(name = 'printMention')
    @commands.has_guild_permissions(manage_guild = True)
    async def printMention(self, ctx: discord.ext.commands.Context, member: discord.Member):
        await ctx.send(member.mention)
        print(member.mention)


    @commands.command(name = 'fetchtest')
    @commands.has_guild_permissions(manage_guild = True)
    async def fetchTest(self, interaction: discord.Interaction):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        await interaction.response.send_message(f"{DbChecks.checkGuildLogs(cursor, mydb, guildid = interaction.guild.id)}, "
                                                f"{DbChecks.checkLogChannel(cursor, mydb, guildid = interaction.guild.id)}")




async def setup(bot):
    await bot.add_cog(Test(bot))