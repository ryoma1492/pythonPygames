import pygame
import sys
import random
import time
import numpy as np

# Constants
WINDOW_SIZE = 800
CELL_SIZE = 20
GRID_SIZE = WINDOW_SIZE // CELL_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 225, 180)  # Orange for bombs

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Set up the window
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Two Player Snake with Bombs")

# Fonts
font = pygame.font.SysFont(None, 48)
score_font = pygame.font.SysFont(None, 36)

# Functions
def create_sound(frequency=440, duration=0.2, volume=0.5, waveform='sine'):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    if waveform == 'sine':
        wave = np.sin(2 * np.pi * frequency * t)
    elif waveform == 'square':
        wave = np.sign(np.sin(2 * np.pi * frequency * t))
    else:
        raise ValueError("Unsupported waveform")

    audio = (wave * (2**15 - 1) * volume).astype(np.int16)
    stereo_sound = np.repeat(audio[:, np.newaxis], 2, axis=1)

    return pygame.sndarray.make_sound(stereo_sound)

def generate_beep_sound(frequency=880, duration=0.25, amplitude=0.4):
    framerate = 44100
    t = np.linspace(0, duration, int(framerate * duration), False)

    # Create a sine wave
    waveform = np.sin(2 * np.pi * frequency * t)

    # Apply envelope (soft fade in/out)
    envelope = np.linspace(0, 1, len(t)//10)
    envelope = np.concatenate((envelope, np.ones(len(t) - 2*len(envelope)), envelope[::-1]))
    waveform *= envelope[:len(t)]

    # Scale to 16-bit audio
    mono = np.int16(amplitude * waveform * 32767)

    # Duplicate mono to stereo
    stereo = np.column_stack((mono, mono))

    sound = pygame.sndarray.make_sound(stereo)
    return sound


# Sounds
fruit_beep = create_sound(frequency=600, duration=0.1, volume=.5, waveform='sine')
begin_game=generate_beep_sound()
death_buzz = create_sound(frequency=100, duration=0.3, volume=.15,  waveform='square')

def draw_snake(screen, snake, color):
    for segment in snake:
        pygame.draw.rect(screen, color, pygame.Rect(segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_fruit(screen, fruit):
    pygame.draw.rect(screen, WHITE, pygame.Rect(fruit[0]*CELL_SIZE, fruit[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_bomb(screen, bomb):
    pygame.draw.rect(screen, ORANGE, pygame.Rect(bomb[0]*CELL_SIZE, bomb[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

def move_snake(snake, direction, grow=False):
    head_x, head_y = snake[0]
    dir_x, dir_y = direction
    new_head = (head_x + dir_x, head_y + dir_y)
    if grow:
        return [new_head] + snake
    else:
        return [new_head] + snake[:-1]

def check_collision(snake):
    head = snake[0]
    return head in snake[1:] or head[0] < 0 or head[1] < 0 or head[0] >= GRID_SIZE or head[1] >= GRID_SIZE

def wait_for_input():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                begin_game.play()
                return

def get_random_position(snake1, snake2, bombs=[]):
    while True:
        position = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if position not in snake1 and position not in snake2 and position not in bombs:
            return position

def draw_score(screen, score1, score2):
    score_text = f"GREEN: {score1} |   RED : {score2}"
    score_surface = score_font.render(score_text, True, WHITE)
    screen.blit(score_surface, (10, 10))

def game_loop():
    # Initial game setup
    snake1 = [(5, 5), (4, 5), (3, 5)]
    snake2 = [(GRID_SIZE - 6, GRID_SIZE - 6), (GRID_SIZE - 5, GRID_SIZE - 6), (GRID_SIZE - 4, GRID_SIZE - 6)]
    direction1 = RIGHT
    direction2 = LEFT
    grow1 = False
    grow2 = False
    fruit = get_random_position(snake1, snake2)
    bombs = []
    score1 = 0
    score2 = 0
    last_bomb_time = time.time()
    bomb_spawn_interval = 2
    game_over = False
    winner = None
    death_reason = ""

    screen.fill(BLACK)
    draw_snake(screen, snake1, GREEN)
    draw_snake(screen, snake2, RED)
    draw_fruit(screen, fruit)
    pygame.display.flip()
    wait_for_input()

    while not game_over:
        grow1 = grow2 = False
        current_time = time.time()

        if current_time - last_bomb_time >= bomb_spawn_interval:
            bombs.append(get_random_position(snake1, snake2, bombs=bombs))
            last_bomb_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Snake 1 controls
                if event.key == pygame.K_w and direction1 != DOWN:
                    direction1 = UP
                elif event.key == pygame.K_s and direction1 != UP:
                    direction1 = DOWN
                elif event.key == pygame.K_a and direction1 != RIGHT:
                    direction1 = LEFT
                elif event.key == pygame.K_d and direction1 != LEFT:
                    direction1 = RIGHT
                # Snake 2 controls
                elif event.key == pygame.K_UP and direction2 != DOWN:
                    direction2 = UP
                elif event.key == pygame.K_DOWN and direction2 != UP:
                    direction2 = DOWN
                elif event.key == pygame.K_LEFT and direction2 != RIGHT:
                    direction2 = LEFT
                elif event.key == pygame.K_RIGHT and direction2 != LEFT:
                    direction2 = RIGHT

        # Check for fruit eating
        next_head1 = (snake1[0][0] + direction1[0], snake1[0][1] + direction1[1])
        next_head2 = (snake2[0][0] + direction2[0], snake2[0][1] + direction2[1])

        if next_head1 == fruit:
            grow1 = True
            fruit = get_random_position(snake1, snake2, bombs)
            score1 += 1
            fruit_beep.play()
        if next_head2 == fruit:
            grow2 = True
            fruit = get_random_position(snake1, snake2, bombs)
            score2 += 1
            fruit_beep.play()

        # Move snakes
        snake1 = move_snake(snake1, direction1, grow1)
        snake2 = move_snake(snake2, direction2, grow2)

        # Collision checks

# Collision checks
        if check_collision(snake1):
            if snake1[0][0] < 0 or snake1[0][1] < 0 or snake1[0][0] >= GRID_SIZE or snake1[0][1] >= GRID_SIZE:
                death_reason = "GREEN hit the wall"
            else:
                death_reason = "GREEN ran into itself"
            game_over = True
            winner = "RED"
        elif check_collision(snake2):
            if snake2[0][0] < 0 or snake2[0][1] < 0 or snake2[0][0] >= GRID_SIZE or snake2[0][1] >= GRID_SIZE:
                death_reason = "RED hit the wall"
            else:
                death_reason = "RED ran into itself"
            game_over = True
            winner = "GREEN"
        elif snake1[0] == snake2[0]:
            game_over = True
            winner = "Draw"
            death_reason = "head-on collision"
        elif snake1[0] in snake2:
            game_over = True
            winner = "RED"
            death_reason = "GREEN ran into RED"
        elif snake2[0] in snake1:
            game_over = True
            winner = "GREEN"
            death_reason = "RED ran into GREEN"

        # Bomb collisions
        if snake1[0] in bombs:
            game_over = True
            winner = "RED"
            death_reason = "GREEN exploded"
        if snake2[0] in bombs:
            game_over = True
            winner = "GREEN"
            death_reason = "RED exploded"

        if game_over:
            death_buzz.play()

        # Draw everything
        screen.fill(BLACK)
        draw_snake(screen, snake1, GREEN)
        draw_snake(screen, snake2, RED)
        draw_fruit(screen, fruit)
        for bomb in bombs:
            draw_bomb(screen, bomb)
        draw_score(screen, score1, score2)

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

    # Game Over message
    if winner == "Draw":
      result_message = f"It's a draw! ({death_reason})"
    else:
      result_message = f"{winner} wins! ({death_reason})"

    # Retry message
    retry_message = "Press R to retry or Q to quit."

    # Render the result message
    result_surface = font.render(result_message, True, WHITE)
    screen.blit(result_surface, (WINDOW_SIZE // 2 - result_surface.get_width() // 2, WINDOW_SIZE // 2 - 20))

    # Render the retry message
    retry_surface = font.render(retry_message, True, WHITE)
    screen.blit(retry_surface, (WINDOW_SIZE // 2 - retry_surface.get_width() // 2, WINDOW_SIZE // 2 + 40))

    pygame.display.flip()
 
    # Wait for retry
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    game_loop()
