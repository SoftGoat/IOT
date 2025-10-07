import pygame
import config

class SpawnConfigSlider:
    """
    A combined slider and editable text box UI for setting the spawn count
    of the currently selected stairs tile in the Simulation State.
    """
    def __init__(self, x, y, width, height, initial_value, callback_update, min_val=0, max_val=999):
        
        self.callback_update = callback_update
        self.min_val = min_val
        self.max_val = max_val
        self.is_active = False # Controls visibility/interaction
        
        # Overall Rect and Dimensions
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)

        # --- Text Box Setup (Top Section) ---
        TEXT_BOX_HEIGHT = height // 3
        TEXT_PADDING = 5
        self.text_rect = pygame.Rect(x + TEXT_PADDING, y + TEXT_PADDING, width - 2*TEXT_PADDING, TEXT_BOX_HEIGHT - 2*TEXT_PADDING)
        self.text_input = str(initial_value)
        self.is_text_active = False # Text box focus

        # 1. Adjust text box width to fit arrows
        ARROW_W = TEXT_BOX_HEIGHT - 2 * TEXT_PADDING 
        text_w_new = width - 2 * TEXT_PADDING - 2 * ARROW_W
        text_x_new = x + TEXT_PADDING + ARROW_W
        
        self.text_rect = pygame.Rect(text_x_new, y + TEXT_PADDING, text_w_new, TEXT_BOX_HEIGHT - 2*TEXT_PADDING)
        self.text_input = str(initial_value)
        self.is_text_active = False
        
        # 2. Define Arrow Button Rects
        self.left_arrow_rect = pygame.Rect(x + TEXT_PADDING, y + TEXT_PADDING, ARROW_W, TEXT_BOX_HEIGHT - 2*TEXT_PADDING)
        self.right_arrow_rect = pygame.Rect(x + width - TEXT_PADDING - ARROW_W, y + TEXT_PADDING, ARROW_W, TEXT_BOX_HEIGHT - 2*TEXT_PADDING)

        # Button State Tracking ---
        self.is_left_pressed = False
        self.is_right_pressed = False
        
        # 3. Load and scale the Arrow Images
        try:
            img_left = pygame.image.load(config.ARROW_LEFT).convert_alpha()
            img_right = pygame.image.load(config.ARROW_RIGHT).convert_alpha()
            img_left_p = pygame.image.load(config.ARROW_LEFT_PRESSED).convert_alpha()
            img_right_p = pygame.image.load(config.ARROW_RIGHT_PRESSED).convert_alpha()
            
            size = self.left_arrow_rect.height
            
            # --- ASSIGN NORMAL IMAGES HERE ---
            self.left_arrow_image = pygame.transform.scale(img_left, (size, size))
            self.right_arrow_image = pygame.transform.scale(img_right, (size, size))
            
            self.left_arrow_image_pressed = pygame.transform.scale(img_left_p, (size, size))
            self.right_arrow_image_pressed = pygame.transform.scale(img_right_p, (size, size))

        except pygame.error as e:
            print(f"ERROR loading arrow image (or pressed image): {e}")
            # If loading fails, all four attributes are safely set to None
            self.left_arrow_image = self.left_arrow_image_pressed = None 
            self.right_arrow_image = self.right_arrow_image_pressed = None 

        
        # --- Slider Setup (Bottom Section) ---
        SLIDER_Y = y + TEXT_BOX_HEIGHT + TEXT_PADDING
        SLIDER_HEIGHT = height - TEXT_BOX_HEIGHT - 2*TEXT_PADDING
        SLIDER_W = width - 2*TEXT_PADDING
        
        self.slider_rect = pygame.Rect(x + TEXT_PADDING, SLIDER_Y, SLIDER_W, SLIDER_HEIGHT)
        self.slider_handle_radius = 10
        self.is_dragging = False
        
        self.set_value(initial_value) # Sets initial position and text
        
    def set_value(self, new_value):
        """Sets the internal value, updates the text, and positions the handle."""
        # Clamp and update value
        value = max(self.min_val, min(self.max_val, int(new_value)))
        self.text_input = str(value)

        # Update slider handle position
        range_val = self.max_val - self.min_val
        # Slider track length is rect width minus handle diameter
        track_len = self.slider_rect.width - 2 * self.slider_handle_radius 
        
        if range_val > 0:
            ratio = (value - self.min_val) / range_val
            handle_x = self.slider_rect.x + self.slider_handle_radius + int(ratio * track_len)
        else:
            handle_x = self.slider_rect.centerx
            
        self.slider_handle_pos = (handle_x, self.slider_rect.centery)
        self.current_value = value
        
        # Call back to SimulationState to update the data
        self.callback_update(self.current_value)

    def _get_value_from_pos(self, x_pos):
        """Calculates value based on handle X position."""
        track_len = self.slider_rect.width - 2 * self.slider_handle_radius
        
        # Clamp position to the track area
        min_x = self.slider_rect.x + self.slider_handle_radius
        max_x = self.slider_rect.x + self.slider_rect.width - self.slider_handle_radius
        x_clamped = max(min_x, min(max_x, x_pos))
        
        # Calculate ratio
        ratio = (x_clamped - min_x) / track_len
        
        new_value = self.min_val + int(ratio * (self.max_val - self.min_val))
        return new_value
        

    def handle_event(self, event):
        """Handles slider dragging, text box activation, and key input."""
        
        # NOTE: The 'is_active' check is already done by SimulationState before 
        # it even passes the event, but we keep it here for robustness.
        if not self.is_active: return 

        # --- Text Box Input Logic ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.text_rect.collidepoint(event.pos):
                self.is_text_active = True
                self.is_dragging = False
            else:
                if self.is_text_active:
                    self.is_text_active = False
                    # Use a try-except block here for safety in case of empty input
                    try:
                        self.set_value(self.text_input) # Update value when focus is lost
                    except ValueError:
                        # Revert to current_value if input is empty/invalid number
                        self.set_value(self.current_value)

        if self.is_text_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.is_text_active = False
                try:
                    self.set_value(self.text_input)
                except ValueError:
                    self.set_value(self.current_value)
            elif event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
            elif event.unicode.isdigit():
                if len(self.text_input) < len(str(self.max_val)) + 1: 
                    self.text_input += event.unicode
            return # Block slider interaction if typing

        # --- Arrow Button Logic ---
        # MOUSEBUTTONDOWN (Set pressed state and change value)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.left_arrow_rect.collidepoint(event.pos):
                self.is_left_pressed = True
                new_val = self.current_value - 1
                self.set_value(new_val)
                return
                
            if self.right_arrow_rect.collidepoint(event.pos):
                self.is_right_pressed = True
                new_val = self.current_value + 1
                self.set_value(new_val)
                return
                
        # MOUSEBUTTONUP (Release pressed state)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_left_pressed = False
            self.is_right_pressed = False

        # --- Slider Dragging Logic ---
        # ... (The rest of the logic remains the same) ...
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_rect = pygame.Rect(
                # ... (handle rect calculation) ...
            )
            if handle_rect.collidepoint(event.pos) or self.slider_rect.collidepoint(event.pos):
                self.is_dragging = True
                self.set_value(self._get_value_from_pos(event.pos[0]))

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self.set_value(self._get_value_from_pos(event.pos[0]))

            
    def update(self):
        """No complex update logic needed."""
        pass
        

    def draw(self, screen):
        """Draws the slider and text box."""
        if not self.is_active: return
        
        # 1. Draw Container Background
        pygame.draw.rect(screen, config.LIGHT_GRAY, self.rect)
        pygame.draw.rect(screen, config.BLACK, self.rect, 2) # Border

        # 2. Draw Text Box
        pygame.draw.rect(screen, config.WHITE, self.text_rect) # Text box background
        if self.is_text_active:
             pygame.draw.rect(screen, config.BLACK, self.text_rect, 2) # Active border
             
        display_text = self.text_input if self.text_input else "0"
        text_surf = self.font.render(display_text, True, config.BLACK)
        text_rect = text_surf.get_rect(center=self.text_rect.center)
        screen.blit(text_surf, text_rect)

        # 3. Draw Slider Track (Line)
        track_y = self.slider_rect.centery
        pygame.draw.line(
            screen, config.BLACK, 
            (self.slider_rect.x + self.slider_handle_radius, track_y), 
            (self.slider_rect.right - self.slider_handle_radius, track_y), 
            4
        )
        
        # 4. Draw Slider Handle
        color = config.WHITE if not self.is_dragging else config.BLACK
        pygame.draw.circle(screen, config.BLACK, self.slider_handle_pos, self.slider_handle_radius)
        pygame.draw.circle(screen, color, self.slider_handle_pos, self.slider_handle_radius - 2)


        # Left Button
        pygame.draw.rect(screen, config.GRAY, self.left_arrow_rect)
        pygame.draw.rect(screen, config.BLACK, self.left_arrow_rect, 1)

        if self.is_left_pressed and self.left_arrow_image_pressed:
            screen.blit(self.left_arrow_image_pressed, self.left_arrow_rect.topleft)
        elif self.left_arrow_image:
            screen.blit(self.left_arrow_image, self.left_arrow_rect.topleft)
        
        # Right Button
        pygame.draw.rect(screen, config.GRAY, self.right_arrow_rect)
        pygame.draw.rect(screen, config.BLACK, self.right_arrow_rect, 1)
        
        if self.is_right_pressed and self.right_arrow_image_pressed:
            screen.blit(self.right_arrow_image_pressed, self.right_arrow_rect.topleft)
        elif self.right_arrow_image:
            screen.blit(self.right_arrow_image, self.right_arrow_rect.topleft)
