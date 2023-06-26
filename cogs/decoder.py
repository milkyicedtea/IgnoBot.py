###################
#                 #
#     Decoder     #
#                 #
###################

import os

import discord
from discord.ext import commands
from discord import app_commands

import base64


class Decoder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    base64 = app_commands.Group(name = 'base64', description = 'Base64 string encoding/decoding')

    @base64.command(name = 'encode')
    async def encode(self, interaction: discord.Interaction, *, string: str):
        """Encodes text to base64 format."""
        string_bytes = string.encode('UTF-8')
        # print(string_bytes)
        base64_bytes = base64.b64encode(string_bytes)
        # print(base64_bytes)
        base64_string = base64_bytes.decode('UTF-8')
        # print(base64_string)
        await interaction.response.send_message(f'Original message: {string}\nEncoded string: {base64_string}', ephemeral = True)
        # await ctx.send(':white_check_mark:')

    @base64.command(name = 'decode')
    async def decode(self, interaction: discord.Interaction, *, string: str):
        """Decodes base64 format to string."""
        string_bytes = string.encode('UTF-8')
        # print(string_bytes)
        decode_bytes = base64.b64decode(string_bytes)
        # print(decode_bytes)
        decoded_string = decode_bytes.decode('UTF-8')
        # print(decoded_string)
        await interaction.response.send_message(f'Non-decoded message: {string}.\nDecoded string: {decoded_string}', ephemeral = True)
        # await ctx.send(':white_check_mark:')


async def setup(bot):
    await bot.add_cog(Decoder(bot))
