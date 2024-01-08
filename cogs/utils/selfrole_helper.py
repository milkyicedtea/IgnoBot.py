##########################
#                        #
#     SelfroleHelper     #
#                        #
##########################

import os

import discord

import itertools

from builtins import bot


class SelfroleHelper:

    @staticmethod
    async def remove_role(interaction: discord.Interaction, role: discord.Role):
        """Revokes a role from every member in the guild"""

        member_list = interaction.guild.members
        for member in member_list:
            for roles in member.roles:
                if roles.id == role.id:
                    await member.remove_roles(role)

    @staticmethod
    def get_selfroles_list(cursor, guild: discord.Guild) -> list:
        """Gets the available selfroles for the current guild"""

        cursor.execute(f"select rolenames from roles where guildid = {guild.id} "
                       f"and is_selfrole = 'true';")
        fetch = list(itertools.chain(*cursor.fetchall()))  # convert list of tuples to list
        return fetch

    @staticmethod
    def string_to_discord_role(roles: str | list, guild: discord.Guild) -> list[discord.Role] | None:
        """Gets the discord role from a string or list"""
        if type(roles) is str:
            role_list = [discord.utils.get(guild.roles, name = roles)]
        elif type(roles) is list:
            role_list = [discord.utils.get(guild.roles, name = role) for role in roles]
        else:
            role_list = [None]
            print('Something went wrong')
        return role_list


class SelfroleAssign(discord.ui.Select):
    def __init__(self, role_list: list[discord.Role]):
        select_option_list = [discord.SelectOption(label = role.name, value = str(role.id)) for role in role_list]
        options = select_option_list
        placeholder = 'Select an option.'
        super().__init__(options = options, placeholder = placeholder, max_values = 1)

    async def callback(self, interaction: discord.Interaction):
        print('callback assign')
        embed = discord.Embed(title = "\u2705 Selfrole Assigned!", url = "https://milkyicedtea.epizy.com/Ignobot", color = discord.Colour.random())
        embed.set_author(name = "Selfrole Manager", icon_url = bot.user.display_avatar)
        embed.set_footer(text = interaction.user.display_name, icon_url = interaction.user.display_avatar)
        embed.add_field(name = "", value = f"You have assigned yourself the role {discord.utils.get(interaction.guild.roles, id = int(self.values[0])).mention} to yourself!")
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id = int(self.values[0])),  reason = 'Role assigned using `/selfrole get` command.')
        await interaction.response.edit_message(view = None, embed = embed)


class SelfroleLeave(discord.ui.Select):
    def __init__(self, role_list: list[discord.Role]):
        select_option_list = [discord.SelectOption(label = role.name, value = str(role.id)) for role in role_list]
        options = select_option_list
        placeholder = 'Select an option.'
        super().__init__(options = options, placeholder = placeholder, max_values = 1)

    async def callback(self, interaction: discord.Interaction):
        print('callback leave')
        embed = discord.Embed(title = "\u2705 Selfrole Assigned!", url = "https://milkyicedtea.epizy.com/Ignobot", color = discord.Colour.random())
        embed.set_author(name = "Selfrole Manager", icon_url = bot.user.display_avatar)
        embed.set_footer(text = interaction.user.display_name, icon_url = interaction.user.display_avatar)
        embed.add_field(name = "", value = f"You have unassigned the role {discord.utils.get(interaction.guild.roles, id = int(self.values[0])).mention} from yourself!")
        await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, id = int(self.values[0])), reason = 'Role unassigned using `/selfrole leave` command.')
        await interaction.response.edit_message(view = None, embed = embed)

