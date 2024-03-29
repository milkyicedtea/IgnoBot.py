###################
#                 #
#     Decoder     #
#                 #
###################

import os

import discord
from discord.ext import commands
import base64

class Decoder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command()
    async def encode(self, ctx, *, string):
        string_bytes = string.encode('UTF-8')
        # print(string_bytes)
        base64_bytes = base64.b64encode(string_bytes)
        # print(base64_bytes)
        base64_string = base64_bytes.decode('UTF-8')
        print(base64_string)
        reaction_id = ctx.message.id
        await ctx.author.send(f'Original message: {string}\nEncoded string: {base64_string}')
        await ctx.send(':white_check_mark:')

    @commands.command()
    async def decode(self,ctx, *, string):
        string_bytes = string.encode('UTF-8')
        # print(string_bytes)
        decode_bytes = base64.b64decode(string_bytes)
        # print(decode_bytes)
        decoded_string = decode_bytes.decode('UTF-8')
        print(decoded_string)
        await ctx.author.send(f'Non-decoded message: {string}.\nDecoded string: {decoded_string}')
        await ctx.send(':white_check_mark:')

async def setup(bot):
    await bot.add_cog(Decoder(bot))