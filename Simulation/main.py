# main.py
import pygame
import sys
import config
from game_states.main_menu import MainMenu
from game_states.build_state import BuildState
from game_states.simulation_state import SimulationState

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.SCREEN_TITLE)
    clock = pygame.time.Clock()

    states = {
        "MAIN_MENU": MainMenu,
        "BUILD": BuildState,
        "SIMULATION": SimulationState, 
    }
    
    current_state_name = "MAIN_MENU"
    current_state = states[current_state_name]()

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        current_state.handle_events(events)
        current_state.update()
        
        if current_state.done:
            next_state_name = current_state.next_state
            current_state_name = next_state_name
            current_state = states[current_state_name]()

        current_state.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)

if __name__ == "__main__":
    main()
