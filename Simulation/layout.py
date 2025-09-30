# layout.py

import arcade
import config
import json

class StationLayout:
    """
    Creates the station layout by reading a tilemap from a JSON file
    and identifies key locations like stairs.
    """
    def __init__(self):
        self.all_tiles_list = arcade.SpriteList()
        self.stair_locations = []  # This will store (x, y) tuples for each stair
        self._load_layout_from_json()

    def _load_layout_from_json(self):
        """Reads the matrix from the JSON file and creates sprites."""
        with open(config.LAYOUT_FILE) as f:
            layout_data = json.load(f)["layout"]

        layout_data.reverse()

        for y_index, row in enumerate(layout_data):
            for x_index, tile_type in enumerate(row):
                if tile_type in config.TILE_MAPPING:
                    sprite_path = config.TILE_MAPPING[tile_type]
                    tile_sprite = arcade.Sprite(sprite_path, config.SPRITE_SCALING)

                    tile_sprite.center_x = x_index * config.TILE_SIZE + (config.TILE_SIZE / 2)
                    tile_sprite.center_y = y_index * config.TILE_SIZE + (config.TILE_SIZE / 2)
                    
                    # If the tile is a stair, save its location
                    if tile_type == 3:
                        self.stair_locations.append((tile_sprite.center_x, tile_sprite.center_y))

                    self.all_tiles_list.append(tile_sprite)