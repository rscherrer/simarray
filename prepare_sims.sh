#!bin/bash

# Creates many simulation folders based on parameter values from files

# Error if no arguments
if [ $# -eq 0 ]; then
    echo "No arguments provided"
    exit 1
fi

# For each argument...
for input in "$@"
do

	# Error if the argument is not a file in the working directory
	if [ ! -f $input ]; then
		echo "Could not find file $input"
		exit 1 
	fi
done

echo "Working on it..."

# Read input files and combine their values into simulation folder names
python3 make_folder_names.py "$@"

# Make sure the list of folder names was created
if [ ! -f  "folder_names.txt" ]; then
	echo "Could not find file folder_names.txt"
	exit 1
fi

# Make sure a template parameter file is available
if [ ! -f "parameters.txt" ]; then
	echo "Could not find file parameters.txt"
	exit 1
fi

# For each folder in the list of folder names...
while IFS= read -r folder
do

	# Make that folder
	mkdir "$folder"

	# Copy the template parameter file into it
	cp "parameters.txt" "$folder"

done < "folder_names.txt"

# For each input file...
for input in "$@"
do

	# Extract the corresponding parameter name by removing the .txt extension at the end
	parname=${input::-4}

	# Read the input file and the list of folder names together, and for each line (i.e. new parameter value)...
	while IFS= read -r -u 2 folder && IFS= read -r -u 3 newvalue;
	do

		# Update the value of the corresponding parameter in the parameter file within that folder
		python3 update_value.py "$folder/parameters.txt" "$parname" "$newvalue"	

	done 2<"folder_names.txt" 3<$input

done

# Remove the list of folder names
rm "folder_names.txt"

