##################
#                #
#     Errors     #
#                #
##################

import os

import discord
from discord.ext import commands

mydb = None
cursor = None

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

# Generic error
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("Looks like you don't have the right permissions do that.")

def setup(bot):
    bot.add_cog(Errors(bot))