# core/enums.py

if __name__ == "__main__":
    raise RuntimeError("This module is not meant to be run directly.")


from enum import Enum, auto

class CollisionResult(Enum):
    MISS_OFFSCREEN = auto()
    MISS_OFFTOP = auto()
    HIT_TERRAIN = auto()
    HIT_TANK = auto()
    NO_COLLISION = auto()

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
