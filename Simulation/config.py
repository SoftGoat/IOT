# config.py

import pygame

# --- Screen Layout ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
UI_PANEL_WIDTH = 300 # Increased from 270
SIMULATION_AREA_WIDTH = SCREEN_WIDTH - UI_PANEL_WIDTH

# --- Simulation Parameters ---
FPS = 60

# --- Default Values for Sliders ---
INITIAL_PASSENGERS = 80
INITIAL_DOORS = 4
INITIAL_STAIRS = 3
INITIAL_QUEUE_WIDTH = 1

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
UI_PANEL_COLOR = (35, 35, 45)

# --- Layout Positions ---
TRACK_Y = 100
TRAIN_HEIGHT = 80
PLATFORM_Y = TRACK_Y + TRAIN_HEIGHT + 5
STAIRS_Y = SCREEN_HEIGHT - 100

# Train and Door visual properties
TRAIN_WIDTH = 850 # Reduced to fit in the new smaller sim area
DOOR_HEIGHT = 10

# Passenger
PASSENGER_RADIUS = 5
PASSENGER_SPEED = 1.5
PASSENGER_ROW_SPACING = 15

# Queuing
QUEUE_SPACING = 20



# --- Default Values for Sliders ---
INITIAL_PASSENGERS = 80
INITIAL_DOORS = 4
INITIAL_STAIRS = 3
INITIAL_QUEUE_WIDTH = 1
INITIAL_BOARDING_TIME = 0.5 # Added: default time in seconds