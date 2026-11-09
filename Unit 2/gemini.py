import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders - Python Edition")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 119, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 34, 34)
YELLOW = (255, 204, 0)
ORANGE = (255, 136, 0)

# Fonts
font_small = pygame.font.SysFont("Courier New", 16)
font_large = pygame.font.SysFont("Courier New", 30, bold=True)

# Game State
score = 0
lives = 3
game_over = False
game_won = False
selected_weapon = 'plasma'  # 'plasma', 'stun', 'bomb'

# Player Setup (Blue)
player_width = 40
player_height = 20
player_x = SCREEN_WIDTH // 2 - player_width // 2
player_y = SCREEN_HEIGHT - 50
player_speed = 5
Lists for game objects
bullets = []
enemy_bullets = []
bombs = []
explosions = []

# Invaders Setup (Red)
invader_rows = 4
invader_cols = 8
invader_width = 35
invader_height = 20
invader_padding = 12
invader_offset_top = 50
invader_offset_left = 35
invader_speed = 1
invader_drop_distance = 15

invaders = []

def init_invaders():
    global invaders
    invaders = []
    for r in range(invader_rows):
        for c in range(invader_cols):
            inv_x = invader_offset_left + c * (invader_width + invader_padding)
            inv_y = invader_offset_top + r * (invader_height + invader_padding)
            invaders.append({
                'x': inv_x,
                'y': inv_y,
                'width': invader_width,
                'height': invader_height,
                'alive': True,
                'stunned_until': 0
            })

init_invaders()

clock = pygame.time.Clock()

# Main Game Loop
while True:
    current_time = pygame.time.get_ticks()

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if not game_over and not game_won:
                # Weapon Switching
                if event.key == pygame.K_1:
                    selected_weapon = 'plasma'
                elif event.key == pygame.K_2:
                    selected_weapon = 'stun'
                elif event.key == pygame.K_3:
                    selected_weapon = 'bomb'

                # Shooting / Launching Action
                elif event.key == pygame.K_SPACE:
                    if selected_weapon == 'plasma' and len(bullets) < 4:
                        bullets.append({
                            'x': player_x + player_width // 2 - 2,
                            'y': player_y,
                            'width': 4,
                            'height': 12,
                            'speed': 7,
                            'type': 'plasma'
                        })
                    elif selected_weapon == 'stun' and len(bullets) < 3:
                        bullets.append({
                            'x': player_x + player_width // 2 - 3,
                            'y': player_y,
                            'width': 6,
                            'height': 12,
                            'speed': 6,
                            'type': 'stun'
                        })
                    elif selected_weapon == 'bomb' and len(bombs) < 1:
                        bombs.append({
                            'x': player_x + player_width // 2,
                            'y': player_y,
                            'vy': -6,
                            'target_y': player_y - 120,
                            'radius': 10
                        })

    if not game_over and not game_won:
        # Player Continuous Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x + player_width < SCREEN_WIDTH:
            player_x += player_speed

        # Update Bullets (Plasma & Stun)
        for b in bullets[:]:
            b['y'] -= b['speed']
            if b['y'] < 0:
                bullets.remove(b)

        # Update Bombs
        for b in bombs[:]:
            b['y'] += b['vy']
            if b['y'] <= b['target_y'] or b['y'] < 0:
                explosions.append({
                    'x': b['x'],
                    'y': b['y'],
                    'radius': 10,
                    'max_radius': 75,
                    'alpha': 1.0
                })
                bombs.remove(b)

        # Update Explosions & Range Damage
        for exp in explosions[:]:
            exp['radius'] += 3
            exp['alpha'] -= 0.03

            for inv in invaders:
                if inv['alive']:
                    inv_center_x = inv['x'] + inv['width'] // 2
                    inv_center_y = inv['y'] + inv['height'] // 2
                    dist = math.hypot(inv_center_x - exp['x'], inv_center_y - exp['y'])
                    if dist < exp['radius']:
                        inv['alive'] = False
                        score += 100

            if exp['alpha'] <= 0 or exp['radius'] > exp['max_radius']:
                 explosions.remove(exp)

        # Update Enemy Bullets
        for b in enemy_bullets[:]:
            b['y'] += b['speed']
            # Check collision with player
            if (b['x'] < player_x + player_width and
                b['x'] + b['width'] > player_x and
                b['y'] < player_y + player_height and
                b['y'] + b['height'] > player_y):
                enemy_bullets.remove(b)
                lives -= 1
                if lives <= 0:
                    game_over = True
                continue
            if b['y'] > SCREEN_HEIGHT:
                enemy_bullets.remove(b)

        # Invader Logic
        edge_reached = False
        living_invaders = [inv for inv in invaders if inv['alive']]

        if len(living_invaders) == 0:
            game_won = True

        for inv in living_invaders:
            if current_time > inv['stunned_until']:
                inv['x'] += invaderSpeed
                if inv['x'] + inv['width'] > SCREEN_WIDTH - 20 or inv['x'] < 20:
                    edge_reached = True

        if edge_reached:
            invaderSpeed = -invaderSpeed
            for inv in living_invaders:
                if current_time > inv['stunned_until']:
                    inv['y'] += invader_drop_distance
                    if inv['y'] + inv['height'] >= player_y:
                        game_over = True

        # Random Enemy Shooting
        if random.random() < 0.02 and len(living_invaders) > 0:
            active_shooters = [inv for inv in living_invaders if current_time > inv['stunned_until']]
            if active_shooters:
                shooter = random.choice(active_shooters)
                enemy_bullets.append({
                    'x': shooter['x'] + shooter['width'] // 2 - 2,
                    'y': shooter['y'] + shooter['height'],
                    'width': 4,
                    'height': 10,
                    'speed': 3.5
                })

        # Bullet-Invader Collisions
        for b in bullets[:]:
            bullet_removed = False
            for inv in invaders:
                if inv['alive']:
                    if (b['x'] < inv['x'] + inv['width'] and
                        b['x'] + b['width'] > inv['x'] and
                        b['y'] < inv['y'] + inv['height'] and
                        b['y'] + b['height'] > inv['y']):
                        
                        if b['type'] == 'plasma':
                            inv['alive'] = False
                            score += 100
                        elif b['type'] == 'stun':
                            inv['stunned_until'] = current_time + 3000
                            score += 25

                        bullets.remove(b)
                        bullet_removed = True
                        break
            if bullet_removed:
                continue

    # --- DRAWING ---
    screen.fill(BLACK)

    # Draw Player (Blue)
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_width, player_height))
    pygame.draw.rect(screen, BLUE, (player_x + player_width // 2 - 3, player_y - 6, 6, 6))

    # Draw Bullets
    for b in bullets:
        color = CYAN if b['type'] == 'plasma' else GREEN
        pygame.draw.rect(screen, color, (b['x'], b['y'], b['width'], b['height']))

    # Draw Bombs
    for b in bombs:
        pygame.draw.circle(screen, ORANGE, (int(b['x']), int(b['y'])), b['radius'])

    # Draw Explosions
    for exp in explosions:
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 120, 0, int(exp['alpha'] * 255)), (int(exp['x']), int(exp['y'])), int(exp['radius']))
        screen.blit(surf, (0, 0))

    # Draw Enemy Bullets
    for b in enemy_bullets:
        pygame.draw.rect(screen, RED, (b['x'], b['y'], b['width'], b['height']))

    # Draw Invaders (Red, or Yellow if Stunned)
    for inv in invaders:
        if inv['alive']:
            is_stunned = current_time < inv['stunned_until']
            color = YELLOW if is_stunned else RED
            pygame.draw.rect(screen, color, (inv['x'], inv['y'], inv['width'], inv['height']))
            # Eyes
            pygame.draw.rect(screen, BLACK, (inv['x'] + 8, inv['y'] + 6, 4, 4))
            pygame.draw.rect(screen, BLACK, (inv['x'] + inv['width'] - 12, inv['y'] + 6, 4, 4))

    # Draw HUD / Scoreboard
    weapon_names = {'plasma': 'Plasma Gun', 'stun': 'Stun Gun', 'bomb': 'Bomb'}
    weapon_colors = {'plasma': CYAN, 'stun': GREEN, 'bomb': ORANGE}
    
    score_text = font_small.render(f"Score: {score} | Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))

    w_text = font_small.render(f"Weapon: {weapon_names[selected_weapon]}", True, weapon_colors[selected_weapon])
    screen.blit(w_text, (10, 32))

    # Game Over / Win Screens
    if game_over or game_won:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        msg = "YOU WIN!" if game_won else "GAME OVER"
        msg_color = CYAN if game_won else RED
        
        text_surface = font_large.render(msg, True, msg_color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(text_surface, text_rect)

        sub_surface = font_small.render("Close window to exit", True, WHITE)
        sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(sub_surface, sub_rect)

    pygame.display.flip()
    clock.tick(60)
Controls Summa