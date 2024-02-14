###################
#                 #
#     Animals     #
#                 #
###################

import os

import discord
from discord import app_commands
from discord.ext import commands

import random

from Utils.APIs import duckAPI
from Utils.APIs import catAPI


class Animals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    animal = app_commands.Group(name = 'animal', description = 'Animal images/videos')

    application_check = app_commands.checks.has_permissions

    @animal.command(name = 'duckimage')
    async def duckimage(self, interaction: discord.Interaction):
        """Sends you a cute duck image :3"""
        duck_image = await duckAPI.get_image()
        x = random.choice(range(len(duck_image)))
        await interaction.response.send_message(duck_image[x])

    @animal.command(name = 'duckvideo')
    async def duckvideo(self, interaction: discord.Interaction):
        """Sends you a cute duck video :3"""
        duck_video = await duckAPI.get_video()
        x = random.choice(range(len(duck_video)))
        await interaction.response.send_message(duck_video[x])

    @animal.command(name = 'catimage')
    async def catimage(self, interaction: discord.Interaction):
        """Sends you a cute cat image :3"""
        cat_image = await catAPI.get_image()
        x = random.choice(range(len(cat_image)))
        await interaction.response.send_message(cat_image[x])

    @animal.command(name = 'catvideo')
    async def catvideo(self, interaction: discord.Interaction):
        """Sends you a cute cat video :3"""
        cat_video = await catAPI.get_video()
        x = random.choice(range(len(cat_video)))
        await interaction.response.send_message(cat_video[x])

    @animal.command(name = 'cattos')
    async def cattos(self, interaction: discord.Interaction):
        """Sends more cats images. Only works in specific servers."""
        guild_list = __import__('builtins').guild_list
        guild_id = interaction.guild_id
        if guild_id in guild_list:
            cattos = os.getenv(random.choice(['catto0',
                                              'catto1',
                                              'catto2',
                                              'catto3',
                                              'catto4',
                                              'catto5',
                                              'catto6',
                                              'catto7',
                                              'catto8',
                                              'catto9',
                                              'catto10',
                                              'catto11',
                                              'catto12',
                                              'catto13',
                                              'catto14',
                                              'catto15',
                                              'catto16',
                                              'catto17',
                                              'catto18',
                                              'catto19']))
            await interaction.response.send_message(cattos)
        else:
            await interaction.response.send_message('This command is only available to certain servers.')


async def setup(bot):
    await bot.add_cog(Animals(bot))
