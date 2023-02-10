import csv
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import utm
import re

from analyze_graph import get_average_shortest_path_length, get_average_node_degree, get_average_betweenness


def coord_to_grid_coord(coord, hor_n, ver_n):
    """Takes a values between 0 and 1 and maps it to a grid coordinate

    Args:
        coord (_type_): tuple(x, y)
        hor_n (_type_): amount of columns
        ver_n (_type_): amount of rows

    Returns:
        tuple(): new coordinate containing index of the corresponding cell
    """
    x, y = coord

    x_index = np.ceil(hor_n * x)
    y_index = np.ceil(ver_n * y)

    if x_index >= hor_n:
        x_index = hor_n - 1

    if y_index >= ver_n:
        y_index = ver_n - 1

    return (int(x_index), int(y_index))


def coords_to_grid_indices(coords, hor_n, ver_n):
    """Applies the function coord_to_grid_coord to a dictionary
    """
    grid_indices = {}

    for node_id in coords:
        x, y = coords[node_id]

        grid_indices[node_id] = coord_to_grid_coord((x, y), hor_n, ver_n)

    return grid_indices


def convert_geo_to_relative_coords(geo_coords):
    """Takes a dictionary of node ids to geo-coordinates and maps them to numbers
    between 0 and 1.
    """
    station_locations = {}

    # Convert coordinates to 2D space coordinates
    for i in range(len(geo_coords)):
        station_id = list(geo_coords.keys())[i]
        latitude, longitude = geo_coords[station_id]
        x, y, _, _ = utm.from_latlon(latitude, longitude)

        station_locations[station_id] = (x, y)

    # Scale and translate 2D coordinates
    x_vals = [x for (x, _) in station_locations.values()]
    y_vals = [y for (_, y) in station_locations.values()]

    for i in range(len(geo_coords)):
        node_id = list(station_locations.keys())[i]
        x, y = station_locations[node_id]

        x_new = (x - np.min(x_vals)) / (np.max(x_vals) - np.min(x_vals))
        y_new = (y - np.min(y_vals)) / (np.max(y_vals) - np.min(y_vals))

        station_locations[node_id] = (x_new, y_new)

    return station_locations


def read_nodes(filename):
    """Return a dictionary with node ids as key and coordinates as value
    """
    nodes = {}

    with open(filename, "r") as fp:
        reader = csv.reader(fp, delimiter=';')

        next(reader) # Skip first row

        for line in reader:
            node_id = int(line[0])
            lat = float(line[1])
            lon = float(line[2])

            nodes[node_id] = (lat, lon)

    return nodes


def read_edges(filename):
    edges = {}

    with open(filename, "r") as fp:
        reader = csv.reader(fp, delimiter=';')

        next(reader) # Skip first row

        for line in reader:
            node_A = int(line[0])
            node_B = int(line[1])
            match = re.search("'d': ([0-9]*)", line[2])

            edges[(node_A, node_B)] = int(match.group(1))

    return edges


def create_graph(node_coords, edges):
    G = nx.Graph()

    for edge in edges:
        node_A = edge[0]
        node_B = edge[1]
        d = edges[edge]

        G.add_edge(node_A, node_B, weight=d)

    return G


def get_city_grid(city, hor_N, ver_N):
    node_coords = read_nodes(f"data/{city}/network_nodes.csv")
    edges = read_edges(f"data/{city}/network_rail.csv")
    graph = create_graph(node_coords, edges)

    nodes_to_plot = {}

    for node in graph.nodes:
        nodes_to_plot[node] = node_coords[node]

    relative_coords = convert_geo_to_relative_coords(nodes_to_plot)

    return list(coords_to_grid_indices(relative_coords, hor_N, ver_N).values())


if __name__ == "__main__":
    city = "berlin"
    node_coords = read_nodes(f"data/{city}/network_nodes.csv")
    edges = read_edges(f"data/{city}/network_rail.csv")
    graph = create_graph(node_coords, edges)

    nodes_to_plot = {}
    N = 100

    for node in graph.nodes:
        nodes_to_plot[node] = node_coords[node]

    relative_coords = convert_geo_to_relative_coords(nodes_to_plot)
    grid_indices = coords_to_grid_indices(convert_geo_to_relative_coords(nodes_to_plot), N, N)

    for edge in graph.edges:
        node_a, node_b = edge
        (x_a, y_a) = grid_indices[node_a]
        (x_b, y_b) = grid_indices[node_b]

        plt.plot([x_a, x_b], [y_a, y_b], zorder=-1, color='r')

    plt.scatter([x for (x, y) in grid_indices.values()], [y for (x, y) in grid_indices.values()])

    plt.title("Map of " + city)

    plt.show()

    # Print some stats of the graph
    print(graph)
    print("average shortest path length", get_average_shortest_path_length(graph))
    print("average degree", get_average_node_degree(graph))
    print("average betweenness", get_average_betweenness(graph))
