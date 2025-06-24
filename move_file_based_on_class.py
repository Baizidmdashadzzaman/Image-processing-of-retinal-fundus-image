import pandas as pd
import os
import shutil

# Paths
csv_path = 'train.csv'  # Adjust if needed
image_folder = 'train_images'
output_base_folder = 'sorted_images'  # Will hold class folders 0, 1, ..., 4

# Read the CSV
df = pd.read_csv(csv_path)

# Ensure output folders exist
for class_label in df['diagnosis'].unique():
    class_folder = os.path.join(output_base_folder, str(class_label))
    os.makedirs(class_folder, exist_ok=True)

# Move files
for _, row in df.iterrows():
    image_name = f"{row['id_code']}.png"  # Assuming .png images
    src_path = os.path.join(image_folder, image_name)
    dst_path = os.path.join(output_base_folder, str(row['diagnosis']), image_name)

    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)
    else:
        print(f"Image not found: {src_path}")




