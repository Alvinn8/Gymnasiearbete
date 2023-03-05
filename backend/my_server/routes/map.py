from flask import request
from my_server import app
from my_server.auth import login_required, map_access_required, map_view_access
from my_server.database_handler import create_connection, db_fetch_all, db_to_json


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

    map_data = cur.execute(
        "SELECT name, public FROM Map WHERE id = ?",
        (map_id,)
    ).fetchone()

    map_parts_data = cur.execute(
        "SELECT id, name, offset_x, offset_y, rotation_deg, z FROM MapPart WHERE map_id = ?",
        (map_id,)
    ).fetchall()

    conn.close()

    map_parts = []
    for map_part_data in map_parts_data:
        map_parts.append({
            "id": map_part_data[0],
            "name": map_part_data[1],
            "offsetX": map_part_data[2],
            "offsetY": map_part_data[3],
            "rotationDeg": map_part_data[4],
            "z": map_part_data[5]
        })

    return {
        "success": True,
        "data": {
            "name": map_data[0],
            "public": bool(map_data[1]),
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
        "SELECT id, name, offset_x, offset_y, rotation_deg, z FROM MapPart WHERE map_id = ?",
        (map_id,)
    ).fetchall()

    # Get all rooms on this map
    rooms_data = cur.execute(
        """SELECT Room.id, Room.name, Room.door_at_point_id, Room.x, Room.y, Room.width, Room.height, MapPart.z FROM Room
               JOIN Point ON Point.id = Room.door_at_point_id
               JOIN MapPart ON MapPart.id = Point.map_part_id
               WHERE MapPart.map_id = ?
        """, (map_id,)
    ).fetchall()

    conn.close()

    map_parts = db_to_json(
        map_parts_data, ["id", "name", "offsetX", "offsetY", "rotationDeg", "z"])

    rooms = db_to_json(
        rooms_data, ["id", "name", "doorAtPointId", "x", "y", "width", "height", "z"])

    return {
        "success": True,
        "data": {
            "name": name_data[0],
            "mapParts": map_parts,
            "rooms": rooms
        }
    }


@app.route("/api/map/<map_id>/share", methods=["POST"])
@map_view_access
def share_map(map_id):
    username = request.json["username"]

    conn = create_connection()
    cur = conn.cursor()

    userRow = cur.execute(
        "SELECT id FROM User WHERE username = ?",
        (username,)
    ).fetchone()

    if userRow is None:
        conn.close()
        return {
            "success": False,
            "error": "Användaren kunde inte hittas."
        }

    existingRows = cur.execute(
        "SELECT COUNT(*) FROM UserMapAccess WHERE user_id = ? AND map_id = ?",
        (userRow[0], map_id)
    ).fetchone()[0]

    if existingRows > 0:
        conn.close()
        return {
            "success": False,
            "error": "Användaren har redan tillgång till kartan."
        }

    cur.execute(
        "INSERT INTO UserMapAccess (user_id, map_id) VALUES (?, ?)",
        (userRow[0], map_id)
    )
    conn.commit()

    conn.close()

    return {
        "success": True
    }


@app.route("/api/map/<map_id>/change_public_status", methods=["POST"])
@map_access_required
def change_public_status(map_id):
    public = request.json["public"]

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE Map SET public = ? WHERE id = ?",
        (public, map_id)
    )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
