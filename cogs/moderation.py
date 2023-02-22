######################
#                    #
#     Moderation     #
#                    #
######################

import os

import discord
from discord.ext import commands

from utils.dbhelper import DbHelper
from utils.dbchecks import DbChecks

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Kick command
    @commands.command(name = 'kick')
    @commands.has_guild_permissions(kick_members = True)
    async def kick(self, ctx, member:discord.Member, *, reason = None):
        await member.kick(reason = reason)
        await ctx.send(f'User {member.mention} has been kicked from the server.\nResponsible mod: **{ctx.author}**\nReason: {reason}')

    # Ban command
    @commands.command(name = 'ban')
    @commands.has_guild_permissions(ban_members = True)
    async def ban(self, ctx, member:discord.Member, *, reason = None):
        await member.ban(reason = reason)
        await ctx.send(f'User {member.mention} has been banned from the server.\nResponsible mod: **{ctx.author}**\nReason: {reason}')

    # Unban command
    @commands.command(name = 'unban')
    @commands.has_guild_permissions(ban_members = True)
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
    @commands.command(name = 'purge')
    @commands.has_guild_permissions(manage_messages = True)
    async def purge_messages(self, ctx, amount_to_delete: int = 0):
        if amount_to_delete < 1 or amount_to_delete > 100:
            await ctx.send('You need to enter a value between 1 and 100')
        else:
            await ctx.channel.purge(limit = amount_to_delete + 1)

    # Creating a new channel
    @commands.command(name = 'create_channel')
    @commands.has_guild_permissions(manage_channels = True)
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
    @commands.command(name = 'joindate')
    async def join_date(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.message.author
        joined_at = member.joined_at
        await ctx.send(f'{member.mention} joined on {joined_at}.')

    # Avatar command
    @commands.command(name = 'avatar')
    async def avatar(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.message.author

        avatar_url = member.avatar
        embedVar = discord.Embed(title = f"{member}'s profile image", color = discord.Colour.random())
        embedVar.set_image(url = avatar_url)

        await ctx.send(embed = embedVar)

    # Server image command
    @commands.command(name = 'servericon')
    async def servericon(self, ctx):
        guildraw = ctx.guild
        guildname = guildraw.name.replace("'", "")
        server_icon = guildraw.icon
        embedVar = discord.Embed(title = guildname, color = discord.Colour.random())
        embedVar.set_image(url = server_icon)

        await ctx.send(embed = embedVar)

    # Patch command
    @commands.command(name = 'patchnotes')
    async def patch(self, ctx):
        url = 'https://github.com/milkyicedtea/IgnoBot.py/commits/main'
        await ctx.send(url)

    @commands.command(name = 'assignrole')
    @commands.has_guild_permissions(manage_roles = True)
    async def giverole(self, ctx, member: discord.Member, *, role_name):
        role = discord.utils.get(ctx.message.guild.roles, name = role_name)
        if role:
            await member.add_roles(role)
            await ctx.send(f'The role **{role_name}** has been assigned to {member._user}')

    @commands.command(name = 'dev')
    async def dev(self, ctx):
        links: list = []
        dev_site: str = 'https://milkyicedtea.epizy.com'
        github_link: str = 'https://github.com/milkyicedtea'
        bot_repository: str = 'https://github.com/milkyicedtea/IgnoBot.py'
        twitch_link: str = 'https://twitch.tv/'
        links.append(dev_site)
        links.append(github_link)
        links.append(bot_repository)
        links.append(twitch_link)
        print(links)
        for x in range(len(links)):
            await ctx.send(links[x])

    @commands.command(name = 'memberlist')
    @commands.is_owner()
    async def memberlist(self, ctx):
        #print(ctx.guild.members)
        for member in ctx.guild.members:
            #print(member.name)
            print((member.name + member.discriminator))
            if (member.name + '#' + member.discriminator) == 'ignorance#1928':
                print(member.roles[1].name)
                print(type(member.roles[1]))
                if member.roles[1].name == 'GOD':
                    print('igor god')

    @commands.command(name = 'createrole')
    @commands.has_guild_permissions(manage_roles = True)
    async def create_role(self, ctx, role_color:str, *, role_name: str):
        print(discord.Colour.from_str(f'#{role_color}'))
        color = discord.Colour.from_str(f'#{role_color}')
        await ctx.guild.create_role(name = role_name, color = color)
        await ctx.reply(f'The role **{role_name}** has been created!')

    @commands.command(name = 'deleterole')
    @commands.has_guild_permissions(manage_roles = True)
    async def delete_role(self, ctx, *, role_name: str):
        role = discord.utils.get(ctx.guild, name = role_name)
        print(ctx.message.author)
        await role.delete(reason = f'Delete from command. Issued by: {ctx.message.author}')
            
    @commands.command(name = 'addlogs')
    async def addLogs(self, ctx, channel_id):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        guildid = ctx.guild.id
        guildraw = ctx.guild.name
        guildname = guildraw.replace("'", "")
        userid = ctx.author.id
        usernameraw = ctx.author.name
        username = usernameraw.replace("'", "")

        DbChecks.guildCheck(cursor, mydb, guildid, guildname)

        channel_id = int(channel_id.replace("<", "").replace(">", "").replace("#", ""))
        channel = self.bot.get_channel(channel_id)

        cursor.execute(f"update guildsettings set wantslogs = 'true' where guildid = {guildid}")
        cursor.execute(f"update guildsettings set logchannel = {channel_id} where guildid = {guildid}")
        mydb.commit()
        await ctx.send(f"Your logs channel was updated to <#{channel_id}>.")
        await channel.send(f"This is the start of your logs.")
        dbhelper.close()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        dbhelper = DbHelper()
        mydb = dbhelper.open()
        cursor = dbhelper.get_cursor()

        DbChecks.guildCheck(cursor, mydb, guildid = message.guild.id, guildname = message.guild.name)

        has_logs = DbChecks.checkGuildLogs(cursor, mydb, guildid = message.guild.id)
        if has_logs[0] is True:
            channel_id = int(str(has_logs[1]).replace("(", "").replace(")", "").replace(",", ""))
            channel = self.bot.get_channel(channel_id)

            embed = discord.Embed(color = discord.Colour.random())
            embed.set_author(name = f"Message deleted from\n<@&{message.author.id}>:", icon_url = message.author.avatar)
            embed.add_field(name = '', value = message.clean_content, inline = False)
            await channel.send(embed = embed)
        dbhelper.close()

        # {message.author.display_name}#{message.author.discriminator}

async def setup(bot):
    await bot.add_cog(Moderation(bot))