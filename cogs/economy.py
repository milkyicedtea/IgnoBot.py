import discord
from discord import app_commands
from discord.ext import commands

from Utils.database.database import PgDB 


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def get_balance(user_id):
        async with PgDB() as db:
            cursor = await db.get_cursor()

            await cursor.execute("select balance from user_data where user_id = %s", (user_id,))
            bal = await cursor.fetchone()
            return bal if bal else 0

    @app_commands.command(name = 'balance')
    async def check_balanece(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        balance = self.get_balance(user_id)
        embed = discord.Embed(title = f"<@{user_id}>'s balance", color = discord.Color.yellow())
        await interaction.response.send_message(embed = embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))
