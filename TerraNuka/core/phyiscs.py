# core/physics.py

import math
from .config import WIDTH, HEIGHT, bounds
from .enums import CollisionResult
from .entities import Tank

def check_projectile_collision(x: float, y: float, terrain_heights: list[int], width: int, height: int, tanks: list) -> CollisionResult:
    if x < 0 or x >= width or y >= height:
        return CollisionResult.MISS_OFFSCREEN
    if y < 0:
        return CollisionResult.MISS_OFFTOP

    terrain_x = int(x)
    if 0 <= terrain_x < len(terrain_heights):
        if y >= (bounds.y2 - terrain_heights[terrain_x]):
            return CollisionResult.HIT_TERRAIN

    for tank in tanks:
        tank_rect = pygame.Rect(tank.x, tank.y, tank.width, tank.height)
        if tank_rect.collidepoint(x, y):
            return CollisionResult.HIT_TANK

    return CollisionResult.NO_COLLISION

def apply_explosion_with_collapse(terrain_heights, x_center, y_center, radius=20):
    original_heights = terrain_heights[:]

    for dx in range(-int(radius), int(radius) + 1):
        x = int(x_center) + dx
        if 0 <= x < len(terrain_heights):
            try:
                dy = math.sqrt(radius**2 - dx**2)
            except ValueError:
                continue

            crater_y = y_center + dy
            new_height = bounds.y2 - crater_y
            terrain_heights[x] = max(0, int(min(terrain_heights[x], new_height)))

            original_height = original_heights[x]
            collapsed_space = dy
            height_diff = original_height - (terrain_heights[x] + collapsed_space)

            if height_diff > 0:
                terrain_heights[x] = min(bounds.y2, terrain_heights[x] + height_diff)

def apply_explosion_damage(tank, projectile):
    explosion_x = projectile.x
    explosion_y = projectile.y
    radius = projectile.strength
    max_damage = projectile.strength

    closest_x = max(tank.x, min(explosion_x, tank.x + tank.width))
    closest_y = max(tank.y, min(explosion_y, tank.y + tank.height))

    dx = closest_x - explosion_x
    dy = closest_y - explosion_y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance < radius:
        damage = max_damage * (1 - (distance / radius))
        tank.health -= int(damage)
        tank.health = max(0, tank.health)

def apply_gravity_to_tank(tank: Tank, terrain_heights, max_height):
    terrain_x_start = int(tank.x)
    terrain_x_end = int(tank.x + tank.width)
    max_ground_y = tank.bottomCollide()
    tank_bottom = tank.y + tank.height

    if tank_bottom < (bounds.y2 - max_ground_y):
        tank.y += 1
