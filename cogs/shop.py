import json

import discord
from discord import components
from discord import app_commands
from discord.ext import commands
from Utils.dbhelper import DbHelper as Database


def get_shop():
    path = 'Cog_Utils/shop_items.json'
    try:
        with open(path, 'r') as file:
            data = json.load(file)
            return tuple(data['items'])

    except FileNotFoundError:
        print(f"Error: File '{path}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Unable to decode JSON in '{path}'.")


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_items = get_shop()
        print(self.shop_items)

    @commands.Cog.listener()
    async def on_button_click(self, button: discord.ui.Button, interaction: discord.Interaction):
        print('button_click')
        if button.custom_id.startswith("shop_pagination"):
            page_number = int(button.custom_id.split("_")[-1])
            await self.send_shop_embed(interaction, page_number)

    async def send_shop_embed(self, interaction, page_number):
        items_per_page = 25
        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page
        page_items = self.shop_items[start_index:end_index]

        embed = discord.Embed(title='Welcome to the Shop!', color=discord.Color.blue())
        for item in page_items:
            name, price = item['name'], item['price']
            embed.add_field(name=name, value=f"{price} :coin:", inline=False)

        buttons = [
            discord.ui.Button(style = discord.ButtonStyle.primary, label = "Previous", custom_id = f"shop_pagination_{page_number - 1}" if page_number > 1 else "disabled", disabled = page_number == 1),
            discord.ui.Button(style = discord.ButtonStyle.primary, label = "Next", custom_id = f"shop_pagination_{page_number + 1}" if end_index < len(self.shop_items) else "disabled", disabled = end_index >= len(self.shop_items))
        ]

        view = discord.ui.View()
        for button in buttons:
            view.add_item(button)

        embed.set_footer(text=f"To buy an item, use `/buy <item>` | Page {page_number}")

        print('sending embed..')

        await interaction.edit_original_response(content=None, embed=embed, view = view)

    @app_commands.command(name="shop")
    async def shop(self, interaction: discord.Interaction):
        """Displays available items in the shop"""

        await interaction.response.defer()

        page_number = 1
        await self.send_shop_embed(interaction, page_number)


async def setup(bot):
    await bot.add_cog(Shop(bot))
