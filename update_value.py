#!/usr/bin/python3

# This script changes a parameter value in the parameter file to the value supplied
# It takes as arguments:
# (1) the parameter file name
# (2) the name of the parameter to change
# (3) the new value(s), as arguments
# Example: 'python3 updateValue.py parameters.txt scaleI "0 0 0"' (use quotes if the last argument has multiple values)

import sys
import re

# There should be three arguments
if len(sys.argv) != 4:
	raise Exception("There should be three arguments")

# Get the name of the parameter file
filename = sys.argv[1];
parname = sys.argv[2];
newvalue = sys.argv[3];

# Read each line in the file
# But change the line in case it is the parameter to be changed
# Add said line to what is to write
# Rewrite everything

# Prepare to collect the lines in the file
lines = ''

# Open the file
with open(filename, "rt") as f:

	# Go through the lines
	for cnt, line in enumerate(f):

		# If the parameter of interest is here...
		if re.match(parname, line):
			
			# Update its value
			line = re.sub(" .*$", " " + newvalue, line)
			
		# Collect the current line (to rewrite them all later)
		lines = lines + line


# Rewrite the file
with open(filename, "w+") as f:
	f.write(lines)