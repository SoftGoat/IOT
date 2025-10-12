# queue_manager.py

import random
import math

class QueueManager:
    """
    Handles the distribution of total desired passengers into 
    individual queues associated with each entry tile (ID 4). 
    
    This version uses a utility-based assignment model where each passenger 
    chooses an entry tile based on queue length and distance (Euclidean).
    
    Crucially, passengers are drawn randomly from *all* spawn points 
    to simulate simultaneous arrivals.
    """
    def __init__(self, entry_tile_positions, spawn_data):
        """
        Initializes the queue manager with a queue for each entry tile.

        :param entry_tile_positions: List of (r, c) tuples for all entry tiles (ID 4).
        :param spawn_data: Dictionary mapping stair tiles (ID 5) to their spawn count.
        """
        self.entry_tile_positions = entry_tile_positions
        self.spawn_data = spawn_data
        
        # Format: {(r, c): current_queue_length} for each entry tile
        self.queues = {pos: 0 for pos in entry_tile_positions}

        # Sum the total number of people to be spawned from all stair tiles
        self.total_passengers_to_spawn = sum(self.spawn_data.values())
        
        # Store stair positions (the spawn points for the passengers)
        self.stair_tile_positions = list(spawn_data.keys())

    def _euclidean_distance(self, pos1, pos2):
        """
        Calculates Euclidean distance (straight-line) between two (r, c) tuples.
        """
        r1, c1 = pos1
        r2, c2 = pos2
        
        distance = math.sqrt((r1 - r2)**2 + (c1 - c2)**2)
        return distance

    def distribute_passengers_utility_based(self, k_length=5.0, k_distance=20.0):
        """
        Assigns each individual passenger to an entry queue based on a simple 
        utility function, selecting the next passenger randomly from available spawn points.

        :param k_length: Weighting factor for queue length. Higher value means length is more important.
        :param k_distance: Weighting factor for distance.
        :returns: dict, {pos_key: 0} for all original spawn keys (for simulation initialization).
        """
        
        # 1. Clear existing assignments
        self.clear_queues()

        # 2. Create a working copy of spawn counts that we can decrement
        spawn_counts = self.spawn_data.copy()
        
        # 3. Create a list of all spawn tiles that still have passengers
        active_spawn_tiles = [pos for pos, count in spawn_counts.items() if count > 0]
        
        # 4. Main loop: Iterate until all passengers are assigned
        while active_spawn_tiles:
            
            # --- Randomly Select the Next Passenger's Origin ---
            # Randomly choose one of the remaining active spawn tiles
            stair_pos = random.choice(active_spawn_tiles)
            
            # This passenger makes a greedy decision based on current queue lengths
            best_entry_pos = None
            max_utility = -float('inf')

            for entry_pos in self.entry_tile_positions:
                
                # --- Utility Calculation Factors ---
                
                # 1. Queue Length (L): Use current queue length
                queue_length = self.queues[entry_pos]
                L = max(queue_length, 0.5) 
                
                # 2. Distance (D): Euclidean Distance from spawn to entry point
                D = self._euclidean_distance(stair_pos, entry_pos)
                D = max(D, 1.0) 

                # 3. Random Bias (B): A small random factor to add variety
                B = random.uniform(0.0, 0.5)

                # --- Utility Function (higher is better) ---
                utility = (k_length / L) + (k_distance / D) + B

                if utility > max_utility:
                    max_utility = utility
                    best_entry_pos = entry_pos
            
            # 5. Assign the passenger and update counts
            if best_entry_pos:
                self.queues[best_entry_pos] += 1
                spawn_counts[stair_pos] -= 1 # Decrement the count for the chosen spawn point
                
                # If the spawn point is now empty, remove it from the active list
                if spawn_counts[stair_pos] == 0:
                    active_spawn_tiles.remove(stair_pos)
        
        # 6. Return the zeroed spawn data for the main simulation loop
        return {pos: 0 for pos in self.spawn_data.keys()}

    def get_queue_lengths(self):
        """Returns the current queue lengths dictionary."""
        return self.queues

    def update_total_passengers(self, new_spawn_data):
        """Updates the internal spawn data reference and recalculates the total."""
        self.spawn_data = new_spawn_data
        self.total_passengers_to_spawn = sum(self.spawn_data.values())
        self.stair_tile_positions = list(new_spawn_data.keys()) 

    def clear_queues(self):
        """Sets the length of all queues to zero."""
        for pos in self.entry_tile_positions:
            self.queues[pos] = 0