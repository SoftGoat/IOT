# layout.py

import arcade
import config
import json

class StationLayout:
    """
    Creates the station layout by reading a tilemap from a JSON file.
    """
    def __init__(self):
        # We only need one list now, as the JSON defines all tiles.
        self.all_tiles_list = arcade.SpriteList()
        self._load_layout_from_json()

    def _load_layout_from_json(self):
        """Reads the matrix from the JSON file and creates sprites."""
        with open(config.LAYOUT_FILE) as f:
            layout_data = json.load(f)["layout"]

        # To make positioning easier, we reverse the list. Now, the first
        # row in the data corresponds to the bottom row on the screen.
        layout_data.reverse()

        # Loop through each row and column of the matrix
        for y_index, row in enumerate(layout_data):
            for x_index, tile_type in enumerate(row):
                
                # Check if the number (tile_type) is in our mapping
                if tile_type in config.TILE_MAPPING:
                    sprite_path = config.TILE_MAPPING[tile_type]
                    tile_sprite = arcade.Sprite(sprite_path, config.SPRITE_SCALING)

                    # Calculate the sprite's position on the screen
                    tile_sprite.center_x = x_index * config.TILE_SIZE + (config.TILE_SIZE / 2)
                    tile_sprite.center_y = y_index * config.TILE_SIZE + (config.TILE_SIZE / 2)

                    self.all_tiles_list.append(tile_sprite)