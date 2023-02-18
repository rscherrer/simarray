# simarray

Set of scripts to create an array of simulations with lots of combinations of parameters.

## Prerequisites

* (optional) A program that runs with a parameter file
* [Python](https://www.python.org) version 3.8.10 or higher
* Some way to run shell scripts (native in Linux, see e.g. [here](https://mspoweruser.com/different-ways-to-run-shell-script-files-on-windows/) for Windows)

## Use

### 1. Make lists of parameter values

Make lists of parameter values to run and store them in text files names after the parameter they contain. **All lists should have the same number of lines.** For example, to run all combinations of mutation = { 0.001, 0.01 } and selection = { 1.5, 2 }, create `mutation.txt` as 

```
0.001
0.001
0.01
0.01
```

and `selection.txt` as

```
1.5
2
1.5
2
```

### 2. Make a template parameter file

Create a template `parameters.txt` file which contains at least the parameters that we have created lists for. This file will contain the parameter values to run for a given simulation. In our case, it may look like:

```
mutation 0
selection 0
recombination 0
```

The values are not important for parameters that will be modified, but this is where you fix the values of the parameters you do not wish to change, such as `recombination` here (unless you are happy with the default values). The file will be copied into each simulation folder and modified accordingly to accomodate each combination of parameters.

### 3. Create many simulation folders

```sh
bash prepare_sims.sh mutation.txt selection.txt
```

This will create folders named after the parameters passed to them. Here, it would be:

```
sim-mutation-0.001-selection-1.5
sim-mutation-0.001-selection-2
sim-mutation-0.01-selection-1.5
sim-mutation-0.01-selection-2
```

Each folder contains its own `parameter.txt` file. In the first folder of our example, that would be

```
mutation 0.001
selection 1.5
recombination 0
```

### 4. Dispatch more files if needed

Once the simulation folders have been created, you can copy some files down into each simulation folder (without modification) by running:

```sh
bash dispatch_files.sh <file1> <file2> ...
```

That will copy the files into **every** subdirectory.

### 5. In case of a mistake

The scripts will not overwrite existing directories, so in case of a mistake, best delete simulation folders before re-running the scripts, e.g. by doing

```sh
rm -r sim*
```

## Note

Some parameters may take multiple values, separated by spaces. For example, if the initial number of individuals in each deme shows as

```
demesizes 100 10 10 10 10
```

in `parameters.txt`, the list of parameter values `demesizes.txt` may look like

```
100 10 10 10 10
100 20 20 20 20
100 0 0 0 0
```

That will create the following simulation folders:

```
sim-demesizes-100-10-10-10-10
sim-demesizes-100-20-20-20-20
sim-demesizes-100-0-0-0-0
```

## Disclaimer

These scripts do not create combinations of parameters, they only read the combinations you want to run and set up the simulation folders for you. You must create the combinations beforehand. This is because while some use-cases may require exploring all combinations of a given set of parameter values, other use-cases may require running only subsets of all possible combinations, or some very specific combinations, for which a combination-generating program may not be adequate. For that reason I prefer to keep the generation of parameter combinations and the set-up of simulation arrays separate (this repository is only about the latter).
