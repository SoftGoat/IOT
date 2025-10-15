# game_states/simulation/simulation_ui_controller.py
import pygame
import config
from dialog import LoadDialog
# NOTE: The parent 'simulation' package is a sibling to 'ui_elements'
from ui_elements.button import Button 
from ui_elements.editable_spawn_count import EditableSpawnCount
from ui_elements.spawn_config_slider import SpawnConfigSlider
from ui_elements.text_box import TextBox
# We need to import the utility class used for the counters
from ui_elements.text_box import TextBox # Assuming the TextBox is the counter implementation

class SimulationUIController:
    """
    Manages all UI elements and logic for spawn point configuration 
    within the Simulation State.
    """
    def __init__(self, grid_data, tile_manager, open_load_dialog_cb, load_new_layout_cb, get_tiles_by_id_cb):
        
        # Dependencies from SimulationState
        self.grid_data = grid_data
        self.tile_manager = tile_manager
        self.open_load_dialog = open_load_dialog_cb
        self.get_tiles_by_id = get_tiles_by_id_cb
        self.load_new_layout_cb = load_new_layout_cb
        
        # State data for UI only
        self.selected_stairs_pos = None
        self.stairs_description_text = ""
        self.click_lockout_timer = 0 # UI only lockout
        
        # --- Data to be shared/updated by external logic (SimulationState) ---
        self.spawn_data = {} # Populated by _create_spawn_counters
        self.initial_spawn_data = {}
        self.counter_map = {} 
        self.spawn_counters = []
        self.queue_counter_map = {} 
        self.queue_counters = []

        # UI Setup
        self.font_ui = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)
        self.action_buttons = self._create_action_buttons()
        
        # --- Internal state for the queue ratio ---
        self.queue_k_length_ratio = config.K_RATIO_LENGTH_DEFAULT

        # --- Spawn Count Slider setup ---
        slider_w = config.PALETTE_PANEL_WIDTH - 40
        slider_x = config.PALETTE_PANEL_X + 20
        spawn_slider_y = 150  # <--- DEFINED HERE
        slider_h = 100
        self.spawn_count_slider = SpawnConfigSlider(
            slider_x, spawn_slider_y, slider_w, slider_h, 
            config.SPAWN_COUNT_DEFAULT, 
            self._update_selected_stairs_count, # Internal callback for slider
            min_val=0, max_val=100
        )
        self.spawn_count_slider.is_active = False


        # --- Queue Ratio Slider Setup ---
        # Position below the spawn count slider
        ratio_slider_y = spawn_slider_y + slider_h + 30 
        
        self.queue_ratio_slider = SpawnConfigSlider( # Reusing the slider class
            slider_x, ratio_slider_y, slider_w, slider_h, 
            config.K_RATIO_LENGTH_DEFAULT, 
            self._update_queue_ratio, # NEW Internal callback for ratio
            min_val=config.K_RATIO_LENGTH_MIN, 
            max_val=config.K_RATIO_LENGTH_MAX
        )
        # Ratio slider is always active in this state, unless you hide it later.
        self.queue_ratio_slider.is_active = True 

        # Dialog Initialization (Dialog logic will remain in SimulationState for now)
        
        # Iterations Text Box
        export_btn_w, export_btn_h = 100, 50
        export_btn_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH - export_btn_w) // 2
        export_btn_y = 600

        self.iterations_textbox = TextBox(
            x = export_btn_x, y = export_btn_y, text="100", 
            length=export_btn_w, height=export_btn_h,
            text_color=config.BLACK, bg_color=config.LIGHT_GRAY, 
            outline_color=config.DARK_GRAY, font=self.font_ui, editable=True
        )
        
    def _update_selected_stairs_count(self, new_count):
        """Callback from the slider to update internal data and visuals."""
        if self.selected_stairs_pos:
            r, c = self.selected_stairs_pos
            pos_key = (r, c)
            
            # 1. Update BOTH internal data structures
            self.spawn_data[pos_key] = new_count
            self.initial_spawn_data[pos_key] = new_count 

            # 2. Update the visual counter with the new fraction
            if pos_key in self.counter_map:
                specific_counter = self.counter_map[pos_key]
                
                # --- FIX: Ensure the display text shows the new count / initial count ---
                # Since we update both values to new_count, the display should be new_count/new_count
                display_text = f"{new_count}/{new_count}" 
                specific_counter.set_value(display_text)

    def _update_queue_ratio(self, new_ratio):
        """Callback from the ratio slider to update internal data."""
        
        # --- ADD DEBUG PRINT HERE ---
        print(f"DEBUG SLIDER CALLBACK: New Ratio Received = {new_ratio}")
        # ----------------------------

        self.queue_k_length_ratio = float(new_ratio)

    def get_queue_ratio(self):
        """Public getter for SimulationState to use."""
        return self.queue_k_length_ratio
                
    def handle_event(self, event):
        """Handles events for UI elements (slider, text box, buttons, stairs selection)."""
        
        # Handle the Slider 
        self.spawn_count_slider.handle_event(event)

        # Handle the Iterations Text Box
        self.iterations_textbox.handle_event(event)

        # Handle the NEW Ratio Slider
        self.queue_ratio_slider.handle_event(event) 

        # Handle action button events
        for button in self.action_buttons:
            button.handle_event(event)
            
        # Handle mouse click on a stair tile for selection
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click
            mouse_x, mouse_y = event.pos
            self._select_stairs_at(mouse_x, mouse_y)
            
    def update(self):
        """Updates UI component states (hover, input)."""
        for button in self.action_buttons:
            button.update()
            
        self.spawn_count_slider.update() # RENAMED
        self.queue_ratio_slider.update() # NEW
        self.iterations_textbox.update()
        
        # Update spawn counters
        for counter in self.spawn_counters:
            counter.update()
            
        # Update lockout timer
        if self.click_lockout_timer > 0:
            self.click_lockout_timer -= 1


    def draw(self, screen):
        """Draws the control panel and all associated UI elements."""
        
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
        self.spawn_count_slider.draw(screen)

        # Draw the NEW Queue Ratio Slider
        self.queue_ratio_slider.draw(screen) 


        # Draw the description for the selected stairs
        self._draw_stairs_description(screen) 

        # Draw the iterations text box
        self.iterations_textbox.draw(screen)


    # --- Moved Helper Methods (Retain logic, but now part of Controller) ---

    def _create_action_buttons(self):
        """Creates buttons for the simulation control area (Load, Run, Reset, Export)."""
        # NOTE: Run, Reset, and Export callbacks MUST be passed in or handled by SimulationState
        # For simplicity, we assume SimulationState will handle the button instantiation
        # and just return the list here for drawing/event handling. 
        # Since this controller will be initialized inside SimulationState,
        # we will rely on SimulationState to provide the correct methods for the callbacks.
        
        btn_w, btn_h = 95, 80 
        panel_center_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH // 2)
        buttons_row_y = 60
        total_group_width = (btn_w * 2) + 10 
        run_x = panel_center_x - (total_group_width // 2) - 40
        reset_x = run_x + btn_w - 10 
        
        load_btn_w = 200
        load_btn_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH - load_btn_w) // 2 - 63

        self.load_button = Button(
            load_btn_x, 20, load_btn_w, 80, 
            "Load Station", self.open_load_dialog, # open_load_dialog is a bound method passed in
            config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, text_size=28, hit_size=(200, 40)
        )
        
        # NOTE: The callbacks for RUN, RESET, and EXPORT must be set up 
        # by the parent SimulationState when it creates this controller.
        
        # For now, we will add placeholder methods to be overwritten by the parent.
        # This is the messiest part of the refactor. A cleaner way is to pass all callbacks 
        # to the __init__ of the controller.

        class PlaceholderCallbacks:
             def __init__(self, parent): self.parent = parent
             def _run_simulation_setup(self): print("Placeholder RUN") 
             def _reset_simulation_state(self): print("Placeholder RESET")
             def start_simulation_and_export(self): print("Placeholder EXPORT")

        # Create a temporary object to hold the run/reset/export callbacks
        # This is a bit of a hack, but works if we can't change the Button API to accept a list of callbacks
        temp_callbacks = PlaceholderCallbacks(self) 

        # 2. RUN/SETUP Button
        self.run_button = Button(
            run_x, buttons_row_y, btn_w, btn_h, 
            "RUN", temp_callbacks._run_simulation_setup, 
            config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, text_size=28, hit_size=(75, 40)
        )

        # 3. Reset Button
        self.reset_button = Button(
            reset_x, buttons_row_y, btn_w, btn_h, 
            "RESET", temp_callbacks._reset_simulation_state, 
            config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER, text_size=28, hit_size=(75, 40)
        )


        # 4. Run & Export Button
        run_export_btn_w = 150
        run_export_btn_h = 75
        run_export_btn_x = config.PALETTE_PANEL_X + (config.PALETTE_PANEL_WIDTH - run_export_btn_w) // 2
        run_export_btn_y = 535

        self.run_export_button = Button(
            run_export_btn_x, run_export_btn_y, run_export_btn_w, run_export_btn_h,
            "Run & Export",
            temp_callbacks.start_simulation_and_export,
            config.BUTTON_IN_GAME, config.BUTTON_IN_GAME_HOVER,
            text_size=24, hit_size=(run_export_btn_w, run_export_btn_h)
        )

        return [self.load_button, self.run_button, self.reset_button, self.run_export_button]


    def _create_spawn_counters(self):
        """
        Finds all stairs tiles (ID 5) in the grid, creates a TextBox object 
        for each, and populates state dictionaries.
        """
        # 1. Initialize and clear all related state containers
        self.counter_map.clear()
        self.spawn_data.clear()
        self.initial_spawn_data.clear() 
        
        if not self.grid_data or not self.grid_data[0]:
            print("WARNING: Grid data is empty during counter creation. Skipping population.")
            self.spawn_counters = []
            return 
        
        new_counters = []
        tile_size = config.TILE_SIZE
        bubble_size = config.SPAWN_BUBBLE_SIZE
        half_bubble = bubble_size // 2
        default_value = config.SPAWN_COUNT_DEFAULT

        for r, row in enumerate(self.grid_data):
            for c, tile_id in enumerate(row):
                if tile_id == 5:  # Stairs tile
                    
                    pos_key = (r, c)
                    
                    self.spawn_data[pos_key] = default_value          
                    self.initial_spawn_data[pos_key] = default_value  

                    x_pos = c * tile_size + (tile_size // 2) - half_bubble - 10
                    y_pos = r * tile_size + (tile_size // 2) - bubble_size

                    display_text = f"{default_value}/{default_value}" 
                    counter = TextBox(x_pos, y_pos, display_text, length=bubble_size+20)

                    new_counters.append(counter)
                    self.counter_map[pos_key] = counter 
                    
        self.spawn_counters = new_counters
        
    def _create_queue_counters(self):
        """
        Finds all Entrance tiles (ID 4) and creates a TextBox object 
        below them to display the current queue length.
        """
        self.queue_counter_map.clear() 
        new_queue_counters = []

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

                    x_center = x_tile + (config.TILE_SIZE // 2)
                    y_center = y_tile + (config.TILE_SIZE // 2) + config.TILE_SIZE 

                    counter = TextBox(
                        x_center - config.SPAWN_BUBBLE_SIZE // 2, 
                        y_center - config.SPAWN_BUBBLE_SIZE // 2,
                        "0" 
                    )

                    new_queue_counters.append(counter)
                    self.queue_counter_map[pos_key] = counter 

        self.queue_counters = new_queue_counters
        print(f"DEBUG: Queue counter setup complete with {len(self.queue_counter_map)} entries.")

        
    def _select_stairs_at(self, mouse_x, mouse_y):
        """Handles selecting a stairs tile by clicking."""
        col = int(mouse_x // config.TILE_SIZE)
        row = int(mouse_y // config.TILE_SIZE)
        
        if not (0 <= row < config.GRID_HEIGHT_TILES and 0 <= col < config.GRID_WIDTH_TILES):
            return 
            
        if mouse_x > config.PALETTE_PANEL_X:
            return 
            
        if self.grid_data[row][col] == 5:

            self.selected_stairs_pos = (row, col)
            self.stairs_description_text = (     
                "Value represents the total number of passengers to spawn from this point."
            )

            self.spawn_count_slider.is_active = True
            self.selected_stairs_pos = (row, col)
            
            current_count = self.spawn_data.get((row, col), config.SPAWN_COUNT_DEFAULT)
            self.spawn_count_slider.set_value(current_count)

        else:
            self.selected_stairs_pos = None
            self.spawn_count_slider.is_active = False
            self.stairs_description_text = "" 

    def _draw_selected_stairs_highlight(self, screen):
        """Draws a highlight box around the currently selected stairs tile."""
        if self.selected_stairs_pos:
            row, col = self.selected_stairs_pos
            x = col * config.TILE_SIZE
            y = row * config.TILE_SIZE
            
            highlight_color = (0, 255, 255) 
            pygame.draw.rect(screen, highlight_color, (x, y, config.TILE_SIZE, config.TILE_SIZE), 3)

    def _draw_control_panel(self, screen):
        """Draws the background panel for control buttons and information (Consistent with BuildState)."""
        panel_rect = pygame.Rect(config.PALETTE_PANEL_X, 0, config.PALETTE_PANEL_WIDTH, config.SCREEN_HEIGHT)
        pygame.draw.rect(screen, config.GRAY, panel_rect)

    def _draw_stairs_description(self, screen):
        """Draws the description text for the currently selected stairs tile, with wrapping."""
        
        padding = 10
        max_line_width = config.PALETTE_PANEL_WIDTH - 2 * padding
        
        # Adjust Y position to clear both sliders (150+100+30+100)
        # We'll use 400 to give ample clearance.
        text_y = 400 
        text_x = config.PALETTE_PANEL_X + padding
        
        if not self.stairs_description_text:
            # Display Ratio Info when no stairs tile is selected
            current_ratio = self.queue_k_length_ratio
            text_to_display = (
                f"Queue Ratio (k_length): {current_ratio:.1f}\n"
                f"Low values favor short queues; High values favor short distances."
            )
        else:
            # Display Stairs Info when a stairs tile IS selected
            text_to_display = self.stairs_description_text
            
        words = text_to_display.replace('\n', ' ').split(' ')
        lines = []
        current_line = ''
        
        # Line wrapping logic
        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_surface = self.font_ui.render(test_line, True, config.BLACK) # Render using BLACK text
            
            if test_surface.get_width() > max_line_width and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        lines.append(current_line)
        
        # Draw the lines
        for line in lines:
            text_surface = self.font_ui.render(line, True, config.WHITE)
            screen.blit(text_surface, (text_x, text_y))
            text_y += config.FONT_SIZE_UI + 2 

    def get_iteration_count(self):
        """Safely retrieves and validates the iteration count from the text box."""
        try:
            count = int(self.iterations_textbox.get_text())
            return max(1, count)
        except ValueError:
            return 1
            
    # --- Methods to allow SimulationState to synchronize data ---
    
    def get_spawn_data(self):
        """Returns the current spawn data dictionary."""
        return self.spawn_data

    def get_initial_spawn_data(self):
        """Returns the initial spawn data dictionary."""
        return self.initial_spawn_data

    def set_run_reset_export_callbacks(self, run_cb, reset_cb, export_cb):
        """Updates the callbacks for the action buttons."""
        # Find the specific buttons and update their callback function references
        for button in self.action_buttons:
            if button.text == "RUN":
                button.callback = run_cb
            elif button.text == "RESET":
                button.callback = reset_cb
            elif button.text == "Run & Export":
                button.callback = export_cb