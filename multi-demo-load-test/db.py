import logging
import sqlite3
from sqlite3 import Connection

import config

db_connection: Connection = sqlite3.connect(config.database)
db_connection.row_factory = sqlite3.Row

def init():
    c = db_connection.cursor()
    c.execute("DROP TABLE IF EXISTS wallets;")
    db_connection.commit()
    c = db_connection.cursor()
    c.execute(
        """create table wallets(
        id integer primary key autoincrement,
        wallet_id text,
        wallet_key text,
        wallet_name text,
        token text
        )
        """
    )
    db_connection.commit()


def add(tenant):
    c = db_connection.cursor()
    res = c.execute(
        f"insert into wallets ('wallet_id', 'wallet_key', 'wallet_name', 'token') values ('{tenant.wallet_id}', '{tenant.wallet_key}', '{tenant.wallet_name}', '{tenant.token}')"
    )
    row_id = res.lastrowid
    db_connection.commit()
    return row_id


def fetchall():
    c = db_connection.cursor()
    c.execute("select * from wallets")
    results = c.fetchall()
    logging.info(f"number of wallets = {len(results)}")


def fetch_previous(row_id: int):
    logging.debug(f"> fetch_previous({row_id})")
    # we want to find the preceding wallet...
    # if we are first, we actually want the last one...
    prev_row_id = row_id - 1 if row_id > 1 else config.user_limit
    c = db_connection.cursor()
    c.execute("SELECT * FROM wallets WHERE id=?", (prev_row_id,))
    row = c.fetchone()
    # row could be none if the user_limit hasn't been created yet
    logging.debug(f"< fetch_previous({row_id}, {prev_row_id}) = {row}")
    return row


def close():
    db_connection.close()
