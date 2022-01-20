######################
#                    #
#     Moderation     #
#                    #
######################

import os

import discord
from discord import channel
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Kick command
    @commands.command(name = 'kick', help = 'Kicks a user from the server')
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member:discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'User {member.mention} has been kicked from the server.\nResponsible mod: **{ctx.author}**\nReason: {reason}')

    # Ban command
    @commands.command(name = 'ban', help = 'Bans a member.')
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member:discord.Member, *, reason=None):
        await member.ban(reason=reason)
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
    async def purge(self, ctx, amount_to_delete):
        if amount_to_delete == 0 or amount_to_delete == None:
            await ctx.send('You must enter an amount of messages to purge equal to 1 or more')
        else:
            await ctx.channel.purge(limit = amount_to_delete + 1)

    # Creating a new channel
    @commands.command(name = 'create-channel', help = 'Creates a new channel.')
    @commands.has_permissions(manage_channels = True)
    async def create_channel(self, ctx, channel_name = None):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name = channel_name)
        if existing_channel:
            print(f'Channel already exists')
            await ctx.send(f'A channel named "{channel_name}" already exists. Please delete or rename that channel before using this command.')
        if not existing_channel:
            if channel_name != None:
                print(f'Creating a new channel: {channel_name}')
                await guild.create_text_channel(channel_name)
                await ctx.send(f'Created a channel named {channel_name}')
            else:
                print(f'Creating a new channel: {channel_name}.')
                await guild.create_text_channel(channel_name)
                await ctx.send(f'Created a channel named {channel_name}')

    # Join date command
    @commands.command(name = 'joindate', help = 'Shows the date when a member joined.')
    async def joindate(self, ctx, member = None):
        if member != None:
            await ctx.send(f'{member.mention} joined on {member.joined_at}')
        else: member = ctx.message.author
        await ctx.send(f'{member.mention} joined on {member.joined_at}.')

    # Patch command
    @commands.command(name = 'patchnotes', help = 'Shows the most recent patch')
    async def patch(self, ctx):
        url = 'https://github.com/ignorance-uwu/IgnoBot.py/commits/main'
        await ctx.send(url)



def setup(bot):
    bot.add_cog(Moderation(bot))