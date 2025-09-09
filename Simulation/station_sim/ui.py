import pygame
from .config import UI_W

class Slider:
    def __init__(self, rect, min_v, max_v, value, step=1.0, integer=False, label="", font=None):
        self.rect = pygame.Rect(rect)
        self.min_v, self.max_v = min_v, max_v
        self.value = float(value)
        self.step = step
        self.integer = integer
        self.label = label
        self.dragging = False
        self.font = font

    def handle(self, event, local_pos=None):
        if local_pos is None:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(local_pos):
            self.dragging = True
            self._update_from_mouse(local_pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_from_mouse(local_pos[0])

    def _update_from_mouse(self, mx):
        x0, x1 = self.rect.x + 12, self.rect.right - 12
        t = 0.0 if x1 == x0 else (mx - x0) / (x1 - x0)
        t = max(0.0, min(1.0, t))
        val = self.min_v + t * (self.max_v - self.min_v)
        if self.integer:
            val = int(round(val / self.step) * self.step)
        else:
            val = round(val / self.step) * self.step
        self.value = max(self.min_v, min(self.max_v, val))

    def draw(self, surf, font_m, font_s):
        surf.blit(font_m.render(self.label, True, (240,240,240)), (self.rect.x, self.rect.y - 22))
        pygame.draw.rect(surf, (60,64,72), self.rect, border_radius=8)
        t = (self.value - self.min_v) / (self.max_v - self.min_v + 1e-9)
        x0 = self.rect.x + 12
        x1 = int(self.rect.x + 12 + t * (self.rect.width - 24))
        pygame.draw.rect(surf, (90,140,240), (x0, self.rect.y + self.rect.height//2 - 4, x1 - x0, 8), border_radius=4)
        knob_x = x1
        pygame.draw.circle(surf, (220,220,230), (knob_x, self.rect.y + self.rect.height//2), 9)
        pygame.draw.circle(surf, (40,60,120), (knob_x, self.rect.y + self.rect.height//2), 9, 2)
        val_str = f"{int(self.value)}" if self.integer else f"{self.value:.2f}"
        surf.blit(font_m.render(val_str, True, (220,220,220)), (self.rect.right - 70, self.rect.y - 22))

class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.down = False
        self.clicked = False

    def handle(self, event, local_pos=None):
        if local_pos is None:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(local_pos):
            self.down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.down and self.rect.collidepoint(local_pos):
                self.clicked = True
            self.down = False

    def draw(self, surf, font_m):
        col = (80,120,210) if self.down else (70,100,180)
        pygame.draw.rect(surf, col, self.rect, border_radius=8)
        pygame.draw.rect(surf, (30,50,90), self.rect, 2, border_radius=8)

        # shrink-to-fit with ellipsis
        max_w = self.rect.width - 16
        text = self.text
        if font_m.size(text)[0] > max_w:
            # try trimming and add …
            trimmed = text
            while trimmed and font_m.size(trimmed + "…")[0] > max_w:
                trimmed = trimmed[:-1]
            text = (trimmed + "…") if trimmed else "…"

        label = font_m.render(text, True, (245,245,245))

        # clip drawing to the button rect so nothing spills over
        prev_clip = surf.get_clip()
        surf.set_clip(self.rect)
        surf.blit(label, label.get_rect(center=self.rect.center))
        surf.set_clip(prev_clip)

def build_ui(font_l, font_m, font_s, width=UI_W, height=620):
    panel = pygame.Surface((width, height))
    panel.fill((28, 30, 36))
    pygame.draw.rect(panel, (40, 43, 50), pygame.Rect(0, 0, width, height), 2)

    y = 18
    panel.blit(font_l.render("Controls", True, (240,240,240)), (16, y)); y += 36

    sliders = []
    sliders.append(Slider(pygame.Rect(16, y + 26, width - 32, 26),  50, 800, 240, step=10, integer=True, label="Passengers")); y += 70
    sliders.append(Slider(pygame.Rect(16, y + 26, width - 32, 26),   1, 12,   6, step=1,  integer=True, label="Doors")); y += 70
    sliders.append(Slider(pygame.Rect(16, y + 26, width - 32, 26), 0.5, 2.5, 1.2, step=0.05, integer=False, label="Speed (m/s)")); y += 70
    sliders.append(Slider(pygame.Rect(16, y + 26, width - 32, 26), 0.5, 4.0, 1.6, step=0.05, integer=False, label="Board rate (pax/s/door)")); y += 70

    third = (width - 64)//3
    btn_pause = Button(pygame.Rect(16, y, third, 38), "Pause")
    btn_apply = Button(pygame.Rect(16 + third + 16, y, third, 38), "Apply")
    btn_reset = Button(pygame.Rect(16 + 2*(third + 16), y, third, 38), "Reset")

    y += 54
    panel.blit(font_s.render("Tip: Space pauses, R resets.", True, (200,200,200)), (16, y))

    return panel, sliders, btn_pause, btn_apply, btn_reset
