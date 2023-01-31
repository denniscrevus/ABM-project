import matplotlib.pyplot as plt
from agents import *
from helpers import reduce_graph, text_to_coords
from model import *
from tokyo_mapping import *
from analyze_graph import *


def plot_result(graph, shortest_paths, show_all=True, show_shortest=True):
    fig = plt.figure(dpi=200, figsize=(3, 3))

    if show_all:
        # Plot all connections
        for node, links in graph.items():
            x0, y0 = node

            for connected_coordinate, cost in links:
                x, y = connected_coordinate
                plt.plot([x0, x], [y0, y], color=(255/255, 242/255, 0, 1), lw=.5, zorder=-1)

        x, y = zip(*graph.keys())
        plt.scatter(x, y, color=(213/255, 184/255, 90/255, 1), s=.5)
        x, y = zip(*model.food_locations.values())
        plt.scatter(x, y, color='red', marker='s', s=3)

    if show_shortest:
        # Plot the shortest paths between the food sources
        for path_key in shortest_paths:
            path = shortest_paths[path_key]

            for i in range(len(path) - 1):
                (x0, y0) = path[i]
                (x1, y1) = path[i + 1]

                plt.plot([x0, x1], [y0, y1], color=(1, 0, 0, 1), lw=.5)

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

    plot_result(graph, shortest_paths)
