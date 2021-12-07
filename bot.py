#----------------
#-     Main     -
#----------------

import os

import discord

from discord import guild
from dotenv import load_dotenv
from discord.ext import commands
import discord.utils
import random
from discord.utils import get
import math

from discord import Color as c

# Specific line reader
import linecache

# Database importing
import mysql.connector

# Initializing variables from .env file
load_dotenv()
TOKEN = os.getenv('bot_token')

# Prefix setup
client = commands.Bot(command_prefix = 'i.')

bot = commands.Bot(command_prefix='i.')

bot.load_extension("cogs.music")
bot.load_extension("cogs.database")

#----------------------
#-     Moderation     -
#----------------------

# Kick command
@bot.command(name = 'kick', help = 'Kicks a user from the server')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member:discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member.mention} has been kicked from the server.\nResponsible mod: **{ctx.author}**\nReason: {reason}')

# Ban command
@bot.command(name = 'ban', help = 'Bans a member.')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member:discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member.mention} has been banned from the server.\nResponsible mod: **{ctx.author}**\nReason: {reason}')

# Unban command
@bot.command(name = 'unban', help = 'Unbans a previously banned member.')
@commands.has_permissions(ban_members=True)
async def unban(ctx,* , member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

# Purge command
@bot.command(name = 'purge', help = 'Deletes multiple messages.')
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)

# Creating a new channel
@bot.command(name = 'create-channel', help = 'Creates a new channel.')
@commands.has_permissions(manage_channels=True)
async def create_channel(ctx, channel_name='new-channel'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if existing_channel:
        print(f'Channel already exists')
        await ctx.send('A channel named "*new-channel*" already exists. Please delete or rename that channel before using this command.')
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}.')
        await guild.create_text_channel(channel_name)

# Join date command
@bot.command(name = 'joindate', help = 'Shows the date when a member joined.')
async def joindate(ctx, member: discord.Member):
    await ctx.send(f'{member.mention} joined on {member.joined_at}.')

#-------------------------
#-     Dumb commands     -
#-------------------------

# beep command
@bot.command(name = 'beep', help = 'Literally just says beep.')
async def beep(ctx):
    response = '**Beep!**'
    await ctx.send(response)

# bad command
@bot.command(name = 'bad', help = 'Literally just says bad.')
async def bad(ctx):
    response = '**Bad**'
    await ctx.send(response)

# Am i cool command
@bot.command(name = 'am-i-cool', help = 'Find out if you are cool.')
async def amicool(ctx):
    amicoolquotes = ['You are so cool, how do even you do that?', 'No, you are not cool at all.']
    response = random.choice(amicoolquotes)
    await ctx.send(response)

# uwuduck command
@bot.command(name = 'uwuduck', help = 'uwuduck')
async def uwuduck(ctx):
    await ctx.send('<:uwuduck:916404134821904435>')

#----------------
#-     Test     -
#----------------

# Embed test
@bot.command(name = 'embed-test', help = 'Embed test')
@commands.has_permissions(manage_guild=True)
async def embed_test(ctx):
    linecache.clearcache()
    title_read = linecache.getline('./data/welcome/welcome.ini', 2)
    color_read = linecache.getline('./data/welcome/welcome.ini', 4)
    description_read = linecache.getline('./data/welcome/welcome.ini', 6)
    embed=discord.Embed(
        title = "" + title_read ,
        description = "" + description_read,
        color = "" + c.color_read
    )   
    await ctx.send(embed)

# Read test
@bot.command(name = 'read-test', help = 'Used to test file reading functionality (Requires the user to have manage_guild or administrator permission)')
@commands.has_permissions(manage_guild=True)
async def read_test(ctx):
    linecache.clearcache()
    title = linecache.getline('./data/welcome/welcome.ini', 2)
    color = linecache.getline('./data/welcome/welcome.ini', 4)
    description = linecache.getline('./data/welcome/welcome.ini', 6)
    await ctx.send(title + color + description)

# Dice simulation
@bot.command(name = 'diceroll', help = 'Simulates rolling dice.')
async def roll(ctx, dices_to_roll: int, number_of_sides: int):
    if number_of_sides > 20 or number_of_sides <= 0:
        await ctx.send('The number must be in a range from 1 to 20')
        print(f'bad diceroll')
    else:
        dice = [
            str(random.choice(range(1, number_of_sides + 1)))
            for _ in range(dices_to_roll)
        ]
        await ctx.send(', '.join(dice))


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

WIP
"""

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







# Generic error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
       await ctx.send("Looks like you don't have the right permissions do that.")

# bot login event
@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')

# bot.run
bot.run(TOKEN)