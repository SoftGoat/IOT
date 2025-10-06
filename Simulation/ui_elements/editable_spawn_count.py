import pygame
import config

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
