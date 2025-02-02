import os
import yaml
import numpy as np
import pygame
from PIL import Image
import time

__version__ = "0.3.0"  # 25/02

TILE_FOLDER = "src_city"  # Directory containing tile images
RULES_FILE = TILE_FOLDER
TILE_SIZE = 4  # Tile size after resizing | 27 / 64 | 2, 3, ...
TOLERANCE = 50  # 3, 50,  / Tolerance for grayscale differences (adjustable for stricter matches)

TEXT_HEIGHT = 30  # Space reserved for text above each tile
SPACING = 200  # Space between tiles
TEXT_OFFSET_Y = 10  # Additional vertical spacing for text
TEXT_OFFSET_X = 10  # Additional horizontal spacing for text
FONT_SIZE = 12  # Font size for better readability

TILE_FILES = sorted([f for f in os.listdir(TILE_FOLDER) if f.endswith(".png")])

# Determine grid size based on the number of images
if len(TILE_FILES) <= 12:
    GRID_ROWS, GRID_COLS = 5, 5
else:
    GRID_ROWS, GRID_COLS = 7, 8

# Load and resize tile images
tile_pixels = {}
for i, file in enumerate(TILE_FILES):
    img = Image.open(os.path.join(TILE_FOLDER, file)).convert("L")  # Convert to grayscale
    img = img.resize((TILE_SIZE, TILE_SIZE), Image.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
    tile_pixels[i] = np.array(img, dtype=np.uint8)  # Store as NumPy array

# Function to get an exact pixel-by-pixel edge signature
def get_edge_signature(tile_id, direction):
    """Returns the pixel values of the tile edges as a 1D NumPy array."""
    if direction == "top":
        return tile_pixels[tile_id][0, :]  # First row
    elif direction == "bottom":
        return tile_pixels[tile_id][-1, :]  # Last row
    elif direction == "left":
        return tile_pixels[tile_id][:, 0]  # First column
    elif direction == "right":
        return tile_pixels[tile_id][:, -1]  # Last column

# Function to compare edges with pixel-level accuracy
def is_similar(edge1, edge2, tolerance=TOLERANCE):
    """Checks if two tile edges match pixel by pixel, allowing a small grayscale tolerance."""
    return np.all(np.abs(edge1.astype(int) - edge2.astype(int)) <= tolerance)

# Build connectivity rules for each tile
CONNECTIVITY = {i: {"top": [], "bottom": [], "left": [], "right": []} for i in range(len(tile_pixels))}

# Determine valid connections based on pixel-accurate edge matching
for tile1 in range(len(tile_pixels)):
    for tile2 in range(len(tile_pixels)):
        if is_similar(get_edge_signature(tile1, "top"), get_edge_signature(tile2, "bottom")):
            CONNECTIVITY[tile1]["top"].append(tile2)
        if is_similar(get_edge_signature(tile1, "bottom"), get_edge_signature(tile2, "top")):
            CONNECTIVITY[tile1]["bottom"].append(tile2)
        if is_similar(get_edge_signature(tile1, "left"), get_edge_signature(tile2, "right")):
            CONNECTIVITY[tile1]["left"].append(tile2)
        if is_similar(get_edge_signature(tile1, "right"), get_edge_signature(tile2, "left")):
            CONNECTIVITY[tile1]["right"].append(tile2)

# Ensure the TILE_FOLDER directory exists
os.makedirs(TILE_FOLDER, exist_ok=True)

# Save connectivity rules inside TILE_FOLDER
rules_path = os.path.join(TILE_FOLDER, RULES_FILE + ".yaml")
with open(rules_path, "w") as file:
    yaml.dump(CONNECTIVITY, file, default_flow_style=False)

print(f"Rules saved to: {rules_path}")


# Initialize Pygame for visualization
pygame.init()

# Calculate canvas size with spacing and text area
canvas_width = GRID_COLS * SPACING
canvas_height = GRID_ROWS * SPACING + TEXT_HEIGHT
screen = pygame.Surface((canvas_width, canvas_height))

# Set white background
screen.fill((255, 255, 255))

# Load font
font = pygame.font.Font(None, FONT_SIZE)

# Draw tiles in a grid with connectivity info
for idx, file in enumerate(TILE_FILES[:GRID_ROWS * GRID_COLS]):
    row, col = divmod(idx, GRID_COLS)
    x, y = col * SPACING, row * SPACING + TEXT_HEIGHT  # Leave space for text

    # Load and resize tile image
    img = pygame.image.load(os.path.join(TILE_FOLDER, file))
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    screen.blit(img, (x, y + 60))

    # Retrieve connectivity info
    conn = CONNECTIVITY[idx]
    top_text = f"T: {conn['top']}  B: {conn['bottom']}"
    left_text = f"L: {conn['left']}  R: {conn['right']}"

    # Add tile name and index (shifted for spacing)
    name_surface = font.render(f"Tile {idx}: {file}", True, (0, 0, 0))
    screen.blit(name_surface, (x + TEXT_OFFSET_X, y - TEXT_HEIGHT + TEXT_OFFSET_Y))

    # Add top/bottom connectivity info (shifted for spacing)
    top_surface = font.render(top_text, True, (0, 0, 0))
    screen.blit(top_surface, (x + TEXT_OFFSET_X, y - TEXT_HEIGHT + TEXT_OFFSET_Y + 20))

    # Add left/right connectivity info (shifted for spacing)
    left_surface = font.render(left_text, True, (0, 0, 0))
    screen.blit(left_surface, (x + TEXT_OFFSET_X, y - TEXT_HEIGHT + TEXT_OFFSET_Y + 40))

# Show preview for 5 seconds before saving
pygame.display.set_mode((canvas_width, canvas_height))  # Create a visible window
pygame.display.get_surface().blit(screen, (0, 0))
pygame.display.flip()
time.sleep(5)

# Save the visualization as an image
pygame.image.save(screen, RULES_FILE + ".png")
print("Output saved as:", RULES_FILE + ".png")

pygame.quit()
