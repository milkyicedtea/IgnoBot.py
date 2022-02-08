################
#              #
#     Main     #
#              #
################

import os
from types import NoneType

import discord

from dotenv import load_dotenv
from discord.ext import commands
import discord.utils
import psycopg2

mydb = None
cursor = None

# Initializing variables from .env file
load_dotenv()
TOKEN = os.getenv('bot_token')

# Prefix setup
# client = commands.Bot(command_prefix = 'i.') # not using the client

def get_prefix(bot, message):
    global mydb
    global cursor
    guildid = message.guild.id
    print(f'Guildid for prefix function ({guildid})')
    dbopen()

    cursor.execute(f'select count(*) from guildsettings where guildid = {guildid};')
    result = cursor.fetchone()
    print(f'count for get_prefix is: {result[0]}')
    if result[0] == 0:
        prefix = 'i.'
        cursor.execute(f"insert into guildsettings(guildid) values({guildid});")
        cursor.execute(f"insert into guildsettings(prefix) values('i.');")
        mydb.commit()

    
    cursor.execute(f'select prefix from guildsettings where guildid = {guildid};')
    result = cursor.fetchone()
    prefix = result[0]

    print(f'the prefix (result[0]) is: {result[0]}')
    dbclose()
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

@bot.event
async def on_guild_join(guild):
    global mydb
    global cursor
    guildid = guild.id
    guildname = guild.name
    dbopen()
    
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
    dbclose()

@bot.event
async def on_guild_remove(guild):
    global mydb
    global cursor
    guildid = guild.id
    guildname = guild.name
    dbopen()
    
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
    dbclose()




# db open/close
def dbopen():
    global mydb
    global cursor
    try:
        mydb = psycopg2.connect(host = os.getenv('dbhost'), user = os.getenv('dbuser'), password = os.getenv('dbpw'), database = os.getenv('db_db'), port = os.getenv('dbport'))
        print("Connected to the database")
    except psycopg2.Error as e:
        print(f'Error connecting to the platform (mydb): {e}')

    # getting the cursor
    try:
        cursor = mydb.cursor()
    except psycopg2.Error as c:
        print(f'Error connecting to the platform (cursor): {c}')

def dbclose():
    global mydb
    global cursor
    try:
        cursor.close()
        mydb.close()
        print(f'Database closed')
    except psycopg2.Error as ce:
        print(f'Error while closing the database: {ce}')

# bot.run
bot.run(TOKEN)