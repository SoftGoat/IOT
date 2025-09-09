import pygame
from .config import SIM_W, H, LENGTH_M, Y_MIN, Y_MAX

class ScreenMapper:
    def __init__(self, sim_w_px=SIM_W, h_px=H, length_m=LENGTH_M, y_min=Y_MIN, y_max=Y_MAX):
        self.sim_w = sim_w_px
        self.h = h_px
        self.length_m = length_m
        self.y_min = y_min
        self.y_max = y_max
        self.SX = self.sim_w / self.length_m
        self.SY = self.h / (self.y_max - self.y_min)

    def sxy(self, xm, ym):
        return int(xm * self.SX), int((self.y_max - ym) * self.SY)

    def rect_m(self, x, y, w, h) -> pygame.Rect:
        px, py = self.sxy(x, y + h)
        px2, py2 = self.sxy(x + w, y)
        return pygame.Rect(px, py, px2 - px, py2 - py)
