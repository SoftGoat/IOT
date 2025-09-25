# passenger.py

import pygame
import random
from config import PASSENGER_RADIUS, GREEN, BLUE, YELLOW, RED

# Passenger States - defined here as the single source of truth
APPROACHING = "APPROACHING"
QUEUEING    = "QUEUEING"
BOARDING    = "BOARDING"
BOARDED     = "BOARDED"

class Passenger:
    """Represents a single passenger agent with steering-based movement."""
    def __init__(self, pos, target_door_idx):
        self.pos = pygame.math.Vector2(pos)
        self.target_door = target_door_idx
        self.target_pos = pygame.math.Vector2(pos)
        self.state = APPROACHING

        # --- Steering Behavior Physics ---
        self.velocity = pygame.math.Vector2(0, 0)
        self.max_speed = random.uniform(80.0, 100.0) # Using the faster speed from last time
        self.max_force = random.uniform(1.5, 2.5)

        # --- MODIFIED LINE: Increased the arrival radius ---
        # Used for arrival checks. Changed from 10*10 to a more generous 15*15.
        self.arrival_threshold_sq = 15 * 15
        # --- END MODIFICATION ---

        self.color_map = {
            APPROACHING: BLUE,
            QUEUEING: YELLOW,
            BOARDING: GREEN,
            BOARDED: RED
        }

    def set_target_position(self, target_vec):
        self.target_pos = pygame.math.Vector2(target_vec)

    def update(self, dt):
        """Updates passenger position using steering behaviors. Requires delta_time (dt)."""
        if self.state == BOARDED or dt == 0:
            return

        dist_sq = self.pos.distance_squared_to(self.target_pos)

        if dist_sq > 1: # Only move if not already at target
            # --- Steering Logic (No changes here) ---
            desired_velocity = self.target_pos - self.pos
            if desired_velocity.length() < 100.0:
                desired_velocity.scale_to_length(self.max_speed * (desired_velocity.length() / 100.0))
            else:
                desired_velocity.scale_to_length(self.max_speed)

            steer = desired_velocity - self.velocity
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)

            self.velocity += steer
            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)

            self.pos += self.velocity * dt

        # --- ADDED: Check for boarding completion ---
        # After moving, check if a boarding passenger has reached their final destination.
        if self.state == BOARDING:
            # The target for boarding is just inside the train (y-coordinate is smaller).
            # We check if they have reached or passed that target.
            if self.pos.y < self.target_pos.y + 5: # Add a 5-pixel margin for safety
                self.state = BOARDED
        # --- END OF ADDITION --

    def draw(self, screen):
        color = self.color_map.get(self.state, RED)
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), PASSENGER_RADIUS)

    @property
    def speed_sq(self):
        """Legacy property for arrival checks in queue_manager."""
        return self.arrival_threshold_sq