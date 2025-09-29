# config.py

import arcade

# --- Screen Constants ---
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "JSON-Based Train Station"
BACKGROUND_COLOR = arcade.color.BLACK

# --- File Paths ---
LAYOUT_FILE = "layout.json"

# --- Sprite Sizing ---
SOURCE_TILE_SIZE = 1032
SPRITE_SCALING = 1 / 24
TILE_SIZE = SOURCE_TILE_SIZE * SPRITE_SCALING

# --- TILE MAPPING ---
# This dictionary maps the numbers from the JSON file to the correct image.
TILE_MAPPING = {
    0: ":assets:platform_floor.png",
    1: ":assets:platform_tile.png",
    2: ":assets:track_tile.png",
    3: ":assets:stairs.png"

    # We can easily add more later, e.g., 2: ":assets:track_tile.png"
}