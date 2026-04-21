import discord
from discord import app_commands
from discord.ext import commands

from Utils.database.database import DfDB, PgDB
from Utils.logger import logger
from cogs.Cog_Utils.fishing_helper import FishingHelper, FishingState


class FishingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = 'fish')
    async def fish(self, interaction: discord.Interaction):
        await interaction.response.defer() # noqa

        user_id: int = interaction.user.id
        cooldown_key = f'cooldown:user:{user_id}'

        async with DfDB() as df:
            if await df.exists(cooldown_key):
                await interaction.followup.send("You're still on cooldown. Try again later.")
                return

        async with PgDB() as db:
            cursor = await db.get_cursor()

            try:
                await cursor.execute("""
                    INSERT INTO users (user_id, username)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username
                """, (user_id, interaction.user.global_name))

                user_baits = await FishingHelper.load_user_bait_inventory(user_id)

                if len(user_baits) == 0:
                    await interaction.followup.send("You have no bait! Use `baitshop to buy some.")
                    return
            except Exception as e:
                await interaction.followup.send("Something went wrong while loading your bait inventory.")
                logger.error(f"DB error in fish command: {e}")
                return

            embed = FishingHelper.build_fishing_bait_select_embed(user_baits)
            view = FishingHelper.build_fishing_bait_select_components(user_baits)

            await interaction.followup.send(embed = embed, view = view)

            msg = await interaction.original_response()
            initial_state = FishingState(
                owner_id = user_id,
                selected_bait_id = 0,
            )
            await FishingHelper.save_fishing_state(user_id, msg.id, initial_state)

async def setup(bot):
    await bot.add_cog(FishingSystem(bot))