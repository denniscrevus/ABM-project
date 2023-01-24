from agents import SlimeAgent, ChemAgent
import math
from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
import random
from scipy.spatial.distance import pdist
# from sklearn.neighbors import DistanceMetric

'''Here we define functions applied at the model-wide scale'''

# def compute_total_chemical(model):
#     agent_chems = [agent.chem for agent in model.schedule.agents if isinstance(agent, ChemAgent)]
#     return sum(agent_chems)

def compute_distance_matrix(model):
    agent_pos = [agent.pos for agent in model.schedule.agents if isinstance(agent, SlimeAgent)]
    agent_pos = [list(tup) for tup in agent_pos]
    dist_mat = pdist(agent_pos)
    return np.average(dist_mat)

def compute_average_dist(dist_mat):
    return np.average(dist_mat)


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

        slime = SlimeAgent(self.next_id(), self)
        self.schedule.add(slime)
        
        self.grid.place_agent(slime, self.origin)

        # Food spawn
        x = self.random.randrange(self.grid.width)
        y = self.random.randrange(self.grid.height)
        x = 55
        y = 55
        global basecoord
        global newslime
        basecoord = [x, y]
        base = ChemAgent(self.next_id(), self)
        # self.schedule.add(base)
        self.grid.place_agent(base, (x, y)) # spawn
        base.chem = 1

        for coord in self.grid.coord_iter():
            coord_content, x, y = coord # pull contents, x/y pos from coord obj
            a = ChemAgent(self.next_id(), self) # instantiate a chem agent
            areacoord = [x, y]
            if math.dist(basecoord, areacoord) != 0:
                a.chem = 1/math.dist(basecoord, areacoord)*base.chem*0.95
                if (a.chem < 0.25):
                    a.chem = 0
            # self.schedule.add(a) # add to the schedule
            self.grid.place_agent(a, (x, y)) # spawn the chem agent

        # Initialize datacollector
        self.datacollector = DataCollector(model_reporters={"Average_Distance": compute_distance_matrix})
                                        #    agent_reporters={"Chem": "chem"}


    def get_slimeless_neighborhood(self, neighborhood):
        slimeless_cells = []
        for cell in neighborhood:
            agents = self.grid.get_cell_content(cell)
            if not any(isinstance(agent, SlimeAgent) for agent in agents):
                slimeless_cells.append(cell)
        return slimeless_cells


    def step(self):
        '''Advances the model by one step'''
        # self.validate()
        self.datacollector.collect(self)
        self.schedule.step()
        print(len(self.schedule.agents))
        # print(vars(self.schedule))
        