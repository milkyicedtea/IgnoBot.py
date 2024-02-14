# -*- coding: utf-8 -*-
# わああああああああああああああああああああああああああああああああああああああああ

################
#              #
#     Main     #
#              #
################

import sys

from discord.ext import commands
import discord.utils

import asyncio
import builtins

import logging

from Utils.dbchecks import *
from Utils.dbhelper import *

print('python version is:')
print(sys.version)
print(sys.version_info)

# Initializing variables from .env file
TOKEN = dotenv.get_key(".env", 'BOT_TOKEN')

# THESE GUILD IDS MAY PREVENT
kodama_guild: int = int(dotenv.get_key(".env", "kodama_guild"))
chill_ignorance: int = int(dotenv.get_key(".env", "chill_ignorance"))
# ducks_hideout: int = int(dotenv.get_key(".env", "ducks_hideout"))
ichiban_kuji_guild: int = int(dotenv.get_key(".env", "ichiban_kuji_guild"))

guild_list: list[int] = [kodama_guild, chill_ignorance, ichiban_kuji_guild]
builtins.guild_list = guild_list


def get_prefix(bot: commands.Bot, message) -> str:
    # print('get prefix')

    with Database() as db:
        print('getting prefix..')
        cursor = db.get_cursor()

        guildid = message.guild.id
        # DbChecks.guild_check(db, guildid)

        cursor.execute(f"select count(*) from guildsettings where guildid = {guildid}")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"insert into guildsettings(guildid) values({guildid})")
            # print(f"guild {guildid} added to settings")
            db.commit()

        cursor.execute(f'select prefix from guildsettings where guildid = {guildid}')
        prefix = cursor.fetchone()[0]
        # print(prefix)

    return prefix


# Prefix setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = get_prefix, intents = intents, description = 'ducc')
builtins.bot = bot


# cogs loading and command counting
async def load_cogs():
    for filename in os.listdir('./cogs'):  # loads all files (*.py)
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')  # loads the file without `.py` for example: cogs.ping
            print(f'Loaded {filename[:-3]}')

    print(f'Total number of commands: {len(list(bot.walk_commands()))}')


# Bot login event
@bot.event
async def on_ready():
    await bot.tree.sync()
    for guild in guild_list:
        await bot.tree.sync(guild = discord.Object(id = guild))
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = f'ducks at the park \U0001f986'))


@bot.event
async def on_guild_join(guild):
    with Database() as db:
        cursor = db.get_cursor()

        guildid = guild.id
        guildname = guild.name

        # do stuff in guildinfo
        cursor.execute(f"insert into guildinfo(guildid, guildname) values({guildid}, '{guildname}')")

        # do stuff in guildsettings
        cursor.execute(f"insert into guildsettings(guildid, prefix) values({guildid}, 'i.')")

        # do stuff in welcome
        welcomedef_channel = discord.utils.get(guild.channels, name = 'general')
        welcomedef_channel_id = welcomedef_channel.id
        welcomedef_message = 'Hey %mention_user%! Welcome to {}!'.format(guildname)
        cursor.execute(f"insert into welcome(channel_id, guildid, welcome_message) values({welcomedef_channel_id}, {guildid}, '{welcomedef_message}')")
        db.commit()


@bot.event
async def on_guild_remove(guild):
    with Database() as db:
        cursor = db.get_cursor()

        guildid = guild.id
        guildname = guild.name

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
        db.commit()

        print(f'deleted every information relative to guild {guildname} with id {guildid} from the database')


async def get_bot():
    return bot


# bot.run
async def main():
    handler = logging.FileHandler(filename = 'discord.log', encoding = 'utf-8', mode = 'w')
    discord.utils.setup_logging(handler = handler)
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)
        # await bot.close() # This one is to shut off the bot.


asyncio.run(main())
