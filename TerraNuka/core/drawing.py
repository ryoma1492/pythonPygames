# core/drawing.py


if __name__ == "__main__":
    raise RuntimeError("This module is not meant to be run directly.")

import math
import pygame

from .config import WIDTH, HEIGHT
from .entities import Tank

def draw_health_bar(screen, tank: Tank, bar_width=30, bar_height=6):
    health_ratio = tank.health / tank.max_health
    x = tank.x + tank.width // 2 - bar_width // 2
    y = tank.y - 38

    pygame.draw.rect(screen, (80, 80, 80), (x, y, bar_width, bar_height))
    fill_width = int(bar_width * health_ratio)
    pygame.draw.rect(screen, (0, 255, 0), (x, y, fill_width, bar_height))
    pygame.draw.rect(screen, (180, 180, 180), (x - 1, y - 1, bar_width + 1, bar_height + 1), 1)

def draw_outlined_text(screen, text, font, x, y, main_color, outline_color=(255, 255, 255), outline_thickness=2):
    base = font.render(text, True, main_color)
    for dx in [-outline_thickness, 0, outline_thickness]:
        for dy in [-outline_thickness, 0, outline_thickness]:
            if dx != 0 or dy != 0:
                outline = font.render(text, True, outline_color)
                screen.blit(outline, (x + dx, y + dy))
                screen.blit(base, (x, y))

def draw_explosion_preview(screen, x_center, y_center, weapon_type):
    from .globals import explosionSound
    explosionSound.play()
    preview_color = (255, 50, 50)
    alpha_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(alpha_surface, (*preview_color, 128), (x_center, y_center), weapon_type.explosion_radius)
    screen.blit(alpha_surface, (0, 0))
    pygame.display.flip()

def draw_hud(screen, tank: Tank, hud_height=100):
    pygame.draw.rect(screen, (20, 20, 20), (0, HEIGHT - hud_height, WIDTH, hud_height))

    pygame.draw.rect(screen, (200, 200, 200), (0, HEIGHT - hud_height - 10, WIDTH, 10))  # Top HUD border
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, WIDTH, 5))  # Top border
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, 5, HEIGHT))  # Left border
    pygame.draw.rect(screen, (200, 200, 200), (WIDTH - 5, 0, 5, HEIGHT))  # Right border

    base_font_size = 22
    max_name_length = 20
    font_size = max(10, base_font_size - max(0, len(tank.name) - 8))

    font = pygame.font.SysFont("consolas", font_size)
    font.set_bold(True)
    player_label = font.render(tank.name, True, tuple(255 - c for c in tank.color))
    font.set_bold(False)

    pygame.draw.rect(screen, tank.color, (20, HEIGHT - hud_height + 10, 150, 30))
    screen.blit(player_label, (25, HEIGHT - hud_height + 15))

    font = pygame.font.SysFont("consolas", 22)

    angle_center = (240, HEIGHT - hud_height + 50)
    angle_radius = 40
    pygame.draw.arc(screen, (255, 255, 255),
                    (angle_center[0] - angle_radius, angle_center[1] - angle_radius,
                     angle_radius * 2, angle_radius * 2),
                    math.radians(0), math.radians(180), 3)

    angle_rad = math.radians(tank.aimAngle)
    angle_x = angle_center[0] + angle_radius * math.cos(angle_rad)
    angle_y = angle_center[1] - angle_radius * math.sin(angle_rad)
    pygame.draw.line(screen, (255, 0, 0), angle_center, (angle_x, angle_y), 3)
    angle_label = font.render(f"{tank.aimAngle}°", True, (220, 220, 220))
    screen.blit(angle_label, (angle_center[0] - 40, angle_center[1] + 5))

    fuel_bar_width = 120
    fuel_bar_height = 20
    fuel_bar_x = 340
    fuel_bar_y = HEIGHT - hud_height + 40
    fuel_level = tank.fuel
    pygame.draw.rect(screen, (255, 255, 255), (fuel_bar_x, fuel_bar_y, fuel_bar_width, fuel_bar_height), 2)
    fill_width = int(fuel_bar_width * fuel_level)
    pygame.draw.rect(screen, (255, 0, 0), (fuel_bar_x, fuel_bar_y, fill_width, fuel_bar_height))
    fuel_label = font.render("FUEL", True, (220, 220, 220))
    screen.blit(fuel_label, (fuel_bar_x + fuel_bar_width // 2 - 50, fuel_bar_y - 25))

    missile_label = font.render("MISSILE", True, (255, 255, 255))
    missile_type = font.render(tank.current_weapon_str, True, (255, 255, 255))
    pygame.draw.rect(screen, (50, 50, 50), (555, HEIGHT - hud_height + 10, 200, 60))
    pygame.draw.rect(screen, (200, 200, 200), (555, HEIGHT - hud_height + 10, 200, 60), 3)
    screen.blit(missile_label, (565, HEIGHT - hud_height + 15))
    screen.blit(missile_type, (565, HEIGHT - hud_height + 40))

    power = tank.cannonPower / 100.0
    triangle_width = 100
    triangle_max_height = 20
    current_width = int(triangle_width * power)
    current_height = int(triangle_max_height * power)

    triangle_x = 820
    triangle_y = HEIGHT - hud_height + 40

    base_left = (triangle_x, triangle_y)
    base_right = (triangle_x + triangle_width, triangle_y)
    top_right = (triangle_x + triangle_width, triangle_y - triangle_max_height)
    pygame.draw.polygon(screen, (255, 255, 255), [base_left, base_right, top_right], 2)

    point1 = (triangle_x, triangle_y)
    point2 = (triangle_x + current_width, triangle_y)
    point3 = (triangle_x + current_width, triangle_y - current_height)
    pygame.draw.polygon(screen, (255, 255, 0), [point1, point2, point3])

    power_label = font.render("POWER", True, (255, 255, 255))
    screen.blit(power_label, (triangle_x, triangle_y + 10))
