import os
import yaml
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# 📂 Složka s dlaždicemi
TILE_FOLDER = "src"
TILE_FILES = sorted([f for f in os.listdir(TILE_FOLDER) if f.endswith(".png")])
TILE_SIZE = 64  # Velikost dlaždic po zmenšení

# Debug: Ověříme, že máme správný počet dlaždic
print(f"\n📂 Nalezené PNG soubory ve složce `{TILE_FOLDER}`: {len(TILE_FILES)} souborů.")
if len(TILE_FILES) < 9:
    print("⚠️ Varování: Očekáváno minimálně 9 dlaždic!")

# 🖼 Načtení a zmenšení dlaždic
tile_pixels = {}
for i, file in enumerate(TILE_FILES):
    img = Image.open(os.path.join(TILE_FOLDER, file)).convert("RGB")
    img = img.resize((TILE_SIZE, TILE_SIZE))  # Zmenšíme na 64x64
    tile_pixels[i] = np.array(img)

    # Debug: Ověření načtení
    print(f"\n✅ Dlaždice {i}: `{file}` (PŘIZPŮSOBENA NA {TILE_SIZE}x{TILE_SIZE})")
    print(f"   - Nová velikost: {img.size}")

# 📏 Funkce pro získání zjednodušeného "otisku" hran
def get_edge_signature(tile_id, direction):
    """Vrátí průměrné hodnoty hran dlaždice"""
    if direction == "top":
        return np.mean(tile_pixels[tile_id][0, :, :], axis=0)  # Průměr každého sloupce
    elif direction == "bottom":
        return np.mean(tile_pixels[tile_id][-1, :, :], axis=0)
    elif direction == "left":
        return np.mean(tile_pixels[tile_id][:, 0, :], axis=0)  # Průměr každého řádku
    elif direction == "right":
        return np.mean(tile_pixels[tile_id][:, -1, :], axis=0)

# 🔍 Funkce pro porovnání hran s tolerancí
def is_similar(edge1, edge2, tolerance=15):  # Nižší tolerance kvůli průměru
    """Porovná dvě zjednodušené hrany."""
    diff = np.abs(edge1 - edge2)
    return np.all(diff <= tolerance)

# 🏗 Automatická konstrukce CONNECTIVITY
CONNECTIVITY = {i: {"top": [], "bottom": [], "left": [], "right": []} for i in range(len(tile_pixels))}

# 🔄 Napojení dlaždic podle zjednodušených hran
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

# 📝 Uložíme nová pravidla do `rules.yaml`
with open("rules.yaml", "w") as file:
    yaml.dump(CONNECTIVITY, file, default_flow_style=False)

print("\n✅ Nová pravidla uložena do `rules.yaml`!")

# 🖼 Vizualizace propojení pravidel
def visualize_connectivity(connectivity, tile_files):
    fig, axs = plt.subplots(3, 3, figsize=(9, 9))
    axs = axs.ravel()

    for tile_id, ax in enumerate(axs):
        if tile_id in connectivity:
            img = Image.open(os.path.join(TILE_FOLDER, tile_files[tile_id])).resize((TILE_SIZE, TILE_SIZE))
            ax.imshow(img)
            ax.axis("off")
            ax.set_title(
                f"Tile {tile_id}\n"
                f"T: {connectivity[tile_id]['top']}\n"
                f"B: {connectivity[tile_id]['bottom']}\n"
                f"L: {connectivity[tile_id]['left']}\n"
                f"R: {connectivity[tile_id]['right']}"
            )

    plt.tight_layout()
    plt.show()

# 🖼 Zobrazíme propojení pravidel
visualize_connectivity(CONNECTIVITY, TILE_FILES)

# 🔍 Kontrola propojení
print("\n🔍 Kontrola propojení dlaždic:")
for tile_id, rules in CONNECTIVITY.items():
    if not any(rules.values()):
        print(f"🚨 Dlaždice {tile_id} nemá žádné sousedy! Možná chyba v napojení.")
    else:
        print(f"✅ Dlaždice {tile_id} propojena s ostatními správně.")
