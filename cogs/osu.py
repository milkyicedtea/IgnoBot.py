import json
from typing import Union

from Utils.logger import logger
from cogs.Cog_Utils.osspy.osu_helper import Osspy

import discord
from discord import app_commands
from discord.ext import commands


class Osu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.osuBot = Osspy()

    osu = app_commands.Group(name = "osu", description = "Osu related commands")
    map = app_commands.Group(name = "map", description = "Commands related to Osu maps", parent = osu)

    @map.command(name = 'lookup')
    async def get_beatmap(self, interaction: discord.Interaction, beatmap_id: int):
        try:
            beatmap = await self.osuBot.get_beatmap(beatmap_id)
            logger.debug(beatmap)

            embed = discord.Embed(
                title = f"{beatmap.beatmapset.artist} - {beatmap.beatmapset.title}",
                url = beatmap.url,
                color = discord.Color.blue()
            )
            embed.add_field(name = "Difficulty", value = f"★ {beatmap.difficulty_rating:.2f}", inline = True)
            embed.add_field(name = "BPM", value = beatmap.bpm, inline = True)
            embed.add_field(name = "Status", value = beatmap.status.name.capitalize(), inline = True)
            embed.add_field(
                name = "Stats",
                value = f"CS:{beatmap.cs} AR:{beatmap.ar} OD:{beatmap.accuracy} HP:{beatmap.drain}",
                inline = False
            )
            embed.set_image(url = beatmap.beatmapset.covers.cover_2x)

            await interaction.response.send_message(embed = embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral = True)

    @app_commands.command(name = 'set')
    async def get_beatmapset(self, interaction: discord.Interaction, beatmapset_id: int):
        try:
            beatmapset = await self.osuBot.get_beatmapset(beatmapset_id)
            # logger.debug(beatmapset)

            embed = discord.Embed(
                title = f"{beatmapset.artist} - {beatmapset.title}",
                description = f"Created by {beatmapset.creator}",
                url = beatmapset.beatmaps[0].url,
                color = discord.Color.blue()
            )
            embed.add_field(name = "Favorites", value = beatmapset.favourite_count, inline = True)
            embed.add_field(name = "Play Count", value = beatmapset.play_count, inline = True)
            embed.add_field(name = "Status", value = beatmapset.status.name.capitalize(), inline = True)
            embed.set_image(url = beatmapset.covers.cover)

            await interaction.response.send_message(embed = embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral = True)

    @app_commands.command(name = 'recent')
    async def rs(self, interaction: discord.Interaction, user_id: int = None):
        if not user_id:
            score = await self.osuBot.get_score()
            await interaction.response.send_message(f"```json\n{score.model_dump_json()}```", ephemeral=True)


    @app_commands.command(name = 'beatmap_to_json')
    async def get_beatmap_to_json(self, interaction: discord.Interaction, beatmap_id: int = None):
        try:
            beatmap = await self.osuBot.get_beatmap(beatmap_id)
            beatmap_json = beatmap.model_dump_json()
            print('printing beatmap')
            await interaction.response.send_message(f"```json\n{beatmap_json}```", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

    @app_commands.command(name = 'score_to_json')
    async def get_score_to_json(self, interaction: discord.Interaction, score_id: int = None):
        try:
            score = await self.osuBot.get_score(score_id)
            await interaction.response.send_message(f"```json\n{score.model_dump_json(indent = 2)}```", ephemeral = True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral = True)

    @app_commands.command(name = 'user')
    async def get_user(self, interaction: discord.Interaction, user_id: int = None):
        pass


async def setup(bot):
    await bot.add_cog(Osu(bot))
