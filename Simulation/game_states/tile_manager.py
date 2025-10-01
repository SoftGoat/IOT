# game_states/tile_manager.py
import pygame
import config
from pathlib import Path
from dialog import LoadDialog, SaveDialog

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))


class TileManager:
    def __init__(self, tile_mapping: dict):
        self.tile_images = {}    # id -> Surface
        self.sprites = pygame.sprite.Group()
        self._load_and_scale(tile_mapping)




    def _load_and_scale(self, tile_mapping):
        for tid, path in tile_mapping.items():
            surf = pygame.image.load(path).convert_alpha()
            surf = pygame.transform.scale(surf, (config.TILE_SIZE, config.TILE_SIZE))
            self.tile_images[tid] = surf

    def create_all(self, grid_data):
        """Populate sprites group from 2D grid_data."""
        self.sprites.empty()
        for row_idx, row in enumerate(grid_data):
            for col_idx, tid in enumerate(row):
                self._add_tile_sprite(tid, col_idx, row_idx)

    def _add_tile_sprite(self, tile_id, col, row):
        img = self.tile_images.get(tile_id)
        if img is None: 
            # fallback: empty transparent surface
            img = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE), pygame.SRCALPHA)
        x, y = col * config.TILE_SIZE, row * config.TILE_SIZE
        self.sprites.add(Tile(img, x, y))

    def update_tile(self, old_tid, new_tid, col, row):
        """Replace single sprite at (row, col). Keeps other sprites intact."""
        # Remove existing sprite at that rect (cheap linear scan; OK for medium grids)
        target_rect = pygame.Rect(col * config.TILE_SIZE, row * config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE)
        for spr in list(self.sprites):   # list() to avoid runtime mutation issues
            if spr.rect.topleft == target_rect.topleft:
                self.sprites.remove(spr)
                break
        self._add_tile_sprite(new_tid, col, row)

class TileButton:
    """An image-based button for the tile palette in the build mode."""
    def __init__(self, x, y, size, tile_id, tile_image, callback):
        self.rect = pygame.Rect(x, y, size, size)
        self.tile_id = tile_id
        self.image = tile_image
        self.callback = callback

    def handle_event(self, event):
        """Checks if the tile button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback(self.tile_id) # Calls the function with the tile_id

    def draw(self, screen, is_selected):
        """Draws the tile button."""
        # Draw the tile image
        screen.blit(self.image, self.rect.topleft)

        # Draw a highlight border if this tile is selected
        if is_selected:
            pygame.draw.rect(screen, config.WHITE, self.rect, 3) # 3 is the border thickness