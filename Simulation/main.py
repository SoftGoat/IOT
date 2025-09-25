# main.py

import pygame
import pygame_gui
import random
from collections import deque

from config import *
from passenger import Passenger, APPROACHING, QUEUEING
from train import Train
import passenger_logic
from queue_manager import QueueManager

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Train Dwell Time Simulation")
        self.clock = pygame.time.Clock()
        self.is_paused = False
        self.gui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.create_gui_elements()
        self.last_slider_values = {}
        self.running = True
        self.setup()

    def create_gui_elements(self):
        panel_x = SIMULATION_AREA_WIDTH + 20
        panel_width = UI_PANEL_WIDTH - 40
        start_y = 480
        
        pygame_gui.elements.UILabel(pygame.Rect((panel_x, start_y), (panel_width, 20)), "Number of Passengers", manager=self.gui_manager)
        self.passenger_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect((panel_x, start_y + 20), (panel_width-30, 20)), start_value=INITIAL_PASSENGERS, value_range=(10, 300), manager=self.gui_manager)
        self.passenger_label = pygame_gui.elements.UILabel(pygame.Rect((panel_x + panel_width - 20, start_y + 20), (40, 20)), str(INITIAL_PASSENGERS), manager=self.gui_manager)
        
        pygame_gui.elements.UILabel(pygame.Rect((panel_x, start_y + 50), (panel_width, 20)), "Number of Doors", manager=self.gui_manager)
        self.door_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect((panel_x, start_y + 70), (panel_width-30, 20)), start_value=INITIAL_DOORS, value_range=(1, 8), manager=self.gui_manager)
        self.door_label = pygame_gui.elements.UILabel(pygame.Rect((panel_x + panel_width - 20, start_y + 70), (40, 20)), str(INITIAL_DOORS), manager=self.gui_manager)
        
        pygame_gui.elements.UILabel(pygame.Rect((panel_x, start_y + 100), (panel_width, 20)), "Number of Stairs", manager=self.gui_manager)
        self.stair_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect((panel_x, start_y + 120), (panel_width-30, 20)), start_value=INITIAL_STAIRS, value_range=(1, 5), manager=self.gui_manager)
        self.stair_label = pygame_gui.elements.UILabel(pygame.Rect((panel_x + panel_width - 20, start_y + 120), (40, 20)), str(INITIAL_STAIRS), manager=self.gui_manager)
        
        pygame_gui.elements.UILabel(pygame.Rect((panel_x, start_y + 150), (panel_width, 20)), "Passengers per Row", manager=self.gui_manager)
        self.queue_width_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect((panel_x, start_y + 170), (panel_width-30, 20)), start_value=INITIAL_QUEUE_WIDTH, value_range=(1, 5), manager=self.gui_manager)
        self.queue_width_label = pygame_gui.elements.UILabel(pygame.Rect((panel_x + panel_width - 20, start_y + 170), (40, 20)), str(INITIAL_QUEUE_WIDTH), manager=self.gui_manager)

        y_pos = start_y + 200
        pygame_gui.elements.UILabel(pygame.Rect((panel_x, y_pos), (panel_width, 20)), "Boarding Time (sec/person)", manager=self.gui_manager)
        self.boarding_time_slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect((panel_x, y_pos + 20), (panel_width-40, 20)), start_value=INITIAL_BOARDING_TIME * 10, value_range=(1, 20), manager=self.gui_manager)
        self.boarding_time_label = pygame_gui.elements.UILabel(pygame.Rect((panel_x + panel_width - 30, y_pos + 20), (50, 20)), f"{INITIAL_BOARDING_TIME:.1f}s", manager=self.gui_manager)

        y_pos = start_y + 240
        self.reset_button = pygame_gui.elements.UIButton(pygame.Rect((panel_x, y_pos), (120, 40)), text='Apply & Reset', manager=self.gui_manager)
        self.pause_button = pygame_gui.elements.UIButton(pygame.Rect((panel_x + 130, y_pos), (100, 40)), text='Pause', manager=self.gui_manager)


    def setup(self):
        self.num_passengers = int(self.passenger_slider.get_current_value())
        self.num_doors = int(self.door_slider.get_current_value())
        self.num_stairs = int(self.stair_slider.get_current_value())
        self.queue_width = int(self.queue_width_slider.get_current_value())
        self.boarding_time_s = self.boarding_time_slider.get_current_value() / 10.0
        
        self.stair_positions = [(i * SIMULATION_AREA_WIDTH // (self.num_stairs + 1), STAIRS_Y) for i in range(1, self.num_stairs + 1)]
        self.passengers = []
        train_x = (SIMULATION_AREA_WIDTH - TRAIN_WIDTH) // 2
        self.train = Train(train_x, TRACK_Y, TRAIN_WIDTH, TRAIN_HEIGHT, self.num_doors, self.queue_width)
        self.queues = {i: deque() for i in range(self.num_doors)}
        self.boarding_slots = {i: [] for i in range(self.num_doors)}
        self.pre_spawn_passengers()
        self.train_state = "ARRIVED"
        self.dwell_start_time = 0
        self.dwell_time = 0
        self.total_boarded = 0
        self.is_paused = False
        self.pause_button.set_text('Pause')

        self.qm = QueueManager(self)
        self.qm.reset()

    def pre_spawn_passengers(self):
        for _ in range(self.num_passengers):
            spawn_pos = random.choice(self.stair_positions)
            chosen_door_idx = passenger_logic.choose_door_strategy(spawn_pos, self.train.doors)
            p = Passenger(spawn_pos, chosen_door_idx)
            self.passengers.append(p)

    def manage_queues_and_boarding(self):
        self.qm.step()

    def update(self):
        self.update_gui_labels()
        self.gui_manager.update(self.delta_time)
        if self.is_paused:
            return
            
        self.manage_queues_and_boarding()
        for p in self.passengers:
            p.update(self.delta_time)
            
        # --- ADDED CALL ---
        # Check every frame if boarding is complete to stop the timer automatically.
        self._check_boarding_complete()

    def draw_hud(self):
        font = pygame.font.SysFont(None, 32)
        if self.train_state == "DWELL" and not self.is_paused:
            current_dwell = (pygame.time.get_ticks() - self.dwell_start_time) / 1000.0
            time_text = f"Dwell Time: {current_dwell:.2f}s"
        elif self.train_state == "DEPARTING":
            time_text = f"Final Dwell: {self.dwell_time:.2f}s"
        else:
            time_text = "Status: Ready (SPACE)"
        waiting_count = sum(1 for p in self.passengers if p.state in [APPROACHING, QUEUEING])
        texts = [time_text, f"Waiting: {waiting_count}", f"Boarded: {self.total_boarded}/{self.num_passengers}"]
        for i, text in enumerate(texts):
            surface = font.render(text, True, WHITE)
            self.screen.blit(surface, (SIMULATION_AREA_WIDTH + 20, 10 + i * 35))

    # --- ADDED METHOD ---
    def _check_boarding_complete(self):
        """If all passengers have boarded, stop the dwell timer and close the doors."""
        if self.train_state == "DWELL" and self.total_boarded >= self.num_passengers:
            self.train.doors_open = False
            self.train_state = "DEPARTING"
            self.dwell_time = (pygame.time.get_ticks() - self.dwell_start_time) / 1000.0

    def run(self):
        while self.running:
            self.delta_time = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.reset_button:
                        self.setup()
                        self.is_paused = True
                        self.pause_button.set_text('Resume')
                    if event.ui_element == self.pause_button:
                        self.is_paused = not self.is_paused
                        self.pause_button.set_text('Resume' if self.is_paused else 'Pause')
            self.gui_manager.process_events(event)
            if event.type == pygame.KEYDOWN and not self.is_paused:
                if event.key == pygame.K_SPACE:
                    if self.train_state == "ARRIVED":
                        self.train.doors_open = True
                        self.train_state = "DWELL"
                        self.dwell_start_time = pygame.time.get_ticks()
                    # --- MODIFIED ---
                    # The logic to close doors was removed from here
                    # as it is now handled automatically by _check_boarding_complete().

    def update_gui_labels(self):
        slider_map = {
            self.passenger_slider: (self.passenger_label, 'passengers', "{:d}"),
            self.door_slider: (self.door_label, 'doors', "{:d}"),
            self.stair_slider: (self.stair_label, 'stairs', "{:d}"),
            self.queue_width_slider: (self.queue_width_label, 'queue_width', "{:d}"),
            self.boarding_time_slider: (self.boarding_time_label, 'boarding_time', "{:.1f}s")
        }
        for slider, (label, key, fmt) in slider_map.items():
            current_value = slider.get_current_value()
            last_value = self.last_slider_values.get(key)
            if current_value != last_value:
                display_value = current_value / 10.0 if key == 'boarding_time' else current_value
                label.set_text(fmt.format(display_value))
                self.last_slider_values[key] = current_value

    def draw_platform(self):
        pygame.draw.line(self.screen, YELLOW, (0, PLATFORM_Y), (SIMULATION_AREA_WIDTH, PLATFORM_Y), 5)
        for pos in self.stair_positions:
            pygame.draw.rect(self.screen, GRAY, (pos[0] - 20, pos[1] - 10, 40, 20))

    def draw(self):
        self.screen.fill(BLACK)
        panel_rect = pygame.Rect(SIMULATION_AREA_WIDTH, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, UI_PANEL_COLOR, panel_rect)
        self.draw_platform()
        self.train.draw(self.screen)
        for p in self.passengers:
            p.draw(self.screen)
        self.draw_hud()
        if self.is_paused:
            pause_font = pygame.font.SysFont(None, 100)
            pause_surface = pause_font.render("PAUSED", True, YELLOW)
            pos = pause_surface.get_rect(center=(SIMULATION_AREA_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(pause_surface, pos)
        self.gui_manager.draw_ui(self.screen)
        pygame.display.flip()

if __name__ == "__main__":
    sim = Simulation()
    sim.run()