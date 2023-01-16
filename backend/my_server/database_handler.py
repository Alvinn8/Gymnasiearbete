import sqlite3
from my_server import app

def create_connection(db_file = app.config["DB_PATH"]):
    # In case of error here, propogate it to the caller and cause an internal server error
    return sqlite3.connect(db_file)