import networkx as nx
import numpy as np


def convert_result_to_graph(connections, main_nodes):
    graph = nx.Graph()

    graph.add_nodes_from(connections.keys())

    for node in connections:
        edges = connections[node]

        for (next_node, cost) in edges:
            graph.add_edge(node, next_node, weight=cost)

    get_all_shortest_paths(graph, main_nodes)


def get_all_shortest_paths(graph, target_nodes):
    for i in range(len(target_nodes)):
        for j in range(i, len(target_nodes)):
            if i != j:
                node_a = target_nodes[i]
                node_b = target_nodes[j]

                try:
                    print(node_a, node_b, len(nx.algorithms.astar_path(graph, node_a, node_b)))
                except nx.exception.NetworkXNoPath:
                    # print(node_b, "not reachable from", node_a)
                    pass


if __name__ == "__main__":
    test_graph = nx.Graph()

    test_graph.add_node(1)
    test_graph.add_node(2)
    test_graph.add_node(3)
    test_graph.add_node(4)

    test_graph.add_edge(1, 2)
    test_graph.add_edge(2, 3)
    test_graph.add_edge(3, 4)
    test_graph.add_edge(1, 4)

    get_all_shortest_paths(test_graph, [1, 4])