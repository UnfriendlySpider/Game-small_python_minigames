"""
flappy_birds.py

A Flappy Bird clone game implementation using Pygame.
Features a bird that must navigate through pipes by jumping.
The player can use an invincibility powerup to temporarily pass through obstacles.
Author: UnfriendlySpider
Date: 2024
Version: 1.0
"""

import pygame
import sys
import random

# Game configuration constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Color definitions
WHITE = (255, 255, 255)
BLUE = (135, 206, 250)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Physics and game constants (per second)
GRAVITY = 800.0         # pixels per second squared
BIRD_JUMP = -300.0      # pixels per second (initial jump velocity)
PIPE_SPEED = 180.0      # pixels per second
PIPE_GAP = 150
PIPE_WIDTH = 50

# Game states
GAME_RUNNING = "running"
GAME_OVER = "game_over"

# Powerup configuration
POWERUP_DURATION = 5000    # milliseconds
POWERUP_COOLDOWN = 10000   # milliseconds

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

class Bird:
    """
    Represents the player-controlled bird character.

    The bird has physics-based movement with gravity and jumping mechanics.
    It can be rendered in different colors based on powerup status.
    """
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.radius = 15
        self.velocity = 0.0

    def draw(self, invincible=False):
        color = YELLOW if invincible else WHITE
        pygame.draw.circle(screen, color, (self.x, int(self.y)), self.radius)

    def update(self, dt):
        """
        Update bird physics for one frame.
        dt: Time since last frame in seconds.
        """
        self.velocity += GRAVITY * dt
        self.y += self.velocity * dt

    def jump(self):
        self.velocity = BIRD_JUMP

class Pipe:
    """
    Represents a pair of pipes (top and bottom) that the bird must navigate through.
    """
    def __init__(self, x):
        self.x = x
        self.top_height = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)
        self.bottom_height = SCREEN_HEIGHT - self.top_height - PIPE_GAP

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, 0, PIPE_WIDTH, self.top_height))
        pygame.draw.rect(screen, GREEN, (self.x, SCREEN_HEIGHT - self.bottom_height, PIPE_WIDTH, self.bottom_height))

    def update(self, dt):
        self.x -= PIPE_SPEED * dt

def show_game_over(score):
    screen.fill(BLUE)
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)

    game_over_text = font_large.render("GAME OVER", True, WHITE)
    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    restart_text = font_small.render("Press R to Restart", True, WHITE)
    quit_text = font_small.render("Press Q to Quit", True, WHITE)

    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 200))
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 260))
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 320))
    screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 350))

    pygame.display.flip()

def main():
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH)]
    score = 0
    game_state = GAME_RUNNING

    # Powerup variables
    invincible = False
    powerup_start_time = 0
    last_powerup_use = -POWERUP_COOLDOWN

    while True:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        current_time = pygame.time.get_ticks()

        # End invincibility if duration elapsed
        if invincible and current_time - powerup_start_time >= POWERUP_DURATION:
            invincible = False

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == GAME_RUNNING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    bird.jump()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    if current_time - last_powerup_use >= POWERUP_COOLDOWN:
                        invincible = True
                        powerup_start_time = current_time
                        last_powerup_use = current_time
            elif game_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        bird = Bird()
                        pipes = [Pipe(SCREEN_WIDTH)]
                        score = 0
                        game_state = GAME_RUNNING
                        invincible = False
                        powerup_start_time = 0
                        last_powerup_use = -POWERUP_COOLDOWN
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

        if game_state == GAME_RUNNING:
            screen.fill(BLUE)

            # Update bird with frame-rate independence
            bird.update(dt)

            # Update pipes and remove/add as needed
            for pipe in pipes[:]:
                pipe.update(dt)
                if pipe.x + PIPE_WIDTH < 0:
                    pipes.remove(pipe)
                    pipes.append(Pipe(SCREEN_WIDTH))
                    score += 1

            # Collision detection (skip if invincible)
            if not invincible:
                for pipe in pipes:
                    if (bird.x + bird.radius > pipe.x and bird.x - bird.radius < pipe.x + PIPE_WIDTH and
                        (bird.y - bird.radius < pipe.top_height or bird.y + bird.radius > SCREEN_HEIGHT - pipe.bottom_height)):
                        game_state = GAME_OVER

                if bird.y - bird.radius < 0 or bird.y + bird.radius > SCREEN_HEIGHT:
                    game_state = GAME_OVER

            bird.draw(invincible)
            for pipe in pipes:
                pipe.draw()

            # Display score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            # Display powerup status
            font_small = pygame.font.Font(None, 24)
            if invincible:
                remaining_time = (POWERUP_DURATION - (current_time - powerup_start_time)) / 1000
                powerup_text = font_small.render(f"INVINCIBLE: {remaining_time:.1f}s", True, YELLOW)
                screen.blit(powerup_text, (10, 50))
            else:
                cooldown_remaining = max(0, (POWERUP_COOLDOWN - (current_time - last_powerup_use)) / 1000)
                if cooldown_remaining > 0:
                    cooldown_text = font_small.render(f"Powerup cooldown: {cooldown_remaining:.1f}s", True, RED)
                    screen.blit(cooldown_text, (10, 50))
                else:
                    ready_text = font_small.render("Press A for invincibility!", True, WHITE)
                    screen.blit(ready_text, (10, 50))

            pygame.display.flip()

        elif game_state == GAME_OVER:
            show_game_over(score)

if __name__ == "__main__":
    main()
