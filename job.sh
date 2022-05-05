#!/bin/bash
#SBATCH --time=3:00:00
#SBATCH --mem=1Gb
#SBATCH --partition=regular
../brachypode parameters.txt
