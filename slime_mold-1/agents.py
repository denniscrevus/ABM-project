from helpers import get_distance
from mesa import Agent
import numpy as np
import random

class FoodAgent(Agent):
    """Agent type that is responsible for setting up the chemical environment in the model."""
    def __init__(self, unique_id, model, position):
        """
        Initialize food agents

        Args:
            unique_id: unique id of the agent (int).
            model: SlimeModel object that the agent is part of.
            position: tuple of (x (int), y (int)) position of the food agent in the grid.
        """
        super().__init__(unique_id, model)
        self.pos = position
        self.update_chem()

    def update_chem(self):
        """Function that updates the chemical environment to create force of attraction towards itself."""
        for _, x, y in self.model.grid.coord_iter():
            x_y_dist = np.abs(np.subtract((x, y), self.pos))
            dist = np.sqrt(np.sum(x_y_dist**2))
            self.model.chem_values[x,y] += self.model.signal_strength / ((dist + 1)**2)


class SlimeAgent(Agent):
    """Agent type that is responsible for formation of networks in the model."""
    def __init__(self, unique_id, model, parent_location, origin=False):
        """
        Initialize slime agents.

        Args:
            unique_id: unique id of the agent (int).
            model: SlimeModel object that the agent is part of.
            parent_location: location from which the new agent is generated.
            origin: tuple of (x, y) coordinates indicating from which coordinate it was generated (int, int); default is False.
        """
        super().__init__(unique_id, model)
        self.previous_pos = parent_location
        self.origin = origin

    def multiply(self, coordinate):
        """
        Generate a new slime agent at a specific location.
        
        Args:
            coordinate: tuple of (x, y) coordinates where new SlimeAgent object will be placed (int, int).
        """
        # Create slime, update connections, and add to grid and schedule.
        new_slime = SlimeAgent(self.model.next_id(), self.model, self.pos)
        cost = get_distance(self.pos, coordinate)
        self.model.connections[coordinate] = ({(self.pos, cost)})
        self.model.connections[self.pos].add((coordinate, cost))
        self.model.grid.place_agent(new_slime, coordinate)
        self.model.schedule.add(new_slime)
    
    def connect(self, coordinate):
        """
        Connect current location to specified location.
        
        Args:
            coordinate: tuple of (x, y) coordinates to connect with.
        """
        # Add new coordinate to set of connected coordinates and vice versa.
        cost = get_distance(self.pos, coordinate)
        self.model.connections[self.pos].add((coordinate, cost))
        self.model.connections[coordinate].add((self.pos, cost))

    def step(self):
        """
        Function that advances a slime agent one step. 
        This step consists of multiplying and connecting to neighbouring slime agents.
        """
        # Get neighborhood and remove coordinate current slime Agent was generated from to prevent later "self-connecting".
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True)
        if not self.origin:
            neighborhood.remove(self.previous_pos)

        # Divide neighborhood in two sets of coordinates that do and do not contain slime cells
        empty_cells, occupied_cells = self.model.divide_neighborhood(neighborhood, SlimeAgent)
        n = len(empty_cells)

        # Go through multiplying steps if there are slime-free grid cells in the neighborhood
        if n != 0:

            # Determine if branching off takes place
            if self.origin:
                n_branches = 4
            elif np.random.uniform() < self.model.p_branch and n > 1:
                n_branches = 2
            else:
                n_branches = 1

            # Apply noise to attraction by neighbouring empty grid cells
            noise = np.random.normal(0, self.model.noise, size=n)
            order = []

            for i, coordinate in enumerate(empty_cells):
                x, y = coordinate
                chem_value = self.model.chem_values[x,y] + noise[i]
                order.append((chem_value, coordinate))

            order.sort(reverse=True)
            new_positions = [order[i] for i in range(n_branches)]

            # Multiply and keep track of connections
            for _, new_position in new_positions:
                self.multiply(new_position)

        # Go through connecting steps if there are slime-occupied grid cells in the nighborhood
        if len(occupied_cells) > 0 and np.random.uniform() < self.model.p_connect:
            
            # Pick random neighbouring slime agent (location) and update connections
            coordinate = random.sample(occupied_cells, 1)[0]
            self.connect(coordinate)

        # Each slime agent goes through one cycle of multiplying/connecting
        self.model.schedule.remove(self)
