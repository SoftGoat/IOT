# passenger_logic.py

import pygame
import random

def choose_door_strategy(spawn_pos, doors):
    """
    Determines which door a passenger will walk towards.
    Passengers are more likely to choose closer doors.
    """
    distances = [pygame.math.Vector2(door.center).distance_to(spawn_pos) for door in doors]
    # Use squared distance to heavily weight closer doors
    weights = [1 / ((d + 1e-6) ** 2) for d in distances]
    chosen_door_idx = random.choices(range(len(doors)), weights=weights, k=1)[0]
    return chosen_door_idx

# The update_passenger_state function has been removed as this logic
# now resides in the Passenger.update() method for better object-orientation.