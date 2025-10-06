
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
