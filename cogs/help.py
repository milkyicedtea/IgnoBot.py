import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = 'help')
    async def help(self, interaction: discord.Interaction):
        pass


async def setup(bot):
    await bot.add_cog(Help(bot))
