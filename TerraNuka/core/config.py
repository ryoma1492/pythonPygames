# core/config.py

if __name__ == "__main__":
    raise RuntimeError("This module is not meant to be run directly.")


import random
from dataclasses import dataclass, field

# --- Global Constants ---
WIDTH, HEIGHT = 1000, 720
FPS = 60
GRAVITY = 0.5

@dataclass
class Bounds:
    x1: int
    x2: int
    y1: int
    y2: int

# Define screen bounds for gameplay area
bounds = Bounds(5, WIDTH - 5, 5, HEIGHT - 105)

@dataclass
class GameConfig:
    player_count: int = 2
    player_colors: list[tuple[int, int, int]] = field(default_factory=lambda: [(255, 255, 0), (0, 255, 255)])
    terrain_bounds: tuple[int, int] = (10, 540)
    terrain_seed: int = random.randint(0, 10000)
    tank_explosion_radius: float = 70
    tank_health: float = 100
    tank_fuel_start: float = 0.5
    tank_strength: float = 15
