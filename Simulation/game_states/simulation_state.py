# game_states/simulation_state.py
import pygame
import config, os
from game_states.tile_manager import TileManager
from game_states.layout_io import load_layout, get_layout_path # Ensure get_layout_path is available
from ui_elements import Button, EditableSpawnCount 
from game_states.state import State 
from dialog import LoadDialog # <-- NEW IMPORT

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
        self.spawn_data = {} 
        self.active_dialog = None # Tracks the active dialog
        self.click_lockout_timer = 0 # To prevent click-through after dialog closes

        # --- UI Components ---
        self.font_ui = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)
        self.spawn_counters = self._create_spawn_counters()
        self.action_buttons = self._create_action_buttons()
        
        # --- Dialog Initialization (NEW) ---
        screen_center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        # LoadDialog needs the load callback and the close callback
        self.load_dialog = LoadDialog(
            screen_center, 
            self.load_new_layout_by_name, # The success callback
            self._close_dialog           # The close/cancel callback
        )


    def handle_events(self, events):
        """Handles user input, prioritizing dialogs."""
        
        # 1. Dialog Handling (Highest Priority)
        if self.active_dialog:
            self.active_dialog.handle_events(events)
            return

        for event in events:
            # Check for State Change
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.next_state = "MAIN_MENU"
                self.done = True
                
            # Handle action button events
            for button in self.action_buttons:
                button.handle_event(event)
                
            # Handle spawn counter events
            for counter in self.spawn_counters:
                counter.handle_event(event)

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
            
        # Update spawn counters
        for counter in self.spawn_counters:
            counter.update()
        
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
            
        # Draw spawn counters (above the tiles)
        for counter in self.spawn_counters:
            counter.draw(screen)
        
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

    def _create_spawn_counters(self):
        """Finds all stairs tiles (ID 5) and creates EditableSpawnCount objects."""
        counters = []


        for r, row in enumerate(self.grid_data):
            for c, tile_id in enumerate(row):
                if tile_id == 5:  # Stairs tile
                    # Grid-based position (top-left of the tile)
                    x_tile = c * config.TILE_SIZE
                    y_tile = r * config.TILE_SIZE

                    # The EditableSpawnCount component needs to know its overall position.
                    # We'll calculate the center point of the tile for the component to use.
                    x_center = x_tile + (config.TILE_SIZE // 2)
                    y_center = y_tile - (config.SPAWN_BUBBLE_SIZE // 2) 

                    # Create a specific callback using a nested function to capture (r, c)
                    def make_callback(r, c):
                        return lambda new_count: self._update_spawn_data(r, c, new_count)

                    counter = EditableSpawnCount(
                        # Pass the center position for the component to draw around
                        x_center, y_center, 
                        config.SPAWN_COUNT_DEFAULT, 
                        make_callback(r, c),

                    )

                    # Store the initial value
                    self.spawn_data[(r, c)] = config.SPAWN_COUNT_DEFAULT
                    counters.append(counter)
        return counters

    def _draw_control_panel(self, screen):
        """Draws the background panel for control buttons and information (Consistent with BuildState)."""
        # This mirrors the palette panel dimensions from config for visual consistency
        panel_rect = pygame.Rect(config.PALETTE_PANEL_X, 0, config.PALETTE_PANEL_WIDTH, config.SCREEN_HEIGHT)
        pygame.draw.rect(screen, config.GRAY, panel_rect)
