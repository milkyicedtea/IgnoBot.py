# -*- coding: utf-8 -*-
# わああああああああああああああああああああああああああああああああああああああああ

################
#              #
#     Main     #
#              #
################

import os

import sys

from discord.ext import commands
import discord.utils

import asyncio
import dotenv
import builtins

import logging

from utils.dbchecks import *
from utils.dbhelper import *


print('python version is:')
print(sys.version)
print(sys.version_info)

# Initializing variables from .env file
TOKEN = dotenv.get_key(".env", 'bot_token')

"""kodama_guild: int = int(dotenv.get_key(".env", "kodama_guild"))
chill_ignorance: int = int(dotenv.get_key(".env", "chill_ignorance"))
# ducks_hideout: int = int(dotenv.get_key(".env", "ducks_hideout"))
ichiban_kuji_guild: int = int(dotenv.get_key(".env", "ichiban_kuji_guild"))

guildList: list[int] = [kodama_guild, chill_ignorance, ichiban_kuji_guild]
builtins.guildList = guildList"""


def get_prefix(bot: commands.Bot, message) -> str:
    # print('get prefix')
    guildid = message.guild.id

    dbhelper = DbHelper()

    mydb = dbhelper.open()
    cursor = dbhelper.get_cursor()

    # DbChecks.guild_check(cursor, mydb, guildid, guildname = message.guild.name)

    cursor.execute(f"select count(*) from guildsettings where guildid = {guildid}")
    result = cursor.fetchone()
    if result[0] == 0:
        cursor.execute(f"insert into guildsettings(guildid) values({guildid})")
        # print(f'guild {guildid} added to settings')
        mydb.commit()
    
    cursor.execute(f'select prefix from guildsettings where guildid = {guildid}')
    result = cursor.fetchone()
    prefix = result[0]
    # print(prefix)

    dbhelper.close()
    return prefix


# Prefix setup
# client = discord.Client(command_prefix = (get_prefix), intents = discord.Intents().all()) # not using the client
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = get_prefix, intents = intents, description = 'ducc')
builtins.bot = bot
# tree = app_commands.CommandTree(bot)


# cogs loading and command counting
async def load_cogs():

    for filename in os.listdir('./cogs'):   # loads all files (*.py)
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')   # loads the file without ".py" for example: cogs.ping
            print(f'Loaded {filename[:-3]}')

    print(f'Total number of commands: {len(list(bot.walk_commands()))}')


# Bot login event
@bot.event
async def on_ready():
    """print(f'{bot.user} has logged in.')
    print("Servers connected to: ")
    for guild in bot.guilds:
        print(guild.name, " ", guild.id)"""
    await bot.tree.sync()
    # for guild in guildList:
    #     await bot.tree.sync(guild = discord.Object(id = guild))
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f'ducks at the park \U0001f986'))


@bot.event
async def on_guild_join(guild):
    guildid = guild.id
    guildname = guild.name
    
    dbhelper = DbHelper()
    mydb = dbhelper.open()
    cursor = dbhelper.get_cursor()
    
    # do stuff in guildinfo
    cursor.execute(f"insert into guildinfo(guildid, guildname) values({guildid}, '{guildname}')")

    # do stuff in guildsettings
    cursor.execute(f"insert into guildsettings(guildid, prefix) values({guildid}, 'i.')")

    # do stuff in welcome
    welcomedef_channel = discord.utils.get(guild.channels, name = 'general')
    welcomedef_channel_id = welcomedef_channel.id
    welcomedef_message = 'Hey %mention_user%! Welcome to {}!'.format(guildname)
    cursor.execute(f"insert into welcome(channel_id, guildid, welcome_message) values({welcomedef_channel_id}, {guildid}, '{welcomedef_message}')")
    mydb.commit()

    dbhelper.close()


@bot.event
async def on_guild_remove(guild):
    guildid = guild.id
    guildname = guild.name
    
    dbhelper = DbHelper()
    mydb = dbhelper.open()
    cursor = dbhelper.get_cursor()
    
    # guildsettings
    cursor.execute(f'delete from guildsettings where guildid = {guildid}')

    # welcome
    cursor.execute(f'delete from welcome where guildid = {guildid}')

    # leveling
    cursor.execute(f'delete from leveling where guildid = {guildid}')

    # roles
    cursor.execute(f'delete from roles where guildid = {guildid}')

    # do stuff in guildinfo
    cursor.execute(f"delete from guildinfo where guildid = {guildid}")
    mydb.commit()

    print(f'deleted every information relative to guild {guildname} with id {guildid} from the database')
    dbhelper.close()


async def get_bot():
    return bot


# bot.run
async def main():
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    discord.utils.setup_logging(handler = handler)
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
