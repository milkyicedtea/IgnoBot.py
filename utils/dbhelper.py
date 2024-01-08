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
        self.mydb = None
        self.cursor = None

    def open(self):
        try:
            self.mydb = psycopg2.connect(dotenv.get_key('.env', 'DB_URL'))
        except psycopg2.Error as e:
            print(f'Error connecting to the platform (mydb): {e}')

        # getting the cursor
        try:
            self.cursor = self.mydb.cursor()
        except psycopg2.Error as c:
            print(f'Error connecting to the platform (cursor): {c}')
        return self.mydb

    def close(self):
        try:
            self.cursor.close()
            self.mydb.close()
        except psycopg2.Error as ce:
            print(f'Error while closing the connection: {ce}')

    def get_cursor(self):
        return self.cursor
