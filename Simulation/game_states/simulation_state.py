# game_states/simulation_state.py
import pygame
import config, os
from game_states.tile_manager import TileManager
from game_states.layout_io import load_layout, get_layout_path # Ensure get_layout_path is available
from ui_elements.button import Button 
from ui_elements.editable_spawn_count import EditableSpawnCount
from ui_elements.spawn_config_slider import SpawnConfigSlider
from ui_elements.text_box import TextBox

from game_states.state import State 
from dialog import LoadDialog

# ----------------------------------------------------------------------
# I. CORE INTERFACE (Called by main.py)
# ----------------------------------------------------------------------

class SimulationState(State):
    def __init__(self):
        super().__init__()
        
        # --- State Data ---
        self.grid_data = self._load_simulation_layout()
        self.tile_manager = TileManager(config.TILE_MAPPING)
        self.tile_manager.create_all(self.grid_data)
        
        # --- Simulation Logic Data ---
        # spawn_data will now store {(r, c): count} for all stairs
        self.spawn_data = {} 
        self.selected_stairs_pos = None # Tracks the currently selected stairs tile (r, c)
        self.active_dialog = None 
        self.click_lockout_timer = 0 

        # --- UI Components ---
        self.font_ui = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)
        self.spawn_counters = self._create_spawn_counters()
        self.action_buttons = self._create_action_buttons()
        
        # Initialize Spawn Config Slider (Positioned below action buttons)
        slider_w = config.PALETTE_PANEL_WIDTH - 40
        slider_x = config.PALETTE_PANEL_X + 20
        slider_y = 150 
        slider_h = 100
        
        self.spawn_config_slider = SpawnConfigSlider(
            slider_x, slider_y, slider_w, slider_h, 
            config.SPAWN_COUNT_DEFAULT, 
            self._update_selected_stairs_count, # The callback when slider value changes
            min_val=0, max_val=999 # Reasonable min/max values
        )
        self.spawn_config_slider.is_active = False # Hidden until a stair is selected
        
        # --- Dialog Initialization (NEW) ---
        screen_center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        self.load_dialog = LoadDialog(
            screen_center, 
            self.load_new_layout_by_name, 
            self._close_dialog          
        )


    def handle_events(self, events):
        """Handles user input, prioritizing dialogs."""
        
        # 1. Dialog Handling (Highest Priority)
        # We pass the LIST of events to the dialog, as the dialog's handler 
        # is expected to iterate over them.
        if self.active_dialog:
            self.active_dialog.handle_events(events)
            return
            
        # REMOVED: # 2. Handle Slider Events (if active)
        # REMOVED: self.spawn_config_slider.handle_event(events)
        
        # Now, we iterate over the LIST 'events'
        for event in events: # event is now a SINGLE event object
            
            # --- Handle the Slider (using the SINGLE event) ---
            self.spawn_config_slider.handle_event(event) # <-- CORRECT: passes the singular 'event'

            # Check for State Change
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.next_state = "MAIN_MENU"
                self.done = True
                
            # Handle action button events
            for button in self.action_buttons:
                button.handle_event(event) # Passes the singular 'event'
                
                
            # NEW: Handle mouse click on a stair tile for selection
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
                mouse_x, mouse_y = event.pos
                self._select_stairs_at(mouse_x, mouse_y)

    def update(self):
        """Updates UI components and core simulation logic."""
        
        # Update action buttons for hover state
        for button in self.action_buttons:
            button.update()
            
        # 1. Dialog Update/Exit Priority
        if self.active_dialog:
            self.active_dialog.update()
            return

        # 2. Lockout Check
        if self.click_lockout_timer > 0:
            self.click_lockout_timer -= 1
            return 
            
        # Update slider
        self.spawn_config_slider.update()

        # Update spawn counters
        for counter in self.spawn_counters:
            counter.update(self.spawn_config_slider.current_value)
        
        
        # Add core simulation update logic here later...
        pass

    def draw(self, screen):
        """Draws all elements: tiles, control panel, buttons, and spawn counters."""
        screen.fill(config.BLACK)
        self.tile_manager.sprites.draw(screen)
        
        # Drawing Helpers
        self._draw_control_panel(screen)
        
        # Draw action buttons (on the panel)
        for button in self.action_buttons:
            button.draw(screen)
            
        # Draw the Spawn Config Slider
        self.spawn_config_slider.draw(screen)
        
        # Draw spawn counters (above the tiles)
        for counter in self.spawn_counters:
            counter.draw(screen)
            
        # Draw highlight around selected stairs tile
        self._draw_selected_stairs_highlight(screen)
        
        # Draw dialogs (LAST)
        if self.active_dialog:
            self.active_dialog.draw(screen)


# ----------------------------------------------------------------------
# II. PUBLIC ACTIONS (Simulation Flow Control)
# ----------------------------------------------------------------------

    def open_load_dialog(self):
        """Launches the Load Layout Dialog."""
        self.active_dialog = self.load_dialog
        self.active_dialog.show() # show() handles list refresh and activation
        
    def load_new_layout_by_name(self, layout_name):
        """
        Callback function invoked by LoadDialog upon successful selection.
        Loads the new grid and re-initializes visuals and spawn counters.
        """
        try:
            path = get_layout_path(layout_name)
            new_grid = load_layout(path)
            
            # 1. Update Grid Data
            self.grid_data = new_grid
            
            # 2. Rebuild Visuals
            self.tile_manager.create_all(self.grid_data) 
            
            # 3. Rebuild Spawn Counters (Crucial step for the new map)
            self.spawn_data = {}
            self.spawn_counters = self._create_spawn_counters()
            
            self._close_dialog()
            print(f"Loaded layout: {layout_name}")
            
        except FileNotFoundError:
            print(f"Error: Layout {layout_name} not found.")


# ----------------------------------------------------------------------
# III. PRIVATE HELPERS (Setup, Callbacks, Drawing components)
# ----------------------------------------------------------------------
    

    def _close_dialog(self):
        """Callback to close the active dialog and set lockout timer."""
        if self.active_dialog:
            self.active_dialog.is_active = False
            self.active_dialog = None
            
            # Flush mouse events
            pygame.event.get(pygame.MOUSEBUTTONDOWN)
            pygame.event.get(pygame.MOUSEBUTTONUP)
            
            self.click_lockout_timer = 5 # Set multi-frame lockout
            
    def _load_simulation_layout(self):
        """Tries to load the user's layout, falling back to default."""
        try:
            return load_layout(config.USER_LAYOUT_PATH)
        except FileNotFoundError:
            try:
                 return load_layout(config.DEFAULT_LAYOUT_PATH)
            except FileNotFoundError:
                # Emergency fallback to empty grid
                print("Warning: Layouts missing. Starting with empty grid.")
                return [[0]*config.GRID_WIDTH_TILES for _ in range(config.GRID_HEIGHT_TILES)]

    def _create_action_buttons(self):
        """Creates buttons for the simulation control area (Load, Run/Pause)."""
        btn_w, btn_h = 200, 80
        # Position buttons consistently on the right-hand panel
        btn_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH - btn_w) // 2
        
        self.load_button = Button(
            btn_x, 20, btn_w, btn_h, 
            "Load Layout", self.open_load_dialog, 
            config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, text_size=28, hit_size=(200, 40)
        )
        # We will add the Run/Stop button here later
        return [self.load_button] 
        
    def _update_spawn_data(self, r, c, new_count):
        """Callback function to update the internal spawn count data."""
        self.spawn_data[(r, c)] = new_count
        print(f"Spawn at ({r}, {c}) set to: {new_count}")
        
    def _update_selected_stairs_count(self, new_count):
        """
        Callback from the SpawnConfigSlider to update the spawn count 
        for the currently selected stairs tile.
        """
        if self.selected_stairs_pos:
            r, c = self.selected_stairs_pos
            self.spawn_data[(r, c)] = new_count
            
            # Optional: Find the EditableSpawnCount sprite and update its visual if needed
            # (Currently the EditableSpawnCount is used in BuildState, but 
            # if used here, it should be updated, otherwise we rely on the slider text)
            
            # Since the EditableSpawnCount is still drawn in SimulationState, 
            # we should update it to reflect the change made via the slider.
            for counter in self.spawn_counters:
                if (counter.rect.x // config.TILE_SIZE, counter.rect.y // config.TILE_SIZE) == (c, r - (config.SPAWN_BUBBLE_SIZE // config.TILE_SIZE // 2)):
                     counter.value = str(new_count)
                     break
            
            print(f"Slider updated spawn at {self.selected_stairs_pos} to: {new_count}")

    def _create_spawn_counters(self):
        """Finds all stairs tiles (ID 5) and creates EditableSpawnCount objects."""
        # ... (Implementation remains the same) ...
        counters = []
        for r, row in enumerate(self.grid_data):
            for c, tile_id in enumerate(row):
                if tile_id == 5:  # Stairs tile
                    x_tile = c * config.TILE_SIZE
                    y_tile = r * config.TILE_SIZE

                    # Calculate the top-left position for the bubble (approximately centered above tile)
                    x_center = x_tile + (config.TILE_SIZE // 2)
                    y_center = y_tile + (config.TILE_SIZE // 2) - config.SPAWN_BUBBLE_SIZE

                    def make_callback(r, c):
                        return lambda new_count: self._update_spawn_data(r, c, new_count)

                    counter = TextBox(
                        # Pass the top-left corner of the bubble area
                        x_center - config.SPAWN_BUBBLE_SIZE // 2, y_center, 
                        str(config.SPAWN_COUNT_DEFAULT), # Initial text as string
                    )

                    # Store the initial value
                    self.spawn_data[(r, c)] = config.SPAWN_COUNT_DEFAULT
                    counters.append(counter)
        return counters
        
    def _select_stairs_at(self, mouse_x, mouse_y):
        """Handles selecting a stairs tile by clicking."""
        col = mouse_x // config.TILE_SIZE
        row = mouse_y // config.TILE_SIZE
        
        # Check bounds
        if not (0 <= row < config.GRID_HEIGHT_TILES and 0 <= col < config.GRID_WIDTH_TILES):
            return 
            
        # Check if click is on the grid area (not the control panel)
        if mouse_x > config.PALETTE_PANEL_X:
            return 
            
        # Check if the clicked tile is a stairs tile (ID 5)
        if self.grid_data[row][col] == 5:
            # Select this stairs tile
            self.selected_stairs_pos = (row, col)
            print(f"Stairs selected at ({row}, {col}). ACTIVATING SLIDER.")
            self.spawn_config_slider.is_active = True
            
            # Read the current value and update the slider UI
            current_count = self.spawn_data.get((row, col), config.SPAWN_COUNT_DEFAULT)
            self.spawn_config_slider.set_value(current_count)
            print(f"Stairs selected at ({row}, {col}). Current count: {current_count}")
        else:
            # Deselect if they click elsewhere on the grid
            self.selected_stairs_pos = None
            self.spawn_config_slider.is_active = False
            
    def _draw_selected_stairs_highlight(self, screen):
        """Draws a highlight box around the currently selected stairs tile."""
        if self.selected_stairs_pos:
            row, col = self.selected_stairs_pos
            x = col * config.TILE_SIZE
            y = row * config.TILE_SIZE
            
            # Use a distinctive color for selection, e.g., a bright yellow/green
            highlight_color = (0, 255, 255) 
            pygame.draw.rect(screen, highlight_color, (x, y, config.TILE_SIZE, config.TILE_SIZE), 3)

    def _draw_control_panel(self, screen):
        """Draws the background panel for control buttons and information (Consistent with BuildState)."""
        # This mirrors the palette panel dimensions from config for visual consistency
        panel_rect = pygame.Rect(config.PALETTE_PANEL_X, 0, config.PALETTE_PANEL_WIDTH, config.SCREEN_HEIGHT)
        pygame.draw.rect(screen, config.GRAY, panel_rect)