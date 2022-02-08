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

    @commands.command(name = 'encode', help = 'Encodes your message and DMs the base64 result')
    async def encode(self, ctx, *, string):
        string_bytes = string.encode('UTF-8')
        print(string_bytes)
        base64_bytes = base64.b64encode(string_bytes)
        print(base64_bytes)
        base64_string = base64_bytes.decode('UTF-8')
        print(base64_string)
        await ctx.author.send(f'Original message: {string}\nEncoded string: {base64_string}')
        await ctx.send(':white_check_mark:')

    @commands.command(name = 'decode', help = 'Decodes your base64 string and DMs the result')
    async def decode(self,ctx, *, string):
        string_bytes = string.encode('UTF-8')
        decode_bytes = base64.b64decode(string_bytes)
        decoded_string = decode_bytes.decode('UTF-8')
        await ctx.author.send(f'Non-decoded message: {string}.\nDecoded string: {decoded_string}')
        await ctx.send(':white_check_mark:')

def setup(bot):
    bot.add_cog(Decoder(bot))