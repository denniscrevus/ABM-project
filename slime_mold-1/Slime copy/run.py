from matplotlib import animation, cm, colors, rc
import matplotlib.pyplot as plt
import numpy as np
from agents import *
from model import *
from tokyo_mapping import *

size = 100
N_agents = 5
N_steps = 50
model = SlimeModel(size, size, N_agents)


cmap = cm.get_cmap('Greens')
norm = colors.Normalize(vmin = np.min(model.chem_values), vmax=np.max(model.chem_values))
image_colors = np.zeros((size, size))
fig, ax = plt.subplots()


image_colors = cmap(norm(model.chem_values))
images = [image_colors]

for i in range(N_steps):
    model.step()

    image_colors = cmap(norm(model.chem_values))

    for location in model.added_slime_locations:
        x, y = location
        image_colors[x][y] = (255/255, 242/255, 0, 1) # yellow: (255/255, 242/255, 0, 1), darker yellow: (213/255, 184/255, 90/255, 1)

    for x, y in model.slime_locations:
        image_colors[x][y] = (255/255, 242/255, 0, 1) # RGBA for yellow

    for x, y in model.food_locations:
        image_colors[x][y] = (0, 100/255, 0, 1) # RGBA for dark green

    for x, y in model.hub_locations:
        image_colors[x][y] = (0, 0, 1, 1) # RGBA for blue

    images.append(np.copy(image_colors))


im_plot = plt.imshow(image_colors)

def anim_step(frame):
    im_plot.set_data(frame)

    return im_plot,


anim = animation.FuncAnimation(fig, anim_step, images, blit=True)

anim.save("anim.html", writer=animation.HTMLWriter())
