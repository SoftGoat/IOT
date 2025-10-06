import pygame
import config

class TileButton:
    """An image-based button for the tile palette in the build mode."""
    def __init__(self, x, y, size, tile_id, tile_image, callback):
        self.rect = pygame.Rect(x, y, size, size)
        self.tile_id = tile_id
        self.image = tile_image
        self.callback = callback

    def handle_event(self, event):
        """Checks if the tile button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback(self.tile_id)

    def draw(self, screen, is_selected):
        """Draws the tile button."""
        # Draw the tile image
        screen.blit(self.image, self.rect.topleft)

        # Draw a highlight border if this tile is selected
        if is_selected:
            pygame.draw.rect(screen, config.WHITE, self.rect, 3) # 3 is the border thickness