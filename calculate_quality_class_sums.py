import json
import os

# Define the path to your quality results JSON file
# Assuming it's in the same folder where the quality assessment script saved it.
json_file_path = 'processed_images/0/quality_results.json'

def calculate_quality_class_sums(file_path):
    """
    Reads a JSON file containing image quality assessments and calculates
    the sum of images for each quality class.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: A dictionary where keys are quality assessment strings (e.g., "Good")
              and values are the counts of images belonging to that class.
              Returns None if the file cannot be read or parsed.
    """
    if not os.path.exists(file_path):
        print(f"Error: JSON file not found at '{file_path}'")
        return None

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading '{file_path}': {e}")
        return None

    quality_class_counts = {}

    for item in data:
        assessment = item.get('assessment')
        if assessment:
            quality_class_counts[assessment] = quality_class_counts.get(assessment, 0) + 1
        else:
            print(f"Warning: 'assessment' key not found for an item in {item.get('image_name', 'an image')}")

    return quality_class_counts

# --- Main execution ---
print(f"Calculating quality class sums from: '{json_file_path}'")

class_sums = calculate_quality_class_sums(json_file_path)

if class_sums:
    print("\n--- Quality Class Distribution ---")
    for assessment_class, count in class_sums.items():
        print(f"  {assessment_class}: {count} images")
else:
    print("Could not calculate quality class sums. Please ensure the JSON file is valid and accessible.")

print("\nCalculation complete.")
