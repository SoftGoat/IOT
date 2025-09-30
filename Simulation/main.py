# main.py

import pygame
import sys
import config
from game_states import MainMenu, BuildState

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.SCREEN_TITLE)
    clock = pygame.time.Clock()

    # Dictionary to hold the state CLASSES
    states = {
        "MAIN_MENU": MainMenu,
        "BUILD": BuildState,
        # "SIMULATION": SimulationState # We will add this later
    }
    
    # Start with the name of the first state
    current_state_name = "MAIN_MENU"
    # Create an INSTANCE of the first state
    current_state = states[current_state_name]()

    # Main game loop
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        current_state.handle_events(events)
        current_state.update()
        
        # --- NEW: More efficient state transition logic ---
        if current_state.done:
            next_state_name = current_state.next_state
            
            # Switch to the new state name
            current_state_name = next_state_name
            # Create a new instance of the new state CLASS
            current_state = states[current_state_name]()

        current_state.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

if __name__ == "__main__":
    main()