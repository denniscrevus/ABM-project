from matplotlib import animation, cm, colors
import matplotlib.pyplot as plt
import numpy as np
from agents import *
from model import *
from tokyo_mapping import *

size = 100
N = 5
model = SlimeModel(size, size, N)


cmap = cm.get_cmap('Greens')
norm = colors.Normalize(vmin = np.min(model.chem_values), vmax=np.max(model.chem_values))
image_colors = []
fig, ax = plt.subplots()

# print(image_colors)
# for x in range(size):
#     image_colors.append([])
#     for y in range(size):
#         image_colors[x].append(cmap(norm(model.chem_values[x,y])))

# images = [[ax.imshow(image_colors)]]

for i in range(50):
    # print(i)
    model.step()
    # print(model.added_slime_locations)
    # for location in model.added_slime_locations:
    #     print(location)
    #     x, y = location
    #     image_colors[x][y] = (255/255, 242/255, 0, 1) # yellow: (255/255, 242/255, 0, 1), darker yellow: (213/255, 184/255, 90/255, 1)
    # images.append([ax.imshow(image_colors)])
for x in range(size):
    image_colors.append([])
    for y in range(size):
        image_colors[x].append(cmap(norm(model.chem_values[x,y])))

for x, y in model.slime_locations:
    image_colors[x][y] = (255/255, 242/255, 0, 1) # RGBA for yellow

for x, y in model.food_locations:
    image_colors[x][y] = (0, 100/255, 0, 1) # RGBA for dark green

for x, y in model.hub_locations:
    image_colors[x][y] = (0, 0, 1, 1) # RGBA for blue





# ani = animation.ArtistAnimation(fig, images, interval=1, blit=True,
#                                 repeat_delay=1000)

# writer = animation.PillowWriter(fps=30,
#                                 metadata=dict(artist='Me'),
#                                 bitrate=1800)
# ani.save('slime.gif', writer=writer)
# ani.save('slime.mp4')        
# print(vars(model.datacollector))
# data = model.datacollector.get_model_vars_dataframe()

plt.imshow(image_colors)
plt.show()
# print(vars(model.datacollector))
