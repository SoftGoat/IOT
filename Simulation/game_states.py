# game_states.py

import pygame
import config
import os
from ui_elements import Button

# A simple sprite class for our tiles
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

class MainMenu:
    """Class to manage the Main Menu state."""
    def __init__(self):
        self.done = False
        self.next_state = None

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

        button_width, button_height = 400, 80
        button_x = (config.SCREEN_WIDTH - button_width) / 2
        
        self.build_button = Button(button_x, config.SCREEN_HEIGHT/2 - 50, button_width, button_height, "Build Station", self.start_build_mode)
        self.sim_button = Button(button_x, config.SCREEN_HEIGHT/2 + 50, button_width, button_height, "Run Simulation", self.start_simulation)
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

# In game_states.py

# ... (Tile and MainMenu classes are unchanged) ...
from ui_elements import TileButton # Add TileButton to imports
import json # <-- Make sure to import the json library at the top of the file

# In game_states.py

class BuildState:
    """Class to manage the Build Mode state."""
    def __init__(self):
        self.done = False
        self.next_state = None
        self.selected_tile_id = 1
        self.hovered_grid_pos = None
        self.save_message_timer = 0

        # --- NEW: More robust loading logic ---
        try:
            # First, try to load the user's saved file
            with open(config.USER_LAYOUT_PATH, 'r') as f:
                data = json.load(f)
                self.grid_data = data["layout"]
                print(f"Loaded station from {config.USER_LAYOUT_PATH}")
        except FileNotFoundError:
            try:
                # If that fails, try to load the default empty layout
                with open(config.DEFAULT_LAYOUT_PATH, 'r') as f:
                    data = json.load(f)
                    self.grid_data = data["layout"]
                    print(f"Loaded default station from {config.DEFAULT_LAYOUT_PATH}")
            except FileNotFoundError:
                # If both fail, create an empty grid and save it as the new default
                print(f"No default layout found. Creating a new one at {config.DEFAULT_LAYOUT_PATH}")
                self.grid_data = [[0 for _ in range(config.GRID_WIDTH_TILES)] for _ in range(config.GRID_HEIGHT_TILES)]
                
                # Ensure the 'layouts' directory exists
                os.makedirs(os.path.dirname(config.DEFAULT_LAYOUT_PATH), exist_ok=True)
                
                # Save the new empty grid as the default
                with open(config.DEFAULT_LAYOUT_PATH, 'w') as f:
                    json.dump({"layout": self.grid_data}, f, indent=4)


        # --- The rest of __init__ is the same ---
        self.tile_images = {id: pygame.image.load(path).convert_alpha() for id, path in config.TILE_MAPPING.items()}
        for id, image in self.tile_images.items():
            self.tile_images[id] = pygame.transform.scale(image, (config.TILE_SIZE, config.TILE_SIZE))
        self.tile_sprites = pygame.sprite.Group()
        self._create_sprites_from_grid_data()

        self.palette_buttons = []
        palette_x, palette_y = config.SCREEN_WIDTH - 220, 50
        palette_button_size = config.TILE_SIZE
        for tile_id, tile_image in self.tile_images.items():
            if tile_id > 0:
                button = TileButton(palette_x, palette_y, palette_button_size, tile_id, tile_image, self.select_tile)
                self.palette_buttons.append(button)
                palette_y += palette_button_size + 10
        
        self.ui_font = pygame.font.Font(config.FONT_NAME, config.FONT_SIZE_UI)
        self.explanation_surfaces = []
        self._update_explanation_text()

    # The _create_sprites..., select_tile, and _update_explanation... methods are unchanged.
    def _create_sprites_from_grid_data(self):
        self.tile_sprites.empty()
        for row_idx, row in enumerate(self.grid_data):
            for col_idx, tile_id in enumerate(row):
                x, y = col_idx * config.TILE_SIZE, row_idx * config.TILE_SIZE
                tile_image = self.tile_images[tile_id]
                self.tile_sprites.add(Tile(tile_image, x, y))

    def select_tile(self, tile_id):
        self.selected_tile_id = tile_id
        self._update_explanation_text()
        print(f"Selected tile ID: {self.selected_tile_id}")
        
    def _update_explanation_text(self):
        self.explanation_surfaces.clear(); text = config.TILE_EXPLANATIONS.get(self.selected_tile_id, ""); words, lines, current_line = text.split(' '), [], ""; max_width = 220
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if self.ui_font.size(test_line)[0] < max_width: current_line = test_line
            else: lines.append(current_line); current_line = word
        lines.append(current_line)
        for line in lines: self.explanation_surfaces.append(self.ui_font.render(line, True, config.WHITE))

    # --- UPDATED: Method to save to the user's station file ---
    def save_to_json(self):
        """Saves the current grid_data to the user's station file."""
        data_to_save = {"layout": self.grid_data}
        # Ensure the 'layouts' directory exists
        os.makedirs(os.path.dirname(config.USER_LAYOUT_PATH), exist_ok=True)
        with open(config.USER_LAYOUT_PATH, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Station saved to {config.USER_LAYOUT_PATH}")
        self.save_message_timer = 120

    # The handle_events, update, and draw methods are unchanged
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.next_state = "MAIN_MENU"; self.done = True
                if event.key == pygame.K_s: self.save_to_json()
            for button in self.palette_buttons: button.handle_event(event)
    
    def update(self):
        if self.save_message_timer > 0: self.save_message_timer -= 1
        mouse_x, mouse_y = pygame.mouse.get_pos(); grid_col, grid_row = mouse_x // config.TILE_SIZE, mouse_y // config.TILE_SIZE
        is_in_grid = 0 <= grid_col < config.GRID_WIDTH_TILES and 0 <= grid_row < config.GRID_HEIGHT_TILES
        is_in_palette = mouse_x > config.SCREEN_WIDTH - 250
        self.hovered_grid_pos = (grid_row, grid_col) if is_in_grid and not is_in_palette else None
        if self.hovered_grid_pos:
            row, col = self.hovered_grid_pos
            if pygame.mouse.get_pressed()[0]:
                if self.grid_data[row][col] != self.selected_tile_id: self.grid_data[row][col] = self.selected_tile_id; self._create_sprites_from_grid_data()
            if pygame.mouse.get_pressed()[2]:
                if self.grid_data[row][col] != 0: self.grid_data[row][col] = 0; self._create_sprites_from_grid_data()

    def draw(self, screen):
        screen.fill(config.BLACK); self.tile_sprites.draw(screen)
        for x in range(0, config.GRID_WIDTH_TILES * config.TILE_SIZE + 1, config.TILE_SIZE): pygame.draw.line(screen, config.GRID_LINE_COLOR, (x, 0), (x, config.SCREEN_HEIGHT))
        for y in range(0, config.GRID_HEIGHT_TILES * config.TILE_SIZE + 1, config.TILE_SIZE): pygame.draw.line(screen, config.GRID_LINE_COLOR, (0, y), (config.SCREEN_WIDTH, y))
        if self.hovered_grid_pos:
            row, col = self.hovered_grid_pos; x, y = col * config.TILE_SIZE, row * config.TILE_SIZE
            ghost_image = self.tile_images[self.selected_tile_id].copy(); ghost_image.set_alpha(150); screen.blit(ghost_image, (x, y))
        palette_bg = pygame.Surface((250, config.SCREEN_HEIGHT)); palette_bg.set_alpha(128); palette_bg.fill(config.BLACK)
        screen.blit(palette_bg, (config.SCREEN_WIDTH - 250, 0))
        for button in self.palette_buttons:
            is_selected = button.tile_id == self.selected_tile_id; button.draw(screen, is_selected)
        explanation_y_start = 400
        for i, surface in enumerate(self.explanation_surfaces):
            y = explanation_y_start + (i * (config.FONT_SIZE_UI + 5)); screen.blit(surface, (config.SCREEN_WIDTH - 240, y))
        font = pygame.font.Font(config.FONT_NAME, 30); text_surf = font.render("BUILD MODE (Press 'S' to Save, ESC to Return)", True, config.WHITE)
        screen.blit(text_surf, (20, config.SCREEN_HEIGHT - 50))
        if self.save_message_timer > 0:
            save_font = pygame.font.Font(config.FONT_NAME, 50); save_surf = save_font.render("Station Saved!", True, config.WHITE)
            save_rect = save_surf.get_rect(center=(config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2)); screen.blit(save_surf, save_rect)