## This script runs unit tests for the simarray.py script.

import os
import shutil
import unittest
from simarray import main
from unittest.mock import patch
import warnings
import sys
import subprocess

class TestSimArray(unittest.TestCase):
    def setUp(self):
        """Set up temporary directories and files for testing."""
        self.test_dir = "test_simarray"
        self.target_dir = os.path.join(self.test_dir, "sims")
        self.input_dir = os.path.join(self.test_dir, "input")
        os.makedirs(self.target_dir, exist_ok=True)
        os.makedirs(self.input_dir, exist_ok=True)

        # Create sample input files
        with open(os.path.join(self.input_dir, "mutation.txt"), "w") as f:
            f.write("0.1\n0.2\n")
        with open(os.path.join(self.input_dir, "selection.txt"), "w") as f:
            f.write("0.5\n0.6\n")

    def tearDown(self):
        """Clean up temporary directories and files after testing."""
        shutil.rmtree(self.test_dir)

    @patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "2"])
    def test_folder_generation(self):
        """Test folder generation with input files."""
        main()
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "sim_selection_0.5_mutation_0.1_r1")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "sim_selection_0.5_mutation_0.1_r2")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "sim_selection_0.6_mutation_0.2_r1")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "sim_selection_0.6_mutation_0.2_r2")))
        
    @patch("sys.argv", ["simarray.py", "file1.txt", "file2.txt", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "2"])
    def test_folder_and_filenames_provided(self):
        """Test that the script works when both --folder and filenames are provided."""
        # Create the specified files in the input folder
        file1_path = os.path.join(self.input_dir, "file1.txt")
        file2_path = os.path.join(self.input_dir, "file2.txt")
        with open(file1_path, "w") as f:
            f.write("0.1\n0.2\n")
        with open(file2_path, "w") as f:
            f.write("0.5\n0.6\n")

        # Run the folder generation mode
        main()

        # Check that the simulation folders are created
        expected_folders = [
            "sim_file1_0.1_file2_0.5_r1",
            "sim_file1_0.1_file2_0.5_r2",
            "sim_file1_0.2_file2_0.6_r1",
            "sim_file1_0.2_file2_0.6_r2"
        ]
        for folder_name in expected_folders:
            folder_path = os.path.join(self.target_dir, folder_name)
            self.assertTrue(os.path.exists(folder_path), f"Simulation folder {folder_name} does not exist.")
            
    @patch("sys.argv", ["simarray.py"])
    def test_folder_generation_no_input_files(self):
        """Test error when folder generation is attempted without input files."""
        # Ensure the input directory exists but contains no input files
        shutil.rmtree(self.input_dir, ignore_errors=True)
        os.makedirs(self.input_dir, exist_ok=True)

        # Attempt to run the folder generation mode
        with self.assertRaises(ValueError) as context:
            main()

        # Check if the error message is correct
        self.assertIn("No files provided", str(context.exception))
        
    @patch("sys.argv", ["simarray.py", "test_simarray/input/file1.txt", "test_simarray/input/file2.txt", "--target", "test_simarray/sims"])
    def test_input_files_with_different_line_counts(self):
        """Test error when input files have different numbers of lines."""
        # Create input files with different numbers of lines
        input_file_1 = os.path.join(self.input_dir, "file1.txt")
        input_file_2 = os.path.join(self.input_dir, "file2.txt")
        
        with open(input_file_1, "w") as f:
            f.write("line1\nline2\nline3\n")  # 3 lines
        with open(input_file_2, "w") as f:
            f.write("line1\nline2\n")  # 2 lines

        # Attempt to run the program
        with self.assertRaises(ValueError) as context:
            main()

        # Check if the error message is correct
        self.assertIn("Files do not have the same number of lines.", str(context.exception))
        
    @patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "4", "--by", "3", "--verbose", "2"])
    def test_folder_generation_with_batches(self):
        """Test folder generation with batches using the --by argument."""
        # Run the folder generation mode
        main()

        # Check the number of batch folders created
        batch_folders = [
            folder for folder in os.listdir(self.target_dir)
            if os.path.isdir(os.path.join(self.target_dir, folder)) and folder.startswith("batch_")
        ]
        self.assertGreater(len(batch_folders), 0, "No batch folders were created.")

        # Verify the number of simulation folders in each batch
        total_simulation_folders = 0
        for batch_folder in batch_folders:
            batch_folder_path = os.path.join(self.target_dir, batch_folder)
            simulation_folders = [
                folder for folder in os.listdir(batch_folder_path)
                if os.path.isdir(os.path.join(batch_folder_path, folder))
            ]
            total_simulation_folders += len(simulation_folders)

            # Check the number of simulation folders in the batch
            self.assertLessEqual(len(simulation_folders), 3, f"Batch {batch_folder} contains more than 3 simulation folders.")
    
        # Verify the total number of simulation folders
        expected_simulation_folders = 8  # 2 combinations x 4 replicates = 8 simulations
        self.assertEqual(total_simulation_folders, expected_simulation_folders, "Total number of simulation folders is incorrect.")
            
    @patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "2", "--template", "test_simarray/template.txt"])
    def test_template_file_handling(self):
        """Test that the template file is copied and modified into each simulation folder."""
        # Create a template file
        template_file = os.path.join(self.test_dir, "template.txt")
        with open(template_file, "w") as f:
            f.write("selection 0\nmutation 0\nrecombination 0.99\n")

        # Run the folder generation mode
        main()

        # Check that the template file is copied and modified in each simulation folder
        expected_folders = [
            "sim_selection_0.5_mutation_0.1_r1",
            "sim_selection_0.5_mutation_0.1_r2",
            "sim_selection_0.6_mutation_0.2_r1",
            "sim_selection_0.6_mutation_0.2_r2",
        ]
        for folder_name in expected_folders:
            folder_path = os.path.join(self.target_dir, folder_name)
            self.assertTrue(os.path.exists(folder_path), f"Simulation folder {folder_name} does not exist.")
            
            # Check if the modified template file exists in the folder
            modified_template_path = os.path.join(folder_path, "template.txt")
            self.assertTrue(os.path.exists(modified_template_path), f"Template file not found in {folder_name}.")

            # Get expected values from the folder name
            selection_value = folder_name.split("_")[2]
            mutation_value = folder_name.split("_")[4]

            # Verify the contents of the modified template file
            with open(modified_template_path, "r") as f:
                content = f.read()
                self.assertIn(f"selection {selection_value}", content)
                self.assertIn(f"mutation {mutation_value}", content)
                self.assertIn(f"recombination 0.99", content)        
            
    @patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "2", "--template", "test_simarray/template.txt"])
    def test_duplicate_parameters_in_template(self):
        """Test error when duplicate parameters are found in the template file."""
        # Create a template file with duplicate parameters
        template_file = os.path.join(self.test_dir, "template.txt")
        with open(template_file, "w") as f:
            f.write("selection 0\nmutation 0\nselection 0\n")

        # Attempt to run the folder generation mode
        with self.assertRaises(ValueError) as context:
            main()

        # Check if the error message is correct
        self.assertIn("Duplicate parameter name 'selection' found in the template file.", str(context.exception))
                
    @patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "2", "--template", "test_simarray/template.txt", "--output-param-file", "parameters.txt"])
    def test_add_missing_parameters_to_output_file(self):
        """Test that missing parameters are added to the output parameter file in each simulation folder."""
        # Create a template file without the "mutation" parameter
        template_file = os.path.join(self.test_dir, "template.txt")
        with open(template_file, "w") as f:
            f.write("selection {selection}\nrecombination {recombination}\n")

        # Run the folder generation mode
        main()

        # Check that the output parameter file exists in each simulation folder
        expected_folders = [
            "sim_selection_0.5_mutation_0.1_r1",
            "sim_selection_0.5_mutation_0.1_r2",
            "sim_selection_0.6_mutation_0.2_r1",
            "sim_selection_0.6_mutation_0.2_r2",
        ]
        for folder_name in expected_folders:
            folder_path = os.path.join(self.target_dir, folder_name)
            self.assertTrue(os.path.exists(folder_path), f"Simulation folder {folder_name} does not exist.")

            # Check the output parameter file in the simulation folder
            output_param_file = os.path.join(folder_path, "parameters.txt")
            self.assertTrue(os.path.exists(output_param_file), f"Output parameter file was not created in {folder_name}.")

            # Verify that the missing parameter "mutation" is added to the output parameter file
            with open(output_param_file, "r") as f:
                content = f.read()
                self.assertIn("mutation", content, f"Missing parameter 'mutation' was not added to the output parameter file in {folder_name}.")                    
    
    @patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "2", "--dispatch", "test_simarray/dispatch1.txt", "test_simarray/dispatch2.txt"])
    def test_dispatch_multiple_files(self):
        """Test dispatching multiple files into newly created simulation folders."""

        # Create files to dispatch
        dispatch_file_1 = os.path.join(self.test_dir, "dispatch1.txt")
        dispatch_file_2 = os.path.join(self.test_dir, "dispatch2.txt")
        with open(dispatch_file_1, "w") as f:
            f.write("This is dispatch file 1.")
        with open(dispatch_file_2, "w") as f:
            f.write("This is dispatch file 2.")

        # Dispatch the files
        main()

        # Check if the files were dispatched into all simulation folders
        expected_folders = [
            "sim_selection_0.5_mutation_0.1_r1",
            "sim_selection_0.5_mutation_0.1_r2",
            "sim_selection_0.6_mutation_0.2_r1",
            "sim_selection_0.6_mutation_0.2_r2",
        ]
        for folder_name in expected_folders:
            folder_path = os.path.join(self.target_dir, folder_name)
            self.assertTrue(os.path.exists(folder_path), f"Simulation folder {folder_name} does not exist.")

            # Check if both dispatch files exist in the folder
            dispatched_file_1 = os.path.join(folder_path, "dispatch1.txt")
            dispatched_file_2 = os.path.join(folder_path, "dispatch2.txt")
            self.assertTrue(os.path.exists(dispatched_file_1), f"File 'dispatch1.txt' was not dispatched to {folder_name}.")
            self.assertTrue(os.path.exists(dispatched_file_2), f"File 'dispatch2.txt' was not dispatched to {folder_name}.")
        
    @patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "2", "--dispatch", "test_simarray/nonexistent.txt"])
    def test_dispatch_missing_file(self):
        """Test error when --dispatch is used with a nonexistent file."""

        # Attempt to run with a nonexistent dispatch file
        with self.assertRaises(ValueError) as context:
            main()

        # Check if the error message is correct
        self.assertIn("File 'test_simarray/nonexistent.txt' specified in --dispatch does not exist or is not a file.", str(context.exception))            
    
    @patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "4", "--by", "3", "--compress"])
    def test_compress_batch_folders(self):
        """Test that batch folders are compressed into tarballs when --compress is enabled."""
        # Run the folder generation mode with batching and compression
        main()

        # Check the number of batch folders created
        batch_folders = [
            folder for folder in os.listdir(self.target_dir)
            if os.path.isdir(os.path.join(self.target_dir, folder)) and folder.startswith("batch_")
        ]
        self.assertGreater(len(batch_folders), 0, "No batch folders were created.")

        # Check that each batch folder has a corresponding tarball
        for batch_folder in batch_folders:
            tarball_path = os.path.join(self.target_dir, f"{batch_folder}.tar.gz")
            self.assertTrue(os.path.exists(tarball_path), f"Tarball for batch folder '{batch_folder}' was not created.")
            
    @patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "2", "--compress", "--sim-prefix", "sim", "--tarball-name", "all_simulations"])
    def test_compress_all_simulation_folders(self):
        """Test that all simulation folders are compressed into a single tarball when --compress is used without --by."""
        # Run the folder generation mode with compression
        main()

        # Check that all simulation folders are created
        expected_folders = [
            "sim_selection_0.5_mutation_0.1_r1",
            "sim_selection_0.5_mutation_0.1_r2",
            "sim_selection_0.6_mutation_0.2_r1",
            "sim_selection_0.6_mutation_0.2_r2",
        ]
        for folder_name in expected_folders:
            folder_path = os.path.join(self.target_dir, folder_name)
            self.assertTrue(os.path.exists(folder_path), f"Simulation folder {folder_name} does not exist.")

        # Check if the single tarball was created
        tarball_path = os.path.join(self.target_dir, "all_simulations.tar.gz")
        self.assertTrue(os.path.exists(tarball_path), "The tarball for all simulation folders was not created.")

        # Verify the contents of the tarball
        import tarfile
        with tarfile.open(tarball_path, "r:gz") as tar:
            folder_names = [os.path.basename(member.name) for member in tar.getmembers() if member.isdir()]
            for folder_name in expected_folders:
                self.assertIn(folder_name, folder_names, f"Simulation folder {folder_name} is missing from the tarball.")
                
    @patch("sys.argv", ["simarray.py", "--target", "test_simarray/sims", "--dispatch", "test_simarray/dispatch.txt", "--dispatch-only", "--verbose", "2"])
    def test_dispatch_only(self):
        """Test dispatching files into existing folders."""
        # First, generate folders
        with patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "1"]):
            main()

        # Create a file to dispatch
        dispatch_file = os.path.join(self.test_dir, "dispatch.txt")
        with open(dispatch_file, "w") as f:
            f.write("This is a test file.")

        # Dispatch the file
        main()

        # Check if the file was dispatched into all simulation folders
        for folder in os.listdir(self.target_dir):
            folder_path = os.path.join(self.target_dir, folder)
            if os.path.isdir(folder_path):
                self.assertTrue(os.path.exists(os.path.join(folder_path, "dispatch.txt")))
                            
    @patch("sys.argv", ["simarray.py", "--target", "test_simarray/sims", "--dispatch", "test_simarray/dispatch.txt", "--dispatch-only", "--dispatch-recursive", "--batch-prefix", "batch_", "--sim-prefix", "sim_", "--verbose", "2"])
    def test_dispatch_only_recursive(self):
        """Test dispatching files into simulation folders recursively within batch folders."""
    
        # Create batch folders in the target directory
        batch_folder_1 = os.path.join(self.target_dir, "batch_1")
        batch_folder_2 = os.path.join(self.target_dir, "batch_2")
        os.makedirs(batch_folder_1, exist_ok=True)
        os.makedirs(batch_folder_2, exist_ok=True)
    
        # Create simulation folders within batch folders
        sim_folder_1 = os.path.join(batch_folder_1, "sim_1")
        sim_folder_2 = os.path.join(batch_folder_2, "sim_2")
        os.makedirs(sim_folder_1, exist_ok=True)
        os.makedirs(sim_folder_2, exist_ok=True)
    
        # Create a file to dispatch
        dispatch_file = os.path.join(self.test_dir, "dispatch.txt")
        with open(dispatch_file, "w") as f:
            f.write("This is a test file.")
    
        # Dispatch the file
        main()
    
        # Check if the file was dispatched into all simulation folders
        for sim_folder in [sim_folder_1, sim_folder_2]:
            self.assertTrue(
                os.path.exists(os.path.join(sim_folder, "dispatch.txt")),
                f"File 'dispatch.txt' was not dispatched to {sim_folder}."
            )
                            
    @patch("sys.argv", ["simarray.py", "--target", "test_simarray/sims", "--dispatch-only"])
    def test_dispatch_only_missing_dispatch(self):
        """Test error when --dispatch-only is used without --dispatch."""
        # First, generate folders
        with patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "1"]):
            main()

        # Attempt to run --dispatch-only without --dispatch
        with self.assertRaises(ValueError) as context:
            main()

        # Check if the error message is correct
        self.assertIn("No files specified for dispatch. Use the --dispatch argument to specify files.", str(context.exception))

    @patch("sys.argv", ["simarray.py", "--target", "test_simarray/sims", "--dispatch", "test_simarray/dispatch.txt", "--dispatch-only"])
    def test_dispatch_only_no_matching_folders(self):
        """Test warning when --dispatch-only is used but no matching simulation folders are found."""
        # Create a file to dispatch
        dispatch_file = os.path.join(self.test_dir, "dispatch.txt")
        with open(dispatch_file, "w") as f:
            f.write("This is a test file.")

        # Ensure no simulation folders exist in the target directory
        shutil.rmtree(self.target_dir)
        os.makedirs(self.target_dir, exist_ok=True)

        # Check if a warning is raised
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Catch all warnings
            main()

            # Verify that a warning was raised
            self.assertTrue(len(w) > 0)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertIn("No simulation folders found", str(w[-1].message))

    @patch("sys.argv", ["simarray.py", "--target", "test_simarray/sims", "--dispatch", "test_simarray/nonexistent.txt", "--dispatch-only"])
    def test_dispatch_only_missing_file(self):
        """Test error when --dispatch-only is used with a nonexistent dispatch file."""
        # First, generate folders
        with patch("sys.argv", ["simarray.py", "--folder", "test_simarray/input", "--target", "test_simarray/sims", "--replicates", "1"]):
            main()

        # Attempt to run --dispatch-only with a nonexistent file
        with self.assertRaises(ValueError) as context:
            main()

        # Check if the error message is correct
        self.assertIn("File 'test_simarray/nonexistent.txt' specified in --dispatch does not exist or is not a file.", str(context.exception))

    @patch("sys.argv", ["simarray.py", "--compress-only", "--compress-all", "--target", "test_simarray/sims", "--sim-prefix", "sim", "--tarball-name", "all_simulations"])
    def test_compress_only_with_compress_all(self):
        """Test compressing all simulation folders into a single tarball using --compress-all."""
        # Create simulation folders in the current working directory
        sim_folder_1 = os.path.join(self.target_dir, "sim_folder_1")
        sim_folder_2 = os.path.join(self.target_dir, "sim_folder_2")
        os.makedirs(sim_folder_1, exist_ok=True)
        os.makedirs(sim_folder_2, exist_ok=True)

        # Add some files to the simulation folders
        with open(os.path.join(sim_folder_1, "file1.txt"), "w") as f:
            f.write("This is file1 in sim_folder_1.")
        with open(os.path.join(sim_folder_2, "file2.txt"), "w") as f:
            f.write("This is file2 in sim_folder_2.")

        # Run the compress-only mode with --compress-all
        main()

        # Check if the tarball was created
        tarball_path = os.path.join(self.target_dir, "all_simulations.tar.gz")
        self.assertTrue(os.path.exists(tarball_path))

        # Verify the contents of the tarball
        import tarfile
        with tarfile.open(tarball_path, "r:gz") as tar:
            folder_names = [os.path.basename(member.name) for member in tar.getmembers() if member.isdir()]
            self.assertIn("sim_folder_1", folder_names)
            self.assertIn("sim_folder_2", folder_names)
    
    @patch("sys.argv", ["simarray.py", "--compress-only", "--compress-all", "--sim-prefix", "sim", "--target", "test_simarray/sims"])
    def test_compress_only_with_compress_all_no_simulation_folders(self):
        """Test warning when --compress-only with --compress-all is used but no simulation folders are found."""
        # Ensure the target directory exists but contains no simulation folders
        shutil.rmtree(self.target_dir, ignore_errors=True)
        os.makedirs(self.target_dir, exist_ok=True)

        # Run the compress-only mode with --compress-all
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Catch all warnings
            main()

            # Verify that a warning was raised
            self.assertTrue(len(w) > 0)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertIn("No simulation folders found", str(w[-1].message))
        
    @patch("sys.argv", ["simarray.py", "--compress-only", "--batch-prefix", "batch_", "--target", "test_simarray/sims"])
    def test_compress_only_without_compress_all(self):
        """Test compressing each batch folder into separate tarballs when --compress-all is off."""
        # Create batch folders in the target directory
        batch_folder_1 = os.path.join(self.target_dir, "batch_1")
        batch_folder_2 = os.path.join(self.target_dir, "batch_2")
        os.makedirs(batch_folder_1, exist_ok=True)
        os.makedirs(batch_folder_2, exist_ok=True)

        # Add some files to the batch folders
        with open(os.path.join(batch_folder_1, "file1.txt"), "w") as f:
            f.write("This is file1 in batch_1.")
        with open(os.path.join(batch_folder_2, "file2.txt"), "w") as f:
            f.write("This is file2 in batch_2.")

        # Run the compress-only mode without --compress-all
        main()

        # Check if tarballs were created for each batch folder
        tarball_1 = os.path.join(self.target_dir, "batch_1.tar.gz")
        tarball_2 = os.path.join(self.target_dir, "batch_2.tar.gz")
        self.assertTrue(os.path.exists(tarball_1))
        self.assertTrue(os.path.exists(tarball_2))

        # Verify the contents of the tarballs
        import tarfile
        with tarfile.open(tarball_1, "r:gz") as tar:
            folder_names = [os.path.basename(member.name) for member in tar.getmembers() if member.isdir()]
            self.assertIn("batch_1", folder_names)
        with tarfile.open(tarball_2, "r:gz") as tar:
            folder_names = [os.path.basename(member.name) for member in tar.getmembers() if member.isdir()]
            self.assertIn("batch_2", folder_names)            
        
    @patch("sys.argv", ["simarray.py", "--compress-only", "--batch-prefix", "batch_", "--target", "test_simarray/sims"])
    def test_compress_only_no_batch_folders(self):
        """Test warning when --compress-only is used but no batch folders are found."""
        # Ensure the target directory exists but contains no batch folders
        shutil.rmtree(self.target_dir, ignore_errors=True)
        os.makedirs(self.target_dir, exist_ok=True)

        # Run the compress-only mode
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Catch all warnings
            main()

            # Verify that a warning was raised
            self.assertTrue(len(w) > 0)
            self.assertTrue(issubclass(w[-1].category, UserWarning))
            self.assertIn("No batch folders found", str(w[-1].message))    
            
    def test_main_entry_point(self):
        """Test the main entry point of the script."""
        # Path to the script
        script_path = os.path.abspath("simarray.py")

        # Run the script as a subprocess
        result = subprocess.run(
            [sys.executable, script_path, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Check that the script runs successfully and exits with code 0
        self.assertEqual(result.returncode, 0, "Script did not exit with code 0.")

        # Check that the version output is correct
        self.assertIn("SimArray", result.stdout)

if __name__ == "__main__":
    unittest.main()