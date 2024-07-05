import os
import json
import pandas as pd
import numpy as np
from common import *

def scan_log_files(directory, out_file):
    mining_data = []
    dir_names = []
    for subdir in os.listdir(directory):
        name = os.path.basename(subdir)
        dir_names.append(name)
    
    print(dir_names)

    for root, dirs, files in os.walk(directory):
        if (os.path.basename(root) in dir_names):
            asic_type = dir_names.index(os.path.basename(root))
        else:
            continue

        for file in files:
            if file.endswith(".log"):  # Check if the file is a log file
                file_path = os.path.join(root, file)
                with open(file_path, "r") as log_file:
                    for line in log_file:
                        try:
                            log_entry = json.loads(line.strip())
                            method = log_entry.get("method", "")
                            params = log_entry.get("params", [])
                            idx = log_entry.get("id", -1)

                            # Check if the log entry corresponds to a mining submission
                            if method == "mining.submit":
                                # Extract relevant data such as mining pool name and nonce
                                nonce = params[4]
                                # b0, b3 = get_b03(nonce)
                                b0, b3 = get_b12(nonce)

                                mining_data.append([asic_type, b0, b3])

                        except json.JSONDecodeError:
                            # Skip lines that are not valid JSON
                            continue

    # Save all the data to a NumPy array file
    np.save(out_file, np.array(mining_data))
    print(f"Data saved to {out_file}")

# Specify the directory containing the log files
log_directory = os.path.join(os.getcwd(), "database/nonce_log") 

# Specify the output file for the NumPy array
out_file = os.path.join(os.getcwd(), "database/mining_data_b12.npy")

# Call the function to scan log files
scan_log_files(log_directory, out_file)

# # Load the data from the file
# mining_data = np.load(out_file)

# # Access the data as needed
# print(mining_data)
# print(np.shape(mining_data))