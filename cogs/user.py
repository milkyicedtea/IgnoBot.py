################
#              #
#     User     #
#              #
################

import os

import discord
from discord import app_commands
from discord.ext import commands


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    userGroup = app_commands.Group(name = 'user', description = 'User related commands')

    @userGroup.command(name = 'avatar')
    async def user_avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        """Returns a user's avatar. Leave blank for your own avatar."""
        if user is None:
            user = interaction.user

        embed = discord.Embed(title = f"{user.mention}'s profile image", color = discord.Colour.random())
        embed.set_image(url = user.avatar)
        await interaction.response.send_message(embed = embed)

    @userGroup.command(name = 'joindate')
    async def join_date(self, interaction: discord.Interaction, user: discord.Member = None):
        """Returns the date that the user joined the server. Leave blank for your own."""
        if user is None:
            user = interaction.user
        await interaction.response.send_message(f'{user.mention} joined on {user.joined_at}.')


async def setup(bot):
    await bot.add_cog(User(bot))
