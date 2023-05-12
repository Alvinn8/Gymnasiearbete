from my_server.database_handler import create_connection
import math
import time

def distance(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

# Get the next point in openSet that has the lowest f_score. In other words, get
# the point which we _think_ will be the shortest path
def get_next_point(open_set, f_score):
    lowest_id = None
    lowest_f_score = math.inf  # Infinity
    for point_id in open_set:
        # The value defaults to infinity
        point_f_score = f_score.get(point_id, math.inf)
        if point_f_score < lowest_f_score:
            # We found a point with a lower score, assign the current
            lowest_id = point_id
            lowest_f_score = point_f_score
    # Return the point with the lowest f score that we found
    return lowest_id

def reconstruct_path(previous, current_id):
    path = [current_id]
    while current_id in previous:
        current_id = previous[current_id]
        path.insert(0, current_id)
    return path

def a_star_find_shortest_path(start_point_id, end_point_id):
    # https://en.wikipedia.org/wiki/A*_search_algorithm#Pseudocode [Read 2023-03-10]

    t0 = time.time()

    conn = create_connection()
    cur = conn.cursor()

    end_point_x, end_point_y = cur.execute(
        "SELECT x, y FROM Point WHERE id = ?",
        (end_point_id,)
    ).fetchone()

    database_access_count = 1

    # A set of points that have been discovered
    open_set = set()
    open_set.add(start_point_id)

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

    neighbor_loop_iterations = 0

    steps = []

    # While the open set isn't empty
    while len(open_set) > 0:
        current_point_id = get_next_point(open_set, f_score)

        step = {
            "id": current_point_id,
            "connections": []
        }

        if current_point_id == end_point_id:
            # We found the end! Let's reconstruct the path we took and return that.
            t1 = time.time()
            print("Pathfinding:")
            print(f"\t Time: {(t1 - t0):.3f} seconds")
            print(f"\t Database lookups: {database_access_count}")
            print(f"\t Neighbor loop iterations: {neighbor_loop_iterations}")
            print("</>")
            conn.close()
            return reconstruct_path(previous, current_point_id), steps

        open_set.remove(current_point_id)

        # Get all connections to the point
        current_point_connections = cur.execute(
            """SELECT point_a_id, point_b_id, point_a.x, point_a.y, point_b.x, point_b.y FROM PointConnection
                JOIN Point AS point_a ON point_a.id = point_a_id
                JOIN Point AS point_b ON point_b.id = point_b_id
                WHERE point_a_id = ? OR point_b_id = ?""",
            (current_point_id, current_point_id)
        ).fetchall()

        database_access_count += 1

        # Get all neighboring points
        for point_connection in current_point_connections:
            # The connection objects will contain two ids, one of which will be the current
            # id, so getting the _other_ id will be the neighbor's id.
            neighbor_is_point_a = point_connection[1] == current_point_id
            neighbor_point_id = point_connection[0] if neighbor_is_point_a else point_connection[1]

            neighbor_loop_iterations += 1

            # The SQL query gets both the current point's x and y and the neighbor point's
            # x abd y. They are labled as point a and point b in the database, we just need
            # to identify which is the current one and which is the neighbor. The variable
            # neighbor_is_point_a is true if the neighbor is point a which is used to assign
            # the correct coordinates.
            point_a_x, point_a_y = point_connection[2], point_connection[3]
            point_b_x, point_b_y = point_connection[4], point_connection[5]

            # If the neighbor is point a, get the neighbor's coordinates for point a, else
            # from point b.
            neighbor_x = point_a_x if neighbor_is_point_a else point_b_x
            neighbor_y = point_a_y if neighbor_is_point_a else point_b_y

            # If the neighbor is point a, get the coordinates for the current point from the
            # other point, from point b, else from point a.
            current_x = point_b_x if neighbor_is_point_a else point_a_x
            current_y = point_b_y if neighbor_is_point_a else point_a_y

            new_neighbor_g_score = g_score[current_point_id] + distance(current_x, current_y, neighbor_x, neighbor_y)

            # Get the current g_score for the neighbor so we can determine if we just found
            # a better score.
            neighbor_g_score = g_score.get(neighbor_point_id, math.inf)

            if new_neighbor_g_score < neighbor_g_score:
                # We found a faster path to get to this point. Save it.
                previous[neighbor_point_id] = current_point_id
                g_score[neighbor_point_id] = new_neighbor_g_score

                # Predict the distance to get to the end point by calculating the bird's-eye
                # distance to the end point
                predicted_distance_to_end = distance(neighbor_x, neighbor_y, end_point_x, end_point_y)

                # Assign the f_score, the predicted distance to get from the start to te end
                # by going trough this neighbor point.
                f_score[neighbor_point_id] = new_neighbor_g_score + predicted_distance_to_end

                # Add the neighbor to the open set so we can consider it for the next iteration.
                # Since f_score was assigned the new point with the lowest predicted score
                # (f_score) will be chosen for the next iteration.
                open_set.add(neighbor_point_id)

                step["connections"].append({
                    "id": neighbor_point_id
                })
        steps.append(step)

    conn.close()
    return None, None

def dijkstra_find_closest(start_point_id, end_category_id, exclude_room_ids):
    # https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Pseudocode

    t0 = time.time()
    
    conn = create_connection()
    cur = conn.cursor()

    open_set = set()
    open_set.add(start_point_id)

    already_explored = set()

    distances = {}
    distances[start_point_id] = 0

    # A dictionary where the map is a point id and the value is the id of the point
    # that came before the key. This can be used to recreate the shortest path after
    # we find an a valid end point.
    previous = {}

    database_access_count = 0
    neighbor_loop_iterations = 0

    steps = []

    while len(open_set) > 0:
        current_point_id = get_next_point(open_set, distances)

        step = {
            "id": current_point_id,
            "connections": []
        }
        steps.append(step)

        result = cur.execute(
            "SELECT category_id, Room.id FROM Room WHERE door_at_point_id = ?",
            (current_point_id,)
        ).fetchone()
        category_id, room_id = result if not result is None else (None, None)

        if not result is None and category_id == end_category_id and room_id not in exclude_room_ids:
            # We found a destination Let's reconstruct the path we took and return that.
            t1 = time.time()
            print("Pathfinding (find closest):")
            print(f"\t Time: {(t1 - t0):.3f} seconds")
            print(f"\t Database lookups: {database_access_count}")
            print(f"\t Neighbor loop iterations: {neighbor_loop_iterations}")
            print("</>")
            conn.close()
            return reconstruct_path(previous, current_point_id), steps
        
        already_explored.add(current_point_id)
        open_set.remove(current_point_id)

        # Get all connections to the point
        current_point_connections = cur.execute(
            """SELECT point_a_id, point_b_id, point_a.x, point_a.y, point_b.x, point_b.y FROM PointConnection
                JOIN Point AS point_a ON point_a.id = point_a_id
                JOIN Point AS point_b ON point_b.id = point_b_id
                WHERE point_a_id = ? OR point_b_id = ?""",
            (current_point_id, current_point_id)
        ).fetchall()

        database_access_count += 1

        # Get all neighboring points
        for point_connection in current_point_connections:
            # The connection objects will contain two ids, one of which will be the current
            # id, so getting the _other_ id will be the neighbor's id.
            neighbor_is_point_a = point_connection[1] == current_point_id
            neighbor_point_id = point_connection[0] if neighbor_is_point_a else point_connection[1]

            if neighbor_point_id in already_explored:
                # This neighbor has already been explored. Ignore.
                continue

            already_explored.add(neighbor_point_id)
            open_set.add(neighbor_point_id)
            step["connections"].append({
                "id": neighbor_point_id
            })

            neighbor_loop_iterations += 1

            # The SQL query gets both the current point's x and y and the neighbor point's
            # x and y. They are labled as point a and point b in the database, we just need
            # to identify which is the current one and which is the neighbor. The variable
            # neighbor_is_point_a is true if the neighbor is point a which is used to assign
            # the correct coordinates.
            point_a_x, point_a_y = point_connection[2], point_connection[3]
            point_b_x, point_b_y = point_connection[4], point_connection[5]

            # If the neighbor is point a, get the neighbor's coordinates for point a, else
            # from point b.
            neighbor_x = point_a_x if neighbor_is_point_a else point_b_x
            neighbor_y = point_a_y if neighbor_is_point_a else point_b_y

            # If the neighbor is point a, get the coordinates for the current point from the
            # other point, from point b, else from point a.
            current_x = point_b_x if neighbor_is_point_a else point_a_x
            current_y = point_b_y if neighbor_is_point_a else point_a_y

            # Calculate the distance from the start to this neighbor
            new_neighbor_distance = distances[current_point_id] + distance(current_x, current_y, neighbor_x, neighbor_y)

            # Get the current distance from the start for the neighbor so we can determine
            # if we just found a shorter distance.
            neighbor_distance = distances.get(neighbor_point_id, math.inf)

            # If we find a better distance...
            if new_neighbor_distance < neighbor_distance:
                # ...store that
                distances[neighbor_point_id] = new_neighbor_distance
                previous[neighbor_point_id] = current_point_id
    
    # No one found
    conn.close()
    return None