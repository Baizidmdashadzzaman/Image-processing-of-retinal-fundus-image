import cv2
import numpy as np
import os

# Define input and output folders
input_folder = 'sorted_images/4'  # Path to your input images
output_folder = 'processed_images/4'  # Path where processed images with transparent background will be saved

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)


def remove_black_background_to_transparent(image_path):
    """
    Removes the black background from a fundus image and replaces it with transparent,
    then crops the image to the bounding box of the circular fundus region.

    Args:
        image_path (str): The path to the input image.

    Returns:
        numpy.ndarray: The processed image with a transparent background and cropped,
                       or None if the image cannot be read.
    """
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Read image with alpha channel if present
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return None

    # If the image is 3-channel (BGR), convert it to 4-channel (BGRA)
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # Convert to grayscale for thresholding
    gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

    # Threshold the image to create a mask for the circular region.
    # Pixels above a certain intensity (e.g., 20) are considered part of the eye.
    # This value might need tuning depending on the image dataset's overall brightness
    # and the specific intensity of the "black" background.
    _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)

    # Find the largest contour, which should correspond to the fundus image circle
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print(f"No significant contours found for {image_path}. Returning original image with opaque background.")
        return image  # Return original if no contours are found

    # Get the largest contour by area
    max_contour = max(contours, key=cv2.contourArea)

    # Create a blank transparent image with the same dimensions as the original.
    # Initialize all alpha values to 0 (transparent).
    transparent_background = np.zeros(image.shape, dtype=np.uint8)  # All zeros means transparent black

    # Create a mask for the fundus region.
    # The mask will be white (255) where the fundus is, and black (0) elsewhere.
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [max_contour], -1, 255, cv2.FILLED)

    # Apply the mask to the original image's color channels (BGR)
    # The area outside the mask will be black.
    fundus_bgr = cv2.bitwise_and(image[:, :, :3], image[:, :, :3], mask=mask)

    # Create an alpha channel based on the fundus mask.
    # Where the fundus is, alpha will be 255 (opaque). Where the background is, alpha will be 0 (transparent).
    alpha_channel = np.zeros(image.shape[:2], dtype=np.uint8)
    alpha_channel[mask == 255] = 255  # Set alpha to 255 (opaque) where mask is white

    # Combine the fundus BGR channels with the new alpha channel
    final_image = cv2.merge([fundus_bgr[:, :, 0], fundus_bgr[:, :, 1], fundus_bgr[:, :, 2], alpha_channel])

    # Get the bounding box of the largest contour (the fundus circle).
    # This is used to crop the image, removing any excess transparent space around the circle.
    x, y, w, h = cv2.boundingRect(max_contour)
    cropped_final_image = final_image[y:y + h, x:x + w]

    return cropped_final_image


# --- Main processing loop ---
print(f"Starting image processing from '{input_folder}' to '{output_folder}' (transparent background)...")

# Iterate over all image files in the input folder
for img_name in os.listdir(input_folder):
    # Construct full paths for input and output images
    input_path = os.path.join(input_folder, img_name)
    # Ensure the output file maintains a .png extension to support transparency
    output_img_name = os.path.splitext(img_name)[0] + '.png'
    output_path = os.path.join(output_folder, output_img_name)

    # Check if the current item is a file (and not a directory)
    if os.path.isfile(input_path):
        try:
            # Process the image using the defined function
            processed_img = remove_black_background_to_transparent(input_path)

            # If processing was successful, save the result
            if processed_img is not None:
                cv2.imwrite(output_path, processed_img)
                # print(f"Successfully processed and saved: {img_name} with transparent background.")
            else:
                print(f"Skipping {img_name} due to an issue during processing (returned None).")
        except Exception as e:
            # Catch any unexpected errors during processing
            print(f"Failed to process {img_name}: {e}")
    else:
        print(f"Skipping '{img_name}' as it is not a file.")

print("Image processing complete. Images with transparent backgrounds saved.")
