##################
#                #
#     Errors     #
#                #
##################

import os

import discord
from discord.ext import commands
import discord.ext
import asyncio

from utils.dbhelper import DbHelper


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

# Generic error
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """print(error)
        print(f"NSFWChannelRequired: {isinstance(error, commands.NSFWChannelRequired)}")
        print(f"MissingPerms: {isinstance(error, commands.MissingPermissions)}")
        print(f"BotMissingPerms: {isinstance(error, commands.BotMissingPermissions)}")
        print(f"CommandNotFound: {isinstance(error, commands.errors.CommandNotFound)}")
        print(f"NotOwner: {isinstance(error, commands.errors.NotOwner)}")"""
        if isinstance(error, commands.errors.NSFWChannelRequired):
            await ctx.reply("You need to be in an NSFW (18+) channel to use this command.", delete_after = 5, mention_author = False)
            await asyncio.sleep(5)
            await ctx.message.delete()
        
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply("Hey! You do not have permissions to do that!", delete_after = 5, mention_author = False)
            await asyncio.sleep(5)
            await ctx.message.delete()

        if isinstance(error, commands.errors.BotMissingPermissions):
            await ctx.reply("I do not have the permission to do that!", delete_after = 5, mention_author = False)
            await asyncio.sleep(5)
            await ctx.message.delete()

        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.reply('There is no command named like that!', delete_after = 5, mention_author = False)
            await asyncio.sleep(5)
            await ctx.message.delete()       

        if isinstance(error, commands.errors.NotOwner):
            await ctx.reply("This command can only be used by the bot's owner.", delete_after = 5, mention_author = False)
            await asyncio.sleep(5)
            await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(Errors(bot))