# main.py

import arcade
import pathlib
import config
from layout import StationLayout

class StationApp(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.SCREEN_TITLE)
        arcade.set_background_color(config.BACKGROUND_COLOR)
        
        self.scene = None
        self.station_layout = None
        self.camera = arcade.camera.Camera2D(window=self)

    def setup(self):
        """ Set up the game here. """
        self.scene = arcade.Scene()
        
        # Create the station layout object (which now reads the JSON)
        self.station_layout = StationLayout()
        
        # Add the single, combined sprite list to the scene
        self.scene.add_sprite_list("Layout", sprite_list=self.station_layout.all_tiles_list)

    def on_draw(self):
        """ Render the screen. """
        self.clear()
        self.camera.use()
        self.scene.draw()

def main():
    """ Main method """
    file_path = pathlib.Path(__file__).parent.resolve()
    assets_path = file_path / "assets"
    arcade.resources.add_resource_handle("assets", assets_path)
    
    window = StationApp()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()