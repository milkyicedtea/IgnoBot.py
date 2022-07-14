######################
#                    #
#     Moderation     #
#                    #
######################

import os

import discord
from discord.ext import commands
import re

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Kick command
    @commands.command(name = 'kick', help = 'Kicks a user from the server')
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member:discord.Member, *, reason = None):
        await member.kick(reason = reason)
        await ctx.send(f'User {member.mention} has been kicked from the server.\nResponsible mod: **{ctx.author}**\nReason: {reason}')

    # Ban command
    @commands.command(name = 'ban', help = 'Bans a member.')
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member:discord.Member, *, reason = None):
        await member.ban(reason = reason)
        await ctx.send(f'User {member.mention} has been banned from the server.\nResponsible mod: **{ctx.author}**\nReason: {reason}')

    # Unban command
    @commands.command(name = 'unban', help = 'Unbans a previously banned member.')
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx,* , member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return

    # Purge command
    @commands.command(name = 'purge', help = 'Deletes multiple messages.')
    @commands.has_permissions(manage_messages = True)
    async def purge_messages(self, ctx, amount_to_delete: int = 0):
        if amount_to_delete < 1 or amount_to_delete > 100:
            await ctx.send('You need to enter a value between 1 and 100')
        else:
            await ctx.channel.purge(limit = amount_to_delete + 1)

    # Creating a new channel
    @commands.command(name = 'create-channel', help = 'Creates a new channel.')
    @commands.has_permissions(manage_channels = True)
    async def create_channel(self, ctx, channel_name = None):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name = channel_name)
        if existing_channel:
            await ctx.send(f'A channel named "{channel_name}" already exists. Please delete or rename that channel before using this command.')
        if not existing_channel:
            if channel_name != None:
                channel_name = 'new-channel'
                await guild.create_text_channel(channel_name)
                await ctx.send(f'Created a channel named {channel_name}')
            else:
                await guild.create_text_channel(channel_name)
                await ctx.send(f'Created a channel named {channel_name}')

    # Join date command
    @commands.command(name = 'joindate', help = 'Shows the date when a member joined.')
    async def join_date(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.message.author
        joined_at = member.joined_at
        await ctx.send(f'{member.mention} joined on {joined_at}.')

    # Avatar command
    @commands.command(name = 'avatar', help = 'Gets you the avatar of a user')
    async def avatar(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.message.author

        avatar_url = member.avatar_url
        embedVar = discord.Embed(title = f"{member}'s profile image", color = discord.Colour.random())
        embedVar.set_image(url = avatar_url)

        await ctx.send(embed = embedVar)

    # Server image command
    @commands.command(name = 'servericon', help = 'Gets you the icon of the server')
    async def servericon(self, ctx):
        guildraw = ctx.guild
        guildname = guildraw.name.replace("'", "")
        server_icon = guildraw.icon_url
        embedVar = discord.Embed(title = guildname, color = discord.Colour.random())
        embedVar.set_image(url = server_icon)

        await ctx.send(embed = embedVar)

    # Patch command
    @commands.command(name = 'patchnotes', help = 'Shows the most recent patch')
    async def patch(self, ctx):
        url = 'https://github.com/ignorance-uwu/IgnoBot.py/commits/main'
        await ctx.send(url)

    @commands.command(name = 'assignrole')
    @commands.has_permissions(manage_roles = True)
    async def giverole(self, ctx, member: discord.Member, *, role_name):
        role = discord.utils.get(ctx.message.guild.roles, name = role_name)
        if role:
            await member.add_roles(role)
            await ctx.send(f'The role **{role_name}** has been assigned to {member._user}')


def setup(bot):
    bot.add_cog(Moderation(bot))