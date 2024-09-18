#!/bin/bash

# set -x # Uncomment to debug

# Step 1: Prompt for the Hall of Fame CSV file
echo -n "Please enter the filename of the Hall of Fame CSV (e.g., hall_of_fame.csv): "
read hof_csv

# Check if the file exists
if [ ! -f "$hof_csv" ]; then
    echo -e "\nError: File '$hof_csv' not found in the current directory."
    exit 1
fi

echo -e "\nFound '$hof_csv'"

# Step 2: Generate HLS code and TCL script
echo -e "\nGenerating HLS code and TCL script...\n"
python pysr_automation.py "$hof_csv"

if [ $? -ne 0 ]; then
    echo -e "\nError: Failed to run pysr_automation.py"
    exit 1
fi

# Step 3: Check for run_synthesis.tcl
if [ ! -f run_synthesis.tcl ]; then
    echo -e "\nError: run_synthesis.tcl not found."
    exit 1
fi

# Step 4: Run TCL script with Vitis HLS
echo -e "\nRunning Vitis HLS synthesis...\n"
vitis_hls -f run_synthesis.tcl

if [ $? -ne 0 ]; then
    echo -e "\nError: Vitis HLS synthesis failed."
    exit 1
fi

# Step 5: Run data visualization
echo -e "\nVitis HLS Synthesis completed.\n"
echo -e "\nRunning data visualization...\n"
python plot_automation.py

if [ $? -ne 0 ]; then
    echo -e "\nError: Failed to run plot_automation.py"
    exit 1
fi

echo -e "\nAll tasks completed successfully. Files generated: loss_vs_complexity.png, synthesis_results.png, synthesis_results.csv\n"
