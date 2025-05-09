# SimArray: Simulation Folder Generator

`simarray.py` is a [Python](https://www.python.org/) script designed to automate the creation of simulation folders based on parameter combinations provided in input files.

![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![PEP 8](https://img.shields.io/badge/PEP_8-100%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## Description

This program takes **lists of parameter combinations as input, and creates many simulation folders**, one for each combination, dispatching parameter files into each folder with updated parameter values as needed. It is therefore made for **simulation programs taking in a parameter text file** (see use case below). The script can group simulations into batches and compress them into tarballs (e.g. for efficient transfer to a computer cluster), supports the creation of multiple replicates for each parameter combination, and can dispatch additional files into the simulation folders.

## Use Case

Say you have a CLI **simulation program that takes a parameter text file** as input.

```shell
mySimulator parameters.txt
```

and the parameter file is nothing more than a list of names of parameters and their values, e.g.

```
popsize 10
ndemes 5
traits 0.1 0.2 0.3
selection 0
mutation 0.00001
```

Then, **running many simulations, across many combinations of parameters**, each with a slight difference in parameters can be challenging. SimArray makes it easier to do just that, by generating all the necessary simulation folders, with the right, updated parameter files with the right values into them.

## Input

The script expects **parameter combination files** as input. These files are text files named after their respective parameter and containing the values that said parameters must take in subsequent simulations. All files are expected to have the same number of rows, one per parameter combination, and each file giving the value of one particular parameter. 

For example, `mutation.txt` could look like

```
0.001
0.01
0.1
```

while `selection.txt` could look like:

```
1.4
1.5
1.6
```

The script `simarray.py` would then convert the provided combinations of the two parameter values into three simulation folders:

```
./sim_mutation_0.001_selection_1.4/
./sim_mutation_0.01_selection_1.5/
./sim_mutation_0.1_selection_1.6/
```

### Note

Note that this script does not generate the parameter combination files - they **must be provided**. To generate all possible combinations of some parameters, you can use for example the `expand_grid()` function in [R](https://www.r-project.org/). However, there may be more complex cases of parameter space exploration that are user-specific, and so I chose not to delve into that in the development of this program.

## Usage

```shell
python3 simarray.py [options] filenames
```

or

```shell
./simarray.py [options] filenames
```

For the latter, to run the script directly, make sure to first run `chmod +x simarray.py` to make it executable.

### Arguments

* `filenames`: List of input files containing parameter values (e.g., `mutation.txt`, `selection.txt`).
* `--folder`: Path to a folder containing files to process (all files in that folder will be read as input if `filenames` is not provided).
* `--separator`: Separator to use in output folder names (default: `_`).
* `--target`: Target folder to save results into (default: current directory).
* `--by`: Number of folders per batch (no batching if not provided).
* `--batch-prefix`: Prefix for batch folder names (default: `batch_`).
* `--sim-prefix`: Prefix for simulation folder names (default: `sim` followed by what was provided in `--separator`).
* `--replicates`: Number of replicates per parameter combination (default: 1).
* `--replicate-prefix`: Prefix for replicate identifiers (default: `r`).
* `--template`: Path to the template parameter file (if not given, a new parameter file will be created for each simulation folder).
* `--output-param-file`: Name of the parameter file in the output folders (default: same as `--template` or `parameters.txt` if `--template` is not provided).
* `--param-separator`: Separator between parameter name and value expected in the template file (default: white space).
* `--dispatch`: List of extra files to copy into each simulation folder.
* `--compress`: Compress each batch into a tarball (or compress everything if `--by` was not specified).
* `--tarball-name`: Name of the global tarball if compression without batching (default: `all_simulations`).
* `--verbose`: Verbosity level:
    * `0`: Silent.
    * `1`: Default (high-level messages).
    * `2`: Detailed (prints folder and tarball names).
* `--compress-only`: Compress existing batch folders into tarballs (identifies them in `--target` as folders starting with `--batch-prefix`).
* `--compress-all`: Compress all simulation folders in `--target` into a single tarball (looks for `--sim-prefix` instead).
* `--dispatch-only`: Dispatch files into existing folders.
* `--dispatch-recursive`: When in `--dispatch-only` mode, recursively search for folders with `--sim-prefix` inside of batch folders with `--batch-prefix` within `--target`, or just directly within `--target`.
* `--help`: Show help message and exit.
* `--version`: Show program's version number and exit.

(See examples below.)

## Output

For an example with input files `mutation.txt`, `selection.txt`, and `recombination.txt`, and running

```shell
./simarray.py mutation.txt selection.txt recombination.txt --by 3 --replicates 2 --target target/
```

 we would get something like this:

```
target/
|--batch_1/
|   |--sim_mutation_0.001_selection_1.4_r1/
|   |--sim_mutation_0.001_selection_1.4_r2/
|   |--sim_mutation_0.01_selection_1.5_r1/
|--batch_2/
    |--sim_mutation_0.01_selection_1.5_r2/
    |--sim_mutation_0.1_selection_1.6_r1/
    |--sim_mutation_0.1_selection_1.6_r2/
```

where each simulation folder contains the relevant parameter file `parameters.txt`, with only the relevant parameters modified. For example, the parameter file of the first simulation folder would read:

```
popsize 10
ndemes 5
traits 0.1 0.2 0.3
selection 1.4
mutation 0.001
```

## Examples

### Basic Usage

```shell
./simarray.py mutation.txt selection.txt recombination.txt
```

Creates simulation folders based on the parameter combinations in the input files. The input files should be named after their respective parameter **as expected in the parameter file** (this is defined by the simulation program you use), and **must have the same number of rows**, as they each list the values of one parameter across as many combinations. By default, the above command will create a file named `parameters.txt` and place it into each simulation folder (use the `--output-param-file` argument to change the name of that file). 

The output simulation folders will have names starting with `sim` by default, but that can be changed in `--sim-prefix`. The separator between names and values in the folder names is `_` by default, but that can also be changed, using `--separator`.

### Using a Template

```shell
./simarray.py mutation.txt selection.txt recombination.txt --template parameters.txt
```

This indicates that there is already a template parameter file, called `parameters.txt` (e.g. containing non-default parameters that must remain constant), and that we should not create a new parameter file for each simulation folder. The above command modifies `parameters.txt` for each simulation folder based on the input files. (The template file must exist.)

By default, the script expects parameter names and values to be separated by white spaces, and will write them also separated by white spaces in the output parameter files. To change that, use `--param-separator` (this will not change how names and values are separated in folder names, as this is `--separator`'s job).

### Vector Parameters

The script can handle parameters that come as multiple values, e.g.

```
traits 0 0 1
```

Then, the parameter combination file `traits.txt` should look like:

```
0 0 0
0 0 1
0 0 2
```

Now, running:

```shell
./simarray.py mutation.txt traits.txt
```

will produce the following folders:

```
./sim_mutation_0.001_traits_0_0_0/
./sim_mutation_0.01_traits_0_0_1/
./sim_mutation_0.1_traits_0_0_2/
```

The script expects the different values on a given line in `traits.txt` to be separated by `--param-separator`, and will separate them with that separator too in output parameter files. However, it will use `--separator` to separate the values in folder names (mostly to avoid white spaces in paths). 

### Read from Folder

```shell
./simarray.py --folder pars/
```

This will take all files in the `pars/` directory as input files (instead of having to write `mutation.txt`, `selection.txt`, etc.). Can be handy if there are many parameters to create combinations for. (To reduce cluttering we use this notation in the next examples.)

To only read certain files in `--folder`, just provide their names beforehand:

```shell
./simarray.py  mutation.txt selection.txt --folder pars/
```

### Custom Target

By default the output folders will be generated in the working directory, but

```shell
./simarray.py --folder pars/ --target sims/
```

will locate them in a new target directory called `sims/`.

### With Replicates

```shell
./simarray.py --folder pars/ --replicates 3
```

Creates 3 replicate folders for each parameter combination, appending the replicate identifier `r1`, `r2` and `r3` at the end of the names of each one. To change the replicate identifier, use the `--replicate-prefix` argument.

### Batching

```shell
./simarray.py --folder pars/ --by 10
```

Will group the newly created simulation folders into groups, or batches, of up to 10 folders each, each in their own directory (the last batch will have fewer than `--by` simulation folders if the total number of simulations is not a multiple of `--by`). Can be useful for compression (see below) or if, for example, simulations within a batch must be run sequentially while separate batches must be run in parallel (as can happen in some simulation pipelines). The batches are named `batch_1`, `batch_2`, etc. by default. To change that, use the `--batch-prefix` argument. 

### Compressing

To compress the batches into tarballs,

```shell
./simarray.py --folder pars/ --by 10 --compress
```

This will create `batch_1.tar.gz`, `batch_2.tar.gz`, etc. If no `--by` is specified, all the simulations will be compressed into a single tarball, named `all_simulations.tar.gz` (but this can be changed with the `--tarball-name` argument).

**Note**

Tarballs are `gzip`-compressed and compatible with standard CLI tools like `tar`.

#### Decompression

To decompress a tarball (in a Unix-like command line, e.g. Linux, MacOS or WSL on Windows), you can use:

```shell
tar -xvzf <tarball_name>.tar.gz
```

where:

* `-x`: Extract files from the archive.
* `-v`: Verbose mode (shows the files being extracted).
* `-z`: Use `gzip` to decompress the archive.
* `-f`: Specifies the filename of the tarball.

For non-Unix Windows interface, third-party tools like [7-Zip](https://www.7-zip.org/) or [WinRAR](https://www.win-rar.com/) can be used.

### Compression Only

To simply compress per batch (or all folders in one archive) after the folders have already been created (e.g. in a previous run of `simarray.py`), use:

```shell
./simarray.py --target sims/ --compress-only
```

This will compress batches as detected using the `--batch-prefix` argument (or its default if not provided).

Use the `--compress-all` flag,

```shell
./simarray.py --target sims/ --compress-only --compress-all
```

to skip looking into batch folders and compress all simulation folders (identified with `--sim-prefix` or its default) inside of `--target` into one single tarball named `all_simulations.tar.gz` (or whatever name you provide with `--tarball-name`).

### Dispatching Extra Files

```shell
./simarray.py --folder pars/ --dispatch file1.txt file2.txt
```

Copies `file1.txt` and `file2.txt` into each simulation folder, unchanged. Handy if a run requires more files that must remain constant across simulations.

### Dispatch Only

To use the program to only dispatch files (e.g. assuming that the folders have already been generated in a previous run of `simarray.py` and some files have been forgotten) into the target folders, use:

```shell
./simarray.py --target sims/ --dispatch file1.txt file2.txt --dispatch-only
```

This will look for folers starting with `--sim-prefix` in the `--target` directory. If simulation folders are arranged in batches, add the `--dispatch-recursive` flag:

```shell
./simarray.py --target sims/ --dispatch file1.txt file2.txt --dispatch-only --dispatch-recursive
```

This will look for folders starting with `--sim-prefix` inside of batch folders starting with `--batch-prefix` within `--target`.

## Requirements

* [Python](https://www.python.org/) 3.6 or higher

### Dependencies

This script uses the following Python built-in standard libraries:

* [argparse](https://docs.python.org/3/library/argparse.html)
* [contextlib](https://docs.python.org/3/library/contextlib.html)
* [os](https://docs.python.org/3/library/os.html)
* [shutil](https://docs.python.org/3/library/shutil.html)
* [tarfile](https://docs.python.org/3/library/tarfile.html)
* [warnings](https://docs.python.org/3/library/warnings.html)

## Tests

Tests for this code can be found in the `tests/` folder. The tests make use of the following standard Python libraries:

* [unittest](https://docs.python.org/3/library/unittest.html)
* [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
* [os](https://docs.python.org/3/library/os.html)
* [shutil](https://docs.python.org/3/library/shutil.html)
* [warnings](https://docs.python.org/3/library/warnings.html)
* [sys](https://docs.python.org/3/library/sys.html)
* [subprocess](https://docs.python.org/3/library/subprocess.html)
* [tarfile](https://docs.python.org/3/library/tarfile.html)

## About

This code was written in Python, on Ubuntu Linux 24.04 LTS, using [Visual Studio Code](https://code.visualstudio.com/) 1.99.0 ([Python Extension Pack](https://marketplace.visualstudio.com/items/?itemName=donjayamanne.python-extension-pack) 1.7.0). The script was run using [Python](https://www.python.org/) 3.12.3. Tests were run using the standard [unittest](https://docs.python.org/3/library/unittest.html) module. Code coverage was measured using the [coverage](https://coverage.readthedocs.io/en/7.4.4) 7.4.4 module. Style and syntax were checked against the [PEP 8](https://peps.python.org/pep-0008/) guidelines using [pylint](https://pypi.org/project/pylint/) 3.3.6.
Installation of non-standard modules was done using [pip](https://pypi.org/project/pip/) 24.0 in a virtual environment managed by [venv](https://docs.python.org/3/library/venv.html) 3.12.3. (See the `dev/` folder and [this page](dev/README.md) for details about the checks performed.)

Occasional use was made of [ChatGPT](https://chatgpt.com/) and [GitHub Copilot](https://github.com/features/copilot) in the development of this code.

## Disclaimer

This code comes with no guarantee whatsoever.

## Copyright

Copyright (c) 2025 [Raphaël Scherrer](https://github.com/rscherrer)

This code is licensed under the [MIT license](LICENSE.md).
