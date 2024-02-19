####################
#                  #
#     dbhelper     #
#                  #
####################

import os
import time

import dotenv

import psycopg2
from psycopg2 import pool as Pool

db_url = dotenv.get_key('.env', 'DB_URL')
connection_pool = Pool.ThreadedConnectionPool(minconn = 2, maxconn = 5, dsn = db_url)   # dsn will be passed to connection


class DbHelper:

    def __init__(self):
        self.conn = None
        self.cursor = None

    def open(self):
        try:
            self.conn = connection_pool.getconn()
        except psycopg2.Error as e:
            print(f'Error connecting to the platform (mydb): {e}')

        # getting the cursor
        try:
            self.cursor = self.conn.cursor()
        except psycopg2.Error as c:
            print(f'Error connecting to the platform (cursor): {c}')
        return self.conn

    def close(self):
        try:
            self.cursor.close()
            connection_pool.putconn(self.conn)
        except psycopg2.Error as ce:
            print(f'Error while closing the connection: {ce}')

    def commit(self):
        try:
            self.conn.commit()
        except psycopg2.Error as ce:
            print(f'Error committing changes: {ce}')

    def get_cursor(self):
        return self.cursor

    def __enter__(self):
        # print('entering connection..')
        # print(time.time())
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # print('exiting connection..')
        # print(time.time())
        self.close()
