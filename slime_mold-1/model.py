from agents import FoodAgent, SlimeAgent
import math
from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np

# from sklearn.neighbors import DistanceMetric

'''Here we define functions applied at the model-wide scale'''

class Grid(MultiGrid):
    def __init__(self, width, height, torus=False):
        super().__init__(width, height, torus=False)

    def get_cell_content(self, coordinate):
        x, y = coordinate
        return self.grid[x][y]

    def contains_slime(self, coordinate):
        x, y = coordinate
        return any(isinstance(agent, SlimeAgent) for agent in self.grid[x][y])


class SlimeModel(Model):
    '''
    A model with some number of slime and ubiquitous chemical

    Args:
    width -- grid width (int)
    height -- grid height (int)
    '''
    def __init__(self, width, height, p_branch, p_connect,signal_strength,
                    noise, food_coords):
        '''Initialize the model'''

        super().__init__()
        # Initialise model parameters
        self.width = width
        self.height = height
        self.p_branch = p_branch
        self.p_connect = p_connect
        self.signal_strength = signal_strength
        self.noise = noise

        # Initialise grid and starting agents
        self.grid = Grid(width, height, torus=False)
        self.schedule = BaseScheduler(self)
        self.running = True
        self.origin = (width // 2, height // 2)
        slime = SlimeAgent(self.next_id(), self, (0, 0), self.origin, origin=True)
        self.schedule.add(slime)

        self.grid.place_agent(slime, self.origin)
        self.added_slime_locations = [self.origin]
        self.connections = {self.origin: set()}

        self.food_locations = {}
        self.chem_values = np.zeros((width, height))

        for i, coordinate in enumerate(food_coords):
            food = FoodAgent(self.next_id(), self, coordinate)
            self.grid.place_agent(food, coordinate)
            self.food_locations[i] = coordinate
            food.update_chem()

        self.paths = []

    def run(self, N_steps):
        for _ in range(N_steps):
            self.step()

        return self.connections

    def divide_neighborhood(self, neighborhood, agent_type):
        empty_cells = []
        occupied_cells = []
        for cell in neighborhood:
            agents = self.grid.get_cell_content(cell)
            if not any(isinstance(agent, agent_type) for agent in agents):
                empty_cells.append(cell)
            else:
                occupied_cells.append(cell)
        return empty_cells, occupied_cells

    def step(self):
        '''Advances the model by one step'''
        self.added_slime_locations = []
        self.schedule.step()




