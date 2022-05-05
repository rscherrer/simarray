# simarray

Scripts to set up arrays of simulation folders.

## Goal

This set of scripts is supposed to help quickly generate hundreds of folders that will each contain individual simulations of a given program, each with possibly different parameter values. 

## Preparation

We assume that the simulation program (whichever it is) takes a parameter input file `parameters.txt` as argument. This file contains, on each line, the name of a parameter and the value that parameter has to take, e.g.

```
param1 5
param2 5
param3 5 5 5
```

(here with `param3` taking 3 values).

The scripts provided here make it easy to generate lots of ready-to-run simulation folders, each with its own `parameters.txt` file. For this, all you need is to make lists of values for each parameter you wish to vary. Each list (one per parameter) must be stored in a file named after the parameter whose values it contains. For example, if you want to run simulations where `param1` varies through `1`, `2` or `3`, you must create a file called `param1.txt` that looks like this:

```
1
2
3
```

If the parameter of interest takes multiple values, just use spaces, e.g.

```
1 1 1
2 2 2
3 3 3
```

If you want to run multiple *combinations* of parameters, you need to provide one file per parameter to combine, and each file must contain **the same number of lines**, each of them an entry for a given simulation folder. The different lists of values for each parameter will then be read together and combined. That is, to run simulations with the three following parameter files,

(Simulation 1:)
```
param1 1
param2 1
param3 1 1 1
```

(Simulation 2:)
```
param1 2
param2 2
param3 2 2 2
```

(Simulation 3:)
```
param1 3
param2 3
param3 3 3 3
```

you must provide three text files, `param1.txt`, `param2.txt` and `param3.txt`, each containing 3 lines (one for each simulation). In this case, `param1.txt` and `param2.txt` will both look like

```
1
2
3
```

and `param3.txt` will look like

```
1 1 1
2 2 2
3 3 3
```

Note: these scripts do not create combinations of parameters, they only read the combinations you want to run and set up the simulation folders for you. You must create the combinations beforehand when you write the lists of parameter values (e.g. `param1.txt`, `param2.txt`, `param3.txt`). This is because while some use-cases may require exploring all combinations of a given set of parameter values, other use-cases may require running only subsets of all possible combinations, or some very specific combinations, for which a combination-generating program may not be adequate. For that reason I prefer to keep the generation of parameter combinations and the set-up of simulation arrays separate.

## Usage

Once you have prepared your lists of parameter values (see above), just run the `prepare_sims.sh` script, and pass it the names of the files in which it has to look up parameter values:

```
bash prepare_sims.sh param1.txt param2.txt param3.txt
```

This will create one folder for each simulation in the working directory and copy a corresponding, updated version of the `parameters.txt` template file within it (note that `parameters.txt` must be present in the working directory). Each folder starts with `sim_` and will be named after its parameter values. For example, the folder for simulation 1 above will have the name `sim_param1_1_param2_2_param3_3_3_3`.

Also note that in case a mistake was made, this program will not overwrite existing directories, so it is best to remove simulation folders before re-running it:

```
rm -r sim*
```

## Parameter file template

The parameter file template contains the default parameters to pass to the program. Make sure that it contains a line and dummy value(s) for each of the parameters that will be modified by the script, as the latter will only change parameters  it can find in `parameters.txt`.

## Content

This repository contains:

* `prepare_sims.sh`: the main script, which calls the other scripts below
* `make_folder_names.py`: a routine to turn parameter values into a list of folder names
* `update_value.py`: a routine to change the value of a given parameter in a parameter file
* `param1.txt`, `param2.txt`, `param3.txt`: example lists of parameter values for each parameter of interest
* `parameters.txt`: the template parameter file for the simulation program

- underscores instead of spaces
