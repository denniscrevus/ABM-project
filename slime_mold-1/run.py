import matplotlib.pyplot as plt
from agents import *
from helpers import reduce_graph, text_to_coords
from model import *
from tokyo_mapping import *
from analyze_graph import *


def plot_result(graph, shortest_paths=None, show_all=True):
    fig = plt.figure(dpi=200, figsize=(3, 3))

    # Keep track of plotted objects to improve performance
    plotted_edges = set()
    plotted_nodes = set()

    if shortest_paths:
        shortest_path_nodes = set()

        # Plot the shortest paths between the food sources
        for path_key in shortest_paths:
            path = shortest_paths[path_key]

            for i in range(len(path) - 1):
                (x0, y0) = path[i]
                (x1, y1) = path[i + 1]
                edge_key = frozenset([(x0, y0), (x1, y1)])

                shortest_path_nodes.add((x0, y0))
                shortest_path_nodes.add((x1, y1))

                if edge_key not in plotted_edges:
                    plt.plot([x0, x1], [y0, y1], color=(1, 0, 0, 1), lw=.4)

                    plotted_edges.add(edge_key)

        for node in shortest_path_nodes:
            if node not in plotted_nodes:
                plt.scatter(node[0], node[1], color=(.7, 0, 0, 1), s=.5, zorder=5)

                plotted_nodes.add(node)

    # Plot all connections
    if show_all:
        for node, links in graph.items():
            x0, y0 = node

            for connected_coordinate, _ in links:
                edge_key = frozenset([node, connected_coordinate])

                if edge_key not in plotted_edges:
                    x, y = connected_coordinate
                    plt.plot([x0, x], [y0, y], color=(255/255, 242/255, 0, 1), lw=.5, zorder=-1)

                    plotted_edges.add(edge_key)

        # Plot intermediate nodes
        for node in graph.keys():
            if node not in plotted_nodes:
                plt.scatter(node[0], node[1], color=(213/255, 184/255, 90/255, 1), s=.5)

                plotted_nodes.add(node)

    # Plot food nodes
    x, y = zip(*model.food_locations.values())
    plt.scatter(x, y, color='red', marker='s', s=3, zorder=100)

    plt.savefig("graph.png")
    
    plt.show()


if __name__ == "__main__":
    N_steps = 200
    size = 100
    p_branch = 0.075
    p_connect = 0.1
    signal_strength = 1
    noise = 0.05 * signal_strength
    food_coords = text_to_coords("tokyo_coords.txt")

    model = SlimeModel(size, size, p_branch, p_connect, signal_strength, noise,
                        food_coords)
    graph = model.run(N_steps)

    # Remove unnecessary connections and find all shortest paths between food
    graph = reduce_graph(graph, food_coords)
    shortest_paths = get_all_shortest_paths(graph, food_coords)

    plot_result(graph, shortest_paths, show_all=True)
