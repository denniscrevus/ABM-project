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
        'num_vars': 4,
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

def plot_index(s, params, i, title=''):
    """
    Creates a plot for Sobol sensitivity analysis that shows the contributions
    of each parameter to the global sensitivity.

    Args:
        s (dict): dictionary {'S#': dict, 'S#_conf': dict} of dicts that hold
            the values for a set of parameters
        params (list): the parameters taken from s
        i (str): string that indicates what order the sensitivity is.
        title (str): title for the plot
    """

    if i == '2':
        p = len(params)
        params = list(combinations(params, 2))
        indices = s['S' + i].reshape((p ** 2))
        indices = indices[~np.isnan(indices)]
        errors = s['S' + i + '_conf'].reshape((p ** 2))
        errors = errors[~np.isnan(errors)]
    else:
        indices = s['S' + i]
        errors = s['S' + i + '_conf']
        plt.figure()

    l = len(indices)

    plt.title(title)
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
    plt.axvline(0, c='k')

def sobol_total():
    # We define our variables and bounds
    problem = {
        'num_vars': 4,
        'names': ['p_branch', 'p_connect', 'signal_strength', 'noise'],
        'bounds': [[0.1, 0.5], [0.1, 0.5], [7, 15], [0.75, 1.5]]
    }

    # Set the repetitions, the amount of steps, and the amount of distinct values per variable
    replicates = 1
    max_steps = 200
    distinct_samples = 1

    # We get all our samples here
    param_values = saltelli.sample(problem, distinct_samples, calc_second_order=False)

    # Set the outputs
    food_coords = text_to_coords("tokyo_coords.txt")
    model_reporters = {"Graph size": lambda m: convert_result_to_graph(reduce_graph(m.get_connections(), food_coords)).size(weight="weight")}

    # READ NOTE BELOW CODE
    batch = BatchRunner(SlimeModel, 
                        max_steps=max_steps,
                        variable_parameters={name:[] for name in problem['names']},
                        model_reporters=model_reporters)

    count = 0
    data = pd.DataFrame(index=range(replicates*len(param_values)), 
                                    columns=['p_branch', 'p_connect', 'signal_strength', 'noise'])
    data['Run'], data['Graph size'] = None, None

    for i in range(replicates):
        for vals in param_values: 
            # Transform to dict with parameter names and their values
            variable_parameters = {}
            for name, val in zip(problem['names'], vals):
                variable_parameters[name] = val

            batch.run_iteration(variable_parameters, tuple(vals), count)
            iteration_data = batch.get_model_vars_dataframe().iloc[count]
            iteration_data['Run'] = count # Don't know what causes this, but iteration number is not correctly filled
            data.iloc[count, 0:4] = vals
            data.iloc[count, 4:8] = iteration_data
            count += 1

            clear_output()
            print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')

    # Total order
    Si_graph_size = sobol.analyze(problem, data['Graph size'].values, print_to_console=True, calc_second_order=False)
    plot_index(Si_graph_size, problem['names'], 'T', 'Total order sensitivity')
    plot_index(Si_graph_size, problem['names'], '1', 'First order sensitivity')
    plt.show()

if __name__ == "__main__":
    sobol_total()