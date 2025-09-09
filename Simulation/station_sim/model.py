from dataclasses import dataclass
from typing import Tuple

@dataclass
class Agent:
    x: float
    y: float
    target: float  # The initial target x-coord from the spawner
    speed: float
    # --- New attributes for queueing logic ---
    queue_idx: int = -1
    state: str = 'seeking'  # seeking, queueing, boarded
    target_pos: Tuple[float, float] = None
    slot_idx: int = -1
    boarded: bool = False