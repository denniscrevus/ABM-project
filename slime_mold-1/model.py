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
    def __init__(self, width, height):
        '''Initialize the model'''

        super().__init__()
        self.grid = Grid(width, height, torus=False)
        self.schedule = BaseScheduler(self)
        self.running = True
        self.origin = (width // 2, height // 2)
        self.slime_locations = []
        slime = SlimeAgent(self.next_id(), self)
        self.schedule.add(slime)
        
        self.grid.place_agent(slime, self.origin)
        self.added_slime_locations = [self.origin]
        self.food_sources = []
        self.chem_values = np.zeros((width, height))

        # Place food sources on city locations
        food_coords = text_to_coords('tokyo_coords.txt')
        for x, y in food_coords:
            food = FoodAgent(self.next_id(), self, (x, y))
            self.grid.place_agent(food, (x, y))
            self.food_sources.append(food)

        for cell in self.grid.coord_iter():
            _, x, y = cell
            chem_value = 0
            for food_source in self.food_sources:
                x_y_dist = np.abs(np.subtract((x, y), food_source.pos))
                dist = np.sqrt(np.sum(x_y_dist**2))
                chem_value += 1 / ((dist + 1)**2)

            self.chem_values[x,y] = chem_value
            
            chemical = ChemAgent(self.next_id(), self, chem_value, (x, y))
            # if math.dist(basecoord, areacoord) != 0:
            #     a.chem = 1/math.dist(basecoord, areacoord)*base.chem*0.95
            #     if (a.chem < 0.25):
            #         a.chem = 0
            self.grid.place_agent(chemical, (x, y))

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


        