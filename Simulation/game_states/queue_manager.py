import random
import math
import numpy as np 

# --- ⚙️ GLOBAL CALIBRATION CONSTANTS ⚙️ ---
# These are the constants that were missing.

# 2. Maximum value from the slider
MAX_WEIGHT_VALUE = 100

# 3. Scale Parameter (mu)
# THIS IS NO LONGER A GLOBAL CONSTANT. 
# It will be set by the 'rationality_factor' parameter in the function.
# MU = 1.0  <-- REMOVED

# 4. Preference Heterogeneity (Standard Deviations for theta)
# These control how much *taste variation* ($\sigma_k$) exists.
STD_DEV_DISTANCE = 0.5
STD_DEV_LENGTH = 0.5


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

    def distribute_passengers_utility_based(self, rationality_factor, k_length_ratio):
            """
            Distributes passengers based on a Mixed Logit (MIXL) model,
            inspired by "A High-Fidelity Agent-Based Framework..."
            """

            # --- ⚙️ HELPER FUNCTIONS (based on our previous code) ⚙️ ---

            def generate_agent_preferences(theta):
                """
                Draws this agent's unique $\beta_{k,n}$ from the population 
                distribution f($\beta$|$\theta$).
                """
                agent_betas = {}
                for attr, params in theta.items():
                    beta_name = f"beta_{attr}"
                    # Draw from a normal distribution defined by population mean & std_dev
                    agent_betas[beta_name] = np.random.normal(params['mean'], params['std_dev'])
                return agent_betas

            def calculate_systematic_utility(agent_preferences, choice_attributes):
                """
                Calculates the systematic utility (V_in) for one choice.
                This is the V_in = $\sum \beta_{k,n} X_{ikn}$ part of the utility function.
                """
                v_in = 0.0
                for attr, value in choice_attributes.items():
                    beta_name = f"beta_{attr}"
                    if beta_name in agent_preferences:
                        v_in += agent_preferences[beta_name] * value
                return v_in

            # --- ⚙️ CALIBRATION CONSTANTS ⚙️ ---
            
            # --- THIS IS THE FIX ---
            # Set the Scale Parameter (MU) from the slider value.
            # This 'rationality_factor' parameter controls the $\epsilon$ noise.
            scaling_exponent = (rationality_factor - 80.0) / 10.0
            scaling_factor = 2.0 ** scaling_exponent
            MU = rationality_factor * scaling_factor
            # Ensure MU is not negative if rationality_factor can be 0 or less
            MU = max(0.0, MU)
            # -----------------------

            # (Other constants are still global)

            # --- End of Constants ---

            # DEBUG PRINT STATEMENT
            # print(f"DEBUG: Using MAX_RANDOM_BIAS (slider value) = {rationality_factor}")

            # 1. Clear existing assignments
            self.clear_queues()

            # --- 2. Setup Population-Level Preference Distributions (theta) ---

            # The slider controls the MEAN preference.
            # We get the population mean $\overline{\beta}_{k}$ from the slider.
            k_ratio = max(0.0, min(MAX_WEIGHT_VALUE, k_length_ratio))  # Clamp between 0 and MAX_WEIGHT_VALUE
            print(f"DEBUG: Using k_length_ratio (slider value) = {k_ratio}")
            print(f"DEBUG: Using rationality_factor (slider value) = {MU}")

            # **CRITICAL**: Distance and Length are "costs" or "disutilities".
            # In utility theory, costs have NEGATIVE preference coefficients.
            # A higher slider value should mean agents DISLIKE it MORE.
            # So we make the mean preference NEGATIVE.
            mean_distance_cost_pref = -k_ratio
            mean_length_cost_pref = -(MAX_WEIGHT_VALUE - k_ratio)
            
            # THETA ($\theta$) is the set of parameters defining the preference distributions.
            THETA = {
                'distance': {
                    'mean': mean_distance_cost_pref,
                    'std_dev': STD_DEV_DISTANCE
                },
                'length': {
                    'mean': mean_length_cost_pref,
                    'std_dev': STD_DEV_LENGTH
                }
            }

            # --- 3. Create the list of all individual agents to process ---
            all_agents_to_spawn = []
            for stair_pos, count in self.spawn_data.items():
                for _ in range(count):
                    all_agents_to_spawn.append(stair_pos)

            random.shuffle(all_agents_to_spawn)

            agent_choices = []

            # Store the "stale" queue lengths. All agents see this same snapshot.
            # This is the "stale" information state.
            stale_queue_lengths = self.queues.copy() 

            # --- 4. Main Loop: Each agent makes a choice based on STALE info ---
            # This loop *is* the simulation of the MIXL integral.
            # Each agent is one "draw" from the f($\beta$|$\theta$) distribution.
            for stair_pos in all_agents_to_spawn:

                # --- 4a. Generate Agent-Specific Preferences (MIXL $\beta_{k,n}$) ---
                # Draw this agent's unique $\beta_{k,n}$ from the population distribution
                agent_betas = generate_agent_preferences(THETA)

                # These lists will hold the utility and corresponding choice
                choice_utilities = []
                possible_choices = []

                # --- 4b. Evaluate all choices to get V_in for each ---
                for entry_pos in self.entry_tile_positions:

                    # i. Get attributes ($X_{ikn}$) for this choice
                    distance = self._euclidean_distance(stair_pos, entry_pos) 
                    queue_length = stale_queue_lengths[entry_pos]

                    choice_attributes = {
                        'distance': distance,
                        'length': queue_length
                    }

                    # ii. Calculate Systematic Utility (V_in) for this agent
                    v_in = calculate_systematic_utility(agent_betas, choice_attributes)

                    # Store the utility and the choice
                    choice_utilities.append(v_in)
                    possible_choices.append(entry_pos)

                # --- 4c. Make a Probabilistic Choice ---
                # This is the "inner" logit formula: P_n(i) = exp($\mu$*V_in) / $\sum$exp($\mu$*V_jn)
                # We apply it to *this specific agent's* calculated utilities.

                # Multiply by scale parameter $\mu$ (which is now set by rationality_factor)
                scaled_v = np.array(choice_utilities) * MU

                # Use softmax for numerical stability (prevents overflow)
                exp_v = np.exp(scaled_v - np.max(scaled_v))

                # Get probabilities
                agent_probs = exp_v / np.sum(exp_v)

                # 4. Store the agent's (probabilistic) choice
                # The agent doesn't pick the "max" utility, they pick *based on*
                # the probabilities derived from all utilities.
                if possible_choices:
                    chosen_entry_pos = random.choices(possible_choices, weights=agent_probs, k=1)[0]
                    agent_choices.append(chosen_entry_pos)

            # --- 5. Apply all "simultaneous" choices to the queues ---
            # This simulates all agents arriving at the queues *after*
            # having made their choice based on the stale (empty) state.
            # This is the direct cause of "queue overshooting".
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