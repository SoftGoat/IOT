# config.py

# --- Screen Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Train Station Simulator"
FPS = 60

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
GRID_LINE_COLOR = (40, 40, 40)
RED = (255,160,122)
DARK_GRAY = (100, 100, 100)
HIGHLIGHT_COLOR = (255, 255, 0) # Bright Yellow (used for active text box outline)

# --- Fonts ---
# Using None will load the default pygame font.
# You can replace this with a path to a .ttf file, e.g., "assets/your_font.ttf"
FONT_NAME = "assets/Kenney Pixel.ttf"
FONT_SIZE_TITLE = 74
FONT_SIZE_BUTTON = 50
FONT_SIZE_UI = 32  # <-- Add this for the new UI text

# --- Tile Explanations ---
TILE_EXPLANATIONS = {
    1: "Platform Floor: The main walkable area for passengers and staff.",
    2: "Platform Edge: A floor tile with a yellow warning band. Must be placed adjacent to train tracks.",
    3: "Track: Rails for the train. Trains will travel along these tiles.",
    4: "Entrance Marker: A special platform edge that marks where train doors will align for boarding and alighting.",
    5: "Stairs: The entry and exit point for passengers. Passengers will spawn here.",
    6: "Places a train track with a platform edge below. Click the platform edge to make an Entrance." 

}


# --- Grid Constants ---
TILE_SIZE = 40
GRID_WIDTH_TILES = 40  # Number of tiles across
GRID_HEIGHT_TILES = 20 # Number of tiles down

TRACK_LENGTH = 25
TRACK_ROW_OFFSET = 1 # Row offset for track placement if placed from an infrastructure tile


# --- Tile Mapping ---
# Maps the integer ID from the JSON/grid data to an image file path
TILE_MAPPING = {
    0: "assets/tiles/empty_tile.png",
    1: "assets/tiles/platform_floor.png",
    2: "assets/tiles/platform_tile.png",
    3: "assets/tiles/track_tile.png",
    4: "assets/tiles/entrance_tile.png",
    5: "assets/tiles/stairs.png",
    6: "assets/tiles/track_tile.png" # NEW: We'll use the track image for the structure button, as it represents the main element.
}

TILE_ICONS = {
    1: "assets/tiles_icons/platform_floor_icon.png",
    2: "assets/tiles_icons/platform_tile_icon.png",
    4: "assets/tiles_icons/entrance_tile_icon.png",
    5: "assets/tiles_icons/stairs_icon.png",
    6: "assets/tiles_icons/basic_station_icon.png" # NEW: Reuse track icon
}


# --- Graphics ---
BACKGROUND_IMAGE_PATH = "assets/background.png" 

# --- UI Image Paths ---
BUTTON_NORMAL_PATH = "assets/buttons/button_normal.png"
BUTTON_HOVER_PATH = "assets/buttons/button_hover.png"
BUTTON_IN_GAME = "assets/buttons/button_in_game.png"
BUTTON_IN_GAME_HOVER = "assets/buttons/button_in_game_hover.png"
TITLE_BANNER_PATH = "assets/title_banner.png" 
PASSENGERS_ICON_PATH = "assets/passengers.png"
X_ICON_PATH = "assets/X.png"
ARROW_LEFT = "assets/buttons/arrow_left.png"
ARROW_RIGHT = "assets/buttons/arrow_right.png"
ARROW_LEFT_PRESSED = "assets/buttons/arrow_left_pressed.png"
ARROW_RIGHT_PRESSED = "assets/buttons/arrow_right_pressed.png"

# --- UI Sizing ---
TITLE_BANNER_WIDTH = 800
TITLE_BANNER_HEIGHT = 400


LAYOUTS_DIR = "layouts"
USER_LAYOUT_PATH = f"{LAYOUTS_DIR}/station.json"
DEFAULT_LAYOUT_PATH = f"{LAYOUTS_DIR}/default.json"


# --- Palette UI Constants ---
PALETTE_PANEL_WIDTH = 300
PALETTE_PANEL_X = SCREEN_WIDTH - PALETTE_PANEL_WIDTH
PALETTE_TILE_SIZE = 64 # Larger size for buttons than the grid tiles
PALETTE_TILE_PADDING = 10



# --- Simulation Graphics ---
PASSENGER_SPAWN_BUBBLE = "assets/passengers_bubble.png" 

# --- Editable Text Box Constants ---
SPAWN_COUNT_DEFAULT = 100 
SPAWN_BUBBLE_SIZE = 60 # Size for the square bubble image and text box

# --- Simulation Parameters ---
# Parameters for queue choice utility: Utility = (K_RATIO_LENGTH / QueueLength) + (1.0 / Distance) + RandomBias
K_RATIO_LENGTH_DEFAULT = 10
K_RATIO_LENGTH_MIN = 0.0
K_RATIO_LENGTH_MAX = 30.0 # Allows for extreme preference for short queues



# --- Build Mode Button Constants ---

# Dimensions
BUILD_BTN_W = 150
BUILD_BTN_H = 75

# Positioning Offsets
BUILD_BTN_X_OFFSET = 50                 # The '- 50' offset in btn_x calculation

# Y-Positions
BUILD_BTN_SAVE_Y = 10
BUILD_BTN_LOAD_Y = 42

# Text and Hitbox Sizes (Specific to each button)
BUILD_BTN_TEXT_SIZE_SAVE = 30
BUILD_BTN_HIT_SIZE_SAVE = (110, 25)

BUILD_BTN_TEXT_SIZE_LOAD = 25
BUILD_BTN_HIT_SIZE_LOAD = (110, 25)

BUILD_BTN_TEXT_SIZE_ESCAPE = 25
BUILD_BTN_HIT_SIZE_ESCAPE = (110, 25)
