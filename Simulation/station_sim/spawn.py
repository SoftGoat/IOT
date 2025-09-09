import random
from .model import Agent
from .layout import STAIRS

def spawn_agents(n, door_x, mean_speed):
    agents = []
    for _ in range(n):
        entry = random.choice(STAIRS)
        x = random.uniform(entry["x"], entry["x"] + entry["w"])
        y = random.uniform(entry["y"], entry["y"] + entry["h"])
        target = min(door_x, key=lambda d: abs(d - x)) if door_x else x
        speed = max(0.4, random.gauss(mean_speed, mean_speed * 0.15))
        agents.append(Agent(x, y, target, speed))
    return agents
