####################
#                  #
#     dbhelper     #
#                  #
####################

import os

import discord

import discord.utils
import psycopg2

import random
import itertools

from utils.dbhelper import DbHelper


class DbChecks:


    @staticmethod
    def guildCheck(cursor, mydb, guild: discord.Guild):
        print('guildCheck')
        cursor.execute(f"select count(*) from guildinfo where guildid = {guild.id} "
                       f"and guildname = '{guild.name}';")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f'select count(*) from guildinfo where guildid = {guild.id};')
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"insert into guildinfo(guildid, guildname) "
                               f"values({guild.id}, '{guild.name}');")
                mydb.commit()
                # print(f'guild {guild.id} with name {guild.name} has been added to the database')
            else:
                cursor.execute(f"update guildinfo set guildname = '{guild.name}'"
                               f" where guildid = {guild.id};")
                mydb.commit()
                # print(f'updated guild {guild.id} with new name: {guild.name}')
        # else:
            # print(f'guild {guildid} with name {guildname} is already in the database')


    @staticmethod
    def settingsCheck(cursor, mydb, guild: discord.Guild):
        print('settingsCheck')
        cursor.execute(f"select count(*) from guildsettings where guildid = {guild.id};")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"insert into guildsettings(guildid) values({guild.id});")
            mydb.commit()
            # print(f'guild {guildid} has been added to the database')
        # else:
            # print(f'guild {guildid} is already in the database')


    @staticmethod
    def userCheck(cursor, mydb, guild: discord.Guild, user: discord.User):
        # print('userCheck')
        if not user.bot:
            cursor.execute(f"select count(*) from leveling where guildid = {guild.id} "
                           f"and userid = {user.id} "
                           f"and username = '{user.name}'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"select count(*) from leveling where guildid = {guild.id} "
                               f"and userid = {user.id}")
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"insert into leveling(userid, username, guildid, guildname) "
                                   f"values({user.id}, '{user.name}', {guild.id}, '{guild.name}');")
                    mydb.commit()
                    # print(f'user {user.mention} has been added to the database')
                else:
                    cursor.execute(f"update leveling set username = '{user.name}' "
                                   f"where userid = {user.id};")
                    mydb.commit()
                    # print(f'updated user {user.mention} with new name: {user.name}')
            # else:
                # print(f'user {userid} with name {username} is already in the database')


    @staticmethod
    def checkGuildLogs(cursor, guild: discord.Guild) -> bool:
        cursor.execute(f"select wantslogs from guildsettings where guildid = {guild.id}")
        # print(f'wantslogs = {wantslogs}')
        if cursor.fetchone()[0]:
            return True
        else:
            return False


    @staticmethod
    def checkLogChannel(cursor, guild: discord.Guild) -> discord.TextChannel:
        cursor.execute(f"select logchannel from guildsettings where guildid = {guild.id}")
        logchannel = discord.utils.get(guild.text_channels, id = cursor.fetchone()[0])
        return logchannel


    @staticmethod
    def giveXp(cursor, mydb, guild: discord.Guild, user: discord.User):
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
    async def roleOnMessage(cursor, guild: discord.Guild, user: discord.User, message: discord.Message):
        if not user.bot:    # checks if user is bot
            cursor.execute(f"select rolenames from roles where guildid = {guild.id} "
                           f"and guildname = '{guild.name}';")
            roleListDb = list(itertools.chain(*cursor.fetchall()))

            cursor.execute(f"select reachlevels from roles where guildid = {guild.id} "
                           f"and guildname = '{guild.name}';")
            reachlevels = list(itertools.chain(*cursor.fetchall()))

            roleList: list[discord.Role]
            for role in roleListDb:
                roleList.append(discord.utils.get(guild.roles, name = roleListDb[role]))

            for roles, levels in rolenames, reachlevels:
                role =
                reachlevel = int(str(reachlevels[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                # print(f'level = {level}, reachlevel = {reachlevel}')
                cursor.execute(f"select levelvalue from leveling where guildid = {guild.id} "
                               f"and userid = {user.id}")
                result = cursor.fetchone()
                if result[0] >= reachlevel:
                    # print('if')
                    index = x-1
                    role = discord.utils.get(message.guild.roles, name = str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                    # print(str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                    # print(role)
                    if role:
                        await message.author.add_roles(role)
                    else:
                        realrole = str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")
                        await message.channel.send(f"There was an error while assigning the role **{realrole}**. Please report this to our discord.")