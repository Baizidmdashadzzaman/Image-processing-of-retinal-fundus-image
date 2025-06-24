import cv2
import numpy as np
import os
import json # Import the json module

# Define the folder containing your fundus images
input_folder = 'processed_images/4' # Assuming you want to check images from the previously processed folder
output_results_file = 'quality_results.json' # File to save assessment results

def assess_fundus_image_quality(image_path):
    """
    Assesses the quality of a fundus image based on brightness, contrast, and sharpness.

    Args:
        image_path (str): The path to the input image.

    Returns:
        dict: A dictionary containing quality metrics and a general assessment,
              or None if the image cannot be read.
    """
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return None

    # Convert to grayscale for quality assessment
    if len(image.shape) == 3: # Check if it's a color image (BGR or BGRA)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 4: # If it's BGRA, convert to BGR first then to GRAY
        gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    else: # Already grayscale
        gray = image

    # 1. Brightness (Mean Pixel Intensity)
    # A good range for fundus images often falls between 80-150.
    # Too low indicates underexposure, too high indicates overexposure.
    brightness = np.mean(gray)

    # 2. Contrast (Standard Deviation of Pixel Intensities)
    # Higher standard deviation usually means higher contrast.
    # A typical range for good contrast might be 40-70.
    contrast = np.std(gray)

    # 3. Sharpness (Variance of Laplacian)
    # A common method to estimate sharpness is to apply a Laplacian filter
    # and then calculate the variance of the filtered image. Higher variance
    # indicates more edges and thus sharper image.
    # Values above 100-200 are generally considered sharp, but this can vary.
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    # General Quality Assessment
    quality_assessment = "Good"

    # Define thresholds (these are empirical and might need tuning for your dataset)
    min_brightness = 40
    max_brightness = 200
    min_contrast = 20
    min_sharpness = 50

    if brightness < min_brightness:
        quality_assessment = "Poor (Too Dark)"
    elif brightness > max_brightness:
        quality_assessment = "Poor (Too Bright)"
    elif contrast < min_contrast:
        quality_assessment = "Poor (Low Contrast)"
    elif sharpness < min_sharpness:
        quality_assessment = "Poor (Blurry)"

    # You could add more sophisticated checks here, e.g., for red channel saturation,
    # presence of reflections, or overall uniformity, based on specific fundus image characteristics.

    return {
        "image_name": os.path.basename(image_path), # Include image name for charting
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "sharpness": round(sharpness, 2),
        "assessment": quality_assessment
    }

# --- Main processing loop ---
print(f"Starting quality assessment for images in '{input_folder}'...")

all_results = [] # List to store results for all images

# Iterate over all image files in the input folder
for img_name in os.listdir(input_folder):
    input_path = os.path.join(input_folder, img_name)

    if os.path.isfile(input_path):
        print(f"\n--- Analyzing: {img_name} ---")
        quality_metrics = assess_fundus_image_quality(input_path)

        if quality_metrics:
            all_results.append(quality_metrics) # Add results to the list
            for metric, value in quality_metrics.items():
                print(f"  {metric.capitalize()}: {value}")
        else:
            print(f"  Could not assess quality for {img_name}.")
    else:
        print(f"Skipping '{img_name}' as it is not a file.")

# Save all results to a JSON file
output_json_path = os.path.join(input_folder, output_results_file) # Save in the input folder for easy access
try:
    with open(output_json_path, 'w') as f:
        json.dump(all_results, f, indent=4)
    print(f"\nQuality assessment results saved to: {output_json_path}")
except Exception as e:
    print(f"Error saving results to JSON: {e}")

print("\nQuality assessment complete.")
