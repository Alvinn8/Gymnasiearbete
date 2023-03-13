from flask import request
from my_server import app
from my_server import pathfinding
from my_server.database_handler import create_connection, db_to_json

@app.route("/api/map/pathfinding/find_path", methods=["POST"])
def pathfind():
    data = request.get_json()
    start_point_id = data["startPointId"]
    end_point_id = data["endPointId"]

    path_point_ids = pathfinding.a_star_find_shortest_path(start_point_id, end_point_id)

    if path_point_ids is None:
        return {
            "success": False
        }
    
    # [5, 9, 2]

    # [2, 5, 9]

    # WHERE Point.id IN (5, 9, 2)
    
    conn = create_connection()
    cur = conn.cursor()
    path_data = cur.execute(
        f"""SELECT Point.id, x + offset_x, y + offset_y, z FROM Point
            JOIN MapPart ON map_part_id = MapPart.id
            WHERE Point.id IN ({",".join(["?"] * len(path_point_ids))})""",
            # This is still safe from SQL injections as we are only creating the question
            # marks in the SQL query. The data is still safely passed as a prepared statement.
        path_point_ids
    ).fetchall()
    conn.close()

    path = []

    # path_data is ordered incorrectly because SQL will order by the primary key,
    # but we want to order by the pathfinding result.
    for point_id in path_point_ids:
        for point_data in path_data:
            if point_data[0] == point_id:
                path.append({
                    "id": point_id,
                    "x": point_data[1],
                    "y": point_data[2],
                    "z": point_data[3]
                })

    # path = db_to_json(path_data, ["id", "x", "y", "z"])

    return {
        "success": True,
        "path": path
    }