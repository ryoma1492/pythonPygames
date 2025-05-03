import pygame
import math
from enum import Enum, auto
from dataclasses import dataclass
from noise import pnoise1
import random

@dataclass
class Bounds:
    x1: int
    x2: int
    y1: int
    y2: int

@dataclass
class Tank:
    height: float
    width: float
    cannonRelX: float
    cannonRelY: float
    cannonLen: float
    aimAngle: float
    x: float
    y: float

    def aim(self, direction: str):
        """Adjust the aim angle of the tank."""
        if direction == "left":
            self.aimAngle = min(180, self.aimAngle + 1)
        elif direction == "right":
            self.aimAngle = max(0, self.aimAngle - 1)

    def fire(self, shot_speed: float) -> "Projectile":
        """Fire a projectile from the tank."""
        rad = math.radians(self.aimAngle)
        return Projectile(
            x=self.x + math.cos(rad) * self.cannonLen,
            y=self.y - math.sin(rad) * self.cannonLen,
            vx=shot_speed * math.cos(rad),
            vy=-shot_speed * math.sin(rad),
            strength=20
        )
    
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


# --- Constants ---
WIDTH, HEIGHT = 1000, 640
bounds = Bounds(5, WIDTH - 5, 5, HEIGHT - 105)
FPS = 60
GRAVITY = 0.5
SHOT_SPEED = 15
Shot_Show_Timer = 0
Shot_Show_Timer_Max = 333  # in milliseconds
Pending_Explosion = None  # will store (x, y, radius)

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scorched Earth Prototype")
clock = pygame.time.Clock()

# --- Terrain initialize ---
terrain_heights = generate_terrain(
    WIDTH,
    min_height=50,
    max_height=bounds.y2 - 50,
    scale=150.0,
    octaves=5,
    seed=42
)
terrain_color = (40, 180, 0) # hopefully medium green with a tinge of yellow

# --- Tank state ---
tank1 = Tank(12, 24, 4, 0, 20, 45, WIDTH // 4, bounds.y2 - 20)
tank1.y = bounds.y2 - tank1.height - terrain_heights[tank1.x]
projectile = None  # Will be a dict when active

# --- Helper Functions ---
def check_projectile_collision(x: float, y: float, terrain_heights: list[int], width: int, height: int) -> CollisionResult:
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
        # Scan up from the new terrain height to the top of screen
        new_ground_y = bounds.y2 - terrain_heights[x]
        y = new_ground_y - 1
        while y >= 0:
            # If there's "terrain" floating above (we simulate it with a solid layer), it falls
            # For this simple simulation, just increment the terrain height to "fill" the hole
            terrain_heights[x] += 1
            y -= 1

            # Stop once we reach the old terrain height (simulate a filled-in collapse)
            if terrain_heights[x] >= HEIGHT:
                break


def apply_explosion_with_collapse(terrain_heights, x_center, y_center, radius=20):
    # Store original heights so we know what's above the crater
    original_heights = terrain_heights[:]

    for dx in range(-radius, radius + 1):
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


def draw_explosion_preview(screen, x_center, y_center, radius):
    preview_color = (255, 50, 50)
    alpha_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(alpha_surface, (*preview_color, 128), (x_center, y_center), radius)
    screen.blit(alpha_surface, (0, 0))
    pygame.display.flip()


def generate_terrain(width, min_height, max_height, scale=100.0, octaves=4, seed=None):
    if seed is None:
        seed = random.randint(0, 10000)

    terrain = []
    for x in range(width):
        noise_val = pnoise1(x / scale + seed, octaves=octaves)
        # Normalize noise_val (-1 to 1) -> (0 to 1)
        normalized = (noise_val + 1) / 2
        height = int(min_height + normalized * (max_height - min_height))
        terrain.append(height)
    return terrain

# --- Main loop ---
running = True
while running:
    screen.fill((30, 30, 30))
    dt = clock.tick(FPS) / 1000

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Input ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        tank1.aim("left")
    if keys[pygame.K_RIGHT]:
        tank1.aim("right")
    if keys[pygame.K_SPACE] and projectile is None:
        projectile = tank1.fire(SHOT_SPEED)

    # --- Draw Terrain ---
    terrain_coords = [(0, bounds.y2)]  # Start at bottom-left corner

    for x in range(WIDTH):
        terrain_coords.append((x, bounds.y2 - terrain_heights[x]))

    terrain_coords.append((WIDTH - 1, bounds.y2))  # End at bottom-right

    pygame.draw.polygon(screen, terrain_color, terrain_coords)

    # --- Draw tank ---
    pygame.draw.rect(screen, (200, 200, 0), (tank1.x, tank1.y, tank1.width, tank1.height))
    aim_rad = math.radians(tank1.aimAngle)
    line_len = 30
    line_end = (
        tank1.x + math.cos(aim_rad) * tank1.cannonLen,
        tank1.y - math.sin(aim_rad) * tank1.cannonLen
    )
    pygame.draw.line(screen, (255, 0, 0), (tank1.x,tank1.y), line_end, 3)

    # --- Update projectile ---
    if projectile:
        if projectile.x == tank1.x and projectile.y == tank1.y:
            projectile.x = line_end[0]
            projectile.y = line_end[1]
        projectile.x += projectile.vx
        projectile.y += projectile.vy
        projectile.vy += GRAVITY

        # Check Collision & Remove if off-screen
    if projectile:
        collision = check_projectile_collision(projectile.x, projectile.y, terrain_heights, WIDTH, HEIGHT)

        match collision:
            case CollisionResult.HIT_TERRAIN:
                draw_explosion_preview(screen, projectile.x, projectile.y, projectile.strength)
                Shot_Show_Timer = 0
                Pending_Explosion = (int(projectile.x), int(projectile.y), projectile.strength)
#                apply_explosion_with_collapse(terrain_heights, int(projectile.x), int(projectile.y), projectile.strength)
                projectile = None

            case CollisionResult.HIT_TANK:
                print("Direct hit on a tank!")
                projectile = None

            case CollisionResult.MISS_OFFSCREEN:
                print("Missed! Flew off screen.")
                projectile = None

            case CollisionResult.MISS_OFFTOP:
                pass  # Still flying upward

            case CollisionResult.NO_COLLISION:
                pass  # Still in the air

    if Pending_Explosion:
        impact_x, impact_y, radius = Pending_Explosion

        # Draw a flashing or translucent circle
        preview_color = (255, 50, 50)
        alpha_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surface, (*preview_color, 128), (impact_x, impact_y), radius)
        screen.blit(alpha_surface, (0, 0))

        Shot_Show_Timer += clock.get_time()

        if Shot_Show_Timer >= Shot_Show_Timer_Max:
            apply_explosion_with_collapse(terrain_heights, impact_x, impact_y, radius)
            Shot_Is_Timing = False
            Shot_Show_Timer = 0
            Pending_Explosion = None
    
    # --- Draw projectile ---
    if projectile:
        pygame.draw.circle(screen, (255, 255, 255), (int(projectile.x), int(projectile.y)), 4)

    # --- Draw HUD ---
    HUD_HEIGHT = 100
    pygame.draw.rect(screen, (20, 20, 20), (0, HEIGHT - HUD_HEIGHT, WIDTH, HUD_HEIGHT))
    pygame.draw.rect(screen, (200, 200, 200), (0, HEIGHT - HUD_HEIGHT-10, WIDTH, 10))
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, WIDTH, 5))
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, 5, HEIGHT))
    pygame.draw.rect(screen, (200, 200, 200), (WIDTH-5, 0, 5, HEIGHT))

    font = pygame.font.SysFont("consolas", 22)

    # Dashboard-style labels
    angle_label = font.render(f"ANGLE: {tank1.aimAngle}°", True, (255, 255, 255))
    ammo_label = font.render("AMMO: ∞", True, (255, 255, 255))  # Placeholder
    cannon_label = font.render("CANNON: Baby Missile", True, (255, 255, 255))
    fuel_label = font.render("FUEL: 0", True, (255, 255, 255))  # Stationary tank for now
    power_label = font.render("POWER: 15", True, (255, 255, 255))  # Fixed for now

    # Positioning (like gauges)
    screen.blit(angle_label, (20, HEIGHT - HUD_HEIGHT + 20))
    screen.blit(ammo_label, (240, HEIGHT - HUD_HEIGHT + 20))
    screen.blit(cannon_label, (240, HEIGHT - HUD_HEIGHT + 60))
    screen.blit(fuel_label, (500, HEIGHT - HUD_HEIGHT + 20))
    screen.blit(power_label, (20, HEIGHT - HUD_HEIGHT + 60))

    pygame.display.flip()

pygame.quit()
