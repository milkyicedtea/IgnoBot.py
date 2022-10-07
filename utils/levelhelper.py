#######################
#                     #
#     levelhelper     #
#                     #
#######################

import os

import discord

import random

from utils.dbhelper import DbHelper

class LevelHelper():
    def __init__(self):
        self.mydb = DbHelper.open()
        self.cursor = DbHelper.get_cursor()

    async def guild_check(self, message):

        print('guild check')

        guildid = message.guild.id
        guildraw = message.guild.name
        guildname = guildraw.replace("'", "")
        userid = message.author.id
        usernameraw = message.author.name
        username = usernameraw.replace("'", "")

        self.cursor.execute(f"select count(*) from guildinfo where guildid = {guildid} and guildname = '{guildname}';")  #check for both parameters
        result = self.cursor.fetchone()
        if result[0] == 0:  #id / name not found
            self.cursor.execute(f"select count(*) from guildinfo where guildid = {guildid};")    #id is always the same so check that
            result = self.cursor.fetchone()
            if result[0] == 0:  #id not found, guild is not registered
                self.cursor.execute(f"insert into guildinfo(guildid, guildname) values({guildid}, '{guildname}');")  #register with name and id
                self.mydb.commit()
                print(f'Added new guild ({guildid}) with name: {guildname}.')

            elif result[0] != 0:    #id is there so the name has to be updated
                self.cursor.execute(f"update guildinfo set guildname = '{guildname}' where guildid = {guildid};")    #update :D
                self.mydb.commit()
                print(f'Updated guild ({guildid}) with new name: {guildname}.')
        else:
            print(f'There is no need to update the guild {guildname} ({guildid})')

        self.db.close()

    async def user_check(self, message):

        print('user check')

        userid = message.author.id
        usernameraw = message.author.name
        username = usernameraw.replace("'", "")
        guildid = message.guild.id

        self.cursor.execute(f"select count(*) from leveling where userid = {userid} and username = '{username}';")   #check for both parameters
        result = self.cursor.fetchone()
        if result[0] == 0:  #id / name not found
            self.cursor.execute(f'select count(*) from leveling where userid = {userid};')   #id is always the same so check that
            result = self.cursor.fetchone()
            if result[0] == 0:  #id not found, user is not registered
                self.cursor.execute(f"insert into leveling(guildid, userid, username, xpvalue, levelvalue) values({guildid}, {userid}, '{username}', 0, 0);")    #register with name, id, 0 xp, 0 level
                self.mydb.commit()
                print(f'Added new user ({userid}) with name: {username}.')

            elif result != 0:   #id is there so the name has to be updated
                self.cursor.execute(f"update leveling set username = '{username}' where userid = {userid};")     #update :D
                self.mydb.commit()
                print(f'Updated user ({userid}) with new name: {username}.')
        else:
            print(f'There is no need to update the user {usernameraw} ({userid}).')

        self.db.close()

    async def give_xp(self, message):

        print('give xp')

        userid = message.author.id
        usernameraw = message.author.name
        username = usernameraw.replace("'", "")
        guildid = message.guild.id

        xprange = random.choice(range(1, 20+1))
        self.cursor.execute(f'select xpvalue from leveling where userid = {userid} and guildid = {guildid};')            # getting xp
        result = self.cursor.fetchone()
        xpfromdb = result[0]
        xptodb = xpfromdb + xprange
        self.cursor.execute(f'select levelvalue from leveling where guildid = {guildid} and userid = {userid}')          # getting level
        result = self.cursor.fetchone()
        level = result[0]
        if level == 0:
            neededtolvl = 100
        else:
            neededtolvl = level * level * 100           # determines how much xp is needed to level up
        if xpfromdb >= neededtolvl:
            level += 1
        self.cursor.execute(f'update leveling set xpvalue = {xptodb} where guildid = {guildid} and userid = {userid};')
        self.cursor.execute(f'update leveling set levelvalue = {level} where guildid = {guildid} and userid = {userid};')
        self.mydb.commit()

        self.db.close()

    async def give_role(self, message):

        print('give role')

        userid = message.author.id
        usernameraw = message.author.name
        username = usernameraw.replace("'", "")
        guildid = message.guild.id

        user = message.author
        if not user.bot:    # checks if user is bot
            self.cursor.execute(f"select count(*) from roles where guildid = {guildid};")
            result = self.cursor.fetchone()
            if result[0] != 0:
                self.cursor.execute(f"select rolenames from roles where guildid = {guildid};")       #get roles' names
                rolenames = self.cursor.fetchmany(size = result[0])
                self.cursor.execute(f"select reachlevels from roles where guildid = {guildid};")     #get levels needed for every levelup
                reachlevels = self.cursor.fetchmany(size = result[0])
                self.cursor.execute(f"selecet levelvalue from leveling where guildid = {guildid} and userid = {userid}")
                level = self.cursor.fetchone()
                for x in range(result[0]):
                    #print('dum')
                    reachlevel = int(str(reachlevels[x]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                    #print(f'level = {level}, reachlevel = {reachlevel}')
                    if level >= reachlevel:
                        # print('if')
                        index = x-1
                        role = discord.utils.get(message.guild.roles, name = str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                        # print(str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", ""))
                        if role:
                            return True, role
                        else:
                            realrole = str(rolenames[index]).replace("'", "").replace("(", "").replace(")", "").replace(",", "")
                            return False, realrole
            else:
                print('No roles.')
        else:
            print('User is bot.')
        self.db.close()