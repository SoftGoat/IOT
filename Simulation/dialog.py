# dialogs.py

import pygame
import config
from ui_elements.button import Button
from game_states.layout_io import get_saved_layouts, load_layout, get_layout_path

# --- Base Dialog Class (Abstract Template) ---

class Dialog:
    """Base class for modal dialogs (Load, Save As)."""
    
    def __init__(self, screen_center, title, callback_close, width=600, height=400):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = screen_center
        self.title = title
        self.callback_close = callback_close # Function to call when dialog is closed/canceled
        self.font_title = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_BUTTON)
        self.font_ui = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)
        self.is_active = False
        
        # Base buttons (Cancel/Close)
        btn_w, btn_h = 100, 60
        x_cancel = self.rect.right - btn_w - 20
        y_cancel = self.rect.bottom - btn_h - 20
        self.cancel_button = Button(x_cancel, y_cancel, btn_w, btn_h, "Cancel", self.cancel, config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, hit_size=(80, 20), text_size=28)
        self.buttons = [self.cancel_button]

    def cancel(self):
        """Standard action for closing the dialog without action."""
        self.is_active = False
        self.callback_close()

    def handle_events(self, events):
        """Must be called by the game state to process input."""
        if not self.is_active: return
        for event in events:
            # Handle escape key to cancel
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.cancel()
                return

            # Handle base buttons
            for button in self.buttons:
                button.handle_event(event)
            
            # Subclass specific event handling (must be implemented by subclass)
            self._handle_specific_events(event)

    def update(self):
        """Called every frame. Used to update buttons and internal state."""
        if not self.is_active: return
        for button in self.buttons:
            button.update()
        
        # Subclass specific update
        self._update_specific_logic()

    def draw(self, screen):
        """Draws the dialog overlay and frame."""
        if not self.is_active: return
        
        # 1. Draw transparent overlay (dim the background)
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        screen.blit(overlay, (0, 0))
        
        # 2. Draw dialog background
        pygame.draw.rect(screen, config.LIGHT_GRAY, self.rect, border_radius=10)
        pygame.draw.rect(screen, config.BLACK, self.rect, 3, border_radius=10)
        
        # 3. Draw title
        title_surf = self.font_title.render(self.title, True, config.BLACK)
        title_rect = title_surf.get_rect(midtop=(self.rect.centerx, self.rect.top + 20))
        screen.blit(title_surf, title_rect)
        
        # 4. Draw buttons
        for button in self.buttons:
            button.draw(screen)

        # Subclass specific drawing
        self._draw_specific_content(screen)
        
    # --- Abstract Methods (Placeholder for subclass implementation) ---
    def _handle_specific_events(self, event): pass
    def _update_specific_logic(self): pass
    def _draw_specific_content(self, screen): pass


# --- Load Dialog (Select layout from a list) ---

class LoadDialog(Dialog):
    """Dialog to list and select saved layouts."""
    def __init__(self, screen_center, callback_load_station, callback_close):
        # NOTE: Pass callback_close to the parent Dialog
        super().__init__(screen_center, "Load Station", callback_close, width=600, height=500)
        self.callback_load_station = callback_load_station # Function to call with selected name
        
        self.layout_names = []
        self.selected_index = -1
        self.scroll_offset = 0
        self.list_item_height = config.FONT_SIZE_UI + 10

        # Action Button (Load)
        btn_w, btn_h = 100, 60
        x_load = self.rect.right - 2*btn_w - 40
        y_load = self.rect.bottom - btn_h - 20
        self.load_button = Button(x_load, y_load, btn_w, btn_h, "Load", self._attempt_load, config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, hit_size=(80, 20), text_size=28)
        self.buttons.append(self.load_button) # Add to base buttons

        # Action Button (Remove)
        btn_w, btn_h = 100, 60
        x_remove = self.rect.right - btn_w - 250
        y_remove = self.rect.bottom - btn_h - 20
        self.remove_button = Button(x_remove, y_remove, btn_w, btn_h, "Remove", self._attempt_remove, config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, hit_size=(80, 20), text_size=28)
        self.buttons.append(self.remove_button) # Add to base buttons

    def show(self):
        """Sets the dialog active and REFRESHES the list of layouts."""
        self.layout_names = get_saved_layouts() # <--- REFRESH THE LIST HERE
        self.selected_index = -1 # Reset selection when showing
        self.is_active = True

    def _attempt_load(self):
        """Calls the BuildState's load function with the selected layout name."""
        if self.selected_index != -1:
            layout_name = self.layout_names[self.selected_index]
            self.is_active = False
            self.callback_load_station(layout_name)
    
    def _attempt_remove(self):
        """Removes the selected layout from disk and refreshes the list."""
        if self.selected_index != -1:
            layout_name = self.layout_names[self.selected_index]
            path = get_layout_path(layout_name)
            try:
                import os
                os.remove(path)
            except Exception as e:
                print(f"Error removing layout {layout_name}: {e}")
            # Refresh the list after removal
            self.layout_names = get_saved_layouts()
            self.selected_index = -1 # Reset selection after removal

    def _handle_specific_events(self, event):
        """Handles mouse clicks on the list items."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
            mouse_pos = pygame.mouse.get_pos()
            list_rect = self._get_list_area_rect()
            
            if list_rect.collidepoint(mouse_pos):
                rel_y = mouse_pos[1] - list_rect.top
                clicked_index = rel_y // self.list_item_height + self.scroll_offset
                
                if 0 <= clicked_index < len(self.layout_names):
                    self.selected_index = clicked_index
                    
    # Placeholder for list area drawing (The main feature)
    def _get_list_area_rect(self):
        """Defines the area where the list of layouts is drawn."""
        return pygame.Rect(self.rect.left + 20, self.rect.top + 80, 
                            self.rect.width - 40, self.rect.height - 180)

    def _draw_specific_content(self, screen):
        """Draws the list of saved layouts."""
        list_rect = self._get_list_area_rect()
        pygame.draw.rect(screen, config.WHITE, list_rect, border_radius=5)
        
        # Simple drawing of layout names (no scrolling implemented here)
        y = list_rect.top + 5
        for i, name in enumerate(self.layout_names):
            if i == self.selected_index:
                # Highlight selected item
                select_rect = pygame.Rect(list_rect.left + 2, y - 2, list_rect.width - 4, self.list_item_height)
                pygame.draw.rect(screen, config.GRID_LINE_COLOR, select_rect)
            
            text_surf = self.font_ui.render(name, True, config.BLACK)
            screen.blit(text_surf, (list_rect.left + 10, y))
            y += self.list_item_height

    def _update_specific_logic(self):
        """Logic for list state, etc."""
        # Disable Load button if nothing is selected
        self.load_button.enabled = self.selected_index != -1


# --- Save Dialog (Text input for naming the layout) ---

class SaveDialog(Dialog):
    """Dialog to input a name and save the current layout."""
    def __init__(self, screen_center, callback_save_station, callback_close):
        super().__init__(screen_center, "Save Station As...", callback_close, width=500, height=250)
        self.callback_save_station = callback_save_station # Function to call with new name
        
        self.text_input = ""
        self.input_active = True
        self.input_rect = pygame.Rect(self.rect.centerx - 200, self.rect.top + 80, 400, 40)
        
        # Action Button (Save)
        btn_w, btn_h = 100, 60
        x_save = self.rect.right - 2*btn_w - 40
        y_save = self.rect.bottom - btn_h - 20
        self.save_button = Button(x_save, y_save, btn_w, btn_h, "Save", self._attempt_save, config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER , hit_size=(80, 20), text_size=28)
        self.buttons.append(self.save_button)
        
    def _attempt_save(self):
        """Calls the BuildState's save function with the input name."""
        clean_name = self.text_input.strip()
        if clean_name:
            self.is_active = False
            self.callback_save_station(clean_name)

    
            
    def _handle_specific_events(self, event):
        """Handles keyboard input for the text field."""
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self._attempt_save()
            elif event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
            else:
                # Limit text input to sane characters and length
                if event.unicode.isalnum() or event.unicode in (' ', '_', '-'):
                    self.text_input += event.unicode

    def _draw_specific_content(self, screen):
        """Draws the text input field."""
        
        # Draw input field background
        pygame.draw.rect(screen, config.WHITE, self.input_rect, border_radius=5)
        pygame.draw.rect(screen, config.BLACK, self.input_rect, 2, border_radius=5)
        
        # Draw placeholder/current text
        text_to_display = self.text_input if self.text_input else "Enter layout name..."
        color = config.BLACK if self.text_input else config.GRAY
        
        text_surf = self.font_ui.render(text_to_display, True, color)
        screen.blit(text_surf, (self.input_rect.left + 10, self.input_rect.centery - text_surf.get_height() // 2))

    def _update_specific_logic(self):
        """Logic for save button state."""
        self.save_button.enabled = bool(self.text_input.strip())