# -*- coding: utf-8 -*-
# わああああああああああああああああああああああああああああああああああああああああ

################
#              #
#     Main     #
#              #
################

import asyncio
import sys
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os

import sys

from discord.ext import commands
import discord.utils

from dotenv import dotenv_values

from Utils.database.database import PgDB

from Utils.logger import logger

################
# Environment Setup
################

env = dotenv_values('.env')

TOKEN = env['BOT_TOKEN']
GUILD_IDS = [
    int(env['KODAMA_GUILD']),
    int(env['CHILL_IGNORANCE']),
    int(env['ICHIBAN_KUJI_GUILD']),
    int(env['DUCKS_HIDEOUT'])
]

################
# Bot Setup
################

async def get_prefix(bot: commands.Bot, message: discord.Message) -> str:
    async with PgDB() as db:
        cursor = await db.get_cursor()
        guild_id = message.guild.id

        await cursor.execute("SELECT prefix FROM guild_settings WHERE guild_id = %s", (guild_id,))
        result = await cursor.fetchone()

        if result is None:
            # Initialize settings if not found
            await cursor.execute("INSERT INTO guild_settings (guild_id, prefix) VALUES (%s, %s)", (guild_id, "i."))
            await db.commit()
            return "i."
        return result[0]


intents = discord.Intents.all()
bot = commands.Bot(command_prefix = get_prefix, intents = intents, description = 'ducc :3')


################
# Cog Loader
################

async def load_cogs():
    """Dynamically load all cogs."""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Loaded cog: {filename[:-3]}")
            except Exception as e:
                logger.error(f"Failed to load cog {filename}: {e}")


################
# Events
################

# Bot login event
@bot.event
async def on_ready():
    """Bot startup event."""
    await bot.tree.sync()
    for guild_id in GUILD_IDS:
        await bot.tree.sync(guild = discord.Object(id = guild_id))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the ducks at the park 🦆"))
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_guild_join(guild: discord.Guild):
    """Initialize settings for a new guild."""
    default_channel = discord.utils.get(guild.text_channels, name="general")
    welcome_message = f"Hey %mention_user%! Welcome to {guild.name}!"

    async with PgDB() as db:
        cursor = await db.get_cursor()
        await cursor.execute("""
            INSERT INTO guild_info (guild_id, guild_name) 
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (guild.id, guild.name),)

        await cursor.execute("""
            INSERT INTO guild_settings (guild_id, prefix) 
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (guild.id, "i."),)

        await cursor.execute("""
            INSERT INTO guild_settings (welcome_channel, guild_id, welcome_message)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (default_channel.id if default_channel else None, guild.id, welcome_message),)
        await db.commit()

    logger.info(f"Initialized settings for guild: {guild.name} (ID: {guild.id})")


# @bot.event
# async def on_guild_remove(guild: discord.Guild):
#     """Clean up database entries when the bot leaves a guild."""
#     with PsqlDB() as db:
#         cursor = await db.get_cursor()
#         cursor.execute("DELETE FROM guildinfo WHERE guildid = %s", (guild.id,))
#         cursor.execute("DELETE FROM guildsettings WHERE guildid = %s", (guild.id,))
#         cursor.execute("DELETE FROM welcome WHERE guildid = %s", (guild.id,))
#         cursor.execute("DELETE FROM roles WHERE guildid = %s", (guild.id,))
#         db.commit()
#     logger.info(f"Cleaned up database for guild: {guild.name} (ID: {guild.id})")

################
# Main Runner
################

async def main():
    """Main entry point."""
    try:
        async with bot:
            await load_cogs()
            await asyncio.create_task(bot.start(TOKEN))

    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    logger.info(f"Python version: {sys.version}")
    asyncio.run(main())
