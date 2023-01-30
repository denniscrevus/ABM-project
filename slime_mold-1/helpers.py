from tokyo_mapping import *


def tokyo_coords_to_text(width=100, height=100):
    coords, _ = get_tokyo_grid(width, height)
    with open('tokyo_coords.txt', 'w') as f:
        for x, y in coords:
            f.write(f'{x} {y}\n')

def text_to_coords(file_name):
    coords = []
    with open(file_name, 'r') as f:
        for coord in f:
            x, y = coord.split()
            coords.append((int(x), int(y)))
    return coords

def reduce_graph(graph, food_locations): 
    reduced = False

    # Keep reducing until no more changes have been made
    while not reduced:
        changed = False
        remove_list = []
        for node_0, links in graph.items():
            # print()
            # print(links)
            print(node_0)
            n = len(links)
            # print(n)
            # Remove dead ends if they are not food locations
            if n == 1 and node_0 not in food_locations:
                # print(links)
                (node_1, cost), = links 
                graph[node_1].remove((node_0, cost))
                remove_list.append(node_0)
                changed = True

            # Remove node if it has two links and connect those two links 
            elif n == 2 and node_0 not in food_locations:
                # print(node_0)
                ((node_1, cost_1), (node_2, cost_2)) = links
                cost = cost_1 + cost_2
                # print('node0:', node_0)
                # print('node1', node_1)
                # print('node2:', node_2)
                graph[node_1].add((node_2, cost))
                graph[node_1].remove((node_0, cost_1))
                graph[node_2].add((node_1, cost))
                graph[node_2].remove((node_0, cost_2))
                remove_list.append(node_0)
                changed = True
        # print(changed)
        for node in remove_list:
            del graph[node]
        if not changed:
            reduced = True    

    return graph

def get_distance(start, end):
    x0, y0 = start
    x, y = end
    return np.sqrt((x-x0)**2 + (y-y0)**2)

# def shortest_walk(graph, food_locations):
#     paths = {}

#     for i, start in enumerate(food_locations):
#         cost = 0
#         paths[start] = {}
#         for end in food_locations[i+1:]:
#             node = start
#             while node != end:
#                 for coordinate in graph[node]:
                    
#                     shortest_dist = get_distance(coordinate, end)
#                     paths[coordinate] = 
                    


    
    return paths

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
    for i in range(n):
        x0, y0 = food_locations[i]
        for j in range(i+1, n):
            x, y = food_locations[j]
            D[i, j] = np.sqrt((x - x0)**2 + (y - y0)**2)
            D[j, i] = D[i, j]
    return D

if __name__ == '__main__':
    tokyo_coords_to_text()