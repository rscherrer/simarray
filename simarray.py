#!/usr/bin/env python3

import argparse
from contextlib import ExitStack
import os
import shutil
import tarfile

# Set up argument parser
parser = argparse.ArgumentParser(description="Process multiple files.")
parser.add_argument('filenames', nargs='*', help="List of filenames to process")
parser.add_argument('--folder', help="Path to a folder containing files to process")
parser.add_argument('--separator', default='_', help="Separator to use in folder names (default: '_')")
parser.add_argument('--target', default='.', help="Target folder to save results (default: current directory)")
parser.add_argument('--by', type=int, help="Number of folders per batch (optional)")
parser.add_argument('--batch-prefix', default='batch_', help="Prefix for batch folders (default: 'batch_')")
parser.add_argument('--sim-prefix', default='sim', help="Prefix for simulation folder names (default: 'sim')")
parser.add_argument('--replicates', type=int, default=1, help="Number of replicates per parameter combination (default: 1)")
parser.add_argument('--replicate-prefix', default='r', help="Prefix for replicate identifiers (default: 'r')")
parser.add_argument('--template', help="Path to the template parameter file (optional)")
parser.add_argument('--output-param-file', default=None, help="Name of the parameter file in the final folder (default: same as template or 'parameters.txt')")
parser.add_argument('--param-separator', default=' ', help="Separator between parameter name and value in the template file (default: ' ')")
parser.add_argument('--dispatch', nargs='*', help="List of files to copy into each simulation folder (optional)")
parser.add_argument('--compress', action='store_true', help="Compress each batch into a tarball (or compress everything if no batches are specified)")
parser.add_argument('--tarball-name', default='all_simulations', help="Name of the global tarball (default: 'all_simulations')")
parser.add_argument('--verbose', type=int, choices=[0, 1, 2], default=1, help="Verbosity level: 0 (silent), 1 (default), 2 (detailed)")

# Parse the arguments
args = parser.parse_args()

# Determine the name of the parameter file in the final folder
if args.output_param_file:
    param_file_name = args.output_param_file
elif args.template:
    param_file_name = os.path.basename(args.template)
else:
    param_file_name = "parameters.txt"

# Collect files from folder if provided
if args.folder:
    args.filenames.extend(
        [os.path.join(args.folder, f) for f in os.listdir(args.folder) if os.path.isfile(os.path.join(args.folder, f))]
    )

# Ensure there are files to process
if not args.filenames:
    raise ValueError("No files provided. Use filenames or the --folder option.")

# Check if all files have the same number of lines
line_counts = []
for filename in args.filenames:
    with open(filename, 'r') as f:
        line_counts.append(sum(1 for _ in f))

if len(set(line_counts)) > 1:
    raise ValueError("Files do not have the same number of lines.")

# Open and process files
with ExitStack() as stack:
    files = [stack.enter_context(open(filename, 'r')) for filename in args.filenames]
    parameter_names = [os.path.splitext(os.path.basename(filename))[0] for filename in args.filenames]
    
    # Initialize a list to store all folder paths
    all_folders = []

    # For each line...
    for lines in zip(*files):
        # Strip whitespace and assemble base folder name
        values = [line.strip() for line in lines]
        base_folder_name = f"{args.sim_prefix}{args.separator}" + f"{args.separator}".join(
            f"{param}{args.separator}{value}" for param, value in zip(parameter_names, values)
        )
        
        # Create replicate folders
        for replicate in range(1, args.replicates + 1):
            folder_name = f"{base_folder_name}{args.separator}{args.replicate_prefix}{replicate}"
            all_folders.append((folder_name, dict(zip(parameter_names, values))))

    # Split folders into batches if batching is enabled
    batch_number = 1
    for i, (folder_name, param_values) in enumerate(all_folders):
        # Determine the batch folder path if batching is enabled
        if args.by:
            batch_folder = os.path.join(args.target, f"{args.batch_prefix}{batch_number}")
            target_path = os.path.join(batch_folder, folder_name)
        else:
            target_path = os.path.join(args.target, folder_name)
        
        # Ensure the target folder exists
        os.makedirs(target_path, exist_ok=True)

        # If verbosity level is 2, print the folder name
        if args.verbose == 2:
            print(f"Created folder: {target_path}")

        # If a template is provided, read and modify it
        if args.template:
            with open(args.template, 'r') as template_file:
                template_lines = template_file.readlines()

            # Check for duplicate parameter names in the template file
            seen_parameters = set()
            for line in template_lines:
                line_stripped = line.strip()
                if any(line_stripped.startswith(param + args.param_separator) for param in parameter_names):
                    param_name = line_stripped.split(args.param_separator, 1)[0]
                    if param_name in seen_parameters:
                        raise ValueError(f"Duplicate parameter name '{param_name}' found in the template file.")
                    seen_parameters.add(param_name)

            # Modify the template file
            modified_lines = []
            found_parameters = set()
            for line in template_lines:
                line_stripped = line.strip()
                if any(line_stripped.startswith(param + args.param_separator) for param in parameter_names):
                    param_name = line_stripped.split(args.param_separator, 1)[0]
                    modified_lines.append(f"{param_name}{args.param_separator}{param_values[param_name]}\n")
                    found_parameters.add(param_name)
                else:
                    modified_lines.append(line)

            # Add missing parameters
            for param in parameter_names:
                if param not in found_parameters:
                    modified_lines.append(f"{param}{args.param_separator}{param_values[param]}\n")
        else:
            # If no template is provided, create a new parameter file
            modified_lines = [f"{param}{args.param_separator}{value}\n" for param, value in param_values.items()]

        # Write the parameter file to the target folder
        with open(os.path.join(target_path, param_file_name), 'w') as output_file:
            output_file.writelines(modified_lines)

        # Dispatch files into the simulation folder
        if args.dispatch:
            for file_to_copy in args.dispatch:
                if os.path.isfile(file_to_copy):
                    shutil.copy(file_to_copy, target_path)
                else:
                    raise ValueError(f"File '{file_to_copy}' specified in --dispatch does not exist or is not a file.")

        # Print the target path
        print(target_path)
        
        # Increment batch logic
        if args.by and (i + 1) % args.by == 0:
            batch_number += 1

# Initialize counters for folders and batches
total_folders = len(all_folders)
total_batches = batch_number if args.by else 0

# After folder creation
if args.verbose >= 1:
    print("Folders created.")
    if args.verbose >= 1:
        if args.by:
            print(f"Total folders created: {total_folders} across {total_batches} batches.")
        else:
            print(f"Total folders created: {total_folders}.")

# If needed...
if args.compress:
    if args.verbose >= 1:
        print("Compressing folders...")
    if args.by:
        # Compress each batch folder
        for batch_number in range(1, batch_number + 1):
            batch_folder = os.path.join(args.target, f"{args.batch_prefix}{batch_number}")
            tarball_name = f"{batch_folder}.tar.gz"
            with tarfile.open(tarball_name, "w:gz") as tar:
                tar.add(batch_folder, arcname=os.path.basename(batch_folder))
                
            print(f"Compressed batch folder '{batch_folder}' into '{tarball_name}'")
    else:
        # Compress everything into a single tarball
        tarball_name = os.path.join(args.target, f"{args.tarball_name}.tar.gz")
        with tarfile.open(tarball_name, "w:gz") as tar:
            tar.add(args.target, arcname=os.path.basename(args.target))
            
        print(f"Compressed all simulations into '{tarball_name}'")
        
# Final message
if args.verbose >= 1:
    print("All done.")