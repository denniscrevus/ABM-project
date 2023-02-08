from IPython.display import clear_output
import SALib
from SALib.sample import saltelli
from model import SlimeModel
from agents import SlimeAgent, FoodAgent
from analyze_graph import *
from mesa.batchrunner import BatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

def plot_param_var_conf(ax, df, var, param, i):
    """
    Helper function for plot_all_vars. Plots the individual parameter vs
    variables passed.

    Args:
        ax: the axis to plot to
        df: dataframe that holds the data to be plotted
        var: variables to be taken from the dataframe
        param: which output variable to plot
    """
    x = df.groupby(var).mean().reset_index()[var]
    y = df.groupby(var).mean()[param]

    replicates = df.groupby(var)[param].count()
    err = (1.96 * df.groupby(var)[param].std()) / np.sqrt(replicates)

    ax.plot(x, y, c='k')
    ax.fill_between(x, y - err, y + err)

    ax.set_xlabel(var)
    ax.set_ylabel(param)

def plot_all_vars(df, param, problem):
    """
    Plots the parameters passed vs each of the output variables.

    Args:
        df: dataframe that holds all data
        param: the parameter to be plotted
    """

    f, axs = plt.subplots(3, figsize=(7, 10))
    
    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs[i], data[var], var, param, i)

def do_plots(param, data, problem):
    for param in ('graph_len'):
        plot_all_vars(data, param, problem)
        plt.show()

def OFAT():
    # We define our variables and bounds
    problem = {
        'num_vars': 3,
        'names': ['p_branch', 'p_connect', 'signal_strength', 'noise'],
        'bounds': [[0.1, 0.5], [0.1, 0.5], [7, 15], [0.75, 1.5]]
    }

    # Set the repetitions, the amount of steps, and the amount of distinct values per variable
    replicates = 1
    max_steps = 200
    distinct_samples = 1

    # Set the outputs
    food_coords = text_to_coords("tokyo_coords.txt")
    model_reporters = {"Graph size": lambda m: convert_result_to_graph(reduce_graph(m.get_connections(), food_coords)).size(weight="weight")}

    data = {}

    for i, var in enumerate(problem['names']):
        # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples)
        
        batch = BatchRunner(SlimeModel, 
                            max_steps=max_steps,
                            iterations=replicates,
                            variable_parameters={var: samples},
                            model_reporters=model_reporters,
                            display_progress=True)
        
        batch.run_all()
        
        data[var] = batch.get_model_vars_dataframe()
        print(data)

if __name__ == "__main__":
    OFAT()