import os

base_path = 'sorted_images'

print("Image count in each class folder:")
for class_name in sorted(os.listdir(base_path)):
    class_path = os.path.join(base_path, class_name)
    if os.path.isdir(class_path):
        count = len(os.listdir(class_path))
        print(f"Class {class_name}: {count} images")
