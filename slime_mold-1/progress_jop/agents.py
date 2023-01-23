from mesa import Agent
import numpy as np
import random


class ChemAgent(Agent):
    '''
    An agent representing chemical concentration. This will be spawned in
    every gridspace and hold a float value representing chemical concentration.
    '''
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.chem = 0.01

    def diffuse(self):
        #figure out how many neighbors you have
        n_neighbors = len(self.model.grid.get_neighbors(self.pos,
                                                      moore=True,
                                                      include_center=False))
        #amount to diffuse into each neighbor. at first, just divided total
        #self.chem by neighbors, but then each cell loses all of it's chem.
        #so, now, only 1/2 of the total val leaks out. we can tweak this.
        #but seems to work better to multiply by some scalar < 1.

        amt_per_neighbor = 0.5*(self.chem/n_neighbors)

        for neighbor in self.model.grid.get_neighbors(self.pos, moore=True, include_center=False):
            if isinstance(neighbor, ChemAgent):
                neighbor.chem += amt_per_neighbor
                self.chem -= amt_per_neighbor

    def evaporate(self):
        '''All chem agents lose chemical at 0.005 per step'''
        evap_rate = 0.01
        if self.chem > evap_rate: # so that self.chem stays pos
            self.chem -= evap_rate
        else:
            self.chem = 0

    def step(self):
        '''
        The agent shares chemical with surrounding cells through diffusion.
        Chemical is also lost due to evaporation.
        '''
        
        self.diffuse()
        self.evaporate()


class SlimeAgent(Agent):
    '''
    An agent that excretes chemical, senses, and moves towards higher chemical
    concentration. This agent represents a single slime mold cell.
    '''
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.active = True
        self.chem = 0

    def multiply(self):
        '''
        The agent checks the surrounding cells for the highest concentration
        of chemical and multiplies towards there.
        '''
        # neighbors = self.model.grid.get_neighbors(self.pos, moore=True)
        # chems = filter_agent_type(neighbors, ChemAgent)
        # chem_values = [(i, chem.chem) for i, chem in enumerate(chems)]
        # chem_found = False
        # curIndex = 0
        # idx = 0
        # temp = 0
        # while(curIndex < len(neighborhood)):
        #     if(temp < neighborhood[curIndex].chem):
        #         temp = neighborhood[curIndex].chem  # save the objattr
        #         idx = curIndex  # save the idx
        #     curIndex += 1  # increment idx
        # optimal = neighborhood[idx]  # assign obj w/ said index

        # new_position = optimal.pos  # identify the position of the optimal obj
        # print(new_position)
        # global basecoord
        # if (new_position == basecoord):
        #     self.food = True
        #     print('food found!')
        # self.model.grid.move_agent(self, new_position)

        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True)
        possible_positions = self.model.get_slimeless_neighborhood(neighborhood)

        # If no free spaces around slime, stop
        n_free_cells = len(possible_positions)
        if len(possible_positions) == 0:
            return

        neighbor_lists = [self.model.grid.get_cell_content(cell) for cell in possible_positions]
        all_neighbors = [neighbor for neighbors in neighbor_lists for neighbor in neighbors]
        chem_agents = list(filter(lambda agent: type(agent) is ChemAgent, all_neighbors))
        chem_values = [chem.chem for chem in chem_agents]

        if sum(chem_values) > 0:
            new_positions = [chem_agents[np.argmax(chem_values)].pos]
            n_branches = 1
        else:
            
            n_branches = 1
            if self.model.schedule.steps == 0:
                n_branches = 4
            elif np.random.uniform() < 0.075 and n_free_cells > 1:
                n_branches = 2

            distances = self.dist_to_origin(possible_positions) ** 2
            p = distances / np.sum(distances)
            possible_indices = np.arange(n_free_cells, dtype=int)
            cell_indices = np.random.choice(possible_indices, size=n_branches, p=p)    
            new_positions = [possible_positions[index] for index in cell_indices]

        for i in range(n_branches): 
            new_slime = SlimeAgent(self.model.next_id(), self.model)

            self.model.grid.place_agent(new_slime, new_positions[i])
            self.model.schedule.add(new_slime)
    
    
    def dist_to_origin(self, neighborhood):
        x0, y0 = self.model.origin
        distances = np.zeros(len(neighborhood))
        for i, cell in enumerate(neighborhood):
            x, y = cell
            distances[i] = abs(x - x0) + abs(y - y0)
        return distances


    def step(self):
        if self.active:
            self.multiply()
            self.active = False
            self.model.schedule.remove(self)
        # if np.random.uniform() <= 0.5:
        #     self.secrete()