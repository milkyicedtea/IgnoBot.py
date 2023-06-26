#########################
#                       #
#     Dumb commands     #
#                       #
#########################

import os

import discord
from discord import app_commands
from discord.ext import commands
from builtins import bot

import random


class Dumb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    misc = app_commands.Group(name = 'fun', description = 'fun misc group')

    application_check = app_commands.checks.has_permissions

    @misc.command(name = 'am-i-cool')
    async def amicool(self, interaction: discord.Interaction):
        """Tells you if you're cool or not."""
        amicoolquotes = ['You are so cool, how do even you do that?', 'No, you are not cool at all.']
        response = random.choice(amicoolquotes)
        await interaction.response.send_message(response)

    @app_commands.command(name = 'uwuduck')
    async def uwuduck(self, interaction: discord.Interaction):
        """Sends a very cute uwuduck emoji"""
        await interaction.response.send_message('<:uwuduck:916404134821904435>')

    @misc.command(name = 'diceroll')
    @app_commands.rename(dices_to_roll = 'dices', number_of_sides = 'sides')
    async def roll(self, interaction: discord.Interaction, dices_to_roll: int, number_of_sides: int):
        """Rolls x dices with x sides each"""
        if dices_to_roll > 100 or dices_to_roll <= 0:
            await interaction.response.send_message('The number of dices must range from 1 to 100', ephemeral = True)
        if number_of_sides > 20 or number_of_sides <= 0:
            await interaction.response.send_message('The number of sides must range from 1 to 20', ephemeral = True)
            print(f'bad diceroll')
        else:
            dice_rolls = [
                str(random.choice(range(1, number_of_sides + 1)))
                for _ in range(dices_to_roll)
            ]
            await interaction.response.send_message(', '.join(dice_rolls))


async def setup(bot):
    await bot.add_cog(Dumb(bot))
