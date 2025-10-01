# game_states/layout_io.py
import json
from pathlib import Path
import os
import config # Import config to get the layouts directory path

# --- Constants ---
LAYOUTS_DIR = Path(config.LAYOUTS_DIR) # Assumes you add LAYOUTS_DIR to config

# --- Existing Functions (Modified) ---
def load_layout(path):
    path = Path(path)
    if not path.exists():
        # Changed to Path.is_file() for robustness
        raise FileNotFoundError(f"Layout file not found: {path}")
    with path.open('r') as f:
        data = json.load(f)
    return data.get("layout")

def save_layout(path, grid_data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as f:
        json.dump({"layout": grid_data}, f, indent=4)

# --- NEW Functionality for Dialogs ---

def get_saved_layouts():
    """Returns a list of all saved station layout names (excluding default)."""
    if not LAYOUTS_DIR.exists():
        return []
    
    saved_layouts = []
    # Iterate over files ending with .json, excluding 'default.json'
    for file_path in LAYOUTS_DIR.iterdir():
        if file_path.suffix == '.json' and file_path.name != 'default.json':
            # Returns the file name without the extension
            saved_layouts.append(file_path.stem) 
            
    return sorted(saved_layouts)

def get_layout_path(name):
    """Returns the full Path object for a given layout name."""
    # Ensure the directory exists before returning the path
    LAYOUTS_DIR.mkdir(parents=True, exist_ok=True)
    return LAYOUTS_DIR / f"{name}.json"