import csv
import networkx as nx

from tokyo_mapping import *


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


def create_graph(filename):
    G = nx.Graph()

    with open(filename, "r") as fp:
        reader = csv.reader(fp, delimiter=';')

        next(reader) # Skip first row

        for line in reader:
            node_A = int(line[0])
            node_B = int(line[1])

            G.add_edge(node_A, node_B)

    return G


if __name__ == "__main__":
    node_coords = read_nodes("data/rome/network_nodes.csv")
    graph = create_graph("data/rome/network_rail.csv")

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
    plt.show()