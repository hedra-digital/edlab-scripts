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

# Save to CSV with proper formatting
output_csv_path = "importCovers.csv"
df.to_csv(output_csv_path, index=False, sep=',', quoting=QUOTE_ALL)

# Display first few rows to ensure correctness
print(df.head())
