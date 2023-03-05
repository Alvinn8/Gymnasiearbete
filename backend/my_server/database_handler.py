import sqlite3
from my_server import app


def create_connection(db_file=app.config["DB_PATH"]):
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


"""Convert an array of tuples from the database into an array of json objects.

For example, it is common to fetch data from the database using
    SELECT id, name FROM Table
which yields the following result
    data_array = [(1, "foo"), (2, "bar")]
It is common to want to convert this into JSON to send as an API response. By
passing the result to this function with the following parameters:
    data_json = db_to_json(data_array, ["id", "name"])
returns the following:
    data_json = [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]

"""


def db_to_json(data_array, data_keys):
    result = []
    # Loop trough all the data (all matched rows)
    for row in data_array:
        obj = {}
        # Loop trough all columns
        for i in range(len(row)):
            # Get the value
            data = row[i]
            # And the key to associate with it
            key = data_keys[i]
            # And attach that to the object
            obj[key] = data
        # Append the object
        result.append(obj)

    return result


db_to_json([(1, "foo"), (2, "bar")], ["id", "name"])
