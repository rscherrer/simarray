#!/usr/bin/env python3
"""
SimArray: A script to generate simulation folders, dispatch files, and compress folders.

This script is designed for use in simulation studies where multiple parameter
combinations need to be tested. It can generate folders based on input parameters,
dispatch files into those folders, and optionally compress the results into tarballs.

Usage:
    Run the script from the command line with the appropriate arguments.
    Use the `--help` flag for more details.

Author: Raphaël Scherrer
URL: https://github.com/rscherrer/simarray
License: MIT License
"""

# Copyright (c) 2025 Raphaël Scherrer
#
# This script is licensed under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
from contextlib import ExitStack
import os
import shutil
import tarfile
import warnings
import sys

# Define the version of the script
SCRIPT_VERSION = "1.3.1"

def parse_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "SimArray: A script to generate simulation folders, dispatch "
            "files, and compress folders."
        )
    )
    parser.add_argument(
        'filenames', nargs='*',
        help="List of filenames to process"
    )
    parser.add_argument(
        '--folder',
        help="Path to a folder containing files to process"
    )
    parser.add_argument(
        '--separator', default='_',
        help="Separator to use in folder names (default: '_')"
    )
    parser.add_argument(
        '--target', default='.',
        help="Target folder to save results (default: current directory)"
    )
    parser.add_argument(
        '--by', type=int,
        help="Number of folders per batch (optional)"
    )
    parser.add_argument(
        '--batch-prefix', default='batch_',
        help="Prefix for batch folders (default: 'batch_')"
    )
    parser.add_argument(
        '--sim-prefix', default='sim',
        help="Prefix for simulation folder names (default: 'sim')"
    )
    parser.add_argument(
        '--replicates', type=int, default=1,
        help="Number of replicates per parameter combination (default: 1)"
    )
    parser.add_argument(
        '--replicate-prefix', default='r',
        help="Prefix for replicate identifiers (default: 'r')"
    )
    parser.add_argument(
        '--template',
        help="Path to the template parameter file (optional)"
    )
    parser.add_argument(
        '--output-param-file', default=None,
        help=(
            "Name of the parameter file in the final folder (default: same "
            "as template or 'parameters.txt')"
        )
    )
    parser.add_argument(
        '--param-separator', default=' ',
        help=(
            "Separator between parameter name and value in the template file "
            "(default: ' ')"
        )
    )
    parser.add_argument(
        '--dispatch', nargs='*',
        help="List of files to copy into each simulation folder (optional)"
    )
    parser.add_argument(
        '--compress', action='store_true',
        help=(
            "Compress each batch into a tarball (or compress everything if "
            "no batches are specified)"
        )
    )
    parser.add_argument(
        '--tarball-name', default='all_simulations',
        help="Name of the global tarball (default: 'all_simulations')"
    )
    parser.add_argument(
        '--verbose', type=int, choices=[0, 1, 2], default=1,
        help="Verbosity level: 0 (silent), 1 (default), 2 (detailed)"
    )
    parser.add_argument(
        '--dispatch-only', action='store_true',
        help="Only dispatch files into existing folders (skip folder generation)"
    )
    parser.add_argument(
        '--dispatch-recursive', action='store_true',
        help="Recursively look for simulation folders in batch folders (default: False)"
    )
    parser.add_argument(
        '--compress-only', action='store_true',
        help="Only compress existing folders (skip folder generation)"
    )
    parser.add_argument(
        '--version', action='version', version=f"SimArray {SCRIPT_VERSION}",
        help="Show program's version number and exit"
    )
    parser.add_argument(
        '--compress-all', action='store_true',
        help="Compress all simulation folders into a single archive (default: False)"
    )
    return parser.parse_args()

def dispatch_files(args, target_folders):
    """
    Dispatch files into the specified folders.
    """

    if args.verbose >= 1:
        print(
            f"Dispatching files into {len(target_folders)} folders in target '{args.target}'..."
        )

    for folder in target_folders:

        if args.verbose == 2:
            print(f"Dispatching files into folder: {folder}")

        for file_to_copy in args.dispatch:
            if os.path.isfile(file_to_copy):
                shutil.copy(file_to_copy, folder)
            else:
                raise ValueError(
                    f"File '{file_to_copy}' specified in --dispatch does "
                    f"not exist or is not a file."
                )

    if args.verbose >= 1:
        print("File dispatch completed.")

def dispatch_only_mode(args):
    """
    Handle the dispatch-only mode: dispatch files into existing simulation folders,
    optionally searching recursively within batch folders.
    """
    # Ensure files to dispatch are provided
    if not args.dispatch:
        raise ValueError(
            "No files specified for dispatch. Use the --dispatch argument "
            "to specify files."
        )

    # Determine the target directory
    target_dir = args.target if args.target else os.getcwd()

    # Get the list of simulation folders
    if args.dispatch_recursive:
        # Look for batch folders within the target directory
        batch_folders = [
            os.path.join(target_dir, f)
            for f in os.listdir(target_dir)
            if os.path.isdir(os.path.join(target_dir, f))
            and f.startswith(args.batch_prefix)
        ]

        # Look for simulation folders within each batch folder
        existing_folders = []
        for batch_folder in batch_folders:
            existing_folders.extend([
                os.path.join(batch_folder, f)
                for f in os.listdir(batch_folder)
                if os.path.isdir(os.path.join(batch_folder, f))
                and f.startswith(args.sim_prefix)
            ])
    else:
        # Look for simulation folders directly in the target directory
        existing_folders = [
            os.path.join(target_dir, f)
            for f in os.listdir(target_dir)
            if os.path.isdir(os.path.join(target_dir, f))
            and f.startswith(args.sim_prefix)
        ]

    # Check if any simulation folders were found
    if not existing_folders:
        warnings.warn(
            f"No simulation folders found in '{target_dir}' starting with "
            f"prefix '{args.sim_prefix}'."
        )
        return 0  # Exit early since there are no folders to dispatch files into

    dispatch_files(args, existing_folders)

    return 0

def compress_only_mode(args):
    """
    Handle the compress-only mode: compress simulation folders or batch folders
    based on the provided arguments.
    """
    # Determine the target directory
    target_dir = args.target if args.target else os.getcwd()

    if args.compress_all:
        # Look for simulation folders in the target directory
        simulation_folders = [
            os.path.join(target_dir, f)
            for f in os.listdir(target_dir)
            if os.path.isdir(os.path.join(target_dir, f))
            and f.startswith(args.sim_prefix)
        ]

        if simulation_folders:
            if args.verbose >= 1:
                print(
                    f"Found {len(simulation_folders)} simulation folders "
                    "for compression."
                )
            # Compress all simulation folders into one tarball
            tarball_name = os.path.join(
                target_dir, f"{args.tarball_name}.tar.gz"
            )
            with tarfile.open(tarball_name, "w:gz") as tar:
                for folder in simulation_folders:
                    tar.add(folder, arcname=os.path.basename(folder))
            if args.verbose >= 1:
                print(
                    f"Compressed all simulation folders into '{tarball_name}'"
                )
        else:
            # Issue a warning if no simulation folders are found
            warnings.warn(
                f"No simulation folders found in '{target_dir}' starting "
                f"with prefix '{args.sim_prefix}'."
            )
    else:
        # Look for batch folders in the target directory
        batch_folders = [
            os.path.join(target_dir, f)
            for f in os.listdir(target_dir)
            if os.path.isdir(os.path.join(target_dir, f))
            and f.startswith(args.batch_prefix)
        ]

        if batch_folders:
            if args.verbose >= 1:
                print(
                    f"Found {len(batch_folders)} batch folders for "
                    "compression."
                )
            # Compress each batch folder into its own tarball
            for batch_folder in batch_folders:
                tarball_name = f"{batch_folder}.tar.gz"
                with tarfile.open(tarball_name, "w:gz") as tar:
                    tar.add(
                        batch_folder, arcname=os.path.basename(batch_folder)
                    )
                if args.verbose >= 1:
                    print(
                        f"Compressed batch folder '{batch_folder}' into "
                        f"'{tarball_name}'"
                    )
        else:
            # Issue a warning if no batch folders are found
            warnings.warn(
                f"No batch folders found in '{target_dir}' starting with "
                f"prefix '{args.batch_prefix}'."
            )

def get_output_param_file_name(args):
    """
    Determine the name of the output parameter file based on the provided arguments.
    """
    if args.output_param_file:
        return args.output_param_file

    if args.template:
        return os.path.basename(args.template)

    return "parameters.txt"

def get_filenames_from_folder(args):
    """
    Get filenames from the specified folder and update the args.filenames list.
    """

    # If filenames are provided, prepend the folder path to each filename
    if args.filenames:
        args.filenames = [os.path.join(args.folder, f) for f in args.filenames]
    else:
        # If no filenames are provided, take all files in the folder as input
        args.filenames.extend(
            [
                os.path.join(args.folder, f) for f in os.listdir(args.folder)
                if os.path.isfile(os.path.join(args.folder, f))
            ]
        )

def check_files_provided(filenames):
    """
    Ensure that files are provided. Raise an error if no files are found.
    """
    if not filenames:
        raise ValueError("No files provided. Use filenames or the --folder option.")

def check_line_counts(filenames):
    """
    Check if all files have the same number of lines.
    """
    line_counts = []
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as f:
            line_counts.append(sum(1 for _ in f))

    if len(set(line_counts)) > 1:
        raise ValueError("Files do not have the same number of lines.")

def get_all_folder_names(args, parameter_names, parameter_values):
    """
    Generate all folder names based on the provided arguments, parameter names,
    and parameter values.
    """
    all_folders = []

    # For each combination of parameter values (one line per file)
    for values in zip(*parameter_values):
        # Strip whitespace and assemble base folder name
        values = [value.strip() for value in values]
        base_folder_name = (
            f"{args.sim_prefix}{args.separator}" +
            f"{args.separator}".join(
                f"{param}{args.separator}{args.separator.join(value.split(args.param_separator))}"
                for param, value in zip(parameter_names, values)
            )
        )

        # Create replicate folders
        for repl in range(1, args.replicates + 1):
            folder_name = (
                f"{base_folder_name}{args.separator}{args.replicate_prefix}{repl}"
            )
            all_folders.append((folder_name, dict(zip(parameter_names, values))))

    return all_folders

def get_target_path(args, folder_name, batch_number=None):
    """
    Determine the target path for a folder, considering batching if enabled.
    """
    if args.by and batch_number:
        # If batching is enabled, include the batch folder in the path
        batch_folder = os.path.join(args.target, f"{args.batch_prefix}{batch_number}")
        return os.path.join(batch_folder, folder_name)

    # If batching is not enabled, use the target directory directly
    return os.path.join(args.target, folder_name)

def generate_param_file_lines(args, parameter_names, param_values):
    """
    Generate the lines for the output parameter file.
    """
    # If a template is provided, read and modify it
    if args.template:
        with open(args.template, 'r', encoding='utf-8') as template_file:
            template_lines = template_file.readlines()

        # Check for duplicate parameter names in the template file
        seen_parameters = set()
        for line in template_lines:
            line_stripped = line.strip()
            if any(
                line_stripped.startswith(param + args.param_separator)
                for param in parameter_names
            ):
                param_name = line_stripped.split(args.param_separator, 1)[0]
                if param_name in seen_parameters:
                    raise ValueError(
                        f"Duplicate parameter name '{param_name}' "
                        f"found in the template file."
                    )
                seen_parameters.add(param_name)

        # Modify the template file
        modified_lines = []
        found_parameters = set()
        for line in template_lines:
            line_stripped = line.strip()
            if any(
                line_stripped.startswith(param + args.param_separator)
                for param in parameter_names
            ):
                param_name = line_stripped.split(args.param_separator, 1)[0]
                modified_lines.append(
                f"{param_name}{args.param_separator}{param_values[param_name]}\n"
                )
                found_parameters.add(param_name)
            else:
                modified_lines.append(line)

        # Add missing parameters
        for param in parameter_names:
            if param not in found_parameters:
                modified_lines.append(
                f"{param}{args.param_separator}{param_values[param]}\n"
                )
    else:
        # If no template is provided, create a new parameter file
        modified_lines = [
            f"{param}{args.param_separator}{value}\n"
            for param, value in param_values.items()
        ]

    return modified_lines

def write_param_file(
    args, target_path, parameter_names, param_values,
    param_file_name
):
    """
    Write the output parameter file to the target folder.
    """

    # If verbosity level is 2, print the folder name
    if args.verbose == 2:
        print(f"Created folder: {target_path}")

    modified_lines = generate_param_file_lines(
        args, parameter_names, param_values
    )

    # Write the parameter file to the target folder
    with open(
        os.path.join(target_path, param_file_name), 'w', encoding='utf-8'
    ) as output_file:
        output_file.writelines(modified_lines)

def final_compression(args, batch_number=None):
    """
    Handle the final compression step: compress all simulations or batch folders.
    """
    if args.verbose >= 1:
        print("Compressing folders...")

    if args.by and batch_number:
        # Compress each batch folder
        for batch_num in range(1, batch_number + 1):
            batch_folder = os.path.join(args.target, f"{args.batch_prefix}{batch_num}")
            tarball_name = f"{batch_folder}.tar.gz"
            with tarfile.open(tarball_name, "w:gz") as tar:
                tar.add(batch_folder, arcname=os.path.basename(batch_folder))
            if args.verbose >= 1:
                print(f"Compressed batch folder '{batch_folder}' into '{tarball_name}'")
    else:
        # Compress everything into a single tarball
        tarball_name = os.path.join(args.target, f"{args.tarball_name}.tar.gz")
        with tarfile.open(tarball_name, "w:gz") as tar:
            tar.add(args.target, arcname=os.path.basename(args.target))
        if args.verbose >= 1:
            print(f"Compressed all simulations into '{tarball_name}'")

def main():
    """
    This function runs the main logic of the script. It processes command line arguments,
    generates simulation folders, dispatches files, and compresses folders as needed.
    """

    # Parse command-line arguments
    args = parse_arguments()

    # Dispatch-only mode
    if args.dispatch_only:
        dispatch_only_mode(args)
        return 0

    # Compress-only mode
    if args.compress_only:
        compress_only_mode(args)
        return 0

    # Determine the name of the parameter file in the final folder
    param_file_name = get_output_param_file_name(args)

    # Collect files from folder if provided
    if args.folder:
        get_filenames_from_folder(args)

    # Ensure there are files to process
    check_files_provided(args.filenames)

    # Check if all files have the same number of lines
    check_line_counts(args.filenames)

    # Open and process files
    with ExitStack() as stack:
        files = [
            stack.enter_context(open(filename, 'r', encoding='utf-8'))
            for filename in args.filenames
        ]
        parameter_names = [
            os.path.splitext(os.path.basename(filename))[0]
            for filename in args.filenames
        ]

        all_folders = get_all_folder_names(args, parameter_names, files)

        # Split folders into batches if batching is enabled
        batch_number = 1
        for i, (folder_name, param_values) in enumerate(all_folders):

            # Determine the batch folder path if batching is enabled
            target_path = get_target_path(args, folder_name, batch_number)

            # Ensure the target folder exists
            os.makedirs(target_path, exist_ok=True)

            write_param_file(
                args, target_path, parameter_names, param_values,
                param_file_name
            )

            # Dispatch files into the simulation folder
            if args.dispatch:
                dispatch_files(args, [target_path])

            # Print the target path
            if args.verbose == 2:
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
        if args.by:
            print(f"Total folders created: {total_folders} across {total_batches} batches.")
        else:
            print(f"Total folders created: {total_folders}.")

    # If needed...
    if args.compress:
        final_compression(args, batch_number)

    # Final message
    if args.verbose >= 1:
        print("All done.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
