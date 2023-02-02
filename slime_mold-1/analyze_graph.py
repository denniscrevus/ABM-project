import sys
import networkx as nx
import pickle

from agents import *
from model import *
from helpers import *


class ExperimentResults:
    def __init__(self, _x_vals, _results):
        self.x_vals = _x_vals
        self.results = _results


def convert_result_to_graph(connections):
    """Converts the result of the slime model into a networkx graph
    for easier analysis.

    Args:
        connections: dictionary result from the model

    Returns:
        networkx.Graph: the network containing all nodes and edges
    """
    graph = nx.Graph()

    graph.add_nodes_from(connections.keys())

    for node in connections:
        edges = connections[node]

        for (next_node, cost) in edges:
            graph.add_edge(node, next_node, weight=cost)

    return graph


def get_all_shortest_paths(connections, target_nodes):
    """Finds all shortest paths between the specified nodes

    Returns:
        dict[frozenset(list)]: dictionary containing all discovered shortest paths (use frozenset with the start and end node as key)
    """
    graph = convert_result_to_graph(connections)
    shortest_paths = {}

    for i in range(len(target_nodes)):
        for j in range(i, len(target_nodes)):
            if i != j:
                node_a = target_nodes[i]
                node_b = target_nodes[j]

                if node_a in graph.nodes and node_b in graph.nodes:
                    try:
                        shortest_paths[frozenset([node_a, node_b])] = nx.algorithms.astar_path(graph, node_a, node_b)
                    except nx.exception.NetworkXNoPath:
                        shortest_paths[frozenset([node_a, node_b])] = None

    return shortest_paths


def load_data(filename):
    with open(filename, "rb") as fp:
        data_obj = pickle.load(fp)

        return data_obj.x_vals, data_obj.results


def plot_data(x_vals, data):
    mean_data = np.mean(data, axis=0)
    std_data = np.std(data, axis=0)

    output_vars = ['average nodes per path', 'average degree', 'average betweenness']

    for i in range(len(output_vars)):
        fig = plt.figure(dpi=300)

        plt.plot(x_vals, mean_data[i])
        plt.fill_between(x_vals, mean_data[i] - std_data[i], mean_data[i] + std_data[i], alpha=0.5)

        plt.title("Slime ABM simulation (single run)")
        plt.xlabel("branch probability")
        plt.ylabel(output_vars[i])

        plt.savefig(output_vars[i] + ".png")


def plot_node_distribution():
    N_steps = 200
    size = 100
    p_branch = 0.075
    p_connect = 0.1
    signal_strength = 1
    noise = 0.05 * signal_strength
    food_coords = text_to_coords("tokyo_coords.txt")

    degrees = []
    for _ in range(50):
        model = SlimeModel(size, size, p_branch, p_connect, signal_strength, noise,
                                food_coords)

        connections = model.run(N_steps)
        reduced_graph = reduce_graph(connections, food_coords)
        nx_graph = convert_result_to_graph(reduced_graph)

        degrees += [d for (_, d) in nx_graph.degree(food_coords)]

    fig = plt.figure()

    plt.hist(degrees)

    plt.title("Degree distribution of food nodes")

    plt.show()


def run_experiment(N_runs=1, save_file=None):
    """Vary parameters (except agent count)

    plot average degree, average path length, maybe other outputs
    """
    N_steps = 200
    size = 100
    p_branch_vals = np.linspace(0.0, 1.0, 5)
    p_connect = 0.1
    signal_strength = 1
    noise = 0.05 * signal_strength
    food_coords = text_to_coords("tokyo_coords.txt")

    all_data = np.zeros((N_runs, 3, len(p_branch_vals)))

    print(f"Estimated time: {N_runs * len(p_branch_vals) * 10} second(s)")

    for run_i in range(N_runs):
        average_nodes = np.zeros(len(p_branch_vals))
        average_degree = np.zeros_like(average_nodes)
        average_betweenness = np.zeros_like(average_nodes)

        print("Run", run_i + 1)

        for i in range(len(p_branch_vals)):
            p_branch = p_branch_vals[i]

            # Display progress
            print(f"{100 * i / len(p_branch_vals):.2f}% {p_branch:.4f}")

            model = SlimeModel(size, size, p_branch, p_connect, signal_strength, noise,
                            food_coords)

            connections = model.run(N_steps)
            reduced_graph = reduce_graph(connections, food_coords)
            nx_graph = convert_result_to_graph(reduced_graph)
            shortest_paths = get_all_shortest_paths(reduced_graph, food_coords)

            # Find the average amount of nodes in the shortest paths
            for node_pair in shortest_paths:
                path = shortest_paths[node_pair]

                average_nodes[i] += len(path)

            average_nodes[i] /= len(shortest_paths)

            # Find the average degree
            average_degree[i] = np.mean([d for (_, d) in nx_graph.degree(food_coords)])

            # Find the average betweenness centrality
            average_betweenness[i] = np.mean(list(nx.betweenness_centrality(nx_graph).values()))

        # Save data in numpy array
        all_data[run_i, 0] = average_nodes
        all_data[run_i, 1] = average_degree
        all_data[run_i, 2] = average_betweenness

    print("100.0%\n")

    # Save the data in a different object to be pickled
    if save_file:
        data_obj = ExperimentResults(p_branch_vals, all_data)

        with open(save_file, "wb") as fp:
            pickle.dump(data_obj, fp)

    return p_branch_vals, all_data


if __name__ == "__main__":
    N_runs = 1

    if len(sys.argv) > 1:
        command = sys.argv[1]

        # Plot the data from the specified file
        if command == 'plot':
            filename = None

            if len(sys.argv) > 2:
                filename = sys.argv[2]

                x_vals, results = load_data(filename)
                plot_data(x_vals, results)
            else:
                print("please provide file to load and plot")
        # Run the data with the current parameters and save it in the specified file
        elif command == 'run':
            save_file = None

            if len(sys.argv) > 2:
                save_file = sys.argv[2]

            x_vals, results = run_experiment(N_runs, save_file=save_file)

            if not save_file:
                plot_data(x_vals, results)
        elif command == 'node_hist':
            plot_node_distribution()
