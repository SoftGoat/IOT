# queue_manager.py

import random

class QueueManager:
    """
    Handles the distribution of total desired passengers into 
    individual queues associated with each entry tile (ID 4).
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

    def initialize_queues_uniform(self):
        """
        Distributes all passengers uniformly across all entry tiles.
        The remainder is distributed randomly to achieve different results 
        on each run, while maintaining the overall uniformity.
        """
        if not self.entry_tile_positions:
            return self.queues

        num_entries = len(self.entry_tile_positions)
        
        # 1. Calculate base passengers
        base_passengers = self.total_passengers_to_spawn // num_entries
        remainder = self.total_passengers_to_spawn % num_entries

        # 2. Assign base passengers to all queues
        for pos in self.entry_tile_positions:
            self.queues[pos] = base_passengers
            
        # 3. Distribute remainder randomly
        
        # Create a shuffled list of positions to assign the extra remainder passengers to
        # We slice [:] to create a shallow copy to shuffle, keeping the original intact.
        shuffled_positions = self.entry_tile_positions[:] 
        random.shuffle(shuffled_positions)
        
        # Assign the 'remainder' passengers to the first 'remainder' number of shuffled positions
        for i in range(remainder):
            pos = shuffled_positions[i]
            self.queues[pos] += 1

        return self.queues

    def get_queue_lengths(self):
        """Returns the current queue lengths dictionary."""
        return self.queues

    def update_total_passengers(self, new_spawn_data):
        """Updates the internal spawn data reference and recalculates the total."""
        self.spawn_data = new_spawn_data
        self.total_passengers_to_spawn = sum(self.spawn_data.values())



    def clear_queues(self):
        """Sets the length of all queues to zero."""
        for pos in self.entry_tile_positions:
            self.queues[pos] = 0

    # In queue_manager.py, add this method:
    def distribute_passengers_and_get_zeros(self):
        """
        1. Distributes total passengers uniformly into queues.
        2. Returns a dictionary of the same keys as self.spawn_data, but with values set to 0.
        
        :returns: dict, {pos_key: 0} for all original spawn keys.
        """
        
        # 1. Distribute passengers (updates self.queues randomly)
        self.initialize_queues_uniform()
        
        # 2. Prepare the zeroed spawn data dictionary to be returned
        zeroed_spawn_data = {pos: 0 for pos in self.spawn_data.keys()}
        
        return zeroed_spawn_data