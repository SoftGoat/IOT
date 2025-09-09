import pygame
from .config import LENGTH_M, PLAT_Y0, PLAT_Y1, SAFETY_Y, AGENT_RADIUS
from .layout import BENCHES, KIOSK, STAIRS, OBSTACLES

class Fonts:
    def __init__(self):
        self.s = pygame.font.SysFont(None, 18)
        self.m = pygame.font.SysFont(None, 24)
        self.l = pygame.font.SysFont(None, 28)

def draw_layout(screen, mapper, door_x):
    screen.fill((18, 20, 24), pygame.Rect(0, 0, screen.get_width(), screen.get_height()))
    # tracks
    pygame.draw.rect(screen, (70,70,70), mapper.rect_m(0, -1.2, LENGTH_M, 1.2))
    # platform
    pygame.draw.rect(screen, (230,230,230), mapper.rect_m(0, PLAT_Y0, LENGTH_M, PLAT_Y1-PLAT_Y0))
    # safety line
    pygame.draw.line(screen, (235,180,40), mapper.sxy(0, SAFETY_Y), mapper.sxy(LENGTH_M, SAFETY_Y), 3)
    # train band
    pygame.draw.rect(screen, (190,190,190), mapper.rect_m(0, 0, LENGTH_M, 0.8))
    # doors
    for x in door_x:
        pygame.draw.rect(screen, (190,40,40), mapper.rect_m(x-0.5, 0, 1.0, 0.8))
    # obstacles
    for ob in OBSTACLES:
        if ob in BENCHES: col = (90, 90, 95)
        elif ob in STAIRS: col = (60,110,180)
        else: col = (120,120,120)
        pygame.draw.rect(screen, col, mapper.rect_m(ob["x"], ob["y"], ob["w"], ob["h"]))

def draw_agents(screen, mapper, agents):
    for a in agents:
        if a.boarded: 
            continue
        x, y = mapper.sxy(a.x, a.y)
        pygame.draw.circle(screen, (30,120,255), (x, y), int(AGENT_RADIUS * mapper.SX) + 1)

def draw_heatmap(screen, mapper, agents):
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
            s = pygame.Surface((1,1), pygame.SRCALPHA)
            rect = mapper.rect_m(gx * LENGTH_M / grid_cols,
                                 PLAT_Y0 + gy * (PLAT_Y1 - PLAT_Y0) / grid_rows,
                                 LENGTH_M / grid_cols,
                                 (PLAT_Y1 - PLAT_Y0) / grid_rows)
            if rect.width <= 0 or rect.height <= 0:
                continue
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            s.fill((255, 50, 50, alpha))
            screen.blit(s, rect.topleft)

def draw_stats(screen, fonts: Fonts, t, boarded, total, fps, avg_queue):
    text = f"t={t:5.1f}s   boarded {boarded}/{total}   remaining {total-boarded}   FPS {fps:4.0f}   Avg Queue: {avg_queue:.1f}"
    label_shadow = fonts.m.render(text, True, (20,20,20))
    label = fonts.m.render(text, True, (255,255,255))
    screen.blit(label_shadow, (14, 44))
    screen.blit(label, (13, 43))

def draw_title(screen, fonts: Fonts, title="Train Station — Pygame UI | Space: pause  R: reset  Esc/Q: quit"):
    screen.blit(fonts.l.render(title, True, (235,235,235)), (12, 10))
