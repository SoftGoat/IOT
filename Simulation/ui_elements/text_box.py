import pygame
import config


class TextBox:
    """
    A customizable text box element that can be used for both static display 
    and interactive, editable text input.
    """
    def __init__(self, x, y, text, length = config.SPAWN_BUBBLE_SIZE, height = config.SPAWN_BUBBLE_SIZE, 
                 text_color=config.BLACK, 
                 bg_color=config.LIGHT_GRAY, 
                 outline_color=config.DARK_GRAY,
                 font=None,
                 editable=False): # NEW: Controls if input is allowed
        
        self.value = str(text)
        self.rect = pygame.Rect(x, y, length, height)
        self.editable = editable
        self.is_active = False # Controls keyboard input focus
        
        # Appearance parameters
        self.text_color = text_color
        self.bg_color = bg_color
        self.outline_color = outline_color
        self.outline_width = 2
        
        # Font setup (use the provided font or default to the UI font)
        self.font = font if font else pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)

        # Static display for counters (uses image/bubble logic only if not editable)
        if not self.editable:
            # Load and scale the bubble image for passenger counters
            try:
                image = pygame.image.load(config.PASSENGER_SPAWN_BUBBLE).convert_alpha()
                self.image = pygame.transform.scale(image, (length, height))
            except Exception:
                # Fallback if image path is incorrect or missing
                self.image = None
                print("Warning: Could not load PASSENGER_SPAWN_BUBBLE image for static TextBox.")


    def handle_event(self, event):
        """Handles user input (mouse click for focus, keyboard input)."""
        if not self.editable:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the text box was clicked
            if self.rect.collidepoint(event.pos):
                self.is_active = True
                print("TextBox activated.")
            else:
                self.is_active = False
                
        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_RETURN:
                self.is_active = False # Deactivate on Enter/Return
            elif event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            # NEW: Only allow numeric input (or allow all, depending on need)
            elif event.unicode.isdigit():
                self.value += event.unicode
            elif event.key == pygame.K_SPACE:
                # Block space for numeric input
                pass


    def update(self):
        """No complex update logic needed yet."""
        pass

    def set_value(self, new_value):
        """Updates the displayed value."""
        self.value = str(new_value)
        
    def get_text(self):
        """Returns the current string value of the text box."""
        return self.value

    def draw(self, screen):
        """Draws the text box based on its type (static bubble or editable rectangle)."""

        if self.editable:
            # --- Draw as an Editable Rectangle (for Iterations box) ---
            
            # 1. Draw the Background
            pygame.draw.rect(screen, self.bg_color, self.rect)
            
            # 2. Draw the Outline (Active vs. Inactive)
            outline_color = self.outline_color
            if self.is_active:
                outline_color = config.HIGHLIGHT_COLOR # Use a distinct color for focus
            
            pygame.draw.rect(screen, outline_color, self.rect, self.outline_width)

            # 3. Draw the Text
            display_text = self.value if self.value else ""
            
            # Ensure text fits within the box bounds (optional: could truncate or scale font)
            text_surf = self.font.render(display_text, True, self.text_color)
            
            # Position text slightly inside the left edge with padding
            text_x = self.rect.x + 5
            text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
            
            screen.blit(text_surf, (text_x, text_y))

        else:
            # --- Draw as a Static Bubble (for Spawn/Queue Counters) ---

            if self.image:
                # 1. Draw the bubble image
                screen.blit(self.image, self.rect.topleft)

            # 2. Draw the count text
            display_text = self.value if self.value else "0"
            text_surf = self.font.render(str(display_text), True, config.BLACK)

            # Center the text within the rect
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)