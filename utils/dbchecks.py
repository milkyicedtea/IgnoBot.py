####################
#                  #
#     dbchecks     #
#                  #
####################

import os

import discord

import discord.utils

import random
import itertools

import psycopg2

from utils.dbhelper import DbHelper


class DbChecks:

    @staticmethod
    def guild_check(cursor, mydb, guild: discord.Guild):
        # print('guild_check')
        # print(guild.name)
        # print(guild.id, guild.name)
        guildname = guild.name.replace("'", "")
        cursor.execute(f"select count(*) from guildinfo where guildid = {guild.id} and guildname = '{guildname}';")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f'select count(*) from guildinfo where guildid = {guild.id};')
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"insert into guildinfo(guildid, guildname) values({guild.id}, '{guildname}');")
                mydb.commit()
                # print(f'guild {guild.id} with name {guild.name} has been added to the database')
            else:
                cursor.execute(f"update guildinfo set guildname = '{guildname}' where guildid = {guild.id};")
                mydb.commit()
                # print(f'updated guild {guild.id} with new name: {guild.name}')
        # else:
            # print(f'guild {guildid} with name {guildname} is already in the database')

    @staticmethod
    def settings_check(cursor, mydb, guild: discord.Guild):
        cursor.execute(f"select count(*) from guildsettings where guildid = {guild.id};")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"insert into guildsettings(guildid) values({guild.id});")
            mydb.commit()
            # print(f'guild {guildid} has been added to the database')
        # else:
            # print(f'guild {guildid} is already in the database')

    @staticmethod
    def user_check(cursor, mydb, guild: discord.Guild, user: discord.User):
        # print('user_check')
        if not user.bot and not user.system:
            username = user.name.replace("_", "")
            cursor.execute(f"select count(*) from leveling where guildid = {guild.id} "
                           f"and userid = {user.id} "
                           f"and username = '{username}'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"select count(*) from leveling where guildid = {guild.id} "
                               f"and userid = {user.id}")
                if cursor.fetchone()[0] == 0:
                    try:
                        # print(user.id, username, guild.id)
                        cursor.execute(f"insert into leveling(userid, username, guildid) "
                                       f"values({user.id}, '{username}', {guild.id});")
                        mydb.commit()
                    except psycopg2.Error as err:
                        print(err)
                    # print(f'user {user.mention} has been added to the database')
                else:
                    try:
                        cursor.execute(f"update leveling set username = '{username}' "
                                       f"where userid = {user.id};")
                        mydb.commit()
                    except psycopg2.Error as err:
                        print(err)
                    # print(f'updated user {user.mention} with new name: {user.name}')
            # else:
                # print(f'user {userid} with name {username} is already in the database')

    @staticmethod
    def check_guild_logs(cursor, guild: discord.Guild) -> bool:
        cursor.execute(f"select wantslogs from guildsettings where guildid = {guild.id}")
        # print(f'wantslogs = {wantslogs}')
        if cursor.fetchone()[0]:
            return True
        else:
            return False

    @staticmethod
    def get_log_channel(cursor, guild: discord.Guild) -> discord.TextChannel:
        cursor.execute(f"select logchannel from guildsettings where guildid = {guild.id}")
        logchannel = discord.utils.get(guild.text_channels, id = cursor.fetchone()[0])
        return logchannel

    @staticmethod
    def give_xp(cursor, mydb, guild: discord.Guild, user: discord.User):
        DbChecks.guild_check(cursor, mydb, guild)

        DbChecks.settings_check(cursor, mydb, guild)

        DbChecks.user_check(cursor, mydb, guild, user)
        # print('give_xp')
        if not user.bot:
            cursor.execute(f"select xpvalue from leveling where userid = {user.id} "
                           f"and guildid = {guild.id};")            # getting xp
            result = cursor.fetchone()
            newxp = random.choice(range(1, 20+1)) + result[0]
            # print(f'xpfromdb is {result[0]}')
            # print(f'xptodb is {newxp}')
            cursor.execute(f"select levelvalue from leveling where guildid = {guild.id} "
                           f"and userid = {user.id}")          # getting level
            result = cursor.fetchone()
            level = result[0]
            if level == 0:
                neededtolvl = 100
            else:
                neededtolvl = level * level * 100           # determines how much xp is needed to level up
            if newxp >= neededtolvl:
                level += 1
            cursor.execute(f"update leveling set xpvalue = {newxp} "
                           f"where guildid = {guild.id} "
                           f"and userid = {user.id};")
            cursor.execute(f"update leveling set levelvalue = {level} "
                           f"where guildid = {guild.id} "
                           f"and userid = {user.id};")
            mydb.commit()

    @staticmethod
    async def role_on_message(cursor, guild: discord.Guild, user: discord.User, message: discord.Message):
        if not user.bot:    # checks if user is bot
            guildname = guild.name.replace("'", "")
            cursor.execute(f"select rolenames from roles where guildid = {guild.id} "
                           f"and guildname = '{guildname}' "
                           f"and is_selfrole = 'false';")
            role_list_db = list(itertools.chain(*cursor.fetchall()))

            cursor.execute(f"select reachlevels from roles where guildid = {guild.id} "
                           f"and guildname = '{guildname}' "
                           f"and is_selfrole = 'false';")
            reachlevels = list(itertools.chain(*cursor.fetchall()))

            role_list = [discord.utils.get(guild.roles, name = role) for role in role_list_db]

            for role, level in zip(role_list, reachlevels):
                cursor.execute(f"select levelvalue from leveling where guildid = {guild.id} "
                               f"and userid = {user.id}")
                if cursor.fetchone()[0] >= level:
                    try:
                        await message.author.add_roles(role)
                    except Exception as err:
                        print(err)
                        await message.channel.send(f"There was an error while assigning the role **{role.name}**. To {user.mention}"
                                                   f"Please report this to our discord.")
