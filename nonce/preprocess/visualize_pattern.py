import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os

def compute_patterns(df):
    b0_pattern = df.groupby('Type')['B0'].value_counts(normalize=True).unstack(fill_value=0).transpose()
    b3_pattern = df.groupby('Type')['B3'].value_counts(normalize=True).unstack(fill_value=0).transpose()
    

    asic_columes = [asic_names[type_] for type_ in b0_pattern.columns]
    b0_pattern.columns = asic_columes
    b3_pattern.columns = asic_columes
    return b0_pattern, b3_pattern

# Function to visualize patterns
def visualize_patterns(patterns, title):
    plt.figure(figsize=(10, 6))
    colors = [(0, 0, 0), (0, 1, 1)]  # Black to Red

    # Create the custom colormap
    cmap = LinearSegmentedColormap.from_list("black_to_red", colors)

    # Plot the heatmap with the custom colormap, swapping x and y axes
    # sns.heatmap(patterns, cmap=cmap, fmt=".2f", annot=True, xticklabels=True, yticklabels=True)
    sns.heatmap(patterns, cmap=cmap, fmt=".2f", annot=False, xticklabels=True, yticklabels=True)

    # Set labels and title
    plt.title(title)
    plt.xlabel('ASIC')  # Previously 'Bucket'
    plt.ylabel('Bucket')  # Previously 'ASIC'
    plt.show()

# Load data
# Assuming 'database' directory exists in the current working directory
np_path = os.path.join(os.getcwd(), "database", "mining_data_b12.npy")
np_array = np.load(np_path)

# Define ASIC_NAMES from log directory
log_directory = os.path.join(os.getcwd(), "database/nonce_log") 
asic_names = []
for subdir in os.listdir(log_directory):
    name = os.path.basename(subdir)
    asic_names.append(name)

column_names = ["Type", "B0", "B3"]
df = pd.DataFrame(np_array, columns=column_names)

b0_pattern, b3_pattern = compute_patterns(df)

# Visualize patterns
visualize_patterns(b0_pattern, title='B0 Pattern Distribution')
visualize_patterns(b3_pattern, title='B3 Pattern Distribution')
