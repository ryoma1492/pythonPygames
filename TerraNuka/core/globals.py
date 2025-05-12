# core/globals.py

import pygame
from .config import WIDTH
from .terrain import Terrain

# --- Runtime State ---
terrain = Terrain()
tanks = []
projectile = None

# Explosion queue and overlay timing
Pending_Explosion = None
Pending_Explosion_Next = []
Shot_Show_Timer = 0
Shot_Show_Timer_Max = 333
turn_overlay_timer = 1500
turn_overlay_start = pygame.time.get_ticks()
show_turn_overlay = True
show_game_over_overlay = False
game_over_overlay_start = 0
config_loaded = [False]  # use list for mutability across imports
fireworks = []
spawn_interval = 0
active_tank_index = 0

# --- Sounds ---
pygame.mixer.init()

menuTheme = "assets/sounds/menu_theme.mp3"
gameTheme = "assets/sounds/game_theme.mp3"

explosionSound = pygame.mixer.Sound("assets/sounds/explosion.wav")
explosionSound.set_volume(0.8)

tankExplosionSound = pygame.mixer.Sound("assets/sounds/tank_explosion.wav")
tankExplosionSound.set_volume(0.5)

shotSound = pygame.mixer.Sound("assets/sounds/shot.wav")
shotSound.set_volume(0.8)

fireworksExplosionSound = pygame.mixer.Sound("assets/sounds/fireworks_explosion.wav")
fireworksExplosionSound.set_volume(0.8)
