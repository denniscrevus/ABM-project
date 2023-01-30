import copy
from helpers import get_distance
from mesa import Agent
import numpy as np
import random

class FoodAgent(Agent):
    def __init__(self, unique_id, model, position):
        super().__init__(unique_id, model)
        self.pos = position
        self.found_by = None

    def update_chem(self):
        for _, x, y in self.model.grid.coord_iter():
            x_y_dist = np.abs(np.subtract((x, y), self.pos))
            dist = np.sqrt(np.sum(x_y_dist**2))
            self.model.chem_values[x,y] += self.model.signal_strength / ((dist + 1)**2)


class SlimeAgent(Agent):
    '''
    An agent that excretes chemical, senses, and moves towards higher chemical
    concentration. This agent represents a single slime mold cell.
    '''
    def __init__(self, unique_id, model, direction, prev_pos, origin=False):
        super().__init__(unique_id, model)
        self.active = True
        self.chem = 0
        self.direction = direction
        self.node = False
        self.previous_pos = prev_pos
        self.origin = origin

    def neighborhood_from_direction(self):
        neighborhood = []
        for x, y in self.model.directions[self.direction]:
            x0, y0 = self.pos
            coordinate = (x0 + x, y0 + y)
            if not self.model.grid.out_of_bounds(coordinate):
                neighborhood.append(coordinate)
        return neighborhood

    def multiply(self, coordinate):
        '''
        The agent checks the surrounding cells for the highest concentration
        of chemical and multiplies towards there.
        '''
        x0, y0 = self.pos
        x, y = coordinate
        direction = (x-x0, y-y0)
    
        new_slime = SlimeAgent(self.model.next_id(), self.model, direction, self.pos)

        self.model.added_slime_locations.append(coordinate)
        self.model.grid.place_agent(new_slime, coordinate)
        self.model.slime_cells.append(new_slime)
        self.model.schedule.add(new_slime)
    
    def step(self):

        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True)
        if not self.origin:
            neighborhood.remove(self.previous_pos)

        # Divide neighborhood in two sets of coordinates that do and do not contain slime cells
        empty_cells, occupied_cells = self.model.divide_neighborhood(neighborhood, SlimeAgent)

        n = len(empty_cells)
        noise = np.random.normal(0, self.model.noise, size=n)
        order = []
        
        for i, coordinate in enumerate(empty_cells):
            x, y = coordinate
            chem_value = self.model.chem_values[x,y] + noise[i]
            order.append((chem_value, (x, y)))

        order.sort(reverse=True)
        
        n_branches = 1

        # Allow four initial branches at first reproduction step
        if self.model.schedule.steps == 0:
            n_branches = 4
        elif np.random.uniform() < self.model.p_branch and n > 1:
            n_branches = 2

        if n != 0:
            new_positions = [order[i] for i in range(n_branches)]
            for _, new_position in new_positions:
                self.multiply(new_position)
                cost = get_distance(self.pos, new_position)
                self.model.connections[new_position] = ({(self.pos, cost)})
                self.model.connections[self.pos].add((new_position, cost))

        if len(occupied_cells) > 0 and np.random.uniform() < self.model.p_connect:
            connection = random.sample(occupied_cells, 1)[0]
            cost = get_distance(self.pos, connection)
            self.model.connections[self.pos].add((connection, cost))
            self.model.connections[connection].add((self.pos, cost))

        self.model.schedule.remove(self)


