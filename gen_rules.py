import os
import yaml
import numpy as np
import pygame
from PIL import Image
import time

__version__ = "0.3.7"  # 25/02

TILE_FOLDER = "src3"  # Directory containing tile images
TILE_SIZE = 21  # Tile size for connectivity calculations
TOLERANCE = 20  # Grayscale tolerance for edge matching

COLORS_REDUCE = False  # Apply color reduction (True = reduce, False = original grayscale)
COLORS = 5  # 2/4/8/16/32 ... Maximum number of colors for processing

TEXT_HEIGHT = 30  # Space reserved for text above each tile
TEXT_SPACING_Y = 5  # Space between text lines
TEXT_OFFSET_X = 10  # Space between tile and text
FONT_SIZE = 12  # Font size for better readability
SCREEN_WIDTH = 1000  # Fixed width for preview
DATA_FOLDER = os.path.join(TILE_FOLDER, "data_" + TILE_FOLDER)  # Organized preview folder
RULES_FILE = TILE_FOLDER

# Ensure necessary directories exist
os.makedirs(TILE_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Load tile images
TILE_FILES = sorted([f for f in os.listdir(TILE_FOLDER) if f.endswith(".png")])

# Determine preview grid size
if len(TILE_FILES) <= 30:
    GRID_COLS = 2
    TILE_SIZE_THUMB = 30
else:
    GRID_COLS = 3
    TILE_SIZE_THUMB = 20

COLUMN_WIDTH = SCREEN_WIDTH // GRID_COLS  # Column width based on number of columns
GRID_ROWS = (len(TILE_FILES) + GRID_COLS - 1) // GRID_COLS  # Number of rows needed
SCREEN_HEIGHT = GRID_ROWS * (TILE_SIZE_THUMB + TEXT_HEIGHT + TEXT_SPACING_Y * 3)  # Dynamic height

# Load and process tile images for connectivity calculations
tile_pixels = {}
for i, file in enumerate(TILE_FILES):
    img = Image.open(os.path.join(TILE_FOLDER, file))

    if COLORS_REDUCE:
        img = img.convert("RGB")  # Keep full color mode
        img = img.resize((TILE_SIZE, TILE_SIZE))  # Resize for connectivity
        img = img.convert("P", palette=Image.ADAPTIVE, colors=COLORS).convert("RGB")  # Reduce colors
    else:
        img = img.convert("L")  # Convert to grayscale
        img = img.resize((TILE_SIZE, TILE_SIZE), Image.LANCZOS)  # Keep original processing

    tile_pixels[i] = np.array(img, dtype=np.uint8)  # Store as NumPy array

# Function to get an edge signature of a tile
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

# Function to compare edges with a tolerance value
def is_similar(edge1, edge2, tolerance=TOLERANCE):
    """Compares two edge signatures within a tolerance level."""
    diff = np.abs(edge1.astype(int) - edge2.astype(int))
    return np.all(diff <= tolerance)

# Build connectivity rules for each tile
CONNECTIVITY = {i: {"top": [], "bottom": [], "left": [], "right": []} for i in range(len(tile_pixels))}

# Determine valid connections based on edge similarity
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

# Automatically determine rules file name inside TILE_FOLDER
rules_path = os.path.join(TILE_FOLDER, f"{TILE_FOLDER}.yaml")

# Create an empty rules file if missing
if not os.path.exists(rules_path):
    print(f"Warning: No rules file found. Creating {rules_path}...")
    with open(rules_path, "w") as file:
        yaml.dump({}, file)  # Create an empty YAML file

# Save connectivity rules
with open(rules_path, "w") as file:
    yaml.dump(CONNECTIVITY, file, default_flow_style=False)

print(f"Rules saved to: {rules_path}")

# -------- Pygame Visualization --------
# Initialize Pygame
pygame.init()
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill((255, 255, 255))  # Set white background
font = pygame.font.Font(None, FONT_SIZE)

# Draw tiles and text
for idx, file in enumerate(TILE_FILES):
    row, col = divmod(idx, GRID_COLS)
    x, y = col * COLUMN_WIDTH + TEXT_SPACING_Y, row * (TILE_SIZE_THUMB + TEXT_HEIGHT + TEXT_SPACING_Y * 3)

    # Load and resize tile image
    img = pygame.image.load(os.path.join(TILE_FOLDER, file))
    img = pygame.transform.scale(img, (TILE_SIZE_THUMB, TILE_SIZE_THUMB))
    screen.blit(img, (x, y))

    # Retrieve connectivity info
    if idx in CONNECTIVITY:
        conn = CONNECTIVITY[idx]
        top_text = f"T: {conn.get('top', [])}  B: {conn.get('bottom', [])}"
        left_text = f"L: {conn.get('left', [])}  R: {conn.get('right', [])}"
    else:
        top_text = "T: []  B: []"
        left_text = "L: []  R: []"

    # Add tile name and index next to the tile
    name_surface = font.render(f"Tile {idx}: {file}", True, (0, 0, 0))
    screen.blit(name_surface, (x + TILE_SIZE_THUMB + TEXT_OFFSET_X, y))

    # Add top/bottom connectivity info
    top_surface = font.render(top_text, True, (0, 0, 0))
    screen.blit(top_surface, (x + TILE_SIZE_THUMB + TEXT_OFFSET_X, y + TEXT_SPACING_Y + TILE_SIZE_THUMB))

    # Add left/right connectivity info
    left_surface = font.render(left_text, True, (0, 0, 0))
    screen.blit(left_surface, (x + TILE_SIZE_THUMB + TEXT_OFFSET_X, y + TEXT_SPACING_Y * 2 + TILE_SIZE_THUMB + FONT_SIZE))

# Show preview for 5 seconds before saving
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Create a visible window
pygame.display.get_surface().blit(screen, (0, 0))
pygame.display.flip()
time.sleep(5)  # Keep preview visible for 5 seconds

# Save the preview with correct filename
preview_filename = f"{TILE_FOLDER}_preview.png"
preview_path = os.path.join(DATA_FOLDER, preview_filename)
pygame.image.save(screen, preview_path)
print("Preview saved as:", preview_path)

pygame.quit()
