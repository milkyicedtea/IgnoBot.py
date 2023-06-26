###################
#                 #
#     Weather     #
#                 #
###################

import os

import discord
from discord.ext import commands
from utils.dbhelper import DbHelper


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Weather(bot))