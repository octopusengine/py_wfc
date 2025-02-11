import pygame
import random
import yaml
import os
import datetime

__version__ = "0.3.2"  # 25/02

TILE_FOLDER = "src3"
RULES_FILE = TILE_FOLDER # yaml
TILE_SIZE = 16  # Tile size in pixels | 16, 32, 64 / 27, 54
GRID_SIZE = 64  # Grid dimensions GRID_SIZE x GRID_SIZE | 8, 16, 32, 64, 128, 200
BACKGROUND_COLOR = (10, 10, 10) #(50, 50, 50)

WIDTH, HEIGHT = GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE
if GRID_SIZE < 32:
    DELAY = 10  # Delay in milliseconds (100ms)
else:
    DELAY = 1

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Function Collapse")

# Load tiles from the "src2/" folder
TILE_NAMES = sorted([f for f in os.listdir(TILE_FOLDER) if f.endswith(".png")])

# Debug: Verify the number of tiles
print(f"\nLoaded tiles: {len(TILE_NAMES)} PNG files.")
if len(TILE_NAMES) < 9:
    print("Warning: At least 9 tiles are expected!")

# Load and scale tiles
tiles = {}
for i, name in enumerate(TILE_NAMES):
    try:
        img_path = os.path.join(TILE_FOLDER, name)
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))  # Resize to TILE_SIZE
        tiles[i] = img
    except Exception as e:
        print(f"\nError loading `{name}`: {e}")

# Load connectivity rules from YAML file
def load_connectivity(yaml_file):
    with open(yaml_file, "r") as file:
        return yaml.safe_load(file)

rules_path = os.path.join(TILE_FOLDER, RULES_FILE + ".yaml")
CONNECTIVITY = load_connectivity(rules_path)

# Initialize grid with all possible tiles
grid = [[list(range(len(tiles))) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Function to preset a tile at a specific position before collapse
def preset(x, y, index):
    """Sets a fixed tile at position (x, y) before the collapse starts."""
    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and index in tiles:
        grid[y][x] = [index]
        update_constraints()  # Apply constraints immediately
        print(f"Preset tile {index} at position ({x}, {y})")

# Function to collapse a tile
def collapse_tile(x, y):
    """Randomly selects one tile based on available options."""
    if len(grid[y][x]) > 1:
        grid[y][x] = [random.choice(grid[y][x])]

# Update constraints based on connectivity rules
def update_constraints():
    """Propagates adjacency constraints across the grid."""
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if len(grid[y][x]) == 1:
                tile = grid[y][x][0]

                # Top neighbor
                if y > 0:
                    grid[y - 1][x] = [t for t in grid[y - 1][x] if t in CONNECTIVITY[tile]["top"]]

                # Bottom neighbor
                if y < GRID_SIZE - 1:
                    grid[y + 1][x] = [t for t in grid[y + 1][x] if t in CONNECTIVITY[tile]["bottom"]]

                # Left neighbor
                if x > 0:
                    grid[y][x - 1] = [t for t in grid[y][x - 1] if t in CONNECTIVITY[tile]["left"]]

                # Right neighbor
                if x < GRID_SIZE - 1:
                    grid[y][x + 1] = [t for t in grid[y][x + 1] if t in CONNECTIVITY[tile]["right"]]

# Function to draw the current state of the grid
def draw_grid():
    """Draws the current state of the grid on the screen."""
    screen.fill(BACKGROUND_COLOR)  # Gray background
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if len(grid[y][x]) == 1:  # If the cell is collapsed
                tile = tiles[grid[y][x][0]]
                screen.blit(tile, (x * TILE_SIZE, y * TILE_SIZE))
    pygame.display.flip()

# Wave Function Collapse algorithm
def collapse_grid():
    """Performs the Wave Function Collapse algorithm step by step."""
    for _ in range(GRID_SIZE * GRID_SIZE):
        possible_cells = [(x, y) for y in range(GRID_SIZE) for x in range(GRID_SIZE) if len(grid[y][x]) > 1]
        
        if not possible_cells:
            print("\n[INFO] All cells have collapsed!")
            return

        min_entropy = min(len(grid[y][x]) for x, y in possible_cells)
        candidates = [(x, y) for x, y in possible_cells if len(grid[y][x]) == min_entropy]

        x, y = random.choice(candidates)
        collapse_tile(x, y)
        update_constraints()
        
        # Draw the current state after each step
        draw_grid()
        pygame.time.delay(DELAY)

def text_space():
    # Txt Space Pattern
    for yy in range(GRID_SIZE-10):
        preset(yy+5, int(GRID_SIZE/2+2), 0)
    for yy in range(GRID_SIZE-6):
        preset(yy+3, int(GRID_SIZE/2+1), 0)
    for yy in range(GRID_SIZE):
        preset(yy, int(GRID_SIZE/2), 0)
    for yy in range(GRID_SIZE-6):
        preset(yy+3, int(GRID_SIZE/2-1), 0)
    for yy in range(GRID_SIZE-10):
        preset(yy+5, int(GRID_SIZE/2-2), 0)

    
"""
preset(0, 0, 21)
preset(GRID_SIZE-1, GRID_SIZE-1, 21)

for yy in range(GRID_SIZE):
    preset(yy, int(GRID_SIZE/2), 0)

for yy in range(GRID_SIZE):
    preset(int(GRID_SIZE/2), yy, 21)

for yy in range(GRID_SIZE):
    preset(yy, 0, 0)

for yy in range(GRID_SIZE):
    preset(0, yy, 21)
"""

# text_space()
collapse_grid() # Run the collapse algorithm


def save_final_image():
    """Saves the final generated grid as a PNG image in the 'output/' folder with a timestamp."""
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M")
    filename = f"wfc_{timestamp}.png"
    output_path = os.path.join(output_folder, filename)

    pygame.image.save(screen, output_path)
    print(f"\n[INFO] Final image saved as `{output_path}`!")


save_final_image() # Save the result before exiting

# Keep the window open
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
