# ui_elements.py

import pygame
import config

class Button:
    """An image-based, reusable button class."""
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback
        self.hovered = False
        
        # --- NEW: Load and scale button images ---
        # Load the normal and hovered state images
        normal_image = pygame.image.load(config.BUTTON_NORMAL_PATH).convert_alpha()
        hover_image = pygame.image.load(config.BUTTON_HOVER_PATH).convert_alpha()
        
        # Scale the images to the desired button size
        self.image_normal = pygame.transform.scale(normal_image, (width, height))
        self.image_hover = pygame.transform.scale(hover_image, (width, height))

        # --- Text setup remains the same ---
        self.font = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_BUTTON)
        
        self.text_normal = self.font.render(text, True, config.WHITE)
        self.text_hovered = self.font.render(text, True, config.BLACK)
        
        self.text_rect = self.text_normal.get_rect(center=self.rect.center)

    def handle_event(self, event):
        """Checks if the button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def update(self):
        """Updates the button's state (e.g., hover)."""
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, screen):
        """Draws the button on the screen."""
        # --- NEW: Draw the appropriate image based on hover state ---
        if self.hovered:
            screen.blit(self.image_hover, self.rect.topleft)
            screen.blit(self.text_hovered, self.text_rect)
        else:
            screen.blit(self.image_normal, self.rect.topleft)
            screen.blit(self.text_normal, self.text_rect)


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