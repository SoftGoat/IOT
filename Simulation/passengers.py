# passengers.py
import arcade
import random
import config

class PassengerManager:
    """
    Manages passenger data and drawing the UI elements related to them.
    This version uses arcade.Text objects for sharp, well-aligned text.
    """
    def __init__(self):
        self.bubble_sprite_list = arcade.SpriteList()
        # We will now also keep a list of our text objects
        self.text_object_list = []

    def setup(self, stair_locations):
        """
        Creates bubble sprites and high-quality text objects for each staircase.
        """
        for x, y in stair_locations:
            passenger_count = random.randint(5, 25)

            # Create and position the bubble sprite
            bubble_sprite = arcade.Sprite(config.BUBBLE_SPRITE, config.BUBBLE_SCALING)
            bubble_sprite.center_x = x
            bubble_sprite.center_y = y + config.BUBBLE_Y_OFFSET
            self.bubble_sprite_list.append(bubble_sprite)
            
            # --- New Text Object Creation ---
            # Define the text and its position
            text = str(passenger_count)
            text_x = bubble_sprite.center_x + config.TEXT_X_OFFSET
            text_y = bubble_sprite.center_y + config.TEXT_Y_OFFSET
            
            # Create the arcade.Text object
            text_object = arcade.Text(
                text=text,
                x=text_x, 
                y=text_y,
                color=config.TEXT_COLOR,
                font_size=config.TEXT_FONT_SIZE,
                font_name=config.TEXT_FONT_NAME,
                anchor_x="center",
                anchor_y="center",
                
            )
            self.text_object_list.append(text_object)

    def on_draw(self):
        """
        Draws the bubble sprites and the text objects.
        """
        # Draw all the bubble sprites
        self.bubble_sprite_list.draw()

        # Draw all the text objects
        for text_object in self.text_object_list:
            text_object.draw()