# game_states/build_state.py
import pygame
import config, os
from game_states.tile_manager import TileManager
from game_states.layout_io import load_layout, save_layout
from ui_elements import TileButton 
from game_states.state import State
from ui_elements import TileButton, Button
from dialog import SaveDialog, LoadDialog
# ----------------------------------------------------------------------
# I. CORE INTERFACE (Called by main.py)
# ----------------------------------------------------------------------

class BuildState(State):
    def __init__(self):
        super().__init__() # Call if inheriting from State

        # State Data
        self.selected_tile_id = 1
        self.hovered_grid_pos = None
        self.save_message_timer = 0
        self.active_dialog = None
        self.click_lockout_timer = 0 # Timer to block immediate click-through

        # Setup
        self.grid_data = self._load_any_layout()
        self.tile_manager = TileManager(config.TILE_MAPPING)
        self.tile_manager.create_all(self.grid_data)

        # UI
        self.font_ui = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)
        self.tile_buttons = self._create_tile_palette()
        screen_center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        self.load_dialog = LoadDialog(screen_center, self.load_station_from_name, self._close_dialog)
        self.save_dialog = SaveDialog(screen_center, self.save_station_as, self._close_dialog)
        
        # <-- NEW: Build Mode Action Buttons (Load/Save) -->
        btn_w, btn_h = 250, 150
        btn_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH - btn_w) // 2
        btnSave_y = 10
        btnLoad_y = 70
        
        # NOTE: save_to_json is used here for the Quick Save button
        self.save_button = Button(btn_x, btnSave_y, btn_w, btn_h, "Quick Save", self.open_save_dialog, config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, hit_size=(200, 50))
        # Use a new method to launch the (future) dialog
        self.load_button = Button(btn_x, btnLoad_y, btn_w, btn_h, "Load Station", self.open_load_dialog, config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, hit_size=(200, 50))
        self.action_buttons = [self.save_button, self.load_button]


    def handle_events(self, events):
        """Handles key presses and dispatches events to buttons/dialogs."""
        
        # 1. Dialog Handling (Highest Priority - if a dialog is open, only handle its events)
        if self.active_dialog:
            self.active_dialog.handle_events(events)
            return

        # 2. Regular Build Mode Events
        for event in events:
            # Check for State Change/Save Keys
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.save_to_json() 
                self.next_state = "MAIN_MENU"
                self.done = True
                
            # Dispatch event to Action Buttons (Save/Load)
            for button in self.action_buttons:
                button.handle_event(event)

            # Dispatch event to Palette Buttons
            for button in self.tile_buttons:
                button.handle_event(event)


    def update(self):
        """Updates the game logic: timers, hovered position, and continuous painting."""

        #Update action buttons to enable hover state

        for button in self.action_buttons:
            button.update()

        if self.save_message_timer > 0:
            self.save_message_timer -= 1

        # 1. Dialog Update/Exit Priority
        if self.active_dialog:
            self.active_dialog.update()
            return # Skip all other logic if a dialog is open

        # 2. Lockout Check (Only checks if no dialog is active)
        if self.click_lockout_timer > 0:
            self.click_lockout_timer -= 1
            return # Skip grid interaction due to lockout
            
        mouse_x, mouse_y = pygame.mouse.get_pos()
        col = mouse_x // config.TILE_SIZE
        row = mouse_y // config.TILE_SIZE
        
        # Determine hovered grid position, ensuring it's not over the palette
        if (0 <= row < config.GRID_HEIGHT_TILES and 
            0 <= col < config.GRID_WIDTH_TILES and 
            mouse_x < config.PALETTE_PANEL_X):
            self.hovered_grid_pos = (row, col)
        else:
            self.hovered_grid_pos = None
        
        # Painting logic (continuous mouse press)
        if self.hovered_grid_pos:
            row, col = self.hovered_grid_pos
            if pygame.mouse.get_pressed()[0]:
                self.paint_at(row, col, self.selected_tile_id)
            elif pygame.mouse.get_pressed()[2]:
                self.erase_at(row, col)

    def draw(self, screen):
        """Draws all elements of the build screen."""
        screen.fill(config.BLACK)
        self.tile_manager.sprites.draw(screen)
        
        # Drawing Helpers
        self._draw_hover_outline(screen)
        self._draw_palette_panel(screen)
        self._draw_save_message(screen)
        
        # Draw Action Buttons on the palette
        for button in self.action_buttons:
            button.draw(screen)
            
        # Draw Dialogs (Must be drawn last to appear on top)
        if self.active_dialog:
            self.active_dialog.draw(screen)
            pass 


# ----------------------------------------------------------------------
# II. PUBLIC ACTIONS (Grid/File Manipulation)
# ----------------------------------------------------------------------

    def save_to_json(self):
        """Saves the current grid layout to the user file."""
        # NOTE: This is the quick save; the dialog version would be different.
        save_layout(config.USER_LAYOUT_PATH, self.grid_data)
        self.save_message_timer = 120

    def paint_at(self, row, col, tile_id):
        """Sets a tile's ID and updates the sprite visual."""
        old = self.grid_data[row][col]
        if old == tile_id: return
        self.grid_data[row][col] = tile_id
        self.tile_manager.update_tile(old, tile_id, col, row)

    def erase_at(self, row, col):
        """Paints an empty tile (ID 0)."""
        self.paint_at(row, col, 0)
        
    # <-- NEW: Dialog Launchers (Placeholders for complex dialogs) -->
    def open_load_dialog(self):
        """Launches the Load Station dialog."""
        # In the full implementation, you'd create and show the dialog here.
        print("Launching Load Station Dialog...")
        self.active_dialog = True
        
    def load_station_from_name(self, layout_name):
        """Called by the dialog when a station is selected."""
        try:
            from game_states.layout_io import get_layout_path
            path = get_layout_path(layout_name)
            self.grid_data = load_layout(path)
            self.tile_manager.create_all(self.grid_data) # Rebuild visuals
            self._close_dialog()
            print(f"Loaded layout: {layout_name}")
        except FileNotFoundError:
            print(f"Error: Layout {layout_name} not found.")

    def save_station_as(self, layout_name):
        """Called by the dialog to save to a specific name."""
        from game_states.layout_io import get_layout_path
        path = get_layout_path(layout_name)
        save_layout(path, self.grid_data)
        self._close_dialog()
        self.save_message_timer = 120
        print(f"Saved layout as: {layout_name}")


# ----------------------------------------------------------------------
# III. PRIVATE HELPERS (Setup, Callbacks, Drawing components)
# ----------------------------------------------------------------------

    def _load_any_layout(self):
        """Implements the startup policy: User -> Default -> New Grid."""
        try:
            return load_layout(config.USER_LAYOUT_PATH)
        except FileNotFoundError:
            try:
                return load_layout(config.DEFAULT_LAYOUT_PATH)
            except FileNotFoundError:
                grid = [[0]*config.GRID_WIDTH_TILES for _ in range(config.GRID_HEIGHT_TILES)]
                os.makedirs(os.path.dirname(config.DEFAULT_LAYOUT_PATH), exist_ok=True)
                save_layout(config.DEFAULT_LAYOUT_PATH, grid)
                return grid

    def _create_tile_palette(self):
        """Instantiates all TileButton objects."""
        buttons = []
        x_start = config.PALETTE_PANEL_X + config.PALETTE_TILE_PADDING
        # Start below the new action buttons (adjust y_start)
        current_y = 150 
        
        for tile_id, path in config.TILE_MAPPING.items():
            if tile_id == 0: continue

            original_img = pygame.image.load(path).convert_alpha()
            button_img = pygame.transform.scale(original_img, (config.PALETTE_TILE_SIZE, config.PALETTE_TILE_SIZE))
            
            button = TileButton(
                x=x_start, y=current_y, size=config.PALETTE_TILE_SIZE, tile_id=tile_id, 
                tile_image=button_img, callback=self._select_tile_id
            )
            buttons.append(button)
            current_y += config.PALETTE_TILE_SIZE + config.PALETTE_TILE_PADDING
            
        return buttons
    
    def _select_tile_id(self, new_id):
        """Callback function: updates the currently selected tile ID."""
        self.selected_tile_id = new_id

    def _draw_hover_outline(self, screen):
        """Draws the white outline around the tile currently under the mouse."""
        if self.hovered_grid_pos:
            row, col = self.hovered_grid_pos
            x = col * config.TILE_SIZE
            y = row * config.TILE_SIZE
            pygame.draw.rect(screen, config.WHITE, (x, y, config.TILE_SIZE, config.TILE_SIZE), 3)

    def _draw_palette_panel(self, screen):
        """Draws the palette background, buttons, and explanation text."""
        # Draw background
        panel_rect = pygame.Rect(config.PALETTE_PANEL_X, 0, config.PALETTE_PANEL_WIDTH, config.SCREEN_HEIGHT)
        pygame.draw.rect(screen, config.GRAY, panel_rect)

        # Draw buttons (Palette tiles)
        for button in self.tile_buttons:
            is_selected = button.tile_id == self.selected_tile_id
            button.draw(screen, is_selected)
        
        # Draw Explanation Text
        # ... (Text wrapping logic remains the same) ...
        explanation = config.TILE_EXPLANATIONS.get(self.selected_tile_id, "Select a tile.")
        words = explanation.split(' ')
        lines = []
        current_line = ''
        max_line_width = config.PALETTE_PANEL_WIDTH - 2 * config.PALETTE_TILE_PADDING
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_surface = self.font_ui.render(test_line, True, config.WHITE)
            
            if test_surface.get_width() > max_line_width and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        lines.append(current_line)
        
        text_y = config.SCREEN_HEIGHT - (len(lines) * (config.FONT_SIZE_UI + 5)) - 10
        for line in lines:
            text_surface = self.font_ui.render(line, True, config.WHITE)
            screen.blit(text_surface, (config.PALETTE_PANEL_X + config.PALETTE_TILE_PADDING, text_y))
            text_y += config.FONT_SIZE_UI + 5

    def _draw_save_message(self, screen):
        """Draws the 'Layout Saved!' message when the timer is active."""
        if self.save_message_timer > 0:
            save_surf = self.font_ui.render("Layout Saved!", True, config.WHITE)
            save_rect = save_surf.get_rect(center=(config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT - 30))
            screen.blit(save_surf, save_rect)


    def _close_dialog(self):
            """Callback to close the active dialog."""
            if self.active_dialog:
                self.active_dialog.is_active = False
                self.active_dialog = None

                # This ensures that pygame.mouse.get_pressed() returns (0,0,0) immediately.
                pygame.event.get(pygame.MOUSEBUTTONDOWN)
                pygame.event.get(pygame.MOUSEBUTTONUP)

                self.click_lockout_timer = 5
            
    def open_save_dialog(self):
        """Activates the save dialog."""
        self.active_dialog = self.save_dialog
        self.active_dialog.is_active = True

    def open_load_dialog(self):
        """Activates the load dialog."""
        self.active_dialog = self.load_dialog
        self.active_dialog.show()