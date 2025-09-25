# queue_manager.py
# Optimized queue + boarding logic with timed door access.

from collections import defaultdict
import pygame
from config import QUEUE_SPACING, PASSENGER_ROW_SPACING
from passenger import APPROACHING, QUEUEING, BOARDING, BOARDED

TARGET_ASSIGNMENT_INTERVAL_MS = 150

def slot_to_xy(door_center, queue_width, row, col):
    half = (queue_width - 1) / 2.0
    x = door_center[0] + (col - half) * PASSENGER_ROW_SPACING
    y = door_center[1] + (row + 1) * QUEUE_SPACING
    return pygame.math.Vector2(x, y)

class QueueManager:
    def __init__(self, sim):
        self.sim = sim
        self.reserved_slot = {}
        self.claimed_cols_frame = defaultdict(set)
        self.last_target_assignment_time = 0
        self.reservations_per_door = defaultdict(int)
        self.reserved_cols_by_door = defaultdict(lambda: defaultdict(set))
        
        # --- ADDED: Timer to track when a door becomes free ---
        self.door_free_time = {} # door_idx -> timestamp

    def reset(self):
        self.reserved_slot.clear()
        self.claimed_cols_frame.clear()
        self.last_target_assignment_time = 0
        self.reservations_per_door.clear()
        self.reserved_cols_by_door.clear()
        
        # --- ADDED: Reset door timers ---
        self.door_free_time.clear()

    def step(self):
        self.claimed_cols_frame.clear()
        now = pygame.time.get_ticks()
        if now - self.last_target_assignment_time > TARGET_ASSIGNMENT_INTERVAL_MS:
            self._assign_targets_for_approachers()
            self.last_target_assignment_time = now
        self._check_approacher_arrivals()
        self._snap_queue_grid()
        self._board_from_front()

    def _assign_targets_for_approachers(self):
        # This function is unchanged
        sim = self.sim
        for p in sim.passengers:
            if p.state != APPROACHING or p in self.reserved_slot:
                continue
            door_idx = p.target_door
            door_center = sim.train.doors[door_idx].center
            q = sim.queues[door_idx]
            width = sim.queue_width
            reserved_count = self.reservations_per_door[door_idx]
            total_queue_len = len(q) + reserved_count
            back_row = total_queue_len // width
            occupied_in_deque = {i % width for i in range(back_row * width, len(q))}
            occupied_by_reservations = self.reserved_cols_by_door[door_idx][back_row]
            occupied_this_frame = self.claimed_cols_frame[(door_idx, back_row)]
            occupied_cols = occupied_in_deque | occupied_by_reservations | occupied_this_frame
            open_cols = [c for c in range(width) if c not in occupied_cols]
            if not open_cols:
                back_row += 1
                open_cols = list(range(width))
            targets = [(col, slot_to_xy(door_center, width, back_row, col)) for col in open_cols]
            if targets:
                best_col, best_tgt = min(targets, key=lambda ct: p.pos.distance_squared_to(ct[1]))
                self.claimed_cols_frame[(door_idx, back_row)].add(best_col)
                self.reserved_slot[p] = (door_idx, back_row, best_col)
                self.reservations_per_door[door_idx] += 1
                self.reserved_cols_by_door[door_idx][back_row].add(best_col)
                p.set_target_position(best_tgt)

    def _check_approacher_arrivals(self):
        # This function is unchanged
        sim = self.sim
        arrived_passengers = []
        for p in list(self.reserved_slot.keys()):
            if p.state == APPROACHING and p.pos.distance_squared_to(p.target_pos) < p.speed_sq:
                door_idx, _, _ = self.reserved_slot[p]
                p.state = QUEUEING
                sim.queues[door_idx].append(p)
                arrived_passengers.append(p)
        for p in arrived_passengers:
            if p in self.reserved_slot:
                door_idx, row, col = self.reserved_slot.pop(p)
                self.reservations_per_door[door_idx] -= 1
                self.reserved_cols_by_door[door_idx][row].discard(col)

    def _snap_queue_grid(self):
        # This function is unchanged
        sim = self.sim
        for door_idx, q in sim.queues.items():
            door_center = sim.train.doors[door_idx].center
            width = sim.queue_width
            for idx, qpass in enumerate(q):
                row = idx // width
                col = idx % width
                qpass.set_target_position(slot_to_xy(door_center, width, row, col))

    def _board_from_front(self):
        """
        Board ONE passenger per available door, then set a timer on that door.
        The door will not accept another passenger until the timer expires.
        """
        sim = self.sim
        if not sim.train.doors_open:
            return

        now = pygame.time.get_ticks()
        boarding_time_ms = sim.boarding_time_s * 1000

        for door_idx in range(sim.num_doors):
            # Check if this door is currently busy
            if now < self.door_free_time.get(door_idx, 0):
                continue # Skip to the next door

            q = sim.queues[door_idx]
            door_center = sim.train.doors[door_idx].center

            # Find the first passenger in the front row who is ready
            front = list(q)[:sim.queue_width]
            ready_passengers = [p for p in front if p.pos.distance_squared_to(p.target_pos) < p.speed_sq]

            if ready_passengers:
                # Get the first ready passenger
                p_to_board = ready_passengers[0]

                # Start their boarding process
                if p_to_board in q: q.remove(p_to_board)
                sim.boarding_slots[door_idx].append(p_to_board)
                p_to_board.state = BOARDING
                p_to_board.set_target_position(pygame.math.Vector2(p_to_board.pos.x, door_center[1] - 20))

                # --- IMPORTANT: Set the timer to make this door busy ---
                self.door_free_time[door_idx] = now + boarding_time_ms
        
        # Cleanup logic (unchanged)
        for door_idx in range(sim.num_doors):
            done = [p for p in sim.boarding_slots[door_idx] if p.state == BOARDED]
            for p in done:
                sim.total_boarded += 1
                if p in sim.passengers: sim.passengers.remove(p)
                if p in sim.boarding_slots[door_idx]: sim.boarding_slots[door_idx].remove(p)