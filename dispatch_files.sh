#!/bin/bash

# Dispatch files into all subdirectories

# Error if no arguments
if [ $# -eq 0 ]; then
    echo "No arguments provided"
    exit 1
fi

echo "Dispatching files..."

# For each target folder...
for dir in ./*/
do

	# For each argument (= file to copy)...
	for file in "$@"
	do

		# Error if the argument is not a file in the working directory
		if [ ! -f $file ]; then
			echo "Could not find file $file"
			exit 1 
		fi

		# Otherwise copy the file into the target folder
		cp $file $dir

	done

done