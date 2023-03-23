from flask import request
from my_server import app
from my_server.auth import map_part_required
from my_server.database_handler import create_connection


@app.route("/api/map/<map_id>/part/<part_id>/staircase/new", methods=["POST"])
@map_part_required
def new_staircase(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO Staircase (map_part_id, x, y, width, height) VALUES (?, ?, ?, ?, ?)",
        (part_id, 10, 10, 40, 40)
    )
    staircase_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "success": True,
        "id": staircase_id
    }


@app.route("/api/map/<map_id>/part/<part_id>/staircase/edit", methods=["POST"])
@map_part_required
def edit_staircase(jwt, map_id, part_id):

    conn = create_connection()
    cur = conn.cursor()

    data = request.get_json()
    for staircase in data["changes"]:
        cur.execute(
            "UPDATE Staircase SET x = ?, y = ?, width = ?, height = ?, connects_to = ? WHERE id = ?",
            (staircase["x"], staircase["y"],
             staircase["width"], staircase["height"],
             staircase["connectsTo"], staircase["id"])
        )

    conn.commit()
    conn.close()

    return {
        "success": True
    }
