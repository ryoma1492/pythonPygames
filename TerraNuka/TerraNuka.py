import pygame
import math
from enum import Enum, auto
from dataclasses import dataclass, field
from noise import pnoise1
import random
import tkinter as tk
from tkinter import colorchooser




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


@dataclass
class Bounds:
    x1: int
    x2: int
    y1: int
    y2: int

@dataclass
class Terrain:
    heightMap: list[int] = field(init=False)
    color: tuple[int, int, int] = field(init=False)
    seed: int = random.randint(0, 10000)
    max_height: int = 540
    min_height: int = 10
    scale=360
    octaves=3
    def __post_init__(self):
        self.heightMap = self.generate_terrain()
        self.color = (40, 180, 0)  # Default color
    def generate_terrain(self):
        if self.seed is None:
            self.seed = random.randint(0, 10000)
        tempTerrain = []

        # Step 1: Collect raw noise values
        for x in range(WIDTH):
            noise_val = pnoise1(x / self.scale + self.seed, octaves=self.octaves)
            tempTerrain.append(noise_val)

        # Step 2: Find the actual min and max of the noise
        min_val = min(tempTerrain)
        max_val = max(tempTerrain)
        val_range = max_val - min_val if max_val != min_val else 1  # avoid divide by zero

        # Step 3: Normalize to 0-1 based on actual range, then scale to min/max height
        terrain = []
        for raw in tempTerrain:
            normalized = (raw - min_val) / val_range
            height = int(self.min_height + normalized * (self.max_height - self.min_height))
            terrain.append(height)

        return terrain

@dataclass
class Tank:    
    height: float
    width: float
    cannonRelX: float
    cannonRelY: float
    cannonLen: float
    x: float
    y: float
    name: str = "Player"
    color: tuple[int, int, int] = (200, 200, 0)
    cannonColor: tuple[int, int, int] = (255, 0, 0)
    cannonPower: float = 30
    aimAngle: float = 45
    health: float = 100
    max_health: float = 100
    strength: float = 15
    explosionStrength: float = 70
    fuel: float = .5
    active: bool = True    
    def bottomCollide(self):
        return max(terrain.heightMap[int(self.x) + n] for n in range(self.width))
    def aim(self, direction: str):
        """Adjust the aim angle of the tank."""
        if direction == "left":
            self.aimAngle = min(180, self.aimAngle + 1)
        elif direction == "right":
            self.aimAngle = max(0, self.aimAngle - 1)
    def move(self, direction: str):
        self.fuel -= 0.001
        self.x += .1 if direction == "Right" else -.1
        self.y = bounds.y2 - self.height - self.bottomCollide()
    def fire(self, shot_speed: float) -> "Projectile":
        """Fire a projectile from the tank."""
        rad = math.radians(self.aimAngle)
        shot_speed = shot_speed/2.4
        return Projectile(
            x=self.x + math.cos(rad) * self.cannonLen,
            y=self.y - math.sin(rad) * self.cannonLen,
            vx=shot_speed * math.cos(rad),
            vy=-shot_speed * math.sin(rad),
            strength=self.strength
        )
    def explode(self):
        Pending_Explosion_Next.append((self.x + self.width // 2, self.y + self.height // 2, self.explosionStrength * (self.fuel+.7), 600, self))

    
@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    active: bool = True  # Optional default so you can deactivate on collision
    strength: int = 10

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


current_state = GameState.MENU


# --- Constants ---
WIDTH, HEIGHT = 1000, 720
bounds = Bounds(5, WIDTH - 5, 5, HEIGHT - 105)
FPS = 60
GRAVITY = 0.5
Shot_Show_Timer = 0
Shot_Show_Timer_Max = 333  # in milliseconds
Pending_Explosion = None  # will store (x, y, radius, timer)
Pending_Explosion_Next = []  # will store [] of (x, y, radius, timer)
turn_overlay_timer = 1500  # milliseconds
turn_overlay_start = pygame.time.get_ticks()
show_turn_overlay = True


# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scorched Earth Prototype")
clock = pygame.time.Clock()

# --- Terrain initialize ---
terrain = Terrain()
terrain.color = (40, 180, 0) # hopefully medium green with a tinge of yellow

# --- Tank state ---
tanks = []
tanks.append(Tank(height=12, width=24, cannonRelX=4, cannonRelY=0, cannonLen=20, x=WIDTH // 4, y=bounds.y2-20, aimAngle=45, name="Player 1", color=(255, 255, 0), cannonColor=(255, 0, 180)))
tanks[0].y = bounds.y2 - tanks[0].height - tanks[0].bottomCollide()
tanks.append(Tank(height=12, width=24, cannonRelX=4, cannonRelY=0, cannonLen=20, x=WIDTH // 4 + 200, y=bounds.y2-20, aimAngle=45, name="Player 2", color=(100, 40, 255), cannonColor=(255, 0, 0)))
tanks[1].y = bounds.y2 - tanks[1].height - tanks[1].bottomCollide()
projectile = None  # Will be a dict when active

# --- Helper Functions ---
def check_projectile_collision(x: float, y: float, terrain_heights: list[int], width: int, height: int, tanks: list) -> CollisionResult:
    if x < 0 or x >= width or y >= height:
        return CollisionResult.MISS_OFFSCREEN

    if y < 0:
        return CollisionResult.MISS_OFFTOP  # Still in flight

    # Check collision with terrain
    terrain_x = int(x)
    if 0 <= terrain_x < len(terrain_heights):
        if y >= (bounds.y2 - terrain_heights[terrain_x]):
            return CollisionResult.HIT_TERRAIN

    # Check collision with any tank
    for tank in tanks:
        tank_rect = pygame.Rect(tank.x, tank.y, tank.width, tank.height)
        if tank_rect.collidepoint(x, y):
            return CollisionResult.HIT_TANK

    return CollisionResult.NO_COLLISION
# Original function for reference
def check_projectile_collision_orig(x: float, y: float, terrain_heights: list[int], width: int, height: int) -> CollisionResult:
    if x < 0 or x >= width or y >= height:
        return CollisionResult.MISS_OFFSCREEN

    if y < 0:
        return CollisionResult.MISS_OFFTOP  # Still in flight

    terrain_x = int(x)
    if 0 <= terrain_x < len(terrain_heights):
        if y >= (bounds.y2 - terrain_heights[terrain_x]):
            return CollisionResult.HIT_TERRAIN

    return CollisionResult.NO_COLLISION

def apply_explosion_with_wipe(terrain_heights, x_center, y_center, radius=20):
    # Step 1: Remove terrain within the explosion circle
    for dx in range(-radius, radius + 1):
        x = x_center + dx
        if 0 <= x < len(terrain_heights):
            dy = math.sqrt(radius**2 - dx**2)
            blast_bottom_y = y_center + dy  # Bottom edge of the circle

            # Convert blast bottom to terrain height from bounds
            crater_height = bounds.y2 - blast_bottom_y

            # Remove terrain within the blast
            if terrain_heights[x] > crater_height:
                terrain_heights[x] = crater_height

    # Step 2: Collapse terrain "above" the removed chunk (falling sand)
    for x in range(max(0, x_center - radius), min(len(terrain_heights), x_center + radius + 1)):
        new_ground_y = bounds.y2 - terrain_heights[x]
        y = new_ground_y - 1
        while y >= 0:
            terrain_heights[x] += 1
            y -= 1
            if terrain_heights[x] >= HEIGHT:
                break


def apply_explosion_with_collapse(terrain_heights, x_center, y_center, radius=20):
    # Store original heights so we know what's above the crater
    original_heights = terrain_heights[:]

    for dx in range(-int(radius), int(radius) + 1):
        x = x_center + dx
        if 0 <= x < len(terrain_heights):
            try:
                dy = math.sqrt(radius**2 - dx**2)
            except ValueError:
                continue

            crater_y = y_center + dy
            new_height = bounds.y2 - crater_y
            terrain_heights[x] = max(0, int(min(terrain_heights[x], new_height)))

            # Collapse overhang: only what's above the *cleared* space falls
            original_height = original_heights[x]
            collapsed_space = dy  # vertical blast clearance
            height_diff = original_height - (terrain_heights[x] + collapsed_space)

            if height_diff > 0:
                terrain_heights[x] = min(bounds.y2, terrain_heights[x] + height_diff)

def apply_explosion_damage(tank, projectile):
    # Use projectile's strength for both radius and max damage
    explosion_x = projectile.x
    explosion_y = projectile.y
    radius = projectile.strength
    max_damage = projectile.strength

    # Find closest point on tank's rectangle to the explosion
    closest_x = max(tank.x, min(explosion_x, tank.x + tank.width))
    closest_y = max(tank.y, min(explosion_y, tank.y + tank.height))

    dx = closest_x - explosion_x
    dy = closest_y - explosion_y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    if distance < radius:
        damage = max_damage * (1 - (distance / radius))
        tank.health -= int(damage)
        tank.health = max(0, tank.health)

def apply_gravity_to_tank(tank, terrain_heights, max_height, useRight=False):
    
    terrain_x_start = int(tank.x)
    terrain_x_end = int(tank.x + tank.width)

    # Find the highest terrain under this tank's width span
    max_ground_y = tank.bottomCollide()

    tank_bottom = tank.y + tank.height
    if tank_bottom < (bounds.y2 - max_ground_y):
        tank.y += 1  # Fall by 1 pixel; increase for faster falling

# --- Draw helper functions ---

def draw_explosion_preview(screen, x_center, y_center, radius):
    preview_color = (255, 50, 50)
    alpha_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(alpha_surface, (*preview_color, 128), (x_center, y_center), radius)
    screen.blit(alpha_surface, (0, 0))
    pygame.display.flip()

def draw_hud(screen, tank, hud_height=100):
    """Draw the HUD with a half-moon angle indicator, speedometer-like fuel gauge, and odometer-style missile type."""
    # HUD background
    pygame.draw.rect(screen, (20, 20, 20), (0, HEIGHT - hud_height, WIDTH, hud_height))

    # Borders
    pygame.draw.rect(screen, (200, 200, 200), (0, HEIGHT - hud_height - 10, WIDTH, 10))  # Top HUD border
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, WIDTH, 5))  # Top border
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, 5, HEIGHT))  # Left border
    pygame.draw.rect(screen, (200, 200, 200), (WIDTH - 5, 0, 5, HEIGHT))  # Right border

    font = pygame.font.SysFont("consolas", 22)

    # --- Player Indicator ---
    # Draw player name with a contrasting color
    font.set_bold(True)
    player_label = font.render(tank.name, True, tuple(255 - c for c in tank.color))
    font.set_bold(False)
    # Draw a rectangle behind the player name for better visibility in matching tank color
    pygame.draw.rect(screen, tank.color, (20, HEIGHT - hud_height + 10, 150, 30))  # Background for player name
    screen.blit(player_label, (25, HEIGHT - hud_height + 15))

    # --- Half-Moon Angle Indicator ---
    angle_center = (240, HEIGHT - hud_height + 50)
    angle_radius = 40
    pygame.draw.arc(screen, (255, 255, 255), 
                    (angle_center[0] - angle_radius, angle_center[1] - angle_radius, 
                     angle_radius * 2, angle_radius * 2), 
                    math.radians(0), math.radians(180), 3)
    # Draw the current angle
    angle_rad = math.radians(tank.aimAngle)
    angle_x = angle_center[0] + angle_radius * math.cos(angle_rad)
    angle_y = angle_center[1] - angle_radius * math.sin(angle_rad)
    pygame.draw.line(screen, (255, 0, 0), angle_center, (angle_x, angle_y), 3)
    angle_label = font.render(f"{tank.aimAngle}°", True, (220, 220, 220))
    screen.blit(angle_label, (angle_center[0] - 40, angle_center[1] + 5))

    # --- Fuel Gauge as Horizontal Bar ---
    fuel_bar_width = 120
    fuel_bar_height = 20
    fuel_bar_x = 340
    fuel_bar_y = HEIGHT - hud_height + 40
    fuel_level = tank.fuel  # Replace with actual dynamic value
    pygame.draw.rect(screen, (255, 255, 255), (fuel_bar_x, fuel_bar_y, fuel_bar_width, fuel_bar_height), 2)
    fill_width = int(fuel_bar_width * fuel_level)
    pygame.draw.rect(screen, (255, 0, 0), (fuel_bar_x, fuel_bar_y, fill_width, fuel_bar_height))
    fuel_label = font.render("FUEL", True, (220, 220, 220))
    screen.blit(fuel_label, (fuel_bar_x + fuel_bar_width // 2 - 50, fuel_bar_y - 25))

    # --- Odometer-Style Missile Type ---
    missile_label = font.render("MISSILE", True, (255, 255, 255))
    missile_type = font.render("Baby Missile", True, (255, 255, 255))  # Placeholder for actual missile type
    pygame.draw.rect(screen, (50, 50, 50), (555, HEIGHT - hud_height + 10, 200, 60))  # Background
    pygame.draw.rect(screen, (200, 200, 200), (555, HEIGHT - hud_height + 10, 200, 60), 3)  # Border
    screen.blit(missile_label, (565, HEIGHT - hud_height + 15))
    screen.blit(missile_type, (565, HEIGHT - hud_height + 40))

    # --- Power Gauge as Shallow Triangle ---
    power = tank.cannonPower / 100.0  # Normalize from 0 to 1
    triangle_width = 100  # Full power width
    triangle_max_height = 20   # Max height on the right side
    current_width = int(triangle_width * power)
    current_height = int(triangle_max_height * power)

    # Position
    triangle_x = 820
    triangle_y = HEIGHT - hud_height + 40


    # Outline of full triangle (max size)
    base_left = (triangle_x, triangle_y)
    base_right = (triangle_x + triangle_width, triangle_y)
    top_right = (triangle_x + triangle_width, triangle_y - triangle_max_height)
    pygame.draw.polygon(screen, (255, 255, 255), [base_left, base_right, top_right], 2)

    # Filled triangle (grows with power)
    point1 = (triangle_x, triangle_y)  # bottom-left
    point2 = (triangle_x + current_width, triangle_y)  # bottom-right
    point3 = (triangle_x + current_width, triangle_y - current_height)  # top-right
    pygame.draw.polygon(screen, (255, 255, 0), [point1, point2, point3])

    # Label
    power_label = font.render("POWER", True, (255, 255, 255))
    screen.blit(power_label, (triangle_x, triangle_y + 10))

def draw_health_bar(screen, tank, bar_width=30, bar_height=6):
    # Position it just above the tank
    health_ratio = tank.health / tank.max_health
    x = tank.x + tank.width // 2 - bar_width // 2
    y = tank.y - 38  # adjust as needed

    # Background border
    pygame.draw.rect(screen, (80, 80, 80), (x, y, bar_width, bar_height))

    # Filled health bar
    fill_width = int(bar_width * health_ratio)
    pygame.draw.rect(screen, (0, 255, 0), (x, y, fill_width, bar_height))

    # foreground border
    pygame.draw.rect(screen, (180, 180, 180), (x-1, y-1, bar_width+1, bar_height+1), 1)

def draw_outlined_text(text, font, x, y, main_color, outline_color=(255, 255, 255), outline_thickness=2):
    base = font.render(text, True, main_color)
    for dx in [-outline_thickness, 0, outline_thickness]:
        for dy in [-outline_thickness, 0, outline_thickness]:
            if dx != 0 or dy != 0:
                outline = font.render(text, True, outline_color)
                screen.blit(outline, (x + dx, y + dy))
    screen.blit(base, (x, y))



class GameConfigUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Setup")

        self.players_frame = tk.LabelFrame(root, text="Players", padx=10, pady=10)
        self.players_frame.grid(row=0, column=0, padx=10, pady=10)

        self.num_players_var = tk.IntVar(value=2)
        tk.Label(self.players_frame, text="Number of Players:").grid(row=0, column=0)
        self.num_players_menu = tk.OptionMenu(self.players_frame, self.num_players_var, 1, 2, 3, 4, command=self.update_players)
        self.num_players_menu.grid(row=0, column=1)

        self.player_entries = []
        self.update_players(2)

        self.terrain_frame = tk.LabelFrame(root, text="Terrain", padx=10, pady=10)
        self.terrain_frame.grid(row=1, column=0, padx=10, pady=10)

        tk.Label(self.terrain_frame, text="Terrain Seed:").grid(row=0, column=0)
        self.terrain_seed = tk.Entry(self.terrain_frame)
        self.terrain_seed.insert(0, "12345")
        self.terrain_seed.grid(row=0, column=1)

        self.min_height_var = tk.IntVar(value=10)
        self.max_height_var = tk.IntVar(value=540)

        tk.Label(self.terrain_frame, text="Min Height:").grid(row=1, column=0)
        tk.Scale(self.terrain_frame, from_=0, to=200, orient='horizontal', variable=self.min_height_var).grid(row=1, column=1)

        tk.Label(self.terrain_frame, text="Max Height:").grid(row=2, column=0)
        tk.Scale(self.terrain_frame, from_=300, to=700, orient='horizontal', variable=self.max_height_var).grid(row=2, column=1)

        self.settings_frame = tk.LabelFrame(root, text="Gameplay Settings", padx=10, pady=10)
        self.settings_frame.grid(row=2, column=0, padx=10, pady=10)

        self.fuel_var = tk.DoubleVar(value=0.5)
        self.health_var = tk.IntVar(value=100)

        tk.Label(self.settings_frame, text="Fuel Amount:").grid(row=0, column=0)
        tk.Scale(self.settings_frame, from_=0.1, to=1.0, resolution=0.1, orient='horizontal', variable=self.fuel_var).grid(row=0, column=1)

        tk.Label(self.settings_frame, text="Tank Health:").grid(row=1, column=0)
        tk.Scale(self.settings_frame, from_=10, to=200, orient='horizontal', variable=self.health_var).grid(row=1, column=1)

        self.start_button = tk.Button(root, text="Start Game", command=self.collect_config)
        self.start_button.grid(row=3, column=0, pady=20)

    def update_players(self, count):
        for widget in self.player_entries:
            widget[0].destroy()
            widget[1].destroy()
            widget[2].destroy()
        self.player_entries.clear()

        for i in range(self.num_players_var.get()):
            name_entry = tk.Entry(self.players_frame)
            name_entry.insert(0, f"Player {i+1}")
            name_entry.grid(row=i+1, column=0)

            color_preview = tk.Label(self.players_frame, text="    ", bg="gray")
            color_preview.grid(row=i+1, column=1)
            color_button = tk.Button(self.players_frame, text="Choose Color", command=lambda i=i: self.choose_color(i))
            color_button.grid(row=i+1, column=2)

            self.player_entries.append((name_entry, color_preview, color_button))

        self.colors = ["#808080"] * self.num_players_var.get()  # Default grey

    def choose_color(self, index):
        color = colorchooser.askcolor()[1]
        if color:
            self.colors[index] = color
            self.player_entries[index][1].config(bg=color)

    def collect_config(self):
        player_data = []
        for idx, (name_entry, _, _) in enumerate(self.player_entries):
            name = name_entry.get()
            color = self.colors[idx]
            player_data.append({"name": name, "color": color})

        config = {
            "players": player_data,
            "terrain_seed": self.terrain_seed.get(),
            "terrain_min_height": self.min_height_var.get(),
            "terrain_max_height": self.max_height_var.get(),
            "fuel": self.fuel_var.get(),
            "health": self.health_var.get()
        }

        print("Collected Game Config:")
        print(config)
        current_state = GameState.PLAYING
        self.root.destroy()  # Close the UI and proceed to game

# --- Main loop ---
active_tank_index = 0  # 0 for player 1, 1 for player 2
running = True
while running:

    # Run the config UI
    if current_state == GameState.MENU:
        root = tk.Tk()
        app = GameConfigUI(root)
        root.mainloop()
    elif current_state == GameState.PLAYING:

        screen.fill((30, 30, 30))
        dt = clock.tick(FPS) / 1000

        # --- Events ---
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        tank = tanks[active_tank_index]
        # --- Input ---
        #print(list(filter(lambda c: c == True, pygame.key.get_pressed())))
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and projectile is None:
                    print(active_tank_index)
                    projectile = tank.fire(tank.cannonPower)

        # For smooth continuous controls (like movement or aim), use key.get_pressed()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            tank.aim("left")
        if keys[pygame.K_RIGHT]:
            tank.aim("right")
        if keys[pygame.K_UP]:
            tank.cannonPower = min(100, tank.cannonPower + .1)
        if keys[pygame.K_DOWN]:
            tank.cannonPower = max(0, tank.cannonPower - .1)
        if keys[pygame.K_RCTRL] and tank.fuel > 0:
            tank.move("Right")
        if keys[pygame.K_RALT] and tank.fuel > 0:
            tank.move("Left")
        # --- Draw Terrain ---
        terrain_coords = [(0, bounds.y2)]  # Start at bottom-left corner

        for x in range(WIDTH):
            terrain_coords.append((x, bounds.y2 - terrain.heightMap[x]))

        terrain_coords.append((WIDTH - 1, bounds.y2))  # End at bottom-right

        pygame.draw.polygon(screen, terrain.color, terrain_coords)
        for tank in list(filter(lambda t: t.active == True, tanks)):
            # apply gravity to tank
            apply_gravity_to_tank(tank, terrain.heightMap, bounds.y2)
            # --- Draw tank ---
            pygame.draw.rect(screen, tank.color, (tank.x, tank.y, tank.width, tank.height))
            aim_rad = math.radians(tank.aimAngle)
            line_len = 30
            line_end = (
                tank.x + math.cos(aim_rad) * tank.cannonLen,
                tank.y - math.sin(aim_rad) * tank.cannonLen
            )
            pygame.draw.line(screen, tank.cannonColor, (tank.x,tank.y), line_end, 3)
            draw_health_bar(screen, tank)

            # --- Update projectile ---
            if projectile:
                if projectile.x == tank.x and projectile.y == tank.y:
                    projectile.x = line_end[0]
                    projectile.y = line_end[1]
                projectile.x += projectile.vx
                projectile.y += projectile.vy
                projectile.vy += GRAVITY
            def nextTurn():
                global active_tank_index, show_turn_overlay, turn_overlay_start
                turn_overlay_start = pygame.time.get_ticks()
                active_tank_index = (active_tank_index + 1) % len(tanks)  # Switch to the next tank
                show_turn_overlay = True

            # Check Collision & Remove if off-screen
            if projectile:
                collision = check_projectile_collision(projectile.x, projectile.y, terrain.heightMap, WIDTH, HEIGHT, [tank])

                match collision:
                    case CollisionResult.HIT_TERRAIN | CollisionResult.HIT_TANK:
                        draw_explosion_preview(screen, projectile.x, projectile.y, projectile.strength)
                        Shot_Show_Timer = 0
                        Pending_Explosion = (int(projectile.x), int(projectile.y), projectile.strength, Shot_Show_Timer_Max, None)
                        for tank in tanks:
                            apply_explosion_damage(tank, projectile)
                            apply_gravity_to_tank(tank, terrain.heightMap, bounds.y2)
                            if tank.health <= 0 and tank.active:
                                tank.explode()
                        projectile = None
                        nextTurn()

                    case CollisionResult.MISS_OFFSCREEN:
                        print("Missed! Flew off screen.")
                        projectile = None
                        nextTurn()

                    case CollisionResult.MISS_OFFTOP:
                        pass  # Still flying upward

                    case CollisionResult.NO_COLLISION:
                        pass  # Still in the air


        if Pending_Explosion:
            impact_x, impact_y, radius, anim_timer, origin = Pending_Explosion

            # Draw a flashing or translucent circle
            preview_color = (255, 50, 50)
            alpha_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (*preview_color, 128), (impact_x, impact_y), radius)
            screen.blit(alpha_surface, (0, 0))

            Shot_Show_Timer += clock.get_time()

            if Shot_Show_Timer >= anim_timer:
                apply_explosion_with_collapse(terrain.heightMap, impact_x, impact_y, radius)
                Shot_Is_Timing = False
                Shot_Show_Timer = 0
                if origin != None:
                    origin.active = False
                Pending_Explosion = None if len(Pending_Explosion_Next) <= 0 else Pending_Explosion_Next.pop(0)
        
        # --- Draw projectile ---
        if projectile:
            pygame.draw.circle(screen, (255, 255, 255), (int(projectile.x), int(projectile.y)), 4)

        # --- Draw HUD ---
        draw_hud(screen, tanks[active_tank_index])
        
        if show_turn_overlay:
            elapsed = pygame.time.get_ticks() - turn_overlay_start
            if elapsed > turn_overlay_timer:
                show_turn_overlay = False
            else:
                fade_factor = max(0, 255 - int((elapsed / turn_overlay_timer) * 255))
                overlay_color = (*tanks[active_tank_index].color, fade_factor)
                font_overlay = pygame.font.SysFont(None, 48)
                text_surface = font_overlay.render(tanks[active_tank_index].name, True, overlay_color)
                draw_outlined_text(tanks[active_tank_index].name, font_overlay, WIDTH // 2 - 60, 60, overlay_color)


        pygame.display.flip()

pygame.quit()
