import base64
import pandas as pd
import os
import glob
from csv import QUOTE_ALL

# Directory where images are located
image_dir = "./output_images"

# Load the IDs.csv file
ids_csv_path = "IDs.csv"
ids_df = pd.read_csv(ids_csv_path)

# Get all PNG files in the directory
image_files = glob.glob(os.path.join(image_dir, "*.png"))

# Data for CSV
data = []

for image_file in image_files:
    image_name = os.path.basename(image_file)
    name_without_prefix_suffix = image_name.replace("centered_", "").replace(".png", "")
    with open(image_file, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')
        # Find the corresponding ID
        matching_id_row = ids_df[ids_df['default_code'].astype(str) == name_without_prefix_suffix]
        if not matching_id_row.empty:
            matching_id = matching_id_row['id'].values[0]
        else:
            matching_id = None
        data.append({
            "filename": name_without_prefix_suffix,
            "base64_image": b64_string,
            "ID": matching_id
        })

# Create DataFrame
df = pd.DataFrame(data)

# Create a directory for the CSV files if it doesn't exist
csv_output_dir = "./csv/"
os.makedirs(csv_output_dir, exist_ok=True)

# Split the DataFrame into chunks of 5 rows each and save them to separate CSV files
chunk_size = 25
num_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size != 0 else 0)

for i in range(num_chunks):
    start_row = i * chunk_size
    end_row = start_row + chunk_size
    chunk_df = df.iloc[start_row:end_row]
    chunk_output_path = os.path.join(csv_output_dir, f"importCovers_chunk_{i+1}.csv")
    chunk_df.to_csv(chunk_output_path, index=False, sep=',', quoting=QUOTE_ALL)

print("CSV files have been generated and saved in the 'csv' directory.")
