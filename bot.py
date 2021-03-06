################
#              #
#     Main     #
#              #
################

import os

import discord

from dotenv import load_dotenv
from discord.ext import commands
import discord.utils

from utils.dbhelper import DbHelper

# Initializing variables from .env file
load_dotenv()
TOKEN = os.getenv('bot_token')

# Prefix setup
# client = commands.Bot(command_prefix = 'i.') # not using the client

def get_prefix(bot, message):
    guildid = message.guild.id

    dbhelper = DbHelper()

    mydb = dbhelper.open()
    cursor = dbhelper.get_cursor()

    cursor.execute(f'select count(*) from guildsettings where guildid = {guildid};')
    result = cursor.fetchone()
    if result[0] == 0:
        prefix = 'i.'
        cursor.execute(f"insert into guildsettings(guildid) values({guildid});")
        cursor.execute(f"insert into guildsettings(prefix) values('i.');")
        mydb.commit()

    
    cursor.execute(f'select prefix from guildsettings where guildid = {guildid};')
    result = cursor.fetchone()
    prefix = result[0]

    dbhelper.close()
    return prefix

bot = commands.Bot(command_prefix = (get_prefix), intents = discord.Intents().all())

# cogs loading
for filename in os.listdir('./cogs'): #loads all files (*.py)
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}') #loads the file without ".py" for example: cogs.ping
        print(f'Loaded {filename[:-3]}')    

# Bot login event
@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')
    print('Servers connected to:')
    for guild in bot.guilds:
        print(guild.name)
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f'too many users typing D:'))

@bot.event
async def on_guild_join(guild):
    guildid = guild.id
    guildname = guild.name
    
    dbhelper = DbHelper()
    mydb = dbhelper.open()
    cursor = dbhelper.cursorget_cursor()
    
    # do stuff in guildinfo
    cursor.execute(f"insert into guildinfo(guildid, guildname) values({guildid}, '{guildname}');")

    # do stuff in guildsettings
    cursor.execute(f"insert into guildsettings(guildid, prefix) values({guildid}, 'i.');")

    # do stuff in welcome
    welcomedef_channel = discord.utils.get(guild.channels, name = 'general')
    welcomedef_channel_id = welcomedef_channel.id
    welcomedef_message = 'Hey %mention_user%! Welcome to {}!'.format(guildname)
    cursor.execute(f"insert into welcome(channel_id, guildid, welcome_message) values({welcomedef_channel_id}, {guildid}, '{welcomedef_message}');")
    mydb.commit()

    dbhelper.close()

@bot.event
async def on_guild_remove(guild):
    guildid = guild.id
    guildname = guild.name
    
    dbhelper = DbHelper()
    mydb = dbhelper.open()
    cursor = dbhelper.cursorget_cursor()
    
    # do stuff in guildsettings
    cursor.execute(f'delete from guildsettings where guildid = {guildid};')
    mydb.commit()

    #do stuff in welcome
    cursor.execute(f'delete from welcome where guildid = {guildid};')
    mydb.commit()

    #do stuff in leveling
    cursor.execute(f'delete from leveling where guildid = {guildid};')
    mydb.commit()

    # do stuff in guildinfo
    cursor.execute(f"delete from guildinfo where guildid = {guildid};")
    mydb.commit()

    print(f'deleted every information relative to guild {guildname} with id {guildid} from the database')
    dbhelper.close()

# bot.run
bot.run(TOKEN)