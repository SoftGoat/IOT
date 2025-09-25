# train.py

import pygame
from config import *

class Train:
    """Represents the train and its doors, which are now dynamically sized."""
    def __init__(self, x, y, width, height, num_doors, queue_width):
        self.rect = pygame.Rect(x, y, width, height)
        self.doors = []
        self.doors_open = False
        
        # --- DYNAMIC DOOR WIDTH CALCULATION ---
        # The door width is based on how many passengers can stand in a row.
        # Add a little padding to the sides.
        dynamic_door_width = (queue_width * PASSENGER_ROW_SPACING) + 5
        
        door_spacing = width // (num_doors + 1)
        for i in range(num_doors):
            door_x = x + (i + 1) * door_spacing
            door_rect = pygame.Rect(
                door_x - dynamic_door_width // 2, 
                y + height - DOOR_HEIGHT, 
                dynamic_door_width, 
                DOOR_HEIGHT
            )
            self.doors.append(door_rect)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        for door in self.doors:
            door_color = RED if not self.doors_open else GREEN
            pygame.draw.rect(screen, door_color, door)