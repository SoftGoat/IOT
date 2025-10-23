# game_states/simulation/simulation_state.py (The Refactored Version)
import pygame
import csv
import config
import os

from ..tile_manager import TileManager
from ..layout_io import load_layout, get_layout_path 
from ..state import State 
from ..queue_manager import QueueManager
# --- NEW IMPORT ---
from .simulation_ui_controller import SimulationUIController 
# ------------------

from ui_elements.button import Button # Only needed if creating buttons here
from dialog import LoadDialog

# ----------------------------------------------------------------------
# I. CORE INTERFACE (Called by main.py)
# ----------------------------------------------------------------------

class SimulationState(State):
    def __init__(self):
        super().__init__()
        
        # --- Core State Data (Minimised) ---
        self.grid_data = self._load_simulation_layout()

        # --- Managers ---
        self.tile_manager = TileManager(config.TILE_MAPPING)
        self.tile_manager.create_all(self.grid_data)
        
        # --- UI Controller (Holds all UI logic and UI-specific state) ---
        self.ui_controller = SimulationUIController(
            grid_data=self.grid_data, 
            tile_manager=self.tile_manager,
            open_load_dialog_cb=self.open_load_dialog,
            load_new_layout_cb=self.load_new_layout_by_name,
            get_tiles_by_id_cb=self._get_tiles_by_id # Pass necessary helper
        )
        
        # --- Simulation Data (References to UI Controller data) ---
        # NOTE: We can keep a direct reference or rely on the controller's methods
        self.spawn_data = self.ui_controller.spawn_data # Direct reference for easier access
        self.initial_spawn_data = self.ui_controller.initial_spawn_data

        # Populate initial counters (This call is now internal to the controller)
        self.ui_controller._create_spawn_counters() 
        self.ui_controller._create_queue_counters()

        # --- Queue Manager Setup ---
        entry_tiles = self._get_tiles_by_id(4) 
        self.queue_manager = QueueManager(entry_tiles, self.spawn_data)
        self.queue_manager.clear_queues()
        self._update_queue_visuals() # Initial visual update

        # --- Dialog Initialization (Must remain here to manage the overall state) ---
        screen_center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        self.load_dialog = LoadDialog(
            screen_center, 
            self.load_new_layout_by_name, 
            self._close_dialog          
        )
        self.active_dialog = None
        self.click_lockout_timer = 0 
        
        # --- FINAL STEP: Connect UI Buttons to SimulationState methods ---
        self.ui_controller.set_run_reset_export_callbacks(
            self._run_simulation_setup, 
            self._reset_simulation_state, 
            self.start_simulation_and_export
        )


    def handle_events(self, events):
        """Handles user input, prioritizing dialogs and delegating to UI Controller."""
        
        # 1. Dialog Handling (Highest Priority)
        if self.active_dialog:
            self.active_dialog.handle_events(events)
            return
            
        # 2. Process and Delegate each event to the UI Controller
        for event in events:
            
            # Check for General State Change Keys (Escape)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.next_state = "MAIN_MENU"
                self.done = True
                return # Exit immediately on state change

            # 3. Delegate the individual event to the UI Controller
            # The controller handles buttons, slider, textbox, and stairs selection
            self.ui_controller.handle_event(event) 
            
        # NOTE: No need for code outside the loop now.

    def update(self):
        """Updates core simulation logic and delegates UI updates."""
        
        # 1. Dialog Update/Exit Priority
        if self.active_dialog:
            self.active_dialog.update()
            return

        # 2. Lockout Check
        if self.click_lockout_timer > 0:
            self.click_lockout_timer -= 1
            return 
            
        # 3. Delegate UI updates
        self.ui_controller.update()

        # Add core simulation update logic here later...
        pass

    def draw(self, screen):
        """Draws all elements: tiles, control panel, buttons, and spawn counters."""
        screen.fill(config.BLACK)
        self.tile_manager.sprites.draw(screen)
        
        # Delegate drawing of all UI elements to the controller
        self.ui_controller.draw(screen)
            
        # Draw dialogs (LAST)
        if self.active_dialog:
            self.active_dialog.draw(screen)

# ----------------------------------------------------------------------
# II. PUBLIC ACTIONS (Simulation Flow Control)
# ----------------------------------------------------------------------

    def open_load_dialog(self):
        """Launches the Load Layout Dialog."""
        self.active_dialog = self.load_dialog
        self.active_dialog.show()

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
            
            # 3. Rebuild Spawn Counters (Done via UI Controller)
            self.ui_controller.grid_data = self.grid_data # Update controller's reference
            self.ui_controller._create_spawn_counters()

            # 4. Rebuild Queue Counters and QueueManager
            self.ui_controller._create_queue_counters()
            
            # Re-initialize the QueueManager with the new data and updated spawn_data references
            entry_tiles = self._get_tiles_by_id(4) 
            self.queue_manager = QueueManager(entry_tiles, self.spawn_data)
            
            self.queue_manager.clear_queues()
            self._update_queue_visuals() 
            
            self._close_dialog()
            print(f"Loaded layout: {layout_name}")
            
        except FileNotFoundError:
            print(f"Error: Layout {layout_name} not found.")

    def start_simulation_and_export(self):
        """
        Initiates multiple simulation runs, records the distribution results 
        in the specified CSV format, and saves the data.
        """
        # 1. Get the desired number of runs
        num_iterations = self.ui_controller.get_iteration_count()
        print(f"Starting simulation and export for {num_iterations} rounds...")
        
        # 2. Preparation
        output_dir = "exports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        csv_filename = os.path.join(output_dir, "simulation_results.csv")
        
        # Ensure a clean slate before the first run logic
        self._reset_simulation_state()
        
        # Get the ordered list of spawn and entry tiles for the header
        spawn_tiles_sorted = sorted(self.spawn_data.keys())
        entry_tiles_sorted = sorted(self.queue_manager.entry_tile_positions)
        
        # 3. Define the CSV Header
        header = ['Round']
        header.extend([f"Spawn [{r},{c}]" for r, c in spawn_tiles_sorted])
        header.extend([f"Entry [{r},{c}]" for r, c in entry_tiles_sorted])

        # 4. Create and open the CSV file
        results = []
        
        # 5. Run the Simulation Rounds
        for i in range(1, num_iterations + 1):
            
            # --- Run Logic: Distribute Passengers ---
            # NOTE: _run_simulation_setup handles:
            # 1. Restoring spawn_data if it was zeroed (on round 1 it's restored by _reset)
            # 2. Updating QueueManager with the total passenger count (from spawn_data)
            # 3. Distributing passengers into queues
            # 4. Zeroing out the source spawn_data (for the *next* run/step)
            # 5. Updating queue visuals
            self._run_simulation_setup()

            # --- Data Collection for Export ---
            row_data = [f"round {i}"]
            
            # 5a. Collect Spawn Values (Fixed initial value based on self.initial_spawn_data)
            # This is crucial: the output table shows the *source* count, not the remaining count.
            for pos in spawn_tiles_sorted:
                # Use initial_spawn_data to reflect the constant source value (e.g., 10 or 30)
                spawn_count = self.initial_spawn_data.get(pos, 0)
                row_data.append(spawn_count)
            
            # 5b. Collect Entry Queue Values (Result of distribution from the current round)
            queue_lengths = self.queue_manager.get_queue_lengths()
            for pos in entry_tiles_sorted:
                # Get the queue length (e.g., 25 or 5)
                queue_count = queue_lengths.get(pos, 0)
                row_data.append(queue_count)
            
            results.append(row_data)

            if i % 10 == 0 or i == num_iterations:
                print(f"  Completed Data Collection for Round {i}/{num_iterations}")
        
        
        # 6. Write to CSV
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(results)

        print(f"All runs completed. Results saved to {csv_filename}")
        
        # Optional: Display a confirmation message in your game UI (you'll need to implement this)
        # self.show_dialog(f"Export Complete: {csv_filename}")
        
        # Re-sync visuals after the last distribution run
        self._update_queue_visuals()
        self._update_all_spawn_visuals()



# ----------------------------------------------------------------------
# III. PRIVATE HELPERS (Core state management and delegation)
# ----------------------------------------------------------------------
    
    def _close_dialog(self):
        """Callback to close the active dialog and set lockout timer."""
        if self.active_dialog:
            self.active_dialog.is_active = False
            self.active_dialog = None
            
            pygame.event.get(pygame.MOUSEBUTTONDOWN)
            pygame.event.get(pygame.MOUSEBUTTONUP)
            
            self.click_lockout_timer = 5 
            self.ui_controller.click_lockout_timer = 5 # Also reset controller lockout
            
    def _load_simulation_layout(self):
        """Tries to load the user's layout, falling back to default."""
        try:
            return load_layout(config.USER_LAYOUT_PATH)
        except FileNotFoundError:
            try:
                 return load_layout(config.DEFAULT_LAYOUT_PATH)
            except FileNotFoundError:
                print("Warning: Layouts missing. Starting with empty grid.")
                return [[0]*config.GRID_WIDTH_TILES for _ in range(config.GRID_HEIGHT_TILES)]


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
        and resets spawn counts to zero.
        """
        print("Simulation: Starting passenger distribution.")
        
        current_total_passengers = sum(self.spawn_data.values())
        
        if current_total_passengers == 0:
            print("RUN called on empty spawn pool. Performing soft reset to restore spawn counts.")
            self._reset_simulation_state()

        # 1. Update QueueManager with current (restored/initial) spawn counts
        self.queue_manager.update_total_passengers(self.spawn_data)

        # --- Get the values from BOTH sliders (RENAMED) ---
        k_ratio_val = self.ui_controller.get_k_length_ratio() 
        rationality_val = self.ui_controller.get_rationality_factor() # RENAMED
        # -------------------------------------------------

        # 2. Execute distribution and get the dictionary needed for zeroing spawn_data
        # --- Pass the two values to the correct parameters (RENAMED) ---
        zeroed_data_map = self.queue_manager.distribute_passengers_utility_based(
            rationality_factor = rationality_val, # RENAMED
            k_length_ratio = k_ratio_val
        )
        # ----------------------------------------------------------
        
        # 3. Reset internal spawn_data using the zeroed map
        self.spawn_data.update(zeroed_data_map) 

        # 4. Update Visuals (Delegate to the controller for visual sync)
        self._update_queue_visuals()
        self._update_all_spawn_visuals()

    def _simulation_step(self):
        """Contains all logic that advances the simulation by one frame/instance."""
        # This remains a placeholder for future agent/train logic.
        pass


    def _update_queue_visuals(self):
        """Synchronizes the visual queue counters with the QueueManager data."""
        queue_lengths = self.queue_manager.get_queue_lengths()
        
        # Delegate to the UI controller's counter map
        queue_counter_map = self.ui_controller.queue_counter_map 
        
        for pos, length in queue_lengths.items():
            if pos in queue_counter_map:
                queue_counter_map[pos].set_value(length)


    def _reset_simulation_state(self):
        """
        Restores the simulation progress to its initial state.
        """
        print("Simulation State Reset (Restoring Spawn Pool).")
        
        # 1. RESTORE SPAWN DATA: Set the remaining count equal to the initial count
        for pos_key, initial_count in self.initial_spawn_data.items():
            self.spawn_data[pos_key] = initial_count 

        # 2. Update Spawn Visual Counters 
        self._update_all_spawn_visuals() 

        # 3. Clear all Queues in the QueueManager
        self.queue_manager.clear_queues()
        
        # 4. Update Queue Visuals 
        self._update_queue_visuals()
        
        # 5. Deselect any stairs tile and deactivate the slider (Delegate to controller)
        self.ui_controller.selected_stairs_pos = None

        # Deactivate the spawn count slider
        self.ui_controller.spawn_count_slider.is_active = False

        # The queue_ratio_slider remains active by default in the controller
        self.ui_controller.stairs_description_text = "" 


    def _update_all_spawn_visuals(self):
        """Synchronizes all visual spawn counters with the current self.spawn_data (current/initial format)."""
        
        counter_map = self.ui_controller.counter_map
        
        for pos_key in self.spawn_data.keys():
            current_count = self.spawn_data.get(pos_key, 0)
            initial_count = self.initial_spawn_data.get(pos_key, 0) 
            
            if pos_key in counter_map:
                specific_counter = counter_map[pos_key]
                display_text = f"{current_count}/{initial_count}"
                specific_counter.set_value(display_text)