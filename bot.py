################
#              #
#     Main     #
#              #
################

import os

import discord

from discord import guild
from dotenv import load_dotenv
from discord.ext import commands
import discord.utils
import math

# Initializing variables from .env file
load_dotenv()
TOKEN = os.getenv('bot_token')

# Prefix setup
# client = commands.Bot(command_prefix = 'i.') # not using the client

bot = commands.Bot(command_prefix='i.')

# bot.load_extension("cogs.music")
# bot.load_extension("cogs.database")

# cogs loading
for filename in os.listdir('./cogs'): #loads all files (*.py)
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}') #loads the file without ".py" for example: cogs.ping
        print(f'Loaded {filename[:-3]}')

# unload database cogs until i don't get back home :)
bot.unload_extension('cogs.levelsystem')
print('Unloaded levelsystem')
bot.unload_extension('cogs.database')
print('Unloaded database')

"""
WIP

# Welcome message | setup working but missing the modularity with the embed message
@bot.command(name = 'welcome-message', help = 'Used to setup the welcome message')
@commands.has_permissions(manage_guild=True)
async def welcome_message(ctx, title, color, description):
    welcomepath = "./data/welcome/welcome.ini"
    # open welcome.ini
    f = open(welcomepath,"w")
    # write title, color and description in welcome.ini
    f.write("# title\n" + title + "\n# color\n" + color + "\n# description\n" + description)
    # close opened file
    f.close()
    await ctx.send("Test andato a buon fine.")

# Sends a message when a user joins
@bot.event
async def on_member_join(member):
    print("A member joined the server(" + member.name + ")")
    linecache.clearcache()
    title_read = linecache.getline('./data/welcome/welcome.ini', 2)
    color_read = linecache.getline('./data/welcome/welcome.ini', 4)
    description_read = linecache.getline('./data/welcome/welcome.ini', 6)
    embed=discord.Embed(
        title = title_read ,
        description = description_read,
        color =
    )



# Select role to give on join
@bot.command(name = 'roleonjoin', help = 'Used to select the role to give when a user joins the server.')
@commands.has_permissions(manage_guild = True)
async def roleonjoin(ctx, roleid):
    while roleid is math.nan():
        await ctx.send('You must specify a role id')
    rolepath = './data/rolegive/rolegive.ini'
    f = open(rolepath, 'w')
    f.write('# role\n' + roleid)
    f.close
    rolename = guild.get_role(roleid)
    await ctx.send('Il ruolo selezionato è: ' + rolename + '\nCon id ' + roleid + ".")

# Give role on join
@bot.event
async def on_member_join(member):
    rolepath = './data/rolegive/rolegive.ini'
    roleid = linecache.getline(rolepath, 2)
    await member.add_roles(roleid)

WIP
"""

####################

# Bot login event
@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')

# bot.run
bot.run(TOKEN)