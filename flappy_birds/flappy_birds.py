import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 250)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Game variables
GRAVITY = 0.5
BIRD_JUMP = -10
PIPE_SPEED = 3
PIPE_GAP = 150
GAME_RUNNING = "running"
GAME_OVER = "game_over"
POWERUP_DURATION = 5000  # 5 seconds in milliseconds
POWERUP_COOLDOWN = 10000  # 10 seconds cooldown

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Clock
clock = pygame.time.Clock()

# Bird class
class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.radius = 15
        self.velocity = 0

    def draw(self, invincible=False):
        color = YELLOW if invincible else WHITE
        pygame.draw.circle(screen, color, (self.x, int(self.y)), self.radius)

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def jump(self):
        self.velocity = BIRD_JUMP

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.top_height = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)
        self.bottom_height = SCREEN_HEIGHT - self.top_height - PIPE_GAP

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, 0, 50, self.top_height))
        pygame.draw.rect(screen, GREEN, (self.x, SCREEN_HEIGHT - self.bottom_height, 50, self.bottom_height))

    def update(self):
        self.x -= PIPE_SPEED

# Game over screen
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

# Main game loop
def main():
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH)]
    score = 0
    game_state = GAME_RUNNING
    
    # Powerup variables
    invincible = False
    powerup_start_time = 0
    last_powerup_use = -POWERUP_COOLDOWN  # Allow immediate first use

    while True:
        current_time = pygame.time.get_ticks()
        
        # Check if invincibility should end
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
                    # Activate powerup if cooldown is over
                    if current_time - last_powerup_use >= POWERUP_COOLDOWN:
                        invincible = True
                        powerup_start_time = current_time
                        last_powerup_use = current_time
            elif game_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart game
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
            
            # Update bird
            bird.update()

            # Update pipes
            for pipe in pipes:
                pipe.update()
                if pipe.x + 50 < 0:
                    pipes.remove(pipe)
                    pipes.append(Pipe(SCREEN_WIDTH))
                    score += 1

            # Collision detection (skip if invincible)
            if not invincible:
                for pipe in pipes:
                    if (bird.x + bird.radius > pipe.x and bird.x - bird.radius < pipe.x + 50 and
                        (bird.y - bird.radius < pipe.top_height or bird.y + bird.radius > SCREEN_HEIGHT - pipe.bottom_height)):
                        game_state = GAME_OVER

                if bird.y - bird.radius < 0 or bird.y + bird.radius > SCREEN_HEIGHT:
                    game_state = GAME_OVER

            # Draw bird and pipes
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

            # Update display
            pygame.display.flip()
        
        elif game_state == GAME_OVER:
            show_game_over(score)

        clock.tick(FPS)

if __name__ == "__main__":
    main()
