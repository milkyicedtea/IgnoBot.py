####################
#                  #
#     dbhelper     #
#                  #
####################

import os

import dotenv

import psycopg2


class DbHelper:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def open(self):
        try:
            self.conn = psycopg2.connect(dotenv.get_key('.env', 'DB_URL'))
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
            self.conn.close()
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
        print('entering connection..')
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('exiting connection..')
        self.close()
