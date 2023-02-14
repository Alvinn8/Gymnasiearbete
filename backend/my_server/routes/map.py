from flask import request
from my_server import app
from my_server.auth import login_required, map_access_required, map_view_access
from my_server.database_handler import create_connection, db_fetch_all


@app.route("/api/map/list")
@login_required
def maps(jwt):

    user_id = jwt["user"]["id"]

    data = db_fetch_all(
        """
        SELECT id, name FROM Map
            WHERE id IN (
                SELECT map_id FROM UserMapAccess WHERE user_id = ?
            )
        """,
        (user_id,)
    )

    maps = []
    for map in data:
        maps.append({
            "id": map[0],
            "name": map[1]
        })

    return {
        "success": True,
        "maps": maps
    }


@app.route("/api/map/new", methods=["POST"])
@login_required
def new_map(jwt):
    map_name = request.json["name"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO Map (name) VALUES (?)",
        (map_name,)
    )
    map_id = cur.lastrowid

    cur.execute(
        "INSERT INTO UserMapAccess (map_id, user_id) VALUES (?, ?)",
        (map_id, jwt["user"]["id"])
    )

    conn.commit()
    conn.close()

    return {
        "id": map_id
    }


@app.route("/api/map/<map_id>", methods=["DELETE"])
@login_required
def delete_map(jwt, map_id):

    conn = create_connection()
    cur = conn.cursor()

    count = cur.execute(
        "SELECT COUNT(*) FROM UserMapAccess WHERE map_id = ? AND user_id = ?",
        (map_id, jwt["user"]["id"])
    ).fetchone()[0]

    if not count > 0:
        conn.close()
        return {
            "success": False,
            "error": "Insufficent access to the specified map."
        }, 403

    # We must delete all related rows too

    cur.execute(
        "DELETE FROM UserMapAccess WHERE map_id = ?",
        (map_id,)
    )

    # Delete the map

    cur.execute(
        "DELETE FROM Map WHERE id = ?",
        (map_id,)
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }


@app.route("/api/map/<map_id>/info")
@map_access_required
def map_info(jwt, map_id):

    conn = create_connection()
    cur = conn.cursor()

    name_data = cur.execute(
        "SELECT name FROM Map WHERE id = ?",
        (map_id,)
    ).fetchone()

    map_parts_data = cur.execute(
        "SELECT id, name FROM MapPart WHERE map_id = ?",
        (map_id,)
    ).fetchall()

    conn.close()

    map_parts = []
    for map_part_data in map_parts_data:
        map_parts.append({
            "id": map_part_data[0],
            "name": map_part_data[1]
        })

    return {
        "success": True,
        "data": {
            "name": name_data[0],
            "mapParts": map_parts
        }
    }

@app.route("/api/map/<map_id>/view")
@map_view_access
def view_map(map_id):

    conn = create_connection()
    cur = conn.cursor()

    name_data = cur.execute(
        "SELECT name FROM Map WHERE id = ?",
        (map_id,)
    ).fetchone()

    map_parts_data = cur.execute(
        "SELECT id, name FROM MapPart WHERE map_id = ?",
        (map_id,)
    ).fetchall()

    conn.close()

    map_parts = []
    for map_part_data in map_parts_data:
        map_part_id = map_part_data[0]

        map_parts.append({
            "id": map_part_id,
            "name": map_part_data[1]
        })

    return {
        "success": True,
        "data": {
            "name": name_data[0],
            "mapParts": map_parts
        }
    }
