from tokyo_mapping import *


def tokyo_coords_to_text(width=100, height=100):
    """
    Function that converts an iterable with 2D coordinates to a .txt file on a specified scale.

    Args:
        width: width of the grid.
        height: height of the grid.
    """
    coords, _ = get_tokyo_grid(width, height)

    with open('tokyo_coords.txt', 'w') as f:
        for x, y in coords:
            f.write(f'{x} {y}\n')


def text_to_coords(file_name):
    """
    Function that converts a .txt file with two coordinates on each row into a list of coordinate tuples.

    Args:
        file_name: name of the file read in.

    Returns:
        coords: list of (x, y) coordinate tuples.
    """
    coords = []
    with open(file_name, 'r') as f:
        for coord in f:
            x, y = coord.split()
            coords.append((int(x), int(y)))
    return coords


def reduce_graph(graph, food_locations):
    """
    Function that reduces a graph by removing dead ends and simplifying twofold connected nodes.

    Args:
        graph: dictionary containing locations (x, y) coordinate tuple as keys and sets of ((x, y), cost) tuples as values 
               representing connected coordinates.
        food_locations: list of (x, y) coordinate tuples representing nodes that are not allowed to be removed.
    """
    reduced = False

    # Keep reducing until no more changes have been made
    while not reduced:
        changed = False
        remove_list = []

        for (node_0, links) in graph.items():
            n = len(links)

            # Remove dead ends if they are not food locations
            if n == 1 and node_0 not in food_locations:
                (node_1, cost), = links
                graph[node_1].remove((node_0, cost))
                remove_list.append(node_0)
                changed = True

            # Remove node if it has two links and connect those two links unless those nodes form a triangular path
            elif n == 2 and node_0 not in food_locations:
                ((node_1, cost_1), (node_2, cost_2)) = links
                cost = round(cost_1 + cost_2, 3)

                if not triangular_path(node_0, graph):
                    graph[node_1].add((node_2, cost))
                    graph[node_2].add((node_1, cost))


                graph[node_1].remove((node_0, cost_1))
                graph[node_2].remove((node_0, cost_2))
                remove_list.append(node_0)
                changed = True

        # Remove unnecessary nodes once out of dictionary loop
        for node in remove_list:
            del graph[node]
        if not changed:
            reduced = True
    return graph

def triangular_path(node, graph):
    """
    Function that deduces if a node and its two connections form a triangular path. 
    By design this function only gets called when a node has exactly two connections.

    Args:
        node: (x, y) coordinate tuple.
        graph: dictionary containing locations (x, y) coordinate tuple as keys and sets of ((x, y), cost) tuples as values 
               representing connected coordinates.

    Returns:
        Boolean; True if a triangular path is found, False otherwise.
    """ 
    # Unpacking two ((x, y), cost) tuples
    (node_1, _), (node_2, _) = graph[node]

    # Splitting coordinates from costs
    coordinates_1, _ = zip(*graph[node_1])
    coordinates_2, _ = zip(*graph[node_2])

    if node_2 in coordinates_1 and node_1 in coordinates_2:
        return True
    return False


def get_distance(start, end):
    """Returns the Euclidean distance rounded to three decimals between two twofold unpackable variables.""" 
    x0, y0 = start
    x, y = end
    return round(np.sqrt((x-x0)**2 + (y-y0)**2), 3)


def get_distance_matrix(food_locations):
    """
    Creates square matrix containing the distances between all food locations.

    Arguments:
    food_locations -- dictionary containing the coordinates corresponding to all food sources as (x, y) tuples.

    Returns:
    D -- distance matrix of size n*n, where D[i,j] denotes the distance between city_i and city_j (NumPy array of floats).
    """
    n = len(food_locations)
    D = np.zeros((n, n))

    # Compute Euclidean distances between all coordinates
    for i in range(n):
        x0, y0 = food_locations[i]
        for j in range(i+1, n):
            x, y = food_locations[j]
            D[i, j] = np.sqrt((x - x0)**2 + (y - y0)**2)
            D[j, i] = D[i, j]
    return D


if __name__ == '__main__':
    tokyo_coords_to_text()
