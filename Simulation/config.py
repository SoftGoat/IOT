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
    3: ":assets:stairs.png",
    4: ":assets:entrance_tile.png",
}

# --- UI Constants ---
BUBBLE_WIDTH = 50
BUBBLE_HEIGHT = 30
BUBBLE_Y_OFFSET = 50  # How many pixels above the stair sprite to draw the bubble
BUBBLE_COLOR = arcade.color.WHITE
TEXT_COLOR = arcade.color.ORANGE_PEEL
TEXT_FONT_SIZE = 26


# --- UI Sprites ---
BUBBLE_SPRITE = ":assets:passengers_bubble.png"
BUBBLE_SCALING = 0.15 # Adjust this value to make your sprite bigger or smaller


# --- Text Rendering ---
# The font is now set to your custom font file.
# Make sure "Kenney Pixel.ttf" is inside your "assets" folder.
TEXT_FONT_PATH = ":assets:Kenney Pixel.ttf"  # Path used for loading
TEXT_FONT_NAME = "Kenney Pixel"                     # Internal name used for rendering

# Use these to fine-tune the text's position inside the bubble
TEXT_X_OFFSET = 20
TEXT_Y_OFFSET = 2
