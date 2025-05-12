# core/terrain.py


if __name__ == "__main__":
    raise RuntimeError("This module is not meant to be run directly.")

import random
from dataclasses import dataclass, field
from noise import pnoise1

from .config import WIDTH

@dataclass
class Terrain:
    heightMap: list[int] = field(init=False)
    color: tuple[int, int, int] = field(init=False)
    seed: int = random.randint(0, 100000)
    max_height: int = 540
    min_height: int = 10
    scale = 360
    octaves = 3

    def __post_init__(self):
        self.heightMap = self.generate_terrain()
        self.color = (40, 180, 0)  # Default color

    def scramble_seed(self, seed: int) -> int:
        seed ^= (seed << 13) & 0xFFFFFFFF
        seed ^= (seed >> 17)
        seed ^= (seed << 5) & 0xFFFFFFFF
        return seed

    def generate_terrain(self):
        if self.seed is None:
            self.seed = random.randint(-49999, 50000)
        scrambled = self.scramble_seed(self.seed)
        offset = ((scrambled // 1000) % 100) / 10.0
        octaves = 4 + (scrambled % 6)

        tempTerrain = []
        for x in range(WIDTH):
            noise_val = pnoise1((x + offset) / self.scale + self.seed, octaves=octaves)
            tempTerrain.append(noise_val)

        min_val = min(tempTerrain)
        max_val = max(tempTerrain)
        val_range = max_val - min_val if max_val != min_val else 1

        terrain = []
        for raw in tempTerrain:
            normalized = (raw - min_val) / val_range
            height = int(self.min_height + normalized * (self.max_height - self.min_height))
            terrain.append(height)

        return terrain
