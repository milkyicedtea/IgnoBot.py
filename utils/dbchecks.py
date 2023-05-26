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

from utils.dbhelper import DbHelper


class DbChecks:


    @staticmethod
    def guildCheck(cursor, mydb, guildid, guildname):
        print('guildCheck')
        cursor.execute(f"select count(*) from guildinfo where guildid = {guildid} and guildname = '{guildname}';")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f'select count(*) from guildinfo where guildid = {guildid};')
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"insert into guildinfo(guildid, guildname) values({guildid}, '{guildname}');")
                mydb.commit()
                print(f'guild {guildid} with name {guildname} has been added to the database')
            else:
                cursor.execute(f"update guildinfo set guildname = '{guildname}' where guildid = {guildid};")
                mydb.commit()
                print(f'updated guild {guildid} with new name: {guildname}')
        #else:
            #print(f'guild {guildid} with name {guildname} is already in the database')


    @staticmethod
    def settingsCheck(cursor, mydb, guildid):
        print('settingsCheck')
        cursor.execute(f"select count(*) from guildsettings where guildid = {guildid};")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f"insert into guildsettings(guildid) values({guildid});")
            mydb.commit()
            #print(f'guild {guildid} has been added to the database')
        #else:
            #print(f'guild {guildid} is already in the database')


    @staticmethod
    def userCheck(cursor, mydb, guildid, guildname, username, userid, user):
        print('userCheck')
        if not user.bot:
            cursor.execute(f"select count(*) from leveling where guildid = {guildid} and userid = {userid} and username = '{username}'")
            if cursor.fetchone()[0] == 0:
                cursor.execute(f"select count(*) from leveling where guildid = {guildid} and userid = {userid}")
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"insert into leveling(userid, username, guildid, guildname) values({userid}, '{username}', {guildid}, '{guildname}');")
                    mydb.commit()
                    print(f'user {userid} with name {username} has been added to the database')
                else:
                    cursor.execute(f"update leveling set username = '{username}' where userid = {userid};")
                    mydb.commit()
                    print(f'updated user {userid} with new name: {username}')
            # else:
            #     print(f'user {userid} with name {username} is already in the database')


    @staticmethod
    def checkGuildLogs(cursor, mydb, guildid):
        cursor.execute(f"select wantslogs from guildsettings where guildid = {guildid}")
        wantslogs = cursor.fetchone()
        # print(f'wantslogs = {wantslogs}')
        if wantslogs:
            return True
        else:
            return False


    @staticmethod
    def checkLogChannel(cursor, mydb, guildid):
        cursor.execute(f"select logchannel from guildsettings where guildid = {guildid}")
        channel_id = cursor.fetchone()
        return channel_id


    @staticmethod
    def giveXp(cursor, mydb, guildid, guildname, username, userid, user):
        if not user.bot:
            cursor.execute(f"select xpvalue from leveling where userid = {userid} and guildid = {guildid};")            # getting xp
            result = cursor.fetchone()
            newxp = random.choice(range(1, 20+1)) + result[0]
            # print(f'xpfromdb is {result[0]}')
            # print(f'xptodb is {newxp}')
            cursor.execute(f"select levelvalue from leveling where guildid = {guildid} and userid = {userid}")          # getting level
            result = cursor.fetchone()
            level = result[0]
            if level == 0:
                neededtolvl = 100
            else:
                neededtolvl = level * level * 100           # determines how much xp is needed to level up
            if newxp >= neededtolvl:
                level += 1
            cursor.execute(f"update leveling set xpvalue = {newxp} where guildid = {guildid} and userid = {userid};")
            cursor.execute(f"update leveling set levelvalue = {level} where guildid = {guildid} and userid = {userid};")
            mydb.commit()
        else:
            return
            #print(f'this user is a bot')


    @staticmethod
    async def roleOnMessage(cursor, mydb, guildid, guildname, username, userid, user, message):
        if not user.bot:    # checks if user is bot
            cursor.execute(f"select count(*) from roles where guildid = {guildid} and guildname = '{guildname}';")
            result = cursor.fetchone()
            if result[0] > 0:
                cursor.execute(f"select rolenames from roles where guildid = {guildid} and guildname = '{guildname}';")
                rolenames = cursor.fetchmany(size = result[0])
                cursor.execute(f"select reachlevels from roles where guildid = {guildid} and guildname = '{guildname}';")
                reachlevels = cursor.fetchmany(size = result[0])
                for x in range(result[0]):
                    #print('dum')
                    reachlevel = int(str(reachlevels[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                    #print(f'level = {level}, reachlevel = {reachlevel}')
                    cursor.execute(f"select levelvalue from leveling where guildid = {guildid} and userid = {userid}")
                    result = cursor.fetchone()
                    if result[0] >= reachlevel:
                        #print('if')
                        index = x-1
                        role = discord.utils.get(message.guild.roles, name = str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                        #print(str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                        #print(role)
                        if role:
                            await message.author.add_roles(role)
                        else:
                            realrole = str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")
                            await message.channel.send(f"There was an error while assigning the role **{realrole}**. Please report this to our discord.")
            # else:
                # print('no roles')
        #else:
            #print('no levels and roles for bots!')