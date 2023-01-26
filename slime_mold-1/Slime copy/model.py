from agents import ChemAgent, FoodAgent, SlimeAgent
import math
from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
import random
from scipy.spatial.distance import pdist
from helpers import text_to_coords

# from sklearn.neighbors import DistanceMetric

'''Here we define functions applied at the model-wide scale'''

class Grid(MultiGrid):
    def __init__(self, width, height, torus=False):
        super().__init__(width, height, torus=False)

    def get_cell_content(self, coordinate):
        x, y = coordinate
        return self.grid[x][y]


class SlimeModel(Model):
    '''
    A model with some number of slime and ubiquitous chemical

    Args:
    width -- grid width (int)
    height -- grid height (int)
    '''
    def __init__(self, width, height, N):
        '''Initialize the model'''

        super().__init__()
        self.grid = Grid(width, height, torus=False)
        self.schedule = BaseScheduler(self)
        self.running = True
        self.origin = (width // 2, height // 2)
        self.slime_locations = []

        random_x = np.random.randint(0, width, size=N)
        random_y = np.random.randint(0, height, size=N)

        for i in range(N):
            # Transform to regular int type instead of numpy int32 type as mesa cannot handle numpy ints
            x, y = int(random_x[i]), int(random_y[i])
            slime = SlimeAgent(self.next_id(), self, i)
            self.schedule.add(slime)
            
            self.grid.place_agent(slime, (x, y))
            self.slime_locations.append((x, y))
        
        self.food_sources = []
        self.food_locations = []
        self.hub_locations = []
        self.chem_values = np.zeros((width, height))

        # Place food sources on city locations
        # food_coords = text_to_coords('tokyo_coords.txt')
        # for x, y in food_coords:
        #     food = FoodAgent(self.next_id(), self, (x, y))
        #     self.grid.place_agent(food, (x, y))
        #     self.food_sources.append(food)
        #     self.food_locations.append((x, y))
        #     food.update_chem()
        
        food = FoodAgent(self.next_id(), self, self.origin)
        self.grid.place_agent(food, self.origin)
        self.food_sources.append(food)
        self.food_locations.append(self.origin)
        food.update_chem()

        # Initialize datacollector
        model_reporters = {'chem': 'chem_values'}
        # agent_reporters = {'active': ''}
        self.datacollector = DataCollector(model_reporters=model_reporters, agent_reporters={})


    def get_slimeless_neighborhood(self, neighborhood):
        slimeless_cells = []
        for cell in neighborhood:
            agents = self.grid.get_cell_content(cell)
            if not any(isinstance(agent, SlimeAgent) for agent in agents):
                slimeless_cells.append(cell)
        return slimeless_cells


    def step(self):
        '''Advances the model by one step'''
        self.datacollector.collect(self)
        self.added_slime_locations = []
        self.schedule.step()


        