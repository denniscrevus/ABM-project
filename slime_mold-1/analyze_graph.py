import sys
import networkx as nx
import matplotlib.pyplot as plt
import pickle

from agents import *
from model import *
from helpers import *
from read_geo_data import get_city_grid


class ExperimentResults:
    def __init__(self, _x_vals, _results, _n_runs):
        self.x_vals = _x_vals
        self.results = _results

        # Meta data
        self.n_runs = _n_runs


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


def get_average_shortest_path_length(graph, use_weights=True):
    all_lengths = []

    for C in [graph.subgraph(c).copy() for c in nx.connected_components(graph)]:
        all_lengths.append(nx.average_shortest_path_length(C, weight='weight' if use_weights else None))

    return np.mean(all_lengths)


def get_average_node_degree(graph, target_nodes=None):
    return np.mean([d for (_, d) in graph.degree(target_nodes)])


def get_average_betweenness(graph):
    return np.mean(list(nx.betweenness_centrality(graph).values()))


def remove_unused_nodes(graph, active_nodes: set):
    """Basically reduce the graph further by removing nodes that are not
    in main_nodes and only connecting the main nodes with each other using shortest paths.

    returns a Graph
    """
    new_graph = nx.Graph()

    # Add nodes
    for node in active_nodes:
        new_graph.add_node(node)

    # Add edges
    node_list = list(active_nodes)
    for i in range(len(node_list)):
        for j in range(i, len(node_list)):
            if i != j:
                node_A = node_list[i]
                node_B = node_list[j]

                if node_A in graph.nodes and node_B in graph.nodes:
                    d = nx.shortest_path_length(graph, node_A, node_B)

                    new_graph.add_edge(node_A, node_B, weight=d)

    return new_graph


def load_data(filename):
    with open(filename, "rb") as fp:
        data_obj = pickle.load(fp)

        return data_obj.x_vals, data_obj.results, data_obj.n_runs


def plot_data(x_vals, data, n_runs):
    mean_data = np.mean(data, axis=0)
    std_data = np.std(data, axis=0)

    output_vars = ['average shortest path length', 'average degree', 'average betweenness']

    for i in range(len(output_vars)):
        plt.figure(dpi=300)

        plt.plot(x_vals, mean_data[i])
        plt.fill_between(x_vals, mean_data[i] - std_data[i], mean_data[i] + std_data[i], alpha=0.5)

        plt.title(fr"Slime ABM simulation with Tokyo map ($N_{{runs}}={n_runs}$)")
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

    plt.figure()

    plt.hist(degrees)

    plt.title("Degree distribution of food nodes")

    plt.show()


def run_experiment(N_runs=1, omit_unused=False, save_file=None):
    """Vary parameters (except agent count)

    plot average degree, average path length, maybe other outputs
    """
    N_steps = 200
    size = 100
    resolution = 20
    p_branch_vals = np.linspace(0.0, 1.0, resolution)
    p_branch = 0.075
    p_connect = 0.1
    signal_strength = 1
    noise = 0.05 * signal_strength
    food_coords = get_city_grid("rome", size, size)

    all_data = np.zeros((N_runs, 3, resolution))

    print(f"Estimated time: ~{N_runs * resolution * 10} second(s)")

    for run_i in range(N_runs):
        average_length = np.zeros(resolution)
        average_degree = np.zeros_like(average_length)
        average_betweenness = np.zeros_like(average_length)

        print("Run", run_i + 1)

        for i in range(resolution):
            p_branch = p_branch_vals[i]

            # Display progress
            print(f"{100 * i / resolution:.2f}% {p_branch:.4f}")

            model = SlimeModel(size, size, p_branch, p_connect, signal_strength, noise,
                                food_coords)

            connections = model.run(N_steps)
            reduced_graph = reduce_graph(connections, food_coords)
            nx_graph = convert_result_to_graph(reduced_graph)

            if omit_unused:
                used_nodes = set()
                for index_A in range(len(food_coords)):
                    for index_B in range(i, len(food_coords)):
                        if index_A != index_B:
                            node_A = food_coords[index_A]
                            node_B = food_coords[index_B]

                            if node_A in nx_graph.nodes and node_B in nx_graph.nodes:
                                used_nodes |= set(nx.shortest_path(nx_graph, node_A, node_B))

                nx_graph = remove_unused_nodes(nx_graph, used_nodes)

            # Find the average shortest path length
            average_length[i] = get_average_shortest_path_length(nx_graph)

            # Find the average degree
            average_degree[i] = get_average_node_degree(nx_graph)

            # Find the average betweenness centrality
            average_betweenness[i] = get_average_betweenness(nx_graph)

        # Save data in numpy array
        all_data[run_i, 0] = average_length
        all_data[run_i, 1] = average_degree
        all_data[run_i, 2] = average_betweenness

    print("100.0%\n")

    # Save the data in a different object to be pickled
    if save_file:
        data_obj = ExperimentResults(p_branch_vals, all_data, N_runs)

        with open(save_file, "wb") as fp:
            pickle.dump(data_obj, fp)

    return p_branch_vals, all_data


if __name__ == "__main__":
    """Options to run:
    python analyze_data.py run <name of file to store experiment in>
    python analyze_data.py plot <name of file that contains experiment to plot>
    python analyze_data.py node_hist
        This creates a histogram with node degrees in the graph.
    """
    N_runs = 5

    if len(sys.argv) > 1:
        command = sys.argv[1]

        # Plot the data from the specified file
        if command == 'plot':
            filename = None

            if len(sys.argv) > 2:
                filename = sys.argv[2]

                x_vals, results, N_runs = load_data(filename)
                plot_data(x_vals, results, N_runs)
            else:
                print("please provide file to load and plot")
        # Run the data with the current parameters and save it in the specified file
        elif command == 'run':
            save_file = None

            if len(sys.argv) > 2:
                save_file = sys.argv[2]

            x_vals, results = run_experiment(N_runs, omit_unused=False, save_file=save_file)

            if not save_file:
                plot_data(x_vals, results)
        elif command == 'node_hist':
            plot_node_distribution()
    else:
        print("Please provide a command (run, plot or node_hist)")
