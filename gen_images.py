from PIL import Image
import sys
import os
import numpy as np

__version__ = "0.3.1"  # 25/02

output_dir = "src_city"
image_path = "city12.png"
size = 6  # 3x3


def split_image(image_path, size):
    """Splits an image into smaller tiles and saves them."""
    img = Image.open(image_path)
    width, height = img.size

    if width != height:
        print("Error: Image is not square.")
        sys.exit(1)

    if width % size != 0:
        print(f"Error: Image dimensions ({width}x{height}) are not divisible by {size}.")
        sys.exit(1)

    cell_size = width // size
    os.makedirs(output_dir, exist_ok=True)

    counter = 1
    variants = {'a': 0, 'b': 90, 'c': 180, 'd': 270}

    for row in range(size):
        for col in range(size):
            left, upper = col * cell_size, row * cell_size
            right, lower = left + cell_size, upper + cell_size

            piece = img.crop((left, upper, right, lower))
            index_str = f"{counter:02d}"

            for variant, angle in variants.items():
                rotated_piece = piece.rotate(angle)
                filename = f"i{index_str}{variant}.png"
                filepath = os.path.join(output_dir, filename)
                rotated_piece.save(filepath)

            counter += 1

    print("Image split and saved in:", output_dir)


def remove_duplicates():
    """Finds and removes duplicate images from output_dir."""
    image_files = sorted([f for f in os.listdir(output_dir) if f.endswith(".png")])
    deleted_files = []

    for i in range(len(image_files)):
        ref_path = os.path.join(output_dir, image_files[i])
        if not os.path.exists(ref_path):  # Skip already deleted files
            continue

        ref_img = np.array(Image.open(ref_path).convert("L"))  # Convert to grayscale for better accuracy

        for j in range(i + 1, len(image_files)):
            comp_path = os.path.join(output_dir, image_files[j])
            if not os.path.exists(comp_path):
                continue

            comp_img = np.array(Image.open(comp_path).convert("L"))

            # Compare images pixel by pixel
            if np.array_equal(ref_img, comp_img):
                os.remove(comp_path)
                deleted_files.append(comp_path)
                print(f"Duplicate removed: {image_files[j]}")

    print(f"Total duplicates removed: {len(deleted_files)}")


# Run the process
split_image(image_path, size)
remove_duplicates()
