import discord
from discord import app_commands
from discord.ext import commands

from Utils.dbchecks import DbChecks
from Utils.dbhelper import DbHelper as Database


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_balance(user_id):
        with Database() as db:
            cursor = db.get_cursor()

            cursor.execute("select balance from user_data where user_id = %s", user_id)
            bal = cursor.fetchone()[0]
            return bal if bal else 0

    @app_commands.command(name = 'balance')
    async def check_balanece(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        balance = self.get_balance(user_id)
        embed = discord.Embed(title = f"<@{user_id}>'s balance", color = discord.Color.yellow())
        await interaction.response.send_message(embed = embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))
