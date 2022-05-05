#!/usr/bin/python3

# Script to read parameter values from multiple files and combine them into a list of simulation folder names

import sys
import re

# Initializiation
folders = []

a = 0 # count through input files
n = 0 # count through folders

# Error if no argument is provided
if len(sys.argv) == 1:
	raise Exception("No argument provided")

# For each argument provided (each input file name)...
for filename in sys.argv[1:]:

	# Open that file
	with open(filename, 'r') as f:

		# Extract parameter name from the file name
		parname = filename[0:(len(filename) - 4)]

		# For each line (i.e. parameter value) in the file...
		for count, line in enumerate(f):

			# Make an entry comprising parameter name and current value
			entry = "_" + parname + "_" + re.sub(' ', '_', line.strip())
	
			# If not already done...
			if a == 0:

				# Create a new folder name based on the entry
				folder = "sim" + entry
				folders.append(folder)
				
			else:

				# Otherwise append the entry to existing folder name
				folders[count] = folders[count] + entry

		# Count the number of lines in the first input file
		if a == 0:
			n = count + 1
	
		# Error if any file does not have the same number of lines as the first one
		if (count + 1) != n:
			raise Exception("File " + filename + " does not have the same number of lines as " + sys.argv[1])
	
		# Update input file number
		a = a + 1

# Open an output file
with open("folder_names.txt", 'w') as ff:

	# For each folder in the list we created...
	for folder in folders:

		# Write that folder name to the output file
		ff.writelines(folder + '\n')

