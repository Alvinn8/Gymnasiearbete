from my_server.database_handler import create_connection
import math
import time


def a_star_find_shortest_path(map_id, start_point_id, end_point_id):
    # https://en.wikipedia.org/wiki/A*_search_algorithm#Pseudocode [Read 2023-03-10]

    t0 = time.time()

    conn = create_connection()
    cur = conn.cursor()

    # A set of points that have been discovered
    open_set = set()

    # A dictionary where the map is a point id and the value is the id of the point
    # that came before the key. This can be used to recreate the shortest path after
    # we find the end.
    previous = {}

    # A dictionary of point id to the smallest distance currently known to get to the point.
    # This is the actual distance from the start to the point.
    # If no value is present, the distance is set to infinity
    g_score = {}

    # We are at the starting point, so the distance is 0
    g_score[start_point_id] = 0

    # A dictionary of point id to the predicted distance for a path if the path
    # were to go trough this point.
    # f(x) = g(x) + h(x)
    # Where g(x) is stored in g_score, and
    # where h(x) is our heuristic function which predicts the distance to get to
    # the end point. This is defined as the bird's-eye-view distance, aka the
    # "perfect" distance to get from A to B using the distance formula.
    # If no value is present, the distance is set to infinity
    f_score = {}
    f_score[start_point_id] = 0

    # Get the next point in openSet that has the lowest fScore. In other words, get
    # the point which we _think_ will be the shortest path
    def get_next_point():
        lowest_id = None
        lowest_f_score = math.inf  # Infinity
        for point_id in open_set:
            point_f_score = f_score[point_id]
            # The value defaults to infinity
            if point_f_score is None:
                point_f_score = math.inf
            if point_f_score < lowest_f_score:
                # We found a point with a lower score, assign the current
                lowest_id = point_id
                lowest_f_score = point_f_score
        # Return the point with the lowest f score that we found
        return lowest_id

    # While the open set isn't empty
    while len(open_set) > 0:
        current_point_id = get_next_point()

        if current_point_id == end_point_id:
            pass

        open_set.remove(current_point_id)

        # Get all connections to the point
        current_point_connections = cur.execute(
            """SELECT point_a_id, point_b_id, point_a.x, point_a.y, point_b.x, point_b.y FROM PointConnection
                JOIN Point AS point_a ON point_a.id = point_a_id
                JOIN Point AS point_b ON point_b.id = point_b_id
                WHERE point_a_id = ? OR point_b_id = ?""",
            (current_point_id, current_point_id)
        ).fetchall()

        # Get all neighboring points
        for point_connection in current_point_connections:
            # The connection objects will contain two ids, one of which will be the current
            # id, so getting the _other_ id will be the neighbor's id.
            neighbor_is_point_a = point_connection[1] == current_point_id
            neighbor_point_id = point_connection[0] if neighbor_is_point_a else point_connection[1]

            # The SQL query gets both the current point's x and y and the neighbor point's
            # x abd y. They are labled as point a and point b in the database, we just need
            # to identify which is the current one and which is the neighbor. The variable
            # neighbor_is_point_a is true if the neighbor is point a which is used to assign
            # the correct coordinates.
            point_a_x = point_connection[2], point_a_y = point_connection[3]
            point_b_x = point_connection[4], point_b_y = point_connection[5]

            # If the neighbor is point a, get the neighbor's coordinates for point a, else
            # from point b.
            neighbor_x = point_a_x if neighbor_is_point_a else point_b_x
            neighbor_y = point_a_y if neighbor_is_point_a else point_b_y

            # If the neighbor is point a, get the coordinates for the current point from the
            # other point, from point b, else from point a.
            current_x = point_b_x if neighbor_is_point_a else point_a_x
            current_y = point_b_y if neighbor_is_point_a else point_a_y

            neighbor_distance = g_score[current_point_id]

    t1 = time.time()

    print(f"Pathfinding time: {(t1 - t0):.2f} seconds")
