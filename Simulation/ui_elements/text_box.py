
import pygame
import config


class TextBox:
    """A simple non-interactive text box for displaying passenger counts."""
    def __init__(self, x, y, text):
        self.value = text

        size = config.SPAWN_BUBBLE_SIZE
        self.rect = pygame.Rect(x, y, size, size)

        # Load and scale the bubble image
        image = pygame.image.load(config.PASSENGER_SPAWN_BUBBLE).convert_alpha()
        self.image = pygame.transform.scale(image, (size, size))

        self.font = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)
        self.is_active = False # Controls keyboard input focus


    def update(self):
        """No complex update logic needed here yet."""
        pass

    def set_value(self, new_value):
        """Updates the displayed value."""
        self.value = str(new_value)

    def draw(self, screen):
        """Draws the bubble and the passenger count text."""

        # 1. Draw the bubble image
        screen.blit(self.image, self.rect.topleft)

        # 2. Draw the count text
        display_text = self.value if self.value else "0"
        color = config.BLACK
        text_surf = self.font.render(str(display_text), True, color)

        # Center the text within the rect
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        

