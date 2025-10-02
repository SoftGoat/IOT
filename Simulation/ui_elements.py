# ui_elements.py

import pygame
import config



class Button:
    """An image-based, reusable button class."""
    def __init__(self, x, y, width, height, text, callback, normal_path, hover_path, hit_size=None, text_size=-1): 
        
        # 1. Define Visual Dimensions (for image scaling and text positioning)
        self.visual_width = width
        self.visual_height = height

        # 2. Define Text Size (if provided)
        if text_size == -1:
            self.text_size = config.FONT_SIZE_BUTTON
        else:
            self.text_size = text_size

        # 3. Define Hit Box Dimensions (used for self.rect)
        if hit_size:
            # If hit_size is provided, use it for the rect
            hit_width, hit_height = hit_size
        else:
            # Otherwise, use the full visual dimensions
            hit_width, hit_height = width, height
            
        # The rect now uses the potentially smaller hit dimensions
        self.rect = pygame.Rect(x, y, hit_width, hit_height)
        self.callback = callback
        self.hovered = False
        
        # --- Image Loading and Scaling (Always use visual dimensions) ---
        normal_image = pygame.image.load(normal_path).convert_alpha()
        hover_image = pygame.image.load(hover_path).convert_alpha()
        
        # Images are scaled using the visual dimensions
        self.image_normal = pygame.transform.scale(normal_image, (width, height))
        self.image_hover = pygame.transform.scale(hover_image, (width, height))
        
        # 3. Adjust Image Position to Center over the Hit Rect (CRUCIAL STEP)
        # If the visual image is larger than the hit box, we need to calculate an offset.
        self.image_offset_x = (hit_width - width) // 2
        self.image_offset_y = (hit_height - height) // 2
        
        # --- Text setup remains the same ---
        self.font = pygame.font.Font(config.FONT_NAME, self.text_size)
        
        self.text_normal = self.font.render(text, True, config.WHITE)
        self.text_hovered = self.font.render(text, True, config.BLACK)
        
        # Text is centered on the hit box rect
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
        
        # The draw position must account for the offset, so the image is centered
        # around the smaller self.rect.
        draw_x = self.rect.x + self.image_offset_x
        draw_y = self.rect.y + self.image_offset_y
        draw_pos = (draw_x, draw_y)

        if self.hovered:
            screen.blit(self.image_hover, draw_pos)
            screen.blit(self.text_hovered, self.text_rect)
        else:
            screen.blit(self.image_normal, draw_pos)
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



class EditableSpawnCount:
    """A text box overlayed on the Stairs tile (ID 5) to set passenger spawn count."""
    def __init__(self, x, y, initial_value, callback_update):
        self.value = str(initial_value)
        self.callback_update = callback_update
        
        size = config.SPAWN_BUBBLE_SIZE
        self.rect = pygame.Rect(x, y, size, size)
        
        # Load and scale the bubble image
        image = pygame.image.load(config.PASSENGER_SPAWN_BUBBLE).convert_alpha()
        self.image = pygame.transform.scale(image, (size, size))
        
        self.font = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)
        self.is_active = False # Controls keyboard input focus

    def handle_event(self, event):
        """Handles mouse clicks for activation and keyboard input."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_active = True
            else:
                self.is_active = False # Lose focus if clicking elsewhere
                if self.value:
                    self.callback_update(int(self.value)) # Call back when focus is lost

        if self.is_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.is_active = False
                if self.value:
                    self.callback_update(int(self.value))
                    
            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
                
            elif event.unicode.isdigit():
                # Limit input to digits and a reasonable length
                if len(self.value) < 3: 
                    self.value += event.unicode

    def update(self):
        """No complex update logic needed here yet."""
        pass

    def draw(self, screen):
        """Draws the bubble and the passenger count text."""
        
        # 1. Draw the bubble image
        screen.blit(self.image, self.rect.topleft)
        
        # 2. Draw the count text
        display_text = self.value if self.value else "0"
        color = config.BLACK if not self.is_active else config.WHITE
        
        text_surf = self.font.render(display_text, True, color)
        
        # Center the text within the rect
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        # 3. Draw a highlight if active
        if self.is_active:
             pygame.draw.rect(screen, config.WHITE, self.rect, 2)