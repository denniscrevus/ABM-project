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

    # def evaporate(self):
    #     '''All chem agents lose chemical at 0.005 per step'''
    #     evap_rate = 0.01
    #     if self.chem > evap_rate: # so that self.chem stays pos
    #         self.chem -= evap_rate
    #     else:
    #         self.chem = 0

    def step(self):
        '''
        The agent shares chemical with surrounding cells through diffusion.
        Chemical is also lost due to evaporation.
        '''
        pass
        # self.diffuse()
        # self.evaporate()


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
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True)

        slimeless_neighborhood = self.model.get_slimeless_neighborhood(neighborhood)
        n_free_cells = len(slimeless_neighborhood)
        if n_free_cells > 0:
            
            n_branches = 1
            if self.model.schedule.steps == 0:
                n_branches = 4
            elif np.random.uniform() < 0.05 and n_free_cells > 1:
                n_branches = 2

            distances = self.dist_to_origin(slimeless_neighborhood) ** 2
            p = distances / np.sum(distances)
            cell_indices = np.arange(n_free_cells, dtype=int)
            cell_index = np.random.choice(cell_indices, size=n_branches, p=p)    
 
            for i in range(n_branches): 
                new_slime = SlimeAgent(self.model.next_id(), self.model)
                self.model.grid.place_agent(new_slime, slimeless_neighborhood[cell_index[i]])
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