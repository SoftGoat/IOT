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
    5: "Stairs: The entry and exit point for passengers. Passengers will spawn here."
}


# --- Grid Constants ---
TILE_SIZE = 40
GRID_WIDTH_TILES = 40  # Number of tiles across
GRID_HEIGHT_TILES = 20 # Number of tiles down

# --- Tile Mapping ---
# Maps the integer ID from the JSON/grid data to an image file path
TILE_MAPPING = {
    0: "assets/empty_tile.png",
    1: "assets/platform_floor.png",
    2: "assets/platform_tile.png",
    3: "assets/track_tile.png",
    4: "assets/entrance_tile.png",
    5: "assets/stairs.png"
}


# --- Graphics ---
BACKGROUND_IMAGE_PATH = "assets/background.png" 

# --- UI Image Paths ---
BUTTON_NORMAL_PATH = "assets/button_normal.png"
BUTTON_HOVER_PATH = "assets/button_hover.png"
BUTTON_IN_GAME = "assets/button_in_game.png"
BUTTON_IN_GAME_HOVER = "assets/button_in_game_hover.png"
TITLE_BANNER_PATH = "assets/title_banner.png" 


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