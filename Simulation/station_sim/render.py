import pygame
from .config import LENGTH_M, PLAT_Y0, PLAT_Y1, SAFETY_Y, AGENT_RADIUS, QUEUE_SLOT_COLOR, DOOR_COLOR_OPEN, DOOR_COLOR_CLOSED
from .layout import BENCHES, KIOSK, STAIRS, OBSTACLES
import math # Make sure this import is at the top of the file

class Fonts:
    def __init__(self):
        self.s = pygame.font.SysFont(None, 18)
        self.m = pygame.font.SysFont(None, 24)
        self.l = pygame.font.SysFont(None, 28)

def draw_layout(surface, mapper, door_x, boarding_allowed):
    # This function now correctly takes only one surface and draws everything on it.
    
    # Fill the background of the provided surface
    surface.fill((230,230,230)) # Platform color acts as the base

    # Tracks (drawn first, at the bottom)
    pygame.draw.rect(surface, (70,70,70), mapper.rect_m(0, -1.2, LENGTH_M, 1.2))
    
    # Safety line
    pygame.draw.line(surface, (235,180,40), mapper.sxy(0, SAFETY_Y), mapper.sxy(LENGTH_M, SAFETY_Y), 3)

    # Base part of the train doors (static red part)
    for x in door_x:
        pygame.draw.rect(surface, (190,40,40), mapper.rect_m(x-0.5, 0, 1.0, 0.8))

    # Color-changing part of the doors (green or red indicator)
    door_color = DOOR_COLOR_OPEN if boarding_allowed else DOOR_COLOR_CLOSED
    door_w_m, door_h_m = 1.0, 1.2
    for x_m in door_x:
        rect_m = (x_m - door_w_m / 2, -door_h_m / 2, door_w_m, door_h_m)
        door_rect_px = mapper.rect_m(*rect_m)
        pygame.draw.rect(surface, door_color, door_rect_px)

    # Obstacles
    for ob in OBSTACLES:
        if ob in BENCHES: col = (90, 90, 95)
        elif ob in STAIRS: col = (60,110,180)
        else: col = (120,120,120)
        pygame.draw.rect(surface, col, mapper.rect_m(ob["x"], ob["y"], ob["w"], ob["h"]))

def draw_agents(surface, mapper, agents):
    # Changed parameter name from 'screen' to 'surface' for consistency
    for a in agents:
        if a.boarded: 
            continue
        x, y = mapper.sxy(a.x, a.y)
        pygame.draw.circle(surface, (30,120,255), (x, y), int(AGENT_RADIUS * mapper.SX) + 1)

def draw_heatmap(surface, mapper, agents):
    # Changed parameter name from 'screen' to 'surface' for consistency
    grid_rows = 10
    grid_cols = 20
    grid = [[0]*grid_cols for _ in range(grid_rows)]
    for a in agents:
        if a.boarded: continue
        gx = int(a.x / (LENGTH_M / grid_cols))
        gy = int((a.y - PLAT_Y0) / ((PLAT_Y1 - PLAT_Y0) / grid_rows))
        if 0 <= gx < grid_cols and 0 <= gy < grid_rows:
            grid[gy][gx] += 1
    
    for gy in range(grid_rows):
        for gx in range(grid_cols):
            c = grid[gy][gx]
            if c == 0: 
                continue
            alpha = min(200, c * 20)
            rect = mapper.rect_m(gx * LENGTH_M / grid_cols,
                                 PLAT_Y0 + gy * (PLAT_Y1 - PLAT_Y0) / grid_rows,
                                 LENGTH_M / grid_cols,
                                 (PLAT_Y1 - PLAT_Y0) / grid_rows)
            if rect.width <= 0 or rect.height <= 0:
                continue
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            s.fill((255, 50, 50, alpha))
            surface.blit(s, rect.topleft)

def draw_stats(screen, fonts: Fonts, t, boarded, total, fps, avg_queue):
    text = f"t={t:5.1f}s   boarded {boarded}/{total}   remaining {total-boarded}   FPS {fps:4.0f}   Avg Queue: {avg_queue:.1f}"
    label_shadow = fonts.m.render(text, True, (20,20,20))
    label = fonts.m.render(text, True, (255,255,255))
    screen.blit(label_shadow, (14, 44))
    screen.blit(label, (13, 43))

def draw_title(screen, fonts: Fonts, title="Train Station — Pygame UI | Space: pause  R: reset  Esc/Q: quit"):
    screen.blit(fonts.l.render(title, True, (235,235,235)), (12, 10))



def draw_queue_slots(surface, mapper, queue_slots):
    """Draws a single rectangle for each slot in the queue grid."""
    aspect_ratio = 4.0
    height_m = math.sqrt(1.2 * math.pi / aspect_ratio) * AGENT_RADIUS
    width_m = aspect_ratio * height_m

    # Iterate through the new grid data structure from simulation.py
    for door_grid in queue_slots:
        for row_of_slots in door_grid:
            for slot_center_m in row_of_slots:
                # slot_center_m is now the precise (x,y) coordinate for a single marker
                
                # Calculate the bottom-left corner for the rect_m function
                x_m = slot_center_m[0] - (width_m / 2)
                y_m = slot_center_m[1] - (height_m / 2)

                # Use the mapper to create the pygame.Rect in pixels
                slot_rect_px = mapper.rect_m(x_m, y_m, width_m, height_m)
                
                # Draw the final rectangle
                pygame.draw.rect(surface, QUEUE_SLOT_COLOR, slot_rect_px, width=1, border_radius=3)








