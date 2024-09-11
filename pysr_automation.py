import pandas as pd
import re
import os
import matplotlib.pyplot as plt

def generate_hls_code_from_equations(csv_file, output_file):
    # Read the CSV file
    df = pd.read_csv(csv_file)
    with open(output_file, 'w') as f:
        f.write('#include <math.h>\n')
        # Math macros not natively supported by C that are used by PySR
        f.write("#define square(x) ((x) * (x))\n")
        f.write("#define cube(x) ((x) * (x) * (x))\n")
        f.write("#define neg(x) (-(x))\n")
        f.write("#define relu(x) ((x) > 0 ? (x) : 0)\n\n")

        # Generate a function for each equation
        for index, row in df.iterrows():
            complexity = row['Complexity']
            func_name = f"func_{complexity}"
            equation = row['Equation']

            # Find all unique variables like x0, x1, x2... in the equation
            variables = sorted(set(re.findall(r'x(\d+)', equation)), key=int)
            # Create function arguments like double x0, double x1,...
            func_args = ', '.join([f'double x{var}' for var in variables])
            # Replace 'x' with a valid variable name, e.g., x0, x1 becomes x0, x1 in the function body
            for var in variables:
                equation = equation.replace(f"x{var}", f"x{var}")

            # Write the function definition with direct variable names
            f.write(f"double {func_name}({func_args}) {{\n")
            f.write(f"    return {equation};\n")
            f.write("}\n\n")


def generate_tcl_script(df, base_dir, src_file):
    complexities = df['Complexity'].unique()
    tcl_script = os.path.join(base_dir, "run_synthesis.tcl")
    with open(tcl_script, 'w') as tcl:
        tcl.write("# This script automates the creation of PySR projects for each function in a single file,\n")
        tcl.write("# setting each as the top function, running synthesis, and exporting results.\n\n")
        for comp in complexities:
            proj_name = f"approx_{comp}"
            proj_path = os.path.join(base_dir, proj_name)
            tcl.write(f"file mkdir {proj_path}\n")
            tcl.write(f"cd {proj_path}\n")
            tcl.write(f"open_project {proj_name}\n")
            tcl.write(f"set_top func_{comp}\n")
            tcl.write(f"add_files {src_file}\n")
            tcl.write("open_solution solution1\n")
            tcl.write("set_part {xc7z020clg484-1}\n")
            tcl.write("create_clock -period 10 -name default\n")
            tcl.write("csynth_design\n")
            tcl.write("close_project\n")
            tcl.write(f"cd {base_dir}\n\n")

def main():
    ##### Tweak this #####
    csv_file = 'hall_of_fame_2024-09-10_170009.145.csv'
    ##### Tweak this #####
    # cd to the directory where the CSV file is located before running this script
    base_dir = os.getcwd()
    src_file = os.path.join(base_dir, 'hls_code_generated.c')
    output_hls_file = src_file
    output_tcl_file = os.path.join(base_dir, 'run_synthesis.tcl')
    print("This script generates HLS C code (Experimental) and a TCL script for each function in a CSV file. It also generates a graph of loss vs complexity.")

    # Check if the HLS file already exists
    if os.path.exists(output_hls_file):
        overwrite = input(f"{output_hls_file} already exists. Do you want to overwrite it? (y/n): ")
    if overwrite.lower() != 'y':
        print("Operation cancelled.")
    else:
    # Generate HLS C code
        generate_hls_code_from_equations(csv_file, output_hls_file)
        print("HLS C code has been generated successfully.")


    # Check if the TCL script already exists
    if os.path.exists(output_tcl_file):
        overwrite = input(f"{output_tcl_file} already exists. Do you want to overwrite it? (y/n): ")
    if overwrite.lower() != 'y':
        print("Operation cancelled.")
    else:
        # Generate TCL script
        df = pd.read_csv(csv_file)
        generate_tcl_script(df, base_dir, src_file)
        print("TCL script has been generated successfully.")

    # Generate graph of loss vs complexity
    df = pd.read_csv(csv_file)
    df.plot(x='Complexity', y='Loss', kind='line', marker='o')
    plt.xlabel('Complexity')
    plt.ylabel('Loss')
    plt.title('Loss vs Complexity')
    plt.grid(True)
    plt.savefig('loss_vs_complexity.png')
    print("Graph 'loss_vs_complexity.png' has been generated successfully.")


if __name__ == "__main__":
    main()
