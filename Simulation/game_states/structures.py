# game_states/structures.py
import config

class TrackStructureManager:
    """
    Manages the placement, deletion, and modification of the 1x25 Track/Platform structures.
    Requires a reference to the main grid data and a method to update single tiles.
    """
    def __init__(self, grid_data, tile_update_callback):
        self.grid_data = grid_data
        # Method signature: tile_update_callback(old_id, new_id, col, row)
        self.tile_update_callback = tile_update_callback 
        # Format: {col_start: row_start} -> The top-left corner (Track tile) of the structure
        self.track_structures = {} 
        
        # Initialize by scanning the grid for existing structures
        self._scan_for_track_structures()


    # --- Public API for BuildState ---

    def try_place_structure(self, click_row, click_col):
        """
        Attempts to place a structure. Placement is forced to start at col 0.
        It identifies and deletes any overlapping existing structures and individual tiles 
        before placing the new structure.
        """
        start_col = 0
        N = config.TRACK_LENGTH
        
        # 1. Determine the top-left row of the structure based on the click
        start_row = click_row
        
        # Check area validity only for bounds and alignment (col 0)
        if not self._is_valid_area(start_row, start_col):
            # If the click was on the platform row, try one row up
            if start_row > 0 and self._is_valid_area(start_row - 1, start_col):
                 start_row -= 1
            else:
                 print("Placement failed: Structure is out of bounds or not starting at col 0.")
                 return False 

        # The calculated placement root is (start_row, start_col=0)
        
        # 2. CLEAR THE ENTIRE 2xN AREA OF OLD STRUCTURES AND TILES

        # A. Delete all *registered* structures that overlap the proposed area.
        roots_to_delete = []
        
        # Proposed area spans rows start_row to start_row + 1
        
        # Check for structures rooted at the proposed row (exact match)
        if start_col in self.track_structures and self.track_structures[start_col] == start_row:
             roots_to_delete.append((start_row, start_col))
             
        # Check for structures rooted one row above (R-1 to R)
        if start_col in self.track_structures and self.track_structures[start_col] == start_row - 1:
             roots_to_delete.append((start_row - 1, start_col))
             
        # Check for structures rooted one row below (R+1 to R+2)
        if start_col in self.track_structures and self.track_structures[start_col] == start_row + 1:
             roots_to_delete.append((start_row + 1, start_col))


        # Execute deletions for all found overlapping structures
        for r, c in roots_to_delete:
            self._execute_deletion(r, c)
             
        # B. Clear all individual tiles in the area (handles loose tiles like platform_floor)
        for r in range(start_row, start_row + 2):
            for c in range(start_col, start_col + N):
                current_id = self.grid_data[r][c]
                if current_id != 0:
                    # Manually clear non-empty tile (this should only catch non-registered tiles now)
                    old_id = self.grid_data[r][c]
                    self.grid_data[r][c] = 0
                    self.tile_update_callback(old_id, 0, c, r)

        # 3. EXECUTE PLACEMENT
        self._execute_placement(start_row, start_col)
        return True
        
    def try_delete_structure(self, row, col):
        """
        Checks if the tile is part of a structure and deletes the whole structure if so.
        """
        root = self._get_structure_root(row, col)
        if root:
            self._execute_deletion(root['row'], root['col'])
            return True
        return False

    def try_modify_platform(self, row, col):
        """
        Toggles a Platform Edge (2) to an Entrance (4) or vice-versa, only if it is part of a structure.
        """
        current_id = self.grid_data[row][col]
        
        # Only modify the tile if it's the Platform Edge or Entrance tile, AND it belongs to a structure.
        if current_id in [2, 4] and self._is_part_of_structure(row, col):
            new_id = 4 if current_id == 2 else 2 # Toggle
            old_id = current_id
            
            self.grid_data[row][col] = new_id
            self.tile_update_callback(old_id, new_id, col, row)
            return True
            
        return False

    # --- Private Implementation Helpers ---

    def _is_valid_area(self, start_row, start_col):
        """Checks bounds and ensures alignment (col 0) for a 2xN area."""
        N = config.TRACK_LENGTH
        end_col = start_col + N - 1
        
        # 1. Check bounds
        if (start_col != 0 or end_col >= config.GRID_WIDTH_TILES or
            start_row < 0 or start_row + 1 >= config.GRID_HEIGHT_TILES):
            return False
            
        return True

    def _execute_placement(self, start_row, start_col):
        """Places the Track and Platform Edge tiles and registers the structure."""
        N = config.TRACK_LENGTH
        
        # 1. Place the Track (ID 3)
        for c in range(start_col, start_col + N):
            self.grid_data[start_row][c] = 3
            # old_id is implicitly 0 because the area was cleared in try_place_structure
            self.tile_update_callback(0, 3, c, start_row)
            
        # 2. Place the Platform Edge (ID 2)
        for c in range(start_col, start_col + N):
            self.grid_data[start_row + 1][c] = 2
            # old_id is implicitly 0 because the area was cleared in try_place_structure
            self.tile_update_callback(0, 2, c, start_row + 1)
            
        # 3. Register the structure root
        self.track_structures[start_col] = start_row

    # --- THIS IS THE MISSING FUNCTION THAT CAUSED THE ERROR ---
    def _execute_deletion(self, start_row, start_col):
        """Deletes the 2xN structure and deregisters it."""
        N = config.TRACK_LENGTH
        
        # Erase Track and Platform Edge/Entrance
        for r in range(start_row, start_row + 2):
            for c in range(start_col, start_col + N):
                old_id = self.grid_data[r][c]
                self.grid_data[r][c] = 0
                self.tile_update_callback(old_id, 0, c, r)
            
        # Deregister the structure root
        if start_col in self.track_structures:
            del self.track_structures[start_col]


    def _is_part_of_structure(self, row, col):
        """Checks if a tile is horizontally within the bounds of a registered structure."""
        for start_col, start_row in self.track_structures.items():
            end_col = start_col + config.TRACK_LENGTH - 1
            # Check if (row, col) is within the registered structure's coordinates
            if (row == start_row or row == start_row + 1) and (start_col <= col <= end_col):
                return True
        return False
        
    def _get_structure_root(self, row, col):
        """Finds the root (top-left track tile) of a structure."""
        if self.grid_data[row][col] not in [2, 3, 4]:
            return None
            
        for start_col, start_row in self.track_structures.items():
            end_col = start_col + config.TRACK_LENGTH - 1
            if (row == start_row or row == start_row + 1) and (start_col <= col <= end_col):
                return {'row': start_row, 'col': start_col}
        return None

    def _scan_for_track_structures(self):
        # ... (implementation remains the same) ...
        self.track_structures.clear()
        N = config.TRACK_LENGTH
        
        for row in range(config.GRID_HEIGHT_TILES - 1): 
            col = 0 # Structures must start at col=0
            
            # Check for a Track tile (ID 3) at the root position (row, 0)
            if self.grid_data[row][col] == 3:
                is_valid = True
                
                # Check the full 2xN area
                for c in range(col, col + N):
                    # Check the track row
                    if c >= config.GRID_WIDTH_TILES or self.grid_data[row][c] != 3:
                        is_valid = False
                        break
                    # Check the platform/entrance row
                    platform_tile = self.grid_data[row + 1][c]
                    if platform_tile not in [2, 4]: # Must be a Platform Edge (2) or Entrance (4)
                        is_valid = False
                        break
                        
                if is_valid:
                    self.track_structures[col] = row
                    
        print(f"Structure Manager: Found {len(self.track_structures)} existing track structures.")