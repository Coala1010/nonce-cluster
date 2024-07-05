import os
import json
import pandas as pd
from common import *


def scan_log_files(directory, out_dir, chunk_size=500000):
    for root, dirs, files in os.walk(directory):
        chunk_count = 1
        mining_data = []
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
                                pool_name = params[0]
                                nonce = params[4]
                                b0, b3 = get_b03(nonce)

                                mining_data.append({"Nonce": nonce, "b0": b0, "b3": b3})
                            
                                # Save the data to a new Excel file if chunk size is reached
                                if len(mining_data) >= chunk_size:
                                    save_to_excel(mining_data, chunk_count, root, out_dir)
                                    mining_data = []
                                    chunk_count += 1

                        except json.JSONDecodeError:
                            # Skip lines that are not valid JSON
                            continue

        # Save the remaining data to an Excel file
        save_to_excel(mining_data, chunk_count, root, out_dir)

def save_to_excel(data, chunk_count, folder_name, out_dir):
    mining_df = pd.DataFrame(data)
    excel_file_name = f"{os.path.basename(folder_name)}_ND_{chunk_count}.xlsx"
    excel_file_path = os.path.join(out_dir, excel_file_name)
    mining_df.to_excel(excel_file_path, index=False)
    print(f"{excel_file_name} saved")

# Specify the directory containing the log files
log_directory = os.path.join(os.getcwd(), "database/preprocessed1") 

out_directory = os.path.join(os.getcwd(), "database/filtered") 
if (not os.path.isdir(out_directory)):
    os.mkdir(out_directory)

# Call the function to scan log files
scan_log_files(log_directory, out_directory)
