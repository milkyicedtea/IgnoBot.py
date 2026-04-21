####################
#                  #
#     dbhelper     #
#                  #
####################

import dotenv

import psycopg
from dotenv import get_key
from psycopg_pool import pool_async
from redis.asyncio import Redis, ConnectionPool as DragonflyPool

from Utils.logger import logger


class PgDB:
    pool: pool_async.AsyncConnectionPool | None = None

    def __init__(self):
        self.conn: psycopg.AsyncConnection | None = None
        self.cursor: psycopg.AsyncCursor | None = None

    async def open(self):
        if PgDB.pool is None:
            db_url = dotenv.get_key('.env', 'DATABASE_URL')
            PgDB.pool = pool_async.AsyncConnectionPool(
                min_size=2,
                max_size=5,
                conninfo=db_url,
                open=False
            )
            await PgDB.pool.open()
            logger.info('Postgres pool successfully created.')
        try:
            self.conn = await self.pool.getconn()
            logger.debug(f'Postgres connection successfully created: {self.conn}')
        except psycopg.Error as e:
            logger.error(f'Error connecting to the platform (mydb): {e}')

        # getting the cursor
        try:
            self.cursor = self.conn.cursor()
        except psycopg.Error as c:
            logger.error(f'Error connecting to the platform (cursor): {c}')
        return self.conn

    async def close(self):
        try:
            if self.conn and not self.conn.closed:
                if self.conn.info.transaction_status != psycopg.pq.TransactionStatus.IDLE:
                    await self.rollback()
            if self.cursor:
                await self.cursor.close()
            if self.conn:
                await self.pool.putconn(self.conn)
        except psycopg.Error as ce:
            print(f'Error while closing the connection: {ce}')

    async def commit(self):
        try:
            await self.conn.commit()
        except psycopg.Error as ce:
            print(f'Error committing changes: {ce}')

    async def rollback(self):
        try:
            await self.conn.rollback()
        except psycopg.Error as ce:
            print(f'Error rolling back changes: {ce}')

    async def get_cursor(self):
        return self.cursor

    async def fetchone_to_dict(self):
        row = await self.cursor.fetchone()
        if row is None:
            return None
        colnames = [desc[0] for desc in self.cursor.description]
        return dict(zip(colnames, row))

    async def fetchall_to_dict(self):
        rows = await self.cursor.fetchall()
        colnames = [desc[0] for desc in self.cursor.description]
        return [dict(zip(colnames, row)) for row in rows]

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


logger.info('Creating connection pool for redis..')
print("REDIS_PORT: ", get_key('.env', 'REDIS_PORT'))
redis_pool = DragonflyPool(
    host=get_key('.env', 'REDIS_HOST'),
    port=get_key('.env', 'REDIS_PORT'),
    password=get_key('.env', 'REDIS_PASSWORD'),
    decode_responses=True,
    protocol=3
)
logger.info('Redis async pool successfully created.')


class DfDB(Redis):
    def __init__(self):
        super().__init__(connection_pool=redis_pool)
