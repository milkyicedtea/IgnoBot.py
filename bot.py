import os

import discord
from dotenv import load_dotenv
import random
# Commands introduction
from discord.ext import commands

# Initializing variables from .env file
load_dotenv()
TOKEN = os.getenv('bot_token')
GUILD = os.getenv('guild_name')

"""

# Using client events and login by client.run

client = discord.Client()

@client.event
async def on_ready():
    guild=discord.utils.get(client.guilds, name=GUILD)

    print(
        f'{client.user} has connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    pong_answer='Pong!'

    if message.content == 'ping':
        response = (pong_answer)
        await message.channel.send(response)
    elif message.content == 'raise-exception':
        raise discord.DiscordException

@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)
"""
# Using bot events and login by bot.run

# Prefix setup
bot = commands.Bot(command_prefix='i.')

# Bot login event
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# "beep" test command
@bot.command(name = 'beep', help = 'Literally just says beep.')
async def beep(ctx):
    response = '**Beep!**'
    await ctx.send(response)

# "bad" test command
@bot.command(name = 'bad', help = 'Literally just says bad.')
async def bad(ctx):
    response = '**Bad**'
    await ctx.send(response)

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

# Creating a new channel
@bot.command(name='create-channel', help='Creates a new channel.')
@commands.has_permissions(manage_channels=True)
async def create_channel(ctx, channel_name='new-channel'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if existing_channel:
        print(f'Channel already exists')
        await ctx.send('A channel named "*new-channel*" already exists. Please delete or rename that channel before using this command')
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

# Error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Something went wrong or you are not able to execute this command.')

# Am i cool command
@bot.command(name='am-i-cool', help='Find out if you are cool')
async def amicool(ctx):
    amicoolquotes = ['You are so cool, how do you do that', 'No, you are not cool at all']
    response = random.choice(amicoolquotes)
    await ctx.send(response)

# Join date command
@bot.command(name='join', help='Shows the date when a member joined')
async def join(ctx, member: discord.Member):
    await ctx.send(f'{member.name} joined on {member.joined_at}')





bot.run(TOKEN)