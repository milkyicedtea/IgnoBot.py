#####################
#                   #
#     Selfroles     #
#                   #
#####################

import os
import asyncio
import itertools


import discord
from discord.ext import commands
from discord import app_commands

from utils.dbchecks import DbChecks
from utils.dbhelper import DbHelper


async def remove_role(interaction, role):
    mList = interaction.guild.members
    for member in mList:
        for roles in member.roles:
            if roles.id == role.id:
                await member.remove_roles(role)


class Selfroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    selfrole = app_commands.Group(name = 'selfrole', description = 'Selfroles related commands')

    application_check = app_commands.checks.has_permissions


    @selfrole.command(name = 'list')
    async def selfrole_list(self, interaction: discord.Interaction):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        user = interaction.user
        colorValue = discord.Colour.random()

        embed = discord.Embed(title = "\U0001f9fe Selfroles list", color = colorValue)

        cursor.execute(f"select rolenames from roles where guildid = {guild.id} "
                       f"and guildname = '{guild.name}' and is_selfrole = 'true';")
        fetch = list(itertools.chain(*cursor.fetchall()))   # convert list of tuples to list
        print(fetch)

        if not fetch:   # fetch is empty (fetch == []
            embed.add_field(name = "", value = "**This server has no selfroles.**", inline = False)
            embed.set_author(name = "", icon_url = interaction.guild.icon)
            await interaction.response.send_message(embed = embed, ephemeral = True)

        else:
            embed.add_field(name = "", value = "**These are the available selfroles in the server.**",
                            inline = False)
            embed.set_author(name = "", icon_url = interaction.guild.icon)
            roles = [role for role in fetch]    # for x in range(len(fetch)):
            for index, role in enumerate(roles):
                role = discord.utils.get(interaction.guild.roles, name = role)
                embed.add_field(name = "", value = f"{index+1}: **<@&{role.id}>**", inline = False)

        embed.set_footer(text = "Use the command `/selfrole give` to give yourself the role")
        await interaction.response.send_message(embed = embed, ephemeral = True)
        dbhelper.close()


    @selfrole.command(name = 'add')
    @application_check(manage_roles = True)
    async def selfrole_add(self, interaction: discord.Interaction, role: discord.Role):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        user = interaction.user
        colorValue = discord.Colour.random()

        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and rolenames = '{role.name}' and is_selfrole = 'true'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"insert into roles(guildid, guildname, rolenames, is_selfrole) "
                           f"values({guild.id}, '{guild.name}', '{role.name}', 'true')")
            mydb.commit()
            await interaction.response.send_message(f"The role **<@&{role.id}>** is now self-assignable!")
        else:
            await interaction.response.send_message(f"The role **<@&{role.id}>** is already self-assignable!",
                                                    delete_after = 10, ephemeral = True)
        dbhelper.close()


    @selfrole.command(name = 'give')
    async def selfrole_give(self, interaction: discord.Interaction, role: discord.Role):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        user = interaction.user
        colorValue = discord.Colour.random()

        exists_in_db: bool = False

        # check if role is in db
        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and guildname = '{guild.name}' and rolenames = '{role.name}' "
                       f"and is_selfrole = 'true';")
        if cursor.fetchone()[0] > 0:
            exists_in_db = True
        else:
            await interaction.response.send_message(f'The role **<@&{role}>** is not a selfrole.', delete_after = 10, ephemeral = True)

        if exists_in_db:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"The role **<@&{role.id}>** has been assigned to you", ephemeral = True)
        dbhelper.close()


    @selfrole.command(name = 'remove')
    @application_check(manage_roles = True)
    async def selfrole_remove(self, interaction: discord.Interaction, role: discord.Role):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        user = interaction.user
        colorValue = discord.Colour.random()

        await interaction.response.defer(ephemeral = True, thinking = True)

        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and guildname = '{guild.name}' and rolenames = '{role.name}' "
                       f"and is_selfrole = 'true';")
        if cursor.fetchone()[0] == 0:
            await interaction.followup.send(f"The role **<@&{role.id}>** was not previously added as a selfrole!", ephemeral = True)
            # await interaction.followup.delete()
        else:
            cursor.execute(f"delete from roles where guildid = {guild.id} "
                           f"and guildname = '{guild.name}' and rolenames = '{role.name}' "
                           f"and is_selfrole = 'true';")
            mydb.commit()
            await remove_role(interaction, role)
            await interaction.followup.send(f'The role **<@&{role.id}>** was removed from every user and is no longer self-assignable')
        dbhelper.close()


    @selfrole.command(name = 'leave')
    async def selfrole_leave(self, interaction: discord.Interaction, role: discord.Role):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guild = interaction.guild
        user = interaction.user
        colorValue = discord.Colour.random()

        cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                       f"and guildname = '{guild.name}' and rolenames = '{role.name}' "
                       f"and is_selfrole = 'true';")
        if cursor.fetchone()[0] == 0:
            await interaction.response.send_message(f'The role **<@&{role.id}>** exists in this guild but is not a selfrole.', delete_after = 10, ephemeral = True)
        else:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"The role **<@&{role.id}** has been removed from your current roles", ephemeral = True)
        dbhelper.close()


async def setup(bot):
    await bot.add_cog(Selfroles(bot))