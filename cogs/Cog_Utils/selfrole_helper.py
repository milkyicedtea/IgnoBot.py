##########################
#                        #
#     SelfroleHelper     #
#                        #
##########################

import asyncio

import discord

import itertools

import psycopg


class SelfroleHelper:

    @staticmethod
    async def remove_role(interaction: discord.Interaction, role: discord.Role):
        """Revokes a role from every member in the guild"""

        members_with_role = [
            member for member in interaction.guild.members if role in member.roles
        ]

        if not members_with_role:
            return  # No memeber has this role, no need to do anything

        # remove role from members with small delay
        for index, member in enumerate(members_with_role):
            try:
                await member.remove_roles(role)
                if index % 5 == 0:  # delay ever 5th member
                    await asyncio.sleep(1)
            except discord.Forbidden:
                print(f"Permission error: Could not remove role from {member.name}.")
            except discord.HTTPException as de:
                print(f"HTTP error occurred while removing role from {member.name}: {de}")

    @staticmethod
    async def get_selfroles_list(cursor: psycopg.AsyncCursor, guild: discord.Guild) -> list:
        """Gets the available selfroles for the current guild"""

        await cursor.execute("""
            select rolenames
            from roles
            where guildid = %s and is_selfrole = %s
        """, (guild.id, True))

        fetch = list(itertools.chain(*(await cursor.fetchall())))  # convert list of tuples to list
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
            max_values = len(role_list) if len(role_list) <= 10 else 10
            super().__init__(options = options, placeholder = placeholder, max_values = max_values)

        async def callback(self, interaction: discord.Interaction):
            print('callback assign')
            embed = discord.Embed(title = "\u2705 Selfrole Assigned!", url = "https://milkyicedtea.epizy.com/Ignobot", color = discord.Colour.random())
            embed.set_author(name = "Selfrole Manager", icon_url = interaction.client.user.display_avatar)
            embed.set_footer(text = interaction.user.display_name, icon_url = interaction.user.display_avatar)
            embed.add_field(name = "", value = f"You have assigned yourself the role {discord.utils.get(interaction.guild.roles, id = int(self.values[0])).mention} to yourself!")
            await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, id = int(self.values[0])),  reason = 'Role assigned using `/selfrole get` command.')
            await interaction.response.edit_message(view = None, embed = embed) # noqa


    class SelfroleLeave(discord.ui.Select):
        def __init__(self, role_list: list[discord.Role]):
            select_option_list = [discord.SelectOption(label = role.name, value = str(role.id)) for role in role_list]
            options = select_option_list
            placeholder = 'Select an option.'
            max_values = len(role_list) if len(role_list) <= 10 else 10
            super().__init__(options = options, placeholder = placeholder, max_values = max_values)

        async def callback(self, interaction: discord.Interaction):
            print('callback leave')
            embed = discord.Embed(title = "\u2705 Selfrole Unassigned!", url = "https://milkyicedtea.epizy.com/Ignobot", color = discord.Colour.random())
            embed.set_author(name = "Selfrole Manager", icon_url = interaction.client.user.display_avatar)
            embed.set_footer(text = interaction.user.display_name, icon_url = interaction.user.display_avatar)
            embed.add_field(name = "", value = f"You have unassigned the role {discord.utils.get(interaction.guild.roles, id = int(self.values[0])).mention} from yourself!")
            await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, id = int(self.values[0])), reason = 'Role unassigned using `/selfrole leave` command.')
            await interaction.response.edit_message(view = None, embed = embed) # noqa

