# game_states/state.py
from abc import ABC, abstractmethod

class State(ABC):
    """
    Abstract Base Class for all game states (Main Menu, Build, Simulation).
    Subclasses must implement all methods marked with @abstractmethod.
    """
    
    def __init__(self):
        # Mandatory attributes for the state machine loop in main.py
        self.done = False
        self.next_state = None

    @abstractmethod
    def handle_events(self, events):
        """Handle user input (mouse clicks, key presses). Must be implemented."""
        pass # The 'pass' is okay here because @abstractmethod handles the enforcement

    @abstractmethod
    def update(self):
        """Update game logic (position, movement, time). Must be implemented."""
        pass

    @abstractmethod
    def draw(self, screen):
        """Draw elements to the screen. Must be implemented."""
        pass