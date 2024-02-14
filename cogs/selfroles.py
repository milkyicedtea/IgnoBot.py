#####################
#                   #
#     Selfroles     #
#                   #
#####################

import os

import itertools

import discord
from discord.ext import commands
from discord import app_commands

from cogs.Cog_Utils.selfrole_helper import SelfroleHelper, SelfroleAssign, SelfroleLeave

from Utils.dbchecks import DbChecks
from Utils.dbhelper import DbHelper as Database


class Selfroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    selfrole = app_commands.Group(name = 'selfrole', description = 'Selfroles related commands')
    application_check = app_commands.checks.has_permissions

    class DropdownView(discord.ui.View):
        def __init__(self, role_list, action):
            super().__init__()
            match action:
                case 'get':
                    self.add_item(SelfroleAssign(role_list))
                case 'leave':
                    self.add_item(SelfroleLeave(role_list))

    @selfrole.command(name = 'get')
    async def select_role(self, interaction: discord.Interaction):
        """Brings up the selfrole menu to give yourself a role."""

        with Database() as db:
            cursor = db.get_cursor()

            guild = interaction.guild

            # view = self.SelfroleSelect(self.string_to_discord_role(self.get_selfroles_list(cursor = cursor, guild = interaction.guild), interaction.guild))
            user_roles: list[discord.Role] = interaction.user.roles
            guild_roles_db: list[discord.Role] = [discord.utils.get(guild.roles, name = roles) for roles in
                                                  SelfroleHelper.get_selfroles_list(cursor, guild)]

            if guild_roles_db:
                roles_to_display = list(set(guild_roles_db).difference(set(user_roles)))
                if roles_to_display:
                    view = Selfroles.DropdownView(roles_to_display, 'get')

                    embed = discord.Embed(title = "Select a role to give yourself!",
                                          url = "https://milkyicedtea.epizy.com/Ignobot",
                                          description = "These are the available selfroles in the server.")
                    embed.set_author(name = "Selfrole Manager", icon_url = self.bot.user.display_avatar)
                    for index, role in enumerate(roles_to_display):
                        embed.add_field(name = "", value = f"{index + 1} {role.mention}", inline = False)
                    await interaction.response.send_message(embed = embed, view = view, ephemeral = True)
                else:
                    await interaction.response.send_message('Something went wrong! (You already have all the possible selfroles, use `/selfrole leave` to remove one!)', ephemeral = True)
            else:
                await interaction.response.send_message('Something went wrong! (The guild does not have any selfrole)', ephemeral = True)

    @selfrole.command(name = 'leave')
    async def selfrole_leave(self, interaction: discord.Interaction):
        """Brings up the selfrole menu to remove a role from yourself."""

        with Database() as db:
            cursor = db.get_cursor()

            guild = interaction.guild

            user_roles: list[discord.Role] = interaction.user.roles
            guild_roles_db: list[discord.Role] = [discord.utils.get(guild.roles, name = roles) for roles in
                                                  SelfroleHelper.get_selfroles_list(cursor, guild)]

            if guild_roles_db:
                roles_to_display = list(set(user_roles).intersection(guild_roles_db))
                if roles_to_display:
                    view = Selfroles.DropdownView(roles_to_display, 'leave')

                    embed = discord.Embed(title = "Select a role to remove from yourself!",
                                          url = "https://milkyicedtea.epizy.com/Ignobot",
                                          description = "These are the roles you currently have.")
                    embed.set_author(name = "Selfrole Manager", icon_url = self.bot.user.display_avatar)
                    for index, role in enumerate(roles_to_display):
                        embed.add_field(name = "", value = f"{index + 1} {role.mention}", inline = False)
                    await interaction.response.send_message(embed = embed, view = view, ephemeral = True)
                else:
                    await interaction.response.send_message('Something went wrong! (You do not have any selfrole, use `/selfrole get` to get one!)', ephemeral = True)
            else:
                await interaction.response.send_message('Something went wrong! (The guild does not have any selfrole)', ephemeral = True)

    @selfrole.command(name = 'list')
    async def selfrole_list(self, interaction: discord.Interaction):
        """Shows a list with all the selfroles in the server."""

        with Database() as db:
            cursor = db.get_cursor()

            guild = interaction.guild
            color_value = discord.Colour.random()

            fetch = SelfroleHelper.get_selfroles_list(cursor, guild)  # convert list of tuples to list
            print(fetch)

            if not fetch:  # fetch is empty (fetch == [])
                embed = discord.Embed(title = "\U0001f9fe Selfroles list", color = color_value)
                embed.add_field(name = "", value = "**This server has no selfroles.**", inline = False)
                embed.set_author(name = "", icon_url = interaction.guild.icon)
                await interaction.response.send_message(embed = embed, ephemeral = True)

            else:
                embed = discord.Embed(title = "\U0001f9fe Selfroles list", color = color_value)
                embed.add_field(name = "", value = "**These are the available selfroles in the server.**",
                                inline = False)
                embed.set_author(name = "", icon_url = interaction.guild.icon)
                roles = [role for role in fetch]  # for x in range(len(fetch)):
                for index, role in enumerate(roles):
                    role = discord.utils.get(interaction.guild.roles, name = role)
                    embed.add_field(name = "", value = f"{index + 1}: **<@&{role.id}>**", inline = False)

            embed.set_footer(text = "Use the command `/selfrole give` to give yourself the role")
            await interaction.response.send_message(embed = embed, ephemeral = True)

    @selfrole.command(name = 'add')
    @application_check(manage_roles = True)
    async def selfrole_add(self, interaction: discord.Interaction, role: discord.Role):
        """Adds a selfrole to the server's selfrole list."""

        with Database() as db:
            cursor = db.get_cursor()

            guild = interaction.guild
            guildname = guild.name.replace("'", "")

            cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                           f"and rolenames = '{role.name}' and is_selfrole = 'true'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"insert into roles(guildid, guildname, rolenames, is_selfrole) "
                               f"values({guild.id}, '{guildname}', '{role.name}', 'true')")
                db.commit()
                await interaction.response.send_message(f"The role **<@&{role.id}>** is now self-assignable!")
            else:
                await interaction.response.send_message(f"The role **<@&{role.id}>** is already self-assignable!",
                                                        delete_after = 10, ephemeral = True)

    @selfrole.command(name = 'remove')
    @application_check(manage_roles = True)
    async def selfrole_remove(self, interaction: discord.Interaction, role: discord.Role):
        """Removes a selfrole to the server's selfrole list."""

        with Database() as db:
            cursor = db.get_cursor()

            guild = interaction.guild
            guildname = guild.name.replace("'", "")

            await interaction.response.defer(ephemeral = True, thinking = True)

            cursor.execute(f"select count(*) from roles where guildid = {guild.id} "
                           f"and guildname = '{guildname}' and rolenames = '{role.name}' "
                           f"and is_selfrole = 'true';")
            if cursor.fetchone()[0] == 0:
                await interaction.followup.send(f"The role **<@&{role.id}>** was not previously added as a selfrole!", ephemeral = True)
                # await interaction.followup.delete()
            else:
                cursor.execute(f"delete from roles where guildid = {guild.id} "
                               f"and guildname = '{guildname}' and rolenames = '{role.name}' "
                               f"and is_selfrole = 'true';")
                db.commit()
                await SelfroleHelper.remove_role(interaction, role)
                await interaction.followup.send(f'The role **<@&{role.id}>** was removed from every user and is no longer self-assignable')


async def setup(bot):
    await bot.add_cog(Selfroles(bot))
