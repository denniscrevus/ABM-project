from matplotlib import animation, cm, colors
import matplotlib.pyplot as plt
import numpy as np
from agents import *
from helpers import reduce_graph, get_distance_matrix
from model import *
from tokyo_mapping import *
from analyze_graph import *


def plot_result(graph, show_all=True, show_shortest=True):
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


size = 100
p_branch = 0.075
p_connect = 0.1
signal_strength = 1
noise = 0.05 * signal_strength
model = SlimeModel(size, size, p_branch, p_connect, signal_strength, noise)

# cmap = cm.get_cmap('Greens')
# norm = colors.Normalize(vmin = np.min(model.chem_values), vmax=np.max(model.chem_values))
# image_colors = []
# # print(image_colors)
# for x in range(size):
#     image_colors.append([])
#     for y in range(size):
#         image_colors[x].append(cmap(norm(model.chem_values[x,y])))
#     print(image_colors[x])
# images.append([plt.imshow(image_colors)])
# image_colors[size//2][size//2] = (255/255, 242/255, 0, 1)
# images = [[plt.imshow(image_colors)]]

for i in range(200):
    # print(i)
    model.step()
    # print(i)
#     for location in model.added_slime_locations:
#         x, y = location
#         image_colors[x][y] = (255/255, 242/255, 0, 1) # yellow: (255/255, 242/255, 0, 1), darker yellow: (213/255, 184/255, 90/255, 1)
#     images.append([plt.imshow(image_colors)])
# slime_x = []
# slime_y = []

food_locations = [model.food_locations[n] for n in model.food_locations]
graph = reduce_graph(model.connections, model.food_locations.values())
nx_graph = convert_result_to_graph(graph)
shortest_paths = get_all_shortest_paths(nx_graph, food_locations)

# print(len(graph))
# D = get_distance_matrix(model.food_locations)
# raise NotImplementedError




plot_result(graph)


# for slime_cell in model.slime_cells:
#     x0, y0 = slime_cell.origin
#     x, y = slime_cell.pos
#     slime_x.append(x0)
#     slime_y.append(y0)
#     # images.append([plt.plot([x0, x], [y0, y], color='yellow')])
#     plt.plot([x0, x], [y0, y], color=(213/255, 184/255, 90/255, 1), lw=.25)
# plt.scatter(slime_x, slime_y, color=(213/255, 184/255, 90/255, 1), linewidths=0, s=0.25)
# ani = animation.ArtistAnimation(fig, images, interval=3, blit=True, repeat_delay=1000)

# writer = animation.PillowWriter(fps=30,
#                                 metadata=dict(artist='Me'),
#                                 bitrate=1800)
# ani.save('slime.gif', writer=writer)
# ani.save('slime.mp4')
# print(vars(model.datacollector))
# data = model.datacollector.get_model_vars_dataframe()

# print(vars(model.datacollector))
