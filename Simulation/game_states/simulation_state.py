# game_states/simulation_state.py
import pygame
import config, os
from game_states.tile_manager import TileManager
from game_states.layout_io import load_layout, get_layout_path # Ensure get_layout_path is available
from ui_elements.button import Button 
from ui_elements.editable_spawn_count import EditableSpawnCount
from ui_elements.spawn_config_slider import SpawnConfigSlider
from ui_elements.text_box import TextBox
from .queue_manager import QueueManager
import csv


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
        self.spawn_data = {}
        self.initial_spawn_data = {}
        self.selected_stairs_pos = None
        self.stairs_description_text = ""
        self.active_dialog = None 
        self.click_lockout_timer = 0 

        # Initialize map and counter list, relying on the function to populate them
        self.counter_map = {} 
        self.spawn_counters = [] # Initialize as empty list here
        self.queue_counter_map = {} 
        self.queue_counters = []
        self._create_queue_counters() # Call the new setup function


        # ONLY call population function once the grid is loaded
        self._create_spawn_counters() 

        # --- UI Components ---
        self.font_ui = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)
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
            min_val=0, max_val=100 # Reasonable min/max values
        )
        self.spawn_config_slider.is_active = False # Hidden until a stair is selected

                # Find all Entry tiles (ID 4) for the Queue Manager
        entry_tiles = self._get_tiles_by_id(4) 
        
        # Initialize Queue Manager
        self.queue_manager = QueueManager(
            entry_tiles, 
            self.spawn_data # Pass the dictionary with spawn counts from stair tiles
        )
        self.queue_manager.clear_queues()
        self._update_queue_visuals() # Initial visual update (sets them all to 0)


        
        # --- Dialog Initialization ---
        screen_center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        self.load_dialog = LoadDialog(
            screen_center, 
            self.load_new_layout_by_name, 
            self._close_dialog          
        )


        # --- Iterations Text Box ---
        export_btn_w, export_btn_h = 200, 50
        export_btn_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH - export_btn_w) // 2
        export_btn_y = 600  # Position below the other buttons


        self.iterations_textbox = TextBox(
        x = export_btn_x, 
        y = export_btn_y,
        text="100", 
        length=export_btn_w,
        height=export_btn_h,
        text_color=config.BLACK,
        bg_color=config.LIGHT_GRAY, 
        outline_color=config.DARK_GRAY,
        font=self.font_ui,
        editable=True
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

            # --- Handle the Iterations Text Box ---
            self.iterations_textbox.handle_event(event)
            
            # --- Handle the Slider (using the SINGLE event) ---
            self.spawn_config_slider.handle_event(event) 

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

        # Update iterations text box
        self.iterations_textbox.update()

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
            
        # Draw highlight around selected stairs tile
        self._draw_selected_stairs_highlight(screen)

        # Draw queue counters
        for counter in self.queue_counters:
            counter.draw(screen)

        # Draw the Spawn Config Slider
        self.spawn_config_slider.draw(screen)

        # Draw the description for the selected stairs (NEW)
        self._draw_stairs_description(screen) 

        # Draw the iterations text box
        self.iterations_textbox.draw(screen)
        
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

            # 4. Rebuild Queue Counters and QueueManager
            self._create_queue_counters()
            
            # Re-initialize the QueueManager with the new data
            entry_tiles = self._get_tiles_by_id(4) 
            self.queue_manager = QueueManager(entry_tiles, self.spawn_data)
            
            #Clear queues on load to ensure the initial state is 0.
            self.queue_manager.clear_queues()
            self._update_queue_visuals() # Sync visuals after clear
            
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
        """Creates buttons for the simulation control area (Load, Run, Reset)."""
        btn_w, btn_h = 95, 80 # REDUCED WIDTH for two buttons to fit
        
        # Position buttons consistently on the right-hand panel
        panel_center_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH // 2)
        
        # New shared Y position for RUN and RESET
        buttons_row_y = 60
        
        # Calculate the X position for the left button (RUN)
        # Total width needed is (btn_w * 2) + spacing (e.g., 10)
        total_group_width = (btn_w * 2) + 10 
        run_x = panel_center_x - (total_group_width // 2) - 40
        
        # Calculate the X position for the right button (RESET)
        reset_x = run_x + btn_w - 10 # 10 pixels of spacing
        
        
        # 1. Load Button (Kept at full width)
        # Use the original full width and centering for the LOAD button
        load_btn_w = 200
        load_btn_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH - load_btn_w) // 2 - 63

        self.load_button = Button(
            load_btn_x, 20, load_btn_w, 80, # Use original width/height
            "Load Station", self.open_load_dialog, 
            config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, text_size=28, hit_size=(200, 40)
        )
        
        # 2. RUN/SETUP Button
        self.run_button = Button(
            run_x, buttons_row_y, btn_w, btn_h, 
            "RUN", self._run_simulation_setup, # Calls the setup function
            config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, text_size=28, hit_size=(75, 40)
        )

        # 3. Reset Button
        self.reset_button = Button(
            reset_x, buttons_row_y, btn_w, btn_h, # Same Y position
            "RESET", self._reset_simulation_state, 
            config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, text_size=28, hit_size=(75, 40)
        )


        # 4. Create the "Run & Export" button with consistent styling and positioning
        # 4. Run & Export Button (styled and positioned consistently)
        run_export_btn_w = 200
        run_export_btn_h = 50
        run_export_btn_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH - run_export_btn_w) // 2
        run_export_btn_y = 400  # Position below the iterations text box

        self.run_export_button = Button(
            run_export_btn_x, run_export_btn_y, run_export_btn_w, run_export_btn_h,
            "Run & Export",
            self.start_simulation_and_export,
            config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER,
            text_size=24, hit_size=(run_export_btn_w, run_export_btn_h)
        )

        return [self.load_button, self.run_button, self.reset_button, self.run_export_button]

        
    def _update_spawn_data(self, r, c, new_count):
        """Callback function to update the internal spawn count data."""
        self.spawn_data[(r, c)] = new_count
        print(f"Spawn at ({r}, {c}) set to: {new_count} 1")
        

    def _update_selected_stairs_count(self, new_count):
            if self.selected_stairs_pos:
                r, c = self.selected_stairs_pos
                pos_key = (r, c)
                
                # 1. Update BOTH internal data structures
                self.spawn_data[pos_key] = new_count
                self.initial_spawn_data[pos_key] = new_count # NEW: Update the denominator

                # 2. Update the visual counter with the new fraction
                if pos_key in self.counter_map:
                    specific_counter = self.counter_map[pos_key]
                    display_text = f"{new_count}/{new_count}" # e.g., "30/30"
                    specific_counter.set_value(display_text)
            


    def _create_spawn_counters(self):
        """
        Finds all stairs tiles (ID 5) in the grid, creates a TextBox object 
        for each, and populates state dictionaries with the initial fractional format 
        ([Default]/[Default]).
        """
        
        # 1. Initialize and clear all related state containers
        self.counter_map.clear()
        self.spawn_data.clear()
        self.initial_spawn_data.clear() # Clear the denominator source
        
        # Guard Clause: Prevent loop execution if grid data is not loaded/valid
        if not self.grid_data or not self.grid_data[0]:
            print("WARNING: Grid data is empty during counter creation. Skipping population.")
            self.spawn_counters = []
            return self.spawn_counters 
        
        new_counters = []
        tile_size = config.TILE_SIZE
        bubble_size = config.SPAWN_BUBBLE_SIZE
        half_bubble = bubble_size // 2
        default_value = config.SPAWN_COUNT_DEFAULT

        for r, row in enumerate(self.grid_data):
            for c, tile_id in enumerate(row):
                if tile_id == 5:  # Stairs tile
                    
                    pos_key = (r, c)
                    
                    # Populate both dictionaries with the default value
                    self.spawn_data[pos_key] = default_value          
                    self.initial_spawn_data[pos_key] = default_value  

                    # Calculate the top-left position for the bubble 
                    # X: Tile center (c*size + size/2) - half bubble width
                    x_pos = c * tile_size + (tile_size // 2) - half_bubble - 10
                    # Y: Tile center (r*size + size/2) - full bubble height
                    y_pos = r * tile_size + (tile_size // 2) - bubble_size

                    # Create the visual counter object with the fractional format
                    display_text = f"{default_value}/{default_value}" 
                    counter = TextBox(
                        x_pos, y_pos, 
                        display_text, # Pass the fractional string
                        length=bubble_size+20
                    )

                    # 3. Store the objects and references
                    new_counters.append(counter)
                    self.counter_map[pos_key] = counter 
                    
        # 4. Final State Assignment
        self.spawn_counters = new_counters
        
        return self.spawn_counters

    def _create_queue_counters(self):
        """
        Finds all Entrance tiles (ID 4) and creates a TextBox object 
        below them to display the current queue length.
        """
        self.queue_counter_map.clear() 
        new_queue_counters = []

        # Ensure grid data is valid
        if not self.grid_data or not self.grid_data[0]:
            print("WARNING: Grid data is empty during queue counter creation.")
            self.queue_counters = []
            return 

        for r, row in enumerate(self.grid_data):
            for c, tile_id in enumerate(row):
                if tile_id == 4:  # Entrance tile

                    pos_key = (r, c)

                    x_tile = c * config.TILE_SIZE
                    y_tile = r * config.TILE_SIZE

                    # Calculate position: Place the bubble centered horizontally 
                    # but BELOW the tile, offset by TILE_SIZE.
                    x_center = x_tile + (config.TILE_SIZE // 2)
                    y_center = y_tile + (config.TILE_SIZE // 2) + config.TILE_SIZE 

                    # Create the visual counter object (initial value: 0)
                    counter = TextBox(
                        x_center - config.SPAWN_BUBBLE_SIZE // 2, 
                        y_center - config.SPAWN_BUBBLE_SIZE // 2, # Center vertically below the tile
                        "0" # Initial queue length
                    )

                    new_queue_counters.append(counter)
                    self.queue_counter_map[pos_key] = counter 

        self.queue_counters = new_queue_counters
        print(f"DEBUG: Queue counter setup complete with {len(self.queue_counter_map)} entries.")

        
    def _select_stairs_at(self, mouse_x, mouse_y):
        """Handles selecting a stairs tile by clicking."""
        col = int(mouse_x // config.TILE_SIZE)
        row = int(mouse_y // config.TILE_SIZE)
        
        # Check bounds
        if not (0 <= row < config.GRID_HEIGHT_TILES and 0 <= col < config.GRID_WIDTH_TILES):
            return 
            
        # Check if click is on the grid area (not the control panel)
        if mouse_x > config.PALETTE_PANEL_X:
            return 
            
        # Check if the clicked tile is a stairs tile (ID 5)
        if self.grid_data[row][col] == 5:

            # --- Update Description Text ---
            self.selected_stairs_pos = (row, col)
            self.stairs_description_text = (     
                "Value represents the total number of passengers to spawn from this point."
            )

            print(f"Stairs selected at ({row}, {col}). ACTIVATING SLIDER.")
            self.spawn_config_slider.is_active = True
            # Select this stairs tile
            self.selected_stairs_pos = (row, col)
            print(f"Stairs selected at ({row}, {col}). ACTIVATING SLIDER.")
            self.spawn_config_slider.is_active = True
            
            # Read the current value and update the slider UI
            current_count = self.spawn_data.get((row, col), config.SPAWN_COUNT_DEFAULT)
            self.spawn_config_slider.set_value(current_count)
            print(f"Stairs selected at ({row}, {col}). Current count: {current_count}")
            if self.selected_stairs_pos in self.counter_map: 
                # Success!
                pass 
            else:
                # This should no longer happen if the keys were populated correctly
                print(f"ERROR: Lookup STILL failed for {self.selected_stairs_pos}")

        else:
            # Deselect if they click elsewhere on the grid
            self.selected_stairs_pos = None
            self.spawn_config_slider.is_active = False
            self.stairs_description_text = "" # NEW: Clear text on deselect

        if (row, col) in self.counter_map:
            # SUCCESS
            pass 
        else:
            print(f"ERROR: Lookup failed on SimulationState ID: {id(self)}")
            print(f"ERROR: Map keys at failure: {list(self.counter_map.keys())}")
            
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


    def _get_tiles_by_id(self, tile_id):
        """Helper to return a list of (r, c) positions for a given tile ID."""
        positions = []
        if not self.grid_data:
            return positions
            
        for r, row in enumerate(self.grid_data):
            for c, id in enumerate(row):
                if id == tile_id:
                    positions.append((r, c))
        return positions


    def _run_simulation_setup(self):
        """
        Callback for the 'RUN' button. Triggers the initial passenger distribution 
        and resets spawn counts to zero. If clicked a second time (spawn pool empty),
        it first automatically performs a soft reset to the user's set values.
        """
        print("Simulation: Starting passenger distribution.")
        
        # Check if the spawn pool is currently empty (meaning the first run completed)
        current_total_passengers = sum(self.spawn_data.values())
        
        if current_total_passengers == 0:
            print("RUN called on empty spawn pool. Performing soft reset to restore spawn counts.")
            
            # Call the reset function to restore the spawn_data to the user's last set values.
            self._reset_simulation_state()
            
            # NOTE: After _reset_simulation_state, self.spawn_data now holds the user's non-zero values.

        # 1. Update QueueManager with current (restored/initial) spawn counts
        self.queue_manager.update_total_passengers(self.spawn_data)

        # 2. Execute distribution and get the dictionary needed for zeroing spawn_data
        # This will distribute the now-restored passenger count randomly into the queues.
        zeroed_data_map = self.queue_manager.distribute_passengers_utility_based()


        
        # 3. Reset internal spawn_data using the zeroed map
        # This empties the spawn source for the next run.
        self.spawn_data.update(zeroed_data_map) 

        # 4. Update Visuals
        self._update_queue_visuals()
        self._update_all_spawn_visuals()

    def _simulation_step(self):
        """Contains all logic that advances the simulation by one frame/instance."""
        
        # This function will be filled with Agent/Train logic later.
        # For now, it remains a placeholder.
        pass


    def _update_queue_visuals(self):
        """Synchronizes the visual queue counters with the QueueManager data."""
        
        # NOTE: self.queue_manager must be initialized before this is called!
        queue_lengths = self.queue_manager.get_queue_lengths()
        
        for pos, length in queue_lengths.items():
            if pos in self.queue_counter_map:
                # Use the set_value method from your TextBox class
                self.queue_counter_map[pos].set_value(length)


    def _reset_simulation_state(self):
        """
        Restores the simulation progress to its initial state (before RUN was pressed).
        Sets the remaining spawn count (numerator) equal to the total set count (denominator).
        """
        print("Simulation State Reset (Restoring Spawn Pool).")
        
        # 1. RESTORE SPAWN DATA: Set the remaining count (numerator) equal to the initial count (denominator)
        for pos_key, initial_count in self.initial_spawn_data.items():
            self.spawn_data[pos_key] = initial_count 

        # 2. Update Spawn Visual Counters (Now reflects [Initial]/[Initial])
        self._update_all_spawn_visuals() 

        # 3. Clear all Queues in the QueueManager
        self.queue_manager.clear_queues()
        
        # 4. Update Queue Visuals (sets them all to zero)
        self._update_queue_visuals()
        
        # 5. Deselect any stairs tile and deactivate the slider
        self.selected_stairs_pos = None
        self.spawn_config_slider.is_active = False
        self.stairs_description_text = "" # Clear description text



    def _update_all_spawn_visuals(self):
        """Synchronizes all visual spawn counters with the current self.spawn_data (current/initial format)."""
        
        for pos_key in self.spawn_data.keys():
            # Current value (Numerator: will be 0 after RUN)
            current_count = self.spawn_data.get(pos_key, 0)
            
            # Initial value (Denominator: will be preserved after RUN)
            initial_count = self.initial_spawn_data.get(pos_key, 0) 
            
            if pos_key in self.counter_map:
                specific_counter = self.counter_map[pos_key]
                # Format the new string: [Numerator]/[Denominator]
                display_text = f"{current_count}/{initial_count}"
                specific_counter.set_value(display_text)

    # In game_states/simulation_state.py, add this new method:

    def _draw_stairs_description(self, screen):
        """Draws the description text for the currently selected stairs tile, with wrapping."""
        if not self.stairs_description_text:
            return

        text_to_display = self.stairs_description_text
        words = text_to_display.split(' ')
        lines = []
        current_line = ''
        
        # Define the area for wrapping (the control panel width minus padding)
        padding = 10
        max_line_width = config.PALETTE_PANEL_WIDTH - 2 * padding

        # Define the starting Y position (e.g., just above the slider, which starts at y=150)
        text_y = 300 
        text_x = config.PALETTE_PANEL_X + padding
        
        # --- Text Wrapping Logic ---
        for word in words:
            test_line = f"{current_line} {word}".strip()
            # Use the UI font defined in __init__ (self.font_ui)
            test_surface = self.font_ui.render(test_line, True, config.BLACK)
            
            if test_surface.get_width() > max_line_width and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        lines.append(current_line)
        
        # --- Drawing Logic ---
        for line in lines:
            text_surface = self.font_ui.render(line, True, config.WHITE)
            screen.blit(text_surface, (text_x, text_y))
            text_y += config.FONT_SIZE_UI + 2 # Add a small gap between lines



    def get_iteration_count(self):
        """Safely retrieves and validates the iteration count from the text box."""
        try:
            # Assuming self.iterations_textbox is your TextBox instance
            count = int(self.iterations_textbox.get_text())
            return max(1, count) # Ensure at least 1 iteration
        except ValueError:
            print("Invalid iteration count. Defaulting to 1.")
            # Optionally, reset the text box to a valid number
            return 1

    def start_simulation_and_export(self):
        """Initiates multiple simulation runs and exports data to CSV."""

        # 1. Get the desired number of runs
        num_iterations = self.get_iteration_count()

        # 2. Setup the CSV file
        output_dir = "exports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        csv_filename = os.path.join(output_dir, "simulation_results.csv")

        # 3. Create and open the CSV file (Ignoring content for now, as requested)
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Header Row (Placeholder)
            writer.writerow(['Run Index', 'Placeholder Result 1', 'Placeholder Result 2'])

            print(f"Starting {num_iterations} simulation runs...")

            for i in range(1, num_iterations + 1):

                # Placeholder for running the simulation once
                # In a real setup, this would call a method that resets and runs the simulation
                # E.g., results = self.run_single_simulation()

                # --- For now, just write a dummy row ---
                dummy_result1 = 0
                dummy_result2 = 0
                writer.writerow([i, dummy_result1, dummy_result2])

                # Optional: Print progress
                if i % 10 == 0 or i == num_iterations:
                    print(f"  Completed Run {i}/{num_iterations}")

        print(f"All runs completed. Results saved to {csv_filename}")

        # Optional: Display a confirmation message in your game UI (using dialog.py)
        # self.show_dialog(f"Export Complete: {csv_filename}") 
