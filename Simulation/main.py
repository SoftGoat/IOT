# main.py

import arcade
import pathlib
import config
from layout import StationLayout
from passengers import PassengerManager

class StationApp(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.SCREEN_TITLE)
        arcade.set_background_color(config.BACKGROUND_COLOR)
        
        self.scene = None
        self.station_layout = None
        self.passenger_manager = None
        self.camera = arcade.camera.Camera2D(window=self)

    def setup(self):
        """ Set up the game here. """
        # NEW: Explicitly load the font. If the path in config.py is wrong,
        # the program will now crash on this line with a clear error.
        arcade.load_font(config.TEXT_FONT_PATH)

        self.scene = arcade.Scene()
        
        # Create the station layout object
        self.station_layout = StationLayout()
        
        # Setup the passenger manager and give it the stair locations
        self.passenger_manager = PassengerManager()
        self.passenger_manager.setup(stair_locations=self.station_layout.stair_locations)
        
        # Add the layout sprite list to the scene
        self.scene.add_sprite_list("Layout", sprite_list=self.station_layout.all_tiles_list)

    def on_draw(self):
        """ Render the screen. """
        self.clear()
        self.camera.use()
        self.scene.draw()
        
        # Draw the passenger UI on top of everything else
        self.passenger_manager.on_draw()

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