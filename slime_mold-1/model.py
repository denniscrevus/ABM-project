from agents import FoodAgent, SlimeAgent
from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import MultiGrid
import numpy as np


class Grid(MultiGrid):
    """Extension of mesa.MultiGrid class to include a custom method."""
    def __init__(self, width, height, torus=False):
        """
        Initiate a custom MultiGrid.

        Args:
            width: width of the grid (int).
            height: height of the grid (int).
            torus: Boolean indicating whether the grid wraps around or not; default False.
        """
        super().__init__(width, height, torus=torus)

    def get_cell_content(self, coordinate):
        """
        Function that returns all agents on a given grid cell.

        Args:
            coordinate: tuple of (x, y) coordinates (int, int)

        Returns:
            list of Agent objects.
        """
        x, y = coordinate
        return self.grid[x][y]


class SlimeModel(Model):
    """Model for simulating slime network formation."""

    def __init__(self, width, height, p_branch, p_connect, signal_strength, noise, food_coords):
        """
        Initiate the model.

        Args:
            width: grid width (int)
            height: grid height (int)
            p_branch: probability of generating 2 new SlimeAgents (float)
            p_connect: probability of connecting to a neighbouring SlimeAgent (float)
            signal_strength: Base attraction strength of food source (float)
            noise: Strength of noise in attraction strength (int/float)
            food_coords: list of (x, y) coordinates to place food sources on (int, int)
        """
        # Initialise model parameters
        super().__init__()

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
        slime = SlimeAgent(self.next_id(), self, self.origin, origin=True)
        self.schedule.add(slime)

        self.grid.place_agent(slime, self.origin)
        self.connections = {self.origin: set()}

        self.food_locations = {}
        self.chem_values = np.zeros((width, height))

        # Initiate food agents
        for i, coordinate in enumerate(food_coords):
            food = FoodAgent(self.next_id(), self, coordinate)
            self.grid.place_agent(food, coordinate)
            self.food_locations[i] = coordinate

    def get_connections(self):
        """Returns the dictionary representing the entire network."""
        return self.connections

    def run(self, N_steps):
        """
        Main function that runs the model for N steps.

        Args:
            N_steps: Amount of steps to run the model (int).

        Returns:
            self.connections: dictionary containing locations (x, y) coordinates corresponding to Slime Agent positions as keys
                              and sets of ((x, y), cost) tuples as values representing connected Slime Agents.
        """
        for _ in range(N_steps):
            self.step()

        return self.connections

    def divide_neighborhood(self, neighborhood, agent_type):
        """
        Function to divide a neighbourhood into two neighborhoods based on the presence/absence of a specified agent type.

        Args:
            neighborhood: list of coordinates that make up the neighborhood.
            agent_type: class of the agent to base division on.

        Returns:
            empty_cells: list of coordinates from initial neighborhood on which specified agent type is not present.
            occupied_cells: list of coordinates from initial neighborhood on which specified agent type is present.
        """
        empty_cells = []
        occupied_cells = []

        # check every cell in neighborhood for presence of agent type.
        for cell in neighborhood:
            agents = self.grid.get_cell_content(cell)
            if any(isinstance(agent, agent_type) for agent in agents):
                occupied_cells.append(cell)
            else:
                empty_cells.append(cell)
        return empty_cells, occupied_cells

    def step(self):
        """Advances the model by one step."""
        self.schedule.step()
