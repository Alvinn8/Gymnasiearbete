import sqlite3
from my_server import app

def create_connection(db_file = app.config["DB_PATH"]):
    # In case of error here, propogate it to the caller and cause an internal server error
    return sqlite3.connect(db_file)

def db_fetch(sql, data, fetchFunc):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(sql, data)
    ret = fetchFunc(cur)
    conn.close()
    return ret

def db_fetch_all(sql, data):
    return db_fetch(sql, data, lambda cur: cur.fetchall())

def db_fetch_one(sql, data):
    return db_fetch(sql, data, lambda cur: cur.fetchone())