# game_states/main_menu.py
import pygame
import config
from ui_elements import Button
from game_states.state import State

class MainMenu(State):
    """Class to manage the Main Menu state."""
    def __init__(self):
        super().__init__()

        # --- Load Assets ---
        image = pygame.image.load(config.BACKGROUND_IMAGE_PATH).convert()
        self.background_image = pygame.transform.scale(image, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        banner_image = pygame.image.load(config.TITLE_BANNER_PATH).convert_alpha()
        self.title_banner_image = pygame.transform.scale(banner_image, (config.TITLE_BANNER_WIDTH, config.TITLE_BANNER_HEIGHT))
        self.title_banner_rect = self.title_banner_image.get_rect(center=(config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 4))
        
        # --- Title and Buttons ---
        self.title_font = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_TITLE)
        self.title_surface = self.title_font.render(config.SCREEN_TITLE, True, config.WHITE)
        self.title_rect = self.title_surface.get_rect(center=self.title_banner_rect.center)

        button_width, button_height = 400, 150
        button_x = (config.SCREEN_WIDTH - button_width) / 2 + 50
        
        self.build_button = Button(button_x, config.SCREEN_HEIGHT/2 - 50, button_width, button_height,
         "Build Station", self.start_build_mode, config.BUTTON_NORMAL_PATH, config.BUTTON_HOVER_PATH, hit_size=(300, 65))
         
        self.sim_button = Button(button_x, config.SCREEN_HEIGHT/2 + 50, button_width, button_height,
         "Run Simulation", self.start_simulation, config.BUTTON_NORMAL_PATH, config.BUTTON_HOVER_PATH, hit_size=(300, 65))

        self.buttons = [self.build_button, self.sim_button]

    def start_build_mode(self):
        self.next_state = "BUILD"
        self.done = True

    def start_simulation(self):
        self.next_state = "SIMULATION"
        self.done = True

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self):
        for button in self.buttons:
            button.update()

    def draw(self, screen):
        screen.blit(self.background_image, (0, 0))
        screen.blit(self.title_banner_image, self.title_banner_rect)
        screen.blit(self.title_surface, self.title_rect)
        for button in self.buttons:
            button.draw(screen)
