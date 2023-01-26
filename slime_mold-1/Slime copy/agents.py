from mesa import Agent
import numpy as np
import random


class FoodAgent(Agent):
    def __init__(self, unique_id, model, position):
        super().__init__(unique_id, model)
        self.pos = position
    
    def update_chem(self):
        for cell in self.model.grid.coord_iter():
            _, x, y = cell
            x_y_dist = np.abs(np.subtract((x, y), self.pos))
            dist = np.sqrt(np.sum(x_y_dist**2))
            self.model.chem_values[x,y] += 1 / ((dist + 1)**2)


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
    def __init__(self, unique_id, model, parent_id):
        super().__init__(unique_id, model)
        self.active = True
        self.chem = 0
        self.parent_id = parent_id
        self.paths = {parent_id}

    def multiply(self, new_position):
        '''
        The agent checks the surrounding cells for the highest concentration
        of chemical and multiplies towards there.
        '''

        self.model.slime_locations.append(new_position)
        new_slime = SlimeAgent(self.model.next_id(), self.model, self.parent_id)

        self.model.grid.place_agent(new_slime, new_position)
        self.model.schedule.add(new_slime)
            
    def create_hub(self, position):
        new_hub = FoodAgent(self.model.next_id(), self.model, position)
        self.model.grid.place_agent(new_hub, position)
        new_hub.update_chem()
        self.model.hub_locations.append(position)

    def step(self):
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True)
        chem_values = np.zeros(len(neighborhood))
        indices = np.arange(len(neighborhood), dtype=int)
        for i, coordinate in enumerate(neighborhood):
            x, y = coordinate
            chem_values[i] = self.model.chem_values[x,y]


        n_branches = 1
        if self.model.schedule.steps == 0:
            n_branches = 4
        elif np.random.uniform() < 0.075:
            n_branches = 2

        p_array = chem_values**2 / sum(chem_values**2)
        indices =  np.random.choice(indices, p=p_array, size=n_branches)

        new_positions = [neighborhood[index] for index in indices]
        for new_position in new_positions:
            slime_on_cell = list(filter(lambda agent: type(agent) is SlimeAgent, self.model.grid.get_cell_content(new_position)))
            new_position = (int(new_position[0]), int(new_position[1]))
            # future_neighbors = self.model.grid.get_neighbors(new_position, moore=True)
            # future_neighbors = list(filter(lambda slime: isinstance(slime, SlimeAgent) and slime.parent_id != self.parent_id, future_neighbors))
            if len(slime_on_cell) > 0 and self.parent_id not in slime_on_cell[0].paths:
                self.create_hub(new_position)

            # elif not any([isinstance(agent, SlimeAgent) for agent in future_neighbors]):
            else:
                self.multiply(new_position)
            
            # Prevent removal from schedule by returning of no actions have been performed
            # else:
            #     return
            
        self.active = False
        self.model.schedule.remove(self)
