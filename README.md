# Agent Based Slime Model
A model inspired by slime molds that creates a network and attempts to create a network with short paths between all possible nodes.

![Network](graph.png)

## Usage
There are a couple of files that can be run in this project.

### run.py
This file simply runs the model with the parameters set in the code. When it finishes, it plots the resulting network with the shortest paths and stores it in an image file (graph.png).

Simply run it with: `python run.py`

It might take some time to finish. To use different food source locations, you will have to change the line `food_coords = get_city_grid(<city_name>, size, size)` and replace <city_name> with: berlin, dublin, helsinki, lisbon, luxembourg, paris or rome.

### analyze_data.py
This file allows you to run the experiments associated with our project, it has a possible arguments that you need to provide.

`python analyze_data.py <command> <filename (ONLY FOR run OR plot)>`

There are currently three commands:
- run
- plot
- node_hist

`run` will execute the experiments with the set parameters in the code. If you want to vary different parameters, you will unfortunately have to change it manually in the code.
You can provide an optional file path, which is where the results of the experiment will be stored. If you do not provide this argument, it will automatically plot the data without storing.

To use `plot`, a filepath must be provided. It will plot the data from the specified file.

`node_hist` simply does a quick experiment that creates a distribution of the node degrees. But we did not use it for our project.


### sensitivity_analysis.py
To run this file simply use `python sensitivity_analysis.py`

## Authors
- Kwan Lie
- Jop Meijer
- Robbie Koevoets
- Jonathan Meeng
- Dennis Curti
