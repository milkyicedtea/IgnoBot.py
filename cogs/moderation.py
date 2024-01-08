######################
#                    #
#     Moderation     #
#                    #
######################

import os

import discord
from discord import app_commands
from discord.ext import commands

import dotenv
import json
from builtins import bot


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # moderationGroup = app_commands.Group(name = 'moderation', description = 'Moderation related commands')
    channel = app_commands.Group(name = 'channel', description = 'Channel related commands', guild_only = True)
    roleGroup = app_commands.Group(name = 'role', description = 'Roles related commands', guild_only = True)
    server = app_commands.Group(name = 'server', description = 'Server related commands', guild_only = True)

    application_check = app_commands.checks.has_permissions

    @app_commands.command(name = 'kick')
    @application_check(kick_members = True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Kicks a user."""

        await member.kick(reason = reason)
        await interaction.response.send_message(f'User {member.mention} has been kicked from the server.\nResponsible mod: **{interaction.user}**\nReason: {reason}')

    @app_commands.command(name = 'vkick')
    @application_check(move_members = True)
    async def vkick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Kicks a user from a voice channel."""

        if member.voice is not None:
            vc: discord.VoiceChannel = member.voice.channel
            await member.edit(voice_channel = None, reason = reason)
            await interaction.response.send_message(f'User {member.mention} has been kicked from {vc.mention}.\nResponsible mod: **{interaction.user}**\nReason: {reason}')
        else:
            await interaction.response.send_message(f'User {member.mention} is not in a voice channel!')

    @app_commands.command(name = 'ban')
    @application_check(ban_members = True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Bans a user."""

        await member.ban(reason = reason)
        embed = discord.Embed(title = "", color = discord.Colour.random())
        embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.avatar)
        embed.add_field(name = "New ban:", value = f"User {member.mention} has been banned")
        embed.add_field(name = "Responsible mod:", value = interaction.user)
        embed.add_field(name = "Reason:", value = reason)
        await interaction.response.send_message(embed = embed)

    @app_commands.command(name = 'unban')
    @application_check(ban_members = True)
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        """Unbans a user."""

        banned_users = interaction.guild.bans()

        async for ban_entry in banned_users:
            user_ban_entry = ban_entry.user

            if user_ban_entry == user:
                await interaction.guild.unban(user, reason = reason)
                embed = discord.Embed(title = "", color = discord.Colour.random())
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.avatar)
                embed.add_field(name = "New unban:", value = f"User {user.mention} has been unbanned")
                embed.add_field(name = "Responsible mod:", value = interaction.user)
                if reason:
                    embed.add_field(name = "Reason:", value = reason)
                return await interaction.response.send_message(embed = embed)

    @app_commands.command(name = 'purge')
    @application_check(manage_messages = True)
    async def purge_messages(self, interaction: discord.Interaction, amount_to_delete: int = 0):
        """Purges x messages."""

        if amount_to_delete < 1 or amount_to_delete > 100:
            await interaction.response.send_message('You need to enter a value between 1 and 100', ephemeral = True, delete_after = 10)
        else:
            await interaction.response.send_message(f'Purged {amount_to_delete} messages!', ephemeral = True, delete_after = 10)
            await interaction.channel.purge(limit = amount_to_delete)

    @channel.command(name = 'create')
    @application_check(manage_channels = True)
    async def create_channel(self, interaction: discord.Interaction, channel_name: str = None, category: discord.CategoryChannel = None, ):
        """Creates a new channel."""

        guild = interaction.guild
        existing_channel = discord.utils.get(guild.channels, name = channel_name)
        if existing_channel:
            await interaction.response.send_message(f'A channel named "{channel_name}" already exists. Please delete or rename that channel before using this command.')
        if not existing_channel:
            if channel_name is None:
                channel_name = 'new-channel'
            await guild.create_text_channel(channel_name, category = category)
            channel = discord.utils.get(interaction.guild.channels, name = channel_name)
            await interaction.response.send_message(f'Channel <#{channel.id}> was succesfully created')

    @channel.command(name = 'delete')
    @application_check(manage_channels = True)
    async def delete_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Deletes a channel."""

        if interaction.channel == channel:
            interaction.response.send_message(f"You can't request to delete a channel while you're in it!", ephemeral = True, delete_after = 10)
        else:
            await channel.delete()
            await interaction.response.send_message(f"Channel **{channel.name}** was succesfully deleted")

    @server.command(name = 'memberlist')
    @application_check(administrator = True)
    async def member_list(self, interaction: discord.Interaction):
        """Returns member list as json file."""

        member_list: list = [member for member in interaction.guild.members]
        dictionary = {
            "members": [

            ]
        }

        for member in member_list:
            # if not member.bot:
            new_dictionary = {
                "name": f"{member.name}",
                "mention": f"{member.mention}",
                "roles": f"{[role for role in member.roles]}, ",
                "created_at": f"{member.created_at}",
                "is_bot": f"{member.bot}"
            }
            dictionary["members"].append(new_dictionary)

        print('opening file')

        with open('memberList.json', "w") as outfile:
            print('dumping')
            json.dump(dictionary, outfile, indent = 1)
            outfile.close()
            await interaction.response.send_message("Check your DMs!", ephemeral = True)
            await interaction.user.send(content = "", file = discord.File("memberList.json"))
            os.remove("memberList.json")

    @server.command(name = 'banner')
    async def server_banner(self, interaction: discord.Interaction):
        """Returns the server's banner."""

        guildraw = interaction.guild
        embed = discord.Embed(title = "", color = discord.Colour.random())
        if guildraw.banner is not None:
            server_banner = guildraw.banner
            embed.set_image(url = server_banner)
        else:
            embed.add_field(name = "An error occurred!", value = "This server does not have a banner!")

        await interaction.response.send_message(embed = embed)

    @server.command(name = 'icon')
    async def server_icon(self, interaction: discord.Interaction):
        """Returns the server's icon."""

        guildraw = interaction.guild
        embed = discord.Embed(title = "", color = discord.Colour.random())
        if guildraw.icon is None:
            embed.add_field(name = "An error occurred!", value = "This server does not have an icon!")
        else:
            server_icon = guildraw.icon
            embed.set_image(url = server_icon)

        await interaction.response.send_message(embed = embed)

    @roleGroup.command(name = 'assign')
    @application_check(manage_roles = True)
    async def assign_role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        """Gives a role to member."""

        await member.add_roles(role)
        await interaction.response.send_message(f'The role **<@&{role.id}>** has been assigned to <@{member.id}>', silent = True)

    @roleGroup.command(name = "unassign")
    @application_check(manage_roles = True)
    async def unassign_role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        """Takes away a role from member"""

        await member.remove_roles(role)
        await interaction.response.send_message(f'The role **<@&{role.id}>** has been removed from <@{member.id}>', silent = True)

    @app_commands.command(name = 'dev')
    async def dev(self, interaction: discord.Interaction):
        """Sends the dev's official site. Site is still WIP"""
        await interaction.response.send_message('https://milkyicedtea.epizy.com')

    @app_commands.command(name = 'patchnotes')
    async def patch(self, interaction: discord.Interaction):
        """Shows the progress of the bot"""
        await interaction.response.send_message('https://github.com/milkyicedtea/IgnoBot.py/commits/main')

    @roleGroup.command(name = 'create')
    @application_check(manage_roles = True)
    @app_commands.rename(role_name = 'name', role_color = 'color')
    @app_commands.describe(role_color = 'The color must be given in hex format (#<hex>), leave blank for random color')
    async def create_role(self, interaction: discord.Interaction, role_name: str, role_color: str = None):
        """Creates a role"""
        color = discord.Colour.random() if not role_color else discord.Colour.from_str(role_color)
        await interaction.guild.create_role(name = role_name, color = color, reason = f'Created using `/role create` command. Issued by: {interaction.user}')
        await interaction.response.send_message(f'The role **{role_name}** has been created!')

    @roleGroup.command(name = 'delete')
    @commands.has_guild_permissions(manage_roles = True)
    async def delete_role(self, interaction: discord.Interaction, role: discord.Role):
        """Deletes role"""
        await role.delete(reason = f'Deleted using `/role delete` command. Issued by: {interaction.user}')
        await interaction.response.send_message(f'Role **{role.name}** has been deleted.')

    class FeedbackModal(discord.ui.Modal, title = "Send us your Feedback!"):
        message_title = discord.ui.TextInput(
            style = discord.TextStyle.short,
            label = "Title",
            required = False,
            placeholder = 'Give your feedback a title'
        )

        message = discord.ui.TextInput(
            style = discord.TextStyle.long,
            label = "Message",
            required = False,
            max_length = 512,
            placeholder = 'Give your message'
        )

        async def on_submit(self, interaction: discord.Interaction):
            duck_guild: discord.Guild = await bot.fetch_guild(int(dotenv.get_key('.env', 'ducks_hideout')))
            print(duck_guild.name)
            print(type(duck_guild))
            feedback_channel: discord.TextChannel = await duck_guild.fetch_channel(int(dotenv.get_key('.env', 'feedback_channel')))
            print(feedback_channel.id)
            print(feedback_channel.name)
            embed_var = discord.Embed(title = f'New feedback', color = discord.Colour.random())

            embed_var.add_field(name = 'Guild:', value = interaction.guild.name)
            embed_var.add_field(name = 'User:', value = f'{interaction.user.name} ({interaction.user.mention})')
            embed_var.add_field(name = 'Feedback title:', value = self.message_title)
            embed_var.add_field(name = 'Message:', value = self.message)

            await feedback_channel.send(embed = embed_var)
            await interaction.response.send_message(f'Thank you, {interaction.user.mention} for your feedback', ephemeral = True)

        async def on_error(self, interaction: discord.Interaction, error):
            ...

    @server.command(name = 'feedback')
    async def feedback(self, interaction: discord.Interaction):
        """Sends a feedback to IgnoBot's support server. Write about any issues or suggestions!"""
        feedback = self.FeedbackModal()
        await interaction.response.send_modal(feedback)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
