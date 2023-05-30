######################
#                    #
#     Moderation     #
#                    #
######################

import os
import json

import discord
from discord import app_commands
from discord.ext import commands

from utils.dbchecks import DbChecks
from utils.dbhelper import DbHelper

class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# moderationGroup = app_commands.Group(name = 'moderation', description = 'Moderation related commands')
	channel = app_commands.Group(name = 'channel', description = 'Channel related commands')
	roleGroup = app_commands.Group(name = 'role', description = 'Roles related commands')
	server = app_commands.Group(name = 'server', description = 'Server related commands', guild_only = True)

	application_check = app_commands.checks.has_permissions


	# Kicks user
	@app_commands.command(name = 'kick', description = "Kicks a user")
	@application_check(kick_members = True)
	async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
		await member.kick(reason = reason)
		await interaction.response.send_message(f'User {member.mention} has been kicked from the server.\nResponsible mod: **{interaction.user}**\nReason: {reason}')


	# Bans user
	@app_commands.command(name = 'ban', description = "Bans a user")
	@application_check(ban_members = True)
	async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
		await member.ban(reason = reason)
		embed = discord.Embed(title = "", color = discord.Colour.random())
		embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.avatar)
		embed.add_field(name = "New ban:", value = f"User {member.mention} has been banned")
		embed.add_field(name = "Responsible mod:", value = interaction.user)
		embed.add_field(name = "Reason:", value = reason)
		await interaction.response.send_message(embed = embed)


	# Unbans users
	@app_commands.command(name = 'unban', description = "Unbans a user")
	@application_check(ban_members = True)
	async def unban(self, interaction: discord.Interaction, member: discord.Member):
		banned_users = await interaction.guild.bans()

		for ban_entry in banned_users:
			user = ban_entry.user

			if (user.name, user.discriminator) == (member.name, member.discriminator):
				await interaction.guild.unban(user)
				embed = discord.Embed(title="", color=discord.Colour.random())
				embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.avatar)
				embed.add_field(name = "New unban:", value = f"User {member.mention} has been unbanned")
				embed.add_field(name = "Responsible mod:", value = interaction.user)
				await interaction.response.send_message(embed = embed)
				return


	# Purges x messages
	@app_commands.command(name = 'purge')
	@application_check(manage_messages = True)
	async def purge_messages(self, interaction: discord.Interaction, amount_to_delete: int = 0):
		if amount_to_delete < 1 or amount_to_delete > 100:
			await interaction.response.send_message('You need to enter a value between 1 and 100', ephemeral = True, delete_after = 10)
		else:
			await interaction.response.send_message(f'Purged {amount_to_delete} messages!', ephemeral = True, delete_after = 10)
			await interaction.channel.purge(limit = amount_to_delete)


	# Creates a new channel
	@channel.command(name = 'create')
	@application_check(manage_channels = True)
	async def create_channel(self, interaction: discord.Interaction, channel_name: str = None, category: discord.CategoryChannel = None, ):
		guild = interaction.guild
		existing_channel = discord.utils.get(guild.channels, name = channel_name)
		if existing_channel:
			await interaction.response.send_message(f'A channel named "{channel_name}" already exists. Please delete or rename that channel before using this command.')
		if not existing_channel:
			if channel_name is None:
				channel_name = 'new-channel'
			await guild.create_text_channel(channel_name, category = category)
			channel = discord.utils.get(interaction.guild.channels , name = channel_name)
			await interaction.response.send_message(f'Channel <#{channel.id}> was succesfully created')


	# Deletes a channel
	@channel.command(name = 'delete')
	@application_check(manage_channels = True)
	async def delete_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
		if interaction.channel == channel:
			interaction.response.send_message(f"You can't request to delete a channel while you're in it!", ephemeral = True, delete_after = 10)
		else:
			await channel.delete()
			await interaction.response.send_message(f"Channel **{channel.name}** was succesfully deleted")


	# Returns member list as json file
	@server.command(name='memberlist')
	@application_check(administrator=True)
	async def memberlist(self, interaction: discord.Interaction):
		mList: list = [member for member in interaction.guild.members]
		dictionary = {
			"members": [

			]
		}

		for member in mList:
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
			json.dump(dictionary, outfile, indent=1)
			outfile.close()
			await interaction.response.send_message("Check your DMs!", ephemeral = True)
			await interaction.user.send(content="", file=discord.File("memberList.json"))
			os.remove("memberList.json")


	# Gets server banner
	@server.command(name = 'banner')
	async def serverbanner(self, interaction: discord.Interaction):
		guildraw = interaction.guild
		embed = discord.Embed(title = "", color = discord.Colour.random())
		if guildraw.banner is not None:
			server_banner = guildraw.banner
			embed.set_image(url=server_banner)
		else:
			embed.add_field(name = "An error occurred!", value = "This server does not have a banner!")

		await interaction.response.send_message(embed = embed)


	# Gets server image
	@server.command(name = 'icon')
	async def servericon(self, interaction: discord.Interaction):
		guildraw = interaction.guild
		embed = discord.Embed(title="", color=discord.Colour.random())
		if guildraw.icon is None:
			embed.add_field(name="An error occurred!", value="This server does not have an icon!")
		else:
			server_icon = guildraw.icon
			embed.set_image(url = server_icon)

		await interaction.response.send_message(embed = embed)


	# Assigns role to member
	@roleGroup.command(name = 'assign')
	@application_check(manage_roles = True)
	async def assign_role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
		await member.add_roles(role)
		await interaction.response.send_message(f'The role **<@&{role.id}>** has been assigned to <@{member.id}>', silent = True)


	# Unassigns role from member
	@roleGroup.command(name = "unassign")
	@application_check(manage_roles = True)
	async def unassign_role(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
		await member.remove_roles(role)
		await interaction.response.send_message(f'The role **<@&{role.id}>** has been removed from <@{member.id}>', silent = True)


	@app_commands.command(name = 'dev')
	async def dev(self, interaction: discord.Interaction):
		await interaction.response.send_message('https://milkyicedtea.epizy.com')


	# Patch command
	@app_commands.command(name = 'patchnotes')
	async def patch(self, interaction: discord.Interaction):
		await interaction.response.send_message('https://github.com/milkyicedtea/IgnoBot.py/commits/main')


	# Creates role
	@roleGroup.command(name = 'create')
	@application_check(manage_roles = True)
	async def create_role(self, interaction: discord.Interaction, role_name: str, role_color: str = None):
		print('here1')
		color = discord.Colour.random() if role_color is None else discord.Colour.from_str(role_color)
		print('here2')
		await interaction.guild.create_role(name = role_name, color = color, reason = f'Create from command. Issued by: {interaction.user}')
		await interaction.response.send_message(f'The role **{role_name}** has been created!')


	# Deletes role
	@roleGroup.command(name = 'delete')
	@commands.has_guild_permissions(manage_roles = True)
	async def delete_role(self, interaction: discord.Interaction, role: discord.Role):
		await role.delete(reason = f'Deleted using ```/delete``` command. Issued by: {interaction.user}')
		await interaction.response.send_message(f'Role **{role.name}** has been deleted')



async def setup(bot):
	await bot.add_cog(Moderation(bot))