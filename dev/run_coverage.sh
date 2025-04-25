#!/bin/bash

## Run this script from the root directory to analyze code coverage
## during tests. It will open the HTML report using Firefox.

# Get coverage and generate report 
python3 -m coverage run --source=simarray -m unittest discover -s tests
python3 -m coverage report
python3 -m coverage html

# Open the HTML report in your browser
xdg-open htmlcov/index.html