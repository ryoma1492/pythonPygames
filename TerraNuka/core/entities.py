# core/entities.py


if __name__ == "__main__":
    raise RuntimeError("This module is not meant to be run directly.")

import math
import random
import pygame
from dataclasses import dataclass, field
from collections import defaultdict 

from core.config import bounds
from core.enums import CollisionResult


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    active: bool = True
    strength: int = 10

@dataclass
class Tank:
    height: float
    width: float
    x: float
    y: float = field(init=False)
    cannonRelX: float = 0
    cannonRelY: float = 0
    cannonLen: float = 20
    name: str = "Player"
    color: tuple[int, int, int] = (200, 200, 0)
    cannonColor: tuple[int, int, int] = (255, 0, 0)
    cannonPower: float = 30
    aimAngle: float = 45
    health: float = 100
    max_health: float = 100
    strength: float = 15
    explosionStrength: float = 70
    fuel: float = 0.5
    active: bool = True
    money: int = 100
    inventory: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def bottomCollide(self):
        from .globals import terrain  # lazy import to avoid circular dependency
        return max(terrain.heightMap[int(self.x) + n] for n in range(self.width))

    def aim(self, direction: str):
        if direction == "left":
            self.aimAngle = min(180, self.aimAngle + 1)
        elif direction == "right":
            self.aimAngle = max(0, self.aimAngle - 1)

    def move(self, direction: str):
        self.fuel -= 0.001
        self.x += 0.1 if direction == "Right" else -0.1
        self.y = bounds.y2 - self.height - self.bottomCollide()

    def fire(self, shot_speed: float) -> Projectile:
        rad = math.radians(self.aimAngle)
        shot_speed = shot_speed / 2.4
        return Projectile(
            x=self.x + math.cos(rad) * self.cannonLen,
            y=self.y - math.sin(rad) * self.cannonLen,
            vx=shot_speed * math.cos(rad),
            vy=-shot_speed * math.sin(rad),
            strength=self.strength
        )

    def explode(self):
        from .globals import tankExplosionSound, Pending_Explosion_Next
        tankExplosionSound.play()
        Pending_Explosion_Next.append((
            self.x + self.width // 2,
            self.y + self.height // 2,
            self.explosionStrength * (self.fuel + 0.7),
            600,
            self
        ))

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: int
    color: pygame.Color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05
        self.life -= 1
        self.color.a = max(0, self.life * 3)

    def draw(self, surf):
        if self.life > 0:
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, self.color, (2, 2), 2)
            surf.blit(s, (self.x - 2, self.y - 2))

@dataclass
class Firework:
    x: int
    y: int
    target_y: int
    trail: list = field(default_factory=list)
    exploded: bool = False
    particles: list = field(default_factory=list)
    color: pygame.Color = field(default_factory=lambda: pygame.Color(0))

    def __post_init__(self):
        hue = random.randint(0, 360)
        self.color.hsva = (hue, 100, 100, 100)

    def update(self):
        if not self.exploded:
            self.y -= 5
            if len(self.trail) == 0 or abs(self.trail[-1][1] - self.y) > 5:
                self.trail.append((self.x, self.y))
            if self.y <= self.target_y:
                self.explode()
        else:
            for p in self.particles:
                p.update()

    def explode(self):
        from .globals import fireworksExplosionSound
        self.exploded = True
        fireworksExplosionSound.play()
        for _ in range(40):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed / 3
            vy = math.sin(angle) * speed / 3
            particle_color = pygame.Color(self.color.r, self.color.g, self.color.b, self.color.a)
            particle_color.a = 255
            self.particles.append(Particle(self.x, self.y, vx, vy, 85, particle_color))

    def draw(self, surf):
        if not self.exploded:
            for pos in self.trail:
                pygame.draw.circle(surf, (255, 255, 255), pos, 2)
            pygame.draw.circle(surf, (255, 255, 255), (self.x, self.y), 3)
        else:
            for p in self.particles:
                p.draw(surf)
