import os

import discord
from discord.ext import commands

import mysql.connector

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

mydb = mysql.connector.connect(host = "localhost", user = "root", password = os.getenv('mariadb'), database = 'ignobot')
print(mydb)

def setup(bot):
    bot.add.cog(Database(bot))