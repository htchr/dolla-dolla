#!/Users/jack/Documents/projects/22-dolla/venv/bin/python3

import sqlite3

money = "/Users/jack/Documents/projects/22-dolla/money.db"

def food_19_22():
    "table for 2019 - 2022 food spending"
    con = sqlite3.connect(money)
    cur = con.cursor()
    with con:
        cur.execute("""CREATE TABLE IF NOT EXISTS food (
                       ID INTEGER PRIMARY KEY,
                       amount REAL NOT NULL,
                       date INT NOT NULL,
                       year INT NOT NULL,
                       month INT NOT NULL,
                       day INT NOT NULL,
                       desc TEXT)""")
    con.close()

def flow_table():
    "table to document money flow"
    con = sqlite3.connect(money)
    cur = con.cursor()
    with con:
        cur.execute("""CREATE TABLE IF NOT EXISTS flow (
                       ID INTEGER PRIMARY KEY,
                       amount REAL NOT NULL,
                       cur TEXT,
                       cc INT,
                       out INT,
                       date INT NOT NULL,
                       year INT NOT NULL,
                       month INT NOT NULL,
                       day INT NOT NULL,
                       cat TEXT NOT NULL,
                       notes TEXT)""")
    con.close()

food_19_22()
flow_table()
