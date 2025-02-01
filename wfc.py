import pygame
import random
import yaml
import os
import datetime

__version__ = "0.1" # 25/01

# 🛠 Constants
TILE_SIZE = 64  # Tile size in pixels
GRID_SIZE = 8    # Grid dimensions (8x8)
WIDTH, HEIGHT = GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE
DELAY = 100  # Delay in milliseconds (100ms)

# 🖥 Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wave Function Collapse")

# 📂 Load tiles from the "src/" folder
TILE_FOLDER = "src"
TILE_NAMES = sorted([f for f in os.listdir(TILE_FOLDER) if f.endswith(".png")])

# Debug: Verify the number of tiles
print(f"\n📂 Loaded tiles: {len(TILE_NAMES)} PNG files.")
if len(TILE_NAMES) < 9:
    print("⚠️ Warning: At least 9 tiles are expected!")

# 🖼 Load and scale tiles
tiles = {}
for i, name in enumerate(TILE_NAMES):
    try:
        img_path = os.path.join(TILE_FOLDER, name)
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))  # Resize to TILE_SIZE
        tiles[i] = img
    except Exception as e:
        print(f"\n🚨 Error loading `{name}`: {e}")

# 📜 Load connectivity rules from YAML file
def load_connectivity(yaml_file):
    with open(yaml_file, "r") as file:
        return yaml.safe_load(file)

CONNECTIVITY = load_connectivity("rules.yaml")

# 🏗 Initialize grid with all possible tiles
grid = [[list(range(len(tiles))) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# 🔽 Function to collapse a tile
def collapse_tile(x, y):
    """Randomly selects one tile based on available options."""
    if len(grid[y][x]) > 1:
        grid[y][x] = [random.choice(grid[y][x])]

# 🔄 Update constraints based on connectivity rules
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

# 🎨 Function to draw the current state of the grid
def draw_grid():
    """Draws the current state of the grid on the screen."""
    screen.fill((50, 50, 50))  # Gray background
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if len(grid[y][x]) == 1:  # If the cell is collapsed
                tile = tiles[grid[y][x][0]]
                screen.blit(tile, (x * TILE_SIZE, y * TILE_SIZE))
    pygame.display.flip()

# 🏗 Wave Function Collapse algorithm
def collapse_grid():
    """Performs the Wave Function Collapse algorithm step by step."""
    for _ in range(GRID_SIZE * GRID_SIZE):
        possible_cells = [(x, y) for y in range(GRID_SIZE) for x in range(GRID_SIZE) if len(grid[y][x]) > 1]
        
        if not possible_cells:
            print("\n✅ [INFO] All cells have collapsed!")
            return

        min_entropy = min(len(grid[y][x]) for x, y in possible_cells)
        candidates = [(x, y) for x, y in possible_cells if len(grid[y][x]) == min_entropy]

        x, y = random.choice(candidates)
        collapse_tile(x, y)
        update_constraints()
        
        # 🔄 Draw the current state after each step
        draw_grid()
        pygame.time.delay(DELAY)

# ▶ Run the collapse algorithm
collapse_grid()

# 📂 Save the final generated image
def save_final_image():
    """Saves the final generated grid as a PNG image in the 'output/' folder with a timestamp."""
    # 📂 Create 'output' folder if it doesn't exist
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # ⏳ Generate timestamp in the format "RRMMDD_HHmm"
    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M")
    filename = f"wfc_{timestamp}.png"
    output_path = os.path.join(output_folder, filename)

    # 📸 Save the Pygame screen as an image
    pygame.image.save(screen, output_path)
    print(f"\n✅ [INFO] Final image saved as `{output_path}`!")

# 💾 Save the result before exiting
save_final_image()

# 🎨 Main loop (to keep the window open)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
