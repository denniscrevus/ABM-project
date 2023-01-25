from mesa import Agent
import numpy as np
import random

class FoodAgent(Agent):
    def __init__(self, unique_id, model, position):
        super().__init__(unique_id, model)
        self.pos = position


class ChemAgent(Agent):
    '''
    An agent representing chemical concentration. This will be spawned in
    every gridspace and hold a float value representing chemical concentration.
    '''
    def __init__(self, unique_id, model, chem_value, position):
        super().__init__(unique_id, model)
        self.chem = chem_value
        self.pos = position


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
        possible_positions = self.model.get_slimeless_neighborhood(neighborhood)

        # If no free spaces around slime, stop
        n_free_cells = len(possible_positions)
        if len(possible_positions) == 0:
            return

        index_array = np.arange(n_free_cells, dtype=int)
        p_array = np.zeros(n_free_cells)
        chem_values = np.zeros(n_free_cells)
        for i, coordinate in enumerate(possible_positions):
            x, y = coordinate
            chem_values[i] = self.model.chem_values[x,y]
        
        p_array = chem_values**2 / sum(chem_values**2)

        n_branches = 1
        if self.model.schedule.steps == 0:
            n_branches = 4
        elif np.random.uniform() < 0.075 and n_free_cells > 1:
            n_branches = 2

        # distances = self.dist_to_origin(possible_positions) ** 2
        # p = distances / np.sum(distances)
        # possible_indices = np.arange(n_free_cells, dtype=int)
        cell_indices = np.random.choice(index_array, size=n_branches, p=p_array)    
        new_positions = [possible_positions[index] for index in cell_indices]
        # valid_positions = list(filter(lambda position: not any(isinstance(self.model.grid.grid[position[0]][position[1]], SlimeAgent)), new_positions))
        self.model.added_slime_locations.extend(new_positions)
        for new_position in new_positions:
            # x, y = new_position
            content = self.model.grid.get_cell_content(new_position)
            if any([isinstance(FoodAgent, type(agent)) for agent in content]):
                new_slime = SlimeAgent(self.model.next_id(), self.model)

                self.model.grid.place_agent(new_slime, new_position)
                return


            new_slime = SlimeAgent(self.model.next_id(), self.model)

            self.model.grid.place_agent(new_slime, new_position)
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
