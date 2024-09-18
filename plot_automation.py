import os
import json
import glob
import matplotlib.pyplot as plt
import pandas as pd

def extract_data(json_file_path, complexity):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            util_data = data.get("ModuleInfo", {}).get("Metrics", {}).get(f"func_{complexity}", {}).get("Area", {})
            time_data = data.get("ModuleInfo", {}).get("Metrics", {}).get(f"func_{complexity}", {}).get("Timing", {})
            latency_data = data.get("ModuleInfo", {}).get("Metrics", {}).get(f"func_{complexity}", {}).get("Latency", {})
            return util_data, time_data, latency_data
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {json_file_path}")
    return None, None, None

def convert_to_float_list(data_list):
    return [float(item.replace('~0', '0')) for item in data_list]

def plot_data(complexities, utils, latencies):
    ff_utils = convert_to_float_list([u['UTIL_FF'] for u in utils])
    lut_utils = convert_to_float_list([u['UTIL_LUT'] for u in utils])
    dsp_utils = convert_to_float_list([u['UTIL_DSP'] for u in utils])
    avg_latencies = convert_to_float_list([l['LatencyAvg'] for l in latencies])
    plt.figure(figsize=(12, 8))
    
    # Utilization plot
    plt.subplot(2, 1, 1)
    plt.plot(complexities, ff_utils, label='FF', marker='o')
    plt.plot(complexities, lut_utils, label='LUT', marker='x')
    plt.plot(complexities, dsp_utils, label='DSP', marker='s')
    plt.xlabel('Complexity')
    plt.ylabel('Utilization (%)')
    plt.title('Utilization Metrics')
    plt.legend()
    plt.grid(True)
    plt.xticks(complexities)  # Ensure x-axis values are integers

    # Latency plot
    plt.subplot(2, 1, 2)
    plt.plot(complexities, avg_latencies, label='Latency', marker='o')
    plt.xlabel('Complexity')
    plt.ylabel('Latency (ns)')
    plt.title('Latency Metrics')
    plt.legend()
    plt.grid(True)
    plt.xticks(complexities)  # Ensure x-axis values are integers

    plt.tight_layout()

    if os.path.exists('synthesis_results.png'):
        overwrite = input("synthesis_results.png already exists. Do you want to overwrite it? (y/n): ")
    if overwrite.lower() == 'y':
        plt.savefig('synthesis_results.png')
    else:
        print("Operation cancelled.")
    # plt.show()


def main(base_dir):
    project_dirs = glob.glob(os.path.join(base_dir, 'approx_*', 'approx_*'))
    complexities = []
    utilizations = []
    latencies = []

    for project_path in project_dirs:
        complexity = os.path.basename(project_path).split('_')[-1]
        json_file_path = os.path.join(project_path, "solution1", "solution1_data.json")
        data = extract_data(json_file_path, complexity)
        util_data, time_data, latency_data = data
        if util_data and time_data and latency_data:
            complexities.append(int(complexity))
            utilizations.append(util_data)
            latencies.append((latency_data))
    # sort the complexities and correspond the complexities to the utilizations and latencies
    complexities, utilizations, latencies = zip(*sorted(zip(complexities, utilizations, latencies)))
    plot_data(complexities, utilizations, latencies)

    print("\nSaving raw synthesis results to synthesis_results.csv...")
    df = pd.DataFrame({
        'Complexity': complexities,
        'Utilization': utilizations,
        'Latency': latencies
    })
    if os.path.exists(os.path.join(base_dir, 'synthesis_results.csv')):
        overwrite = input("synthesis_results.csv already exists. Do you want to overwrite it? (y/n): ")
    if overwrite.lower() == 'y':
        df.to_csv(os.path.join(base_dir, 'synthesis_results.csv'), index=False)
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    # cd to the directory where the approx_* directories are located before running this script
    base_dir = os.getcwd()
    main(base_dir)
