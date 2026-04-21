####################
#                  #
#     dbchecks     #
#                  #
####################

import discord

import discord.utils

import random

import psycopg

from Utils.database.database import PgDB


class DbChecks:

    @staticmethod
    async def guild_check(db: PgDB, guild: discord.Guild):
        # print('guild_check')
        cursor = await db.get_cursor()

        guild_name = guild.name.replace("'", "")
        await cursor.execute("""
            insert into guild_info(guild_id, guild_name)
            values(%s, %s)
            on conflict (guild_id)
            do update set guild_name = EXCLUDED.guild_name
        """, (guild.id, guild_name))
        await db.commit()

    @staticmethod
    async def settings_check(db: PgDB, guild: discord.Guild):
        # print('settings check')
        cursor = await db.get_cursor()

        await cursor.execute("""
            insert into guild_settings(guild_id)
            values(%s)
            on conflict(guild_id) do nothing
        """, (guild.id,))
        await db.commit()

    @staticmethod
    async def user_check(db: PgDB, guild: discord.Guild, user: discord.User):
        # print('user_check')
        cursor = await db.get_cursor()

        if not user.bot and not user.system:
            await cursor.execute("""
                insert into users(user_id, username)
                values(%s, %s)
                on conflict(user_id) do update set username = %s
            """, (user.id, user.name, user.name))

            await cursor.execute("""
                insert into leveling(user_id, guild_id)
                values(%s, %s)
                on conflict(user_id, guild_id) do nothing
            """, (user.id, guild.id))

            await db.commit()

    @staticmethod
    async def check_guild_logs(cursor: psycopg.AsyncCursor, guild: discord.Guild) -> bool:
        await cursor.execute(
            "select wantslogs from guild_settings where guild_id = %s",
            (guild.id,)
        )
        # print(f'wants_logs = {wants_logs}')
        wants_logs = (await cursor.fetchone())[0]
        print(wants_logs)
        return wants_logs

    @staticmethod
    async def get_log_channel(cursor: psycopg.AsyncCursor, guild: discord.Guild) -> discord.TextChannel:
        await cursor.execute(
            "select log_channel from guild_settings where guild_id = %s",
            (guild.id,)
        )
        log_channel = discord.utils.get(guild.text_channels, id = (await cursor.fetchone())[0])
        return log_channel

    @staticmethod
    async def give_xp(db: PgDB, guild: discord.Guild, user: discord.User):
        await DbChecks.guild_check(db, guild)

        await DbChecks.settings_check(db, guild)

        await DbChecks.user_check(db, guild, user)
        # print('give_xp')
        cursor = await db.get_cursor()

        if not user.bot:
            # fetch current XP and level
            await cursor.execute("""
                select xp_value, level_value
                from leveling
                where user_id = %s and guild_id = %s
            """, (user.id, guild.id))
            xp_value, level_value = await cursor.fetchone()

            # add random xp
            new_xp = xp_value + random.choice(range(1, 21))

            # calculate xp needed to level up
            needed_to_level = 100 if level_value == 0 else level_value * level_value * 100

            if new_xp >= needed_to_level:
                level_value += 1

            # update xp and level in the database
            await cursor.execute("""
                update leveling
                set xp_value = %s, level_value = %s
                where guild_id = %s and user_id = %s
            """, (new_xp, level_value, guild.id, user.id))
            await db.commit()

    @staticmethod
    async def role_on_message(cursor: psycopg.AsyncCursor, guild: discord.Guild, user: discord.User, message: discord.Message):
        if not user.bot:    # checks if user is bot
            # fetch role IDs and required levels
            await cursor.execute("""
                select role_id, reach_level
                from roles
                where guild_id = %s and is_selfrole = %s;
            """, (guild.id, False))
            roles_and_levels = await cursor.fetchall()

            # fetch user's current value
            await cursor.execute("""
                select level_value 
                from leveling where guild_id = %s
                and user_id = %s
            """, (guild.id, user.id))
            user_level = (await cursor.fetchone())[0]

            # map roles to levels
            for role_id, required_level in roles_and_levels:
                role = discord.utils.get(guild.roles, id = role_id)

                if user_level >= required_level:
                    try:
                        await message.author.add_roles(role)
                    except Exception as err:
                        print(err)
                        await message.channel.send(
                            f"There was an error while assigning the role **{role.name}** to {user.mention}. "
                            f"Please report this to the admins."
                        )
