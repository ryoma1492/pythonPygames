# main.py

import pygame
import sys
import tkinter as tk
import random
import math

from core import globals as g
from core.config import WIDTH, HEIGHT, FPS, bounds
from core.enums import GameState, CollisionResult
from core.entities import Firework
from core.terrain import Terrain
from core.config_ui import GameConfigUI, load_game_config
from core.physics import (
    apply_gravity_to_tank,
    check_projectile_collision,
    apply_explosion_damage,
    apply_explosion_with_collapse,
)
from core.inventory import cycle_weapon
from core.drawing import (
    draw_hud,
    draw_health_bar,
    draw_outlined_text,
    draw_explosion_preview,
)

# --- Initialize ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scorched Earth Prototype")
clock = pygame.time.Clock()

# --- Main loop ---
running = True
current_state = GameState.MENU

while running:
    if current_state == GameState.MENU:
        pygame.mixer.music.load(g.menuTheme)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        root = tk.Tk()
        GameConfigUI(root)
        root.mainloop()
        current_state = GameState.PLAYING

    elif current_state in (GameState.PLAYING, GameState.GAME_OVER):
        if not g.config_loaded:
            g.config_loaded = load_game_config()
            pygame.mixer.music.fadeout(1000)
            pygame.mixer.music.load(g.gameTheme)
            pygame.mixer.music.set_volume(0.12)
            pygame.mixer.music.play(-1)

        screen.fill((30, 30, 30))
        dt = clock.tick(FPS) / 1000
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        def get_active_tank():
            last_index = (len(g.tanks) + g.active_tank_index - 1) % len(g.tanks)
            while not g.tanks[last_index].active:
                last_index = (last_index - 1) % len(g.tanks)
                if last_index == g.active_tank_index:
                    return None, g.active_tank_index, True

            next_index = g.active_tank_index
            while not g.tanks[next_index].active:
                next_index = (next_index + 1) % len(g.tanks)
                if next_index == last_index:
                    return g.tanks[next_index], next_index, True
            return g.tanks[next_index], next_index, False

        tank, g.active_tank_index, game_over = get_active_tank()
        if game_over:
            current_state = GameState.GAME_OVER

        # --- Input ---
        if current_state == GameState.PLAYING:
            for event in events:
                if event.type == pygame.KEYDOWN and g.projectile is None:
                    if event.key == pygame.K_SPACE:
                        g.shotSound.play()
                        g.projectile = tank.fire(tank.cannonPower)
                    elif event.key == pygame.K_RSHIFT:
                        cycle_weapon(tank, direction=1)
                    elif event.key == pygame.K_SLASH:
                        cycle_weapon(tank, direction=-1)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                tank.aim("left")
            if keys[pygame.K_RIGHT]:
                tank.aim("right")
            if keys[pygame.K_UP]:
                tank.cannonPower = min(100, tank.cannonPower + 0.1)
            if keys[pygame.K_DOWN]:
                tank.cannonPower = max(0, tank.cannonPower - 0.1)
            if keys[pygame.K_RCTRL] and tank.fuel > 0:
                tank.move("Right")
            if keys[pygame.K_RALT] and tank.fuel > 0:
                tank.move("Left")

        elif current_state == GameState.GAME_OVER:
            spawn_timer = 120
            check_interval = pygame.time.get_ticks() - g.turn_overlay_start - g.spawn_interval
            if check_interval > spawn_timer:
                g.fireworks.append(Firework(
                    x=random.randint(100, WIDTH - 100),
                    y=HEIGHT,
                    target_y=random.randint(100, HEIGHT // 2),
                ))
                g.spawn_interval += check_interval + spawn_timer

            for fw in g.fireworks[:]:
                fw.update()
                fw.draw(screen)
                if fw.exploded and all(p.life <= 0 for p in fw.particles):
                    g.fireworks.remove(fw)

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    g.fireworks.append(Firework(
                        x=random.randint(100, WIDTH - 100),
                        y=HEIGHT,
                        target_y=random.randint(100, HEIGHT // 2),
                    ))

        # --- Terrain drawing ---
        terrain_coords = [(0, bounds.y2)]
        for x in range(WIDTH):
            terrain_coords.append((x, bounds.y2 - g.terrain.heightMap[x]))
        terrain_coords.append((WIDTH - 1, bounds.y2))
        pygame.draw.polygon(screen, g.terrain.color, terrain_coords)

        # --- Tank updates & drawing ---
        for tank in [t for t in g.tanks if t.active]:
            apply_gravity_to_tank(tank, g.terrain.heightMap, bounds.y2)
            pygame.draw.rect(screen, tank.color, (tank.x, tank.y, tank.width, tank.height))
            aim_rad = math.radians(tank.aimAngle)
            line_end = (
                tank.x + math.cos(aim_rad) * tank.cannonLen,
                tank.y - math.sin(aim_rad) * tank.cannonLen
            )
            pygame.draw.line(screen, tank.cannonColor, (tank.x, tank.y), line_end, 3)
            draw_health_bar(screen, tank)

        # --- Projectile updates ---
        if g.projectile:
            if g.projectile.x == tank.x and g.projectile.y == tank.y:
                g.projectile.x = line_end[0]
                g.projectile.y = line_end[1]

            steps = int(max(abs(g.projectile.vx), abs(g.projectile.vy), 1))
            for _ in range(steps):
                g.projectile.x += g.projectile.vx / steps
                g.projectile.y += g.projectile.vy / steps
                result = check_projectile_collision(
                    g.projectile.x, g.projectile.y, g.terrain.heightMap, WIDTH, HEIGHT, g.tanks
                )
                if result != CollisionResult.NO_COLLISION:
                    break
            g.projectile.vy += g.GRAVITY

        def next_turn():
            g.turn_overlay_start = pygame.time.get_ticks()
            g.active_tank_index = (g.active_tank_index + 1) % len(g.tanks)
            g.show_turn_overlay = True

        if g.projectile:
            collision = check_projectile_collision(
                g.projectile.x, g.projectile.y, g.terrain.heightMap, WIDTH, HEIGHT, [tank]
            )
            match collision:
                case CollisionResult.HIT_TERRAIN | CollisionResult.HIT_TANK:
                    draw_explosion_preview(screen, g.projectile.x, g.projectile.y, g.projectile.type)
                    g.Shot_Show_Timer = 0
                    g.Pending_Explosion = (
                        int(g.projectile.x), int(g.projectile.y), g.projectile.type,
                        g.Shot_Show_Timer_Max, None
                    )
                    for t in g.tanks:
                        apply_explosion_damage(t, g.projectile)
                        if t.health <= 0 and t.active:
                            t.explode()
                    g.projectile = None
                    next_turn()
                case CollisionResult.MISS_OFFSCREEN:
                    g.projectile = None
                    next_turn()

        if g.Pending_Explosion:
            impact_x, impact_y, weapon_type, anim_timer, origin = g.Pending_Explosion
            draw_explosion_preview(screen, impact_x, impact_y, weapon_type)
            g.Shot_Show_Timer += clock.get_time()
            if g.Shot_Show_Timer >= anim_timer:
                apply_explosion_with_collapse(g.terrain.heightMap, impact_x, impact_y, weapon_type)
                g.Shot_Show_Timer = 0
                if origin:
                    origin.active = False
                g.Pending_Explosion = (
                    None if not g.Pending_Explosion_Next
                    else g.Pending_Explosion_Next.pop(0)
                )

        if g.projectile:
            pygame.draw.circle(screen, (255, 255, 255), (int(g.projectile.x), int(g.projectile.y)), 4)

        draw_hud(screen, g.tanks[g.active_tank_index])

        if game_over and not g.show_turn_overlay and not g.show_game_over_overlay:
            g.show_game_over_overlay = True
            g.game_over_overlay_start = pygame.time.get_ticks()

        if g.show_turn_overlay:
            elapsed = pygame.time.get_ticks() - g.turn_overlay_start
            if elapsed > g.turn_overlay_timer:
                g.show_turn_overlay = False
            else:
                fade = max(0, 255 - int((elapsed / g.turn_overlay_timer) * 255))
                overlay_color = (*g.tanks[g.active_tank_index].color, fade)
                font_overlay = pygame.font.SysFont(None, 48)
                draw_outlined_text(screen, g.tanks[g.active_tank_index].name, font_overlay, WIDTH // 2 - 100, 60, overlay_color)

        if g.show_game_over_overlay:
            elapsed = pygame.time.get_ticks() - g.game_over_overlay_start
            fade = max(0, 255 - int((elapsed / 5000) * 255))
            overlay_color = (*g.tanks[g.active_tank_index].color, fade)
            font_overlay = pygame.font.SysFont(None, 64)
            draw_outlined_text(screen, f"{g.tanks[g.active_tank_index].name} wins!", font_overlay, WIDTH // 3 - 40, 60, overlay_color)
            if elapsed > 5000:
                g.tanks.clear()
                g.terrain = Terrain()
                current_state = GameState.MENU
                g.config_loaded = False

        pygame.display.flip()

pygame.quit()
