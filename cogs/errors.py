##################
#                #
#     Errors     #
#                #
##################

import os

import discord
from discord.ext import commands

from utils.dbhelper import DbHelper

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

# Generic error
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.NSFWChannelRequired):
            await ctx.send("You need to be in an NSFW channel to use this command")

async def setup(bot):
    await bot.add_cog(Errors(bot))