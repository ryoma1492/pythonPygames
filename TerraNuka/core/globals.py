# core/globals.py

if __name__ == "__main__":
    import sys
    print("This module is not meant to be run directly.", file=sys.stderr)
    sys.exit(0)



import pygame
from core.config import WIDTH, HEIGHT, GRAVITY, FPS
from core.terrain import Terrain

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
config_loaded = False
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



# --- searchable weapons for dict ---
ALL_WEAPONS = ["Baby Missile", "Missile", "Baby Nuke", "Nuke",  # etc.
"Leap Frog","Funky Bomb","MIRV","Death's Head", "Napalm",
"Hot Napalm","Tracer","Smoke Tracer", "Baby Roller", 
"Roller","Heavy Roller", "Riot Charge", "Riot Blast", 
"Riot Bomb","Heavy Riot Bomb","Baby Digger", "Digger",
"Heavy Digger","Baby Sandhog","Sandhog","Heavy Sandhog",
"Dirt Clod","Dirt Ball","Ton of Dirt","Liquid Dirt",
"Dirt Charge","Earth Disrupter","Plasma Blast","Laser"]
