import networkx as nx


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


def get_all_shortest_paths(graph, target_nodes):
    """Finds all shortest paths between the specified nodes

    Returns:
        dict[frozenset(list)]: dictionary containing all discovered shortest paths (use frozenset with the start and end node as key)
    """
    shortest_paths = {}

    for i in range(len(target_nodes)):
        for j in range(i, len(target_nodes)):
            if i != j:
                node_a = target_nodes[i]
                node_b = target_nodes[j]

                try:
                    shortest_paths[frozenset([node_a, node_b])] = nx.algorithms.astar_path(graph, node_a, node_b)
                except nx.exception.NetworkXNoPath:
                    shortest_paths[frozenset([node_a, node_b])] = None

    return shortest_paths


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