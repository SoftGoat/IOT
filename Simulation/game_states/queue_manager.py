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

    def distribute_passengers_utility_based(self, max_random_bias=10, std_dev_length=15.0, std_dev_distance=15.0):
        """
        Distributes passengers based on a Mixed Logit (MIXL) model,
        inspired by "A High-Fidelity Agent-Based Framework..."

        This model introduces two key concepts from the paper:
        
        1.  [cite_start]**Heterogeneous Preferences (MIXL):** [cite: 9, 10, 19]
            Instead of one (k_length, k_distance) for all agents, *each agent n*
            [cite_start]gets their own unique preference coefficients ($\beta_{k,n}$)[cite: 10].
            [cite_start]These are drawn from a normal distribution[cite: 11].
            
        2.  [cite_start]**Imperfect / Stale Information:** [cite: 24, 26]
            All agents make their choice based on the *initial* state of the
            queues (all empty), simulating a "decision-action lag" where
            [cite_start]agents can't see the choices of others arriving at the same time[cite: 30].
            [cite_start]This can lead to "queue overshooting"[cite: 28].

        :param max_random_bias: Slider value (0-100). Used to set the *mean*
                               population preference for distance vs. length.
        :param std_dev_length: Standard deviation for the length preference.
                               [cite_start]Controls population heterogeneity (MIXL $\sigma_{k}$)[cite: 11].
        :param std_dev_distance: Standard deviation for the distance preference.
                                 [cite_start]Controls population heterogeneity (MIXL $\sigma_{k}$)[cite: 11].
        :returns: dict, {pos_key: 0} for all original spawn keys.
        """
        
        # --- ⚙️ CALIBRATION CONSTANTS ⚙️ ---

        # The max value of the MAX_RANDOM_BIAS slider
        MAX_WEIGHT_VALUE = 100.0

        K_LENGTH_RATIO = 25.0  # The neutral midpoint value 
        
        # The minimum "floor" for preference weights to avoid zero/negative utility
        MIN_PREFERENCE_WEIGHT = 0.1
        
        # The minimum "floor" for queue length to avoid division-by-zero
        MIN_QUEUE_LENGTH_FLOOR = 0.5
        
        # The minimum "floor" for distance to avoid division-by-zero
        MIN_DISTANCE_FLOOR = 1.0
        

        
        # --- End of Constants ---

        # DEBUG PRINT STATEMENT
        print(f"DEBUG: Using MAX_RANDOM_BIAS (slider value) = {max_random_bias}")

        # 1. Clear existing assignments
        self.clear_queues()
        
        # --- Setup Population-Level Preference Distributions (MIXL) ---
        
        # The slider now controls the MEAN preference for distance
        k_ratio = max(0.0, min(MAX_WEIGHT_VALUE, K_LENGTH_RATIO))
        mean_distance_pref = k_ratio
        
        # The mean length preference is complementary
        mean_length_pref = MAX_WEIGHT_VALUE - k_ratio

        # --- Create the list of all individual agents to process ---
        # This list represents all agents who will arrive "simultaneously"
        all_agents_to_spawn = []
        for stair_pos, count in self.spawn_data.items():
            for _ in range(count):
                all_agents_to_spawn.append(stair_pos)
        
        # Shuffle the list to simulate random (non-ordered) decision-making
        random.shuffle(all_agents_to_spawn)

        # This will store the choice of each agent
        agent_choices = []
        
        # Store the "stale" queue lengths. [cite_start]All agents see this[cite: 26].
        # In this pre-simulation, all queues are initially 0.
        stale_queue_lengths = self.queues.copy() 

        # --- Main Loop: Each agent makes a choice based on STALE info ---
        for stair_pos in all_agents_to_spawn:
            
            # --- 1. Generate Agent-Specific Preferences (MIXL $\beta_{k,n}$) ---
            # [cite_start]Draw this agent's unique $\beta_{k,n}$ from the population distribution [cite: 11]
            
            k_length_n = random.normalvariate(mean_length_pref, std_dev_length)
            k_distance_n = random.normalvariate(mean_distance_pref, std_dev_distance)
            
            # Preferences can't be negative in this utility form (V = k/X)
            k_length_n = max(MIN_PREFERENCE_WEIGHT, k_length_n) 
            k_distance_n = max(MIN_PREFERENCE_WEIGHT, k_distance_n)

            best_entry_pos = None
            max_utility = -float('inf')

            for entry_pos in self.entry_tile_positions:
                
                # --- 2. Get Attributes (based on STALE info) ---
                
                # L = Queue Length (Non-Linear Attribute)
                # [cite_start]Agents see the stale_queue_lengths, not the real-time ones[cite: 26].
                queue_length = stale_queue_lengths[entry_pos] 
                L = max(queue_length, MIN_QUEUE_LENGTH_FLOOR) # Avoid divide-by-zero
                
                # D = Distance (Attribute)
                D = self._euclidean_distance(stair_pos, entry_pos)
                D = max(D, MIN_DISTANCE_FLOOR) # Avoid divide-by-zero

                # [cite_start]B = Random error term ($\epsilon_{in}$ from the paper's formula) [cite: 13]
                B = random.uniform(0.0, max_random_bias)

                # --- 3. Utility Function (MIXL specification) ---
                # [cite_start]U_in = $\beta_{L,n} \cdot X_{L} + \beta_{D,n} \cdot X_{D} + \epsilon_{in}$ [cite: 13]
                # [cite_start]We use X_L = (1/L) and X_D = (1/D) to model non-linear disutility [cite: 43, 44]
                
                utility_length = k_length_n * (1.0 / L)
                utility_distance = k_distance_n * (1.0 / D)
                
                utility = utility_length + utility_distance + B

                if utility > max_utility:
                    max_utility = utility
                    best_entry_pos = entry_pos
            
            # 4. Store the agent's choice
            if best_entry_pos:
                agent_choices.append(best_entry_pos)
        
        # --- 5. Apply all "simultaneous" choices to the queues ---
        # This simulates all agents arriving at the queues *after*
        # [cite_start]having made their choice based on the stale (empty) state[cite: 30, 31].
        for pos in agent_choices:
            self.queues[pos] += 1
        
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