"""!
@file flappy_birds.py
@brief A Flappy Bird clone game implementation using Pygame
@details This game features a bird that must navigate through pipes by jumping.
         The player can use an invincibility powerup to temporarily pass through obstacles.
@author UnfriendlySpider
@date 2024
@version 1.0
"""

import pygame
import sys
import random

# Initialize pygame
pygame.init()

## @name Screen Configuration
## @{
SCREEN_WIDTH = 400      ##< Width of the game window in pixels
SCREEN_HEIGHT = 600     ##< Height of the game window in pixels
FPS = 60               ##< Frames per second for the game loop
## @}

## @name Color Definitions
## @{
WHITE = (255, 255, 255)    ##< RGB color tuple for white
BLUE = (135, 206, 250)     ##< RGB color tuple for sky blue background
GREEN = (0, 200, 0)        ##< RGB color tuple for green pipes
YELLOW = (255, 255, 0)     ##< RGB color tuple for yellow (invincible bird)
RED = (255, 0, 0)          ##< RGB color tuple for red text
## @}

## @name Physics and Game Constants
## @{
GRAVITY = 0.5              ##< Gravitational acceleration applied to the bird
BIRD_JUMP = -10           ##< Upward velocity applied when bird jumps
PIPE_SPEED = 3            ##< Horizontal speed of pipes moving left
PIPE_GAP = 150            ##< Vertical gap between top and bottom pipes
## @}

## @name Game States
## @{
GAME_RUNNING = "running"   ##< String constant for running game state
GAME_OVER = "game_over"   ##< String constant for game over state
## @}

## @name Powerup Configuration
## @{
POWERUP_DURATION = 5000   ##< Duration of invincibility powerup in milliseconds
POWERUP_COOLDOWN = 10000  ##< Cooldown period between powerup uses in milliseconds
## @}

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Clock
clock = pygame.time.Clock()

class Bird:
    """!
    @brief Represents the player-controlled bird character
    @details The bird has physics-based movement with gravity and jumping mechanics.
             It can be rendered in different colors based on powerup status.
    """
    
    def __init__(self):
        """!
        @brief Initialize the bird at starting position
        @details Sets the bird at the left side of screen, vertically centered,
                 with zero initial velocity
        """
        self.x = 50                    ##< Horizontal position (constant)
        self.y = SCREEN_HEIGHT // 2    ##< Vertical position (variable)
        self.radius = 15               ##< Collision radius of the bird
        self.velocity = 0              ##< Current vertical velocity

    def draw(self, invincible=False):
        """!
        @brief Render the bird on the screen
        @param invincible Boolean flag indicating if bird should be drawn in invincible color
        @details Draws the bird as a circle. Color changes to yellow when invincible.
        """
        color = YELLOW if invincible else WHITE
        pygame.draw.circle(screen, color, (self.x, int(self.y)), self.radius)

    def update(self):
        """!
        @brief Update bird physics for one frame
        @details Applies gravity to velocity and updates position based on velocity
        """
        self.velocity += GRAVITY
        self.y += self.velocity

    def jump(self):
        """!
        @brief Make the bird jump upward
        @details Sets the bird's velocity to the jump speed (negative = upward)
        """
        self.velocity = BIRD_JUMP

class Pipe:
    """!
    @brief Represents a pair of pipes (top and bottom) that the bird must navigate through
    @details Each pipe has a random height with a fixed gap between top and bottom sections
    """
    
    def __init__(self, x):
        """!
        @brief Initialize a new pipe pair at the specified x position
        @param x Horizontal position where the pipe should be created
        @details Randomly generates the height of the top pipe, with bottom pipe
                 calculated to maintain the required gap
        """
        self.x = x                     ##< Horizontal position of the pipe
        ## Height of the top pipe section
        self.top_height = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)
        ## Height of the bottom pipe section
        self.bottom_height = SCREEN_HEIGHT - self.top_height - PIPE_GAP

    def draw(self):
        """!
        @brief Render the pipe pair on the screen
        @details Draws two green rectangles representing the top and bottom pipe sections
        """
        pygame.draw.rect(screen, GREEN, (self.x, 0, 50, self.top_height))
        pygame.draw.rect(screen, GREEN, (self.x, SCREEN_HEIGHT - self.bottom_height, 50, self.bottom_height))

    def update(self):
        """!
        @brief Update pipe position for one frame
        @details Moves the pipe horizontally to the left at the defined speed
        """
        self.x -= PIPE_SPEED

def show_game_over(score):
    """!
    @brief Display the game over screen with final score and restart options
    @param score The player's final score to display
    @details Shows game over text, final score, and instructions for restarting or quitting
    """
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
    """!
    @brief Main game loop and entry point
    @details Handles all game logic including:
             - Game state management (running/game over)
             - Event handling (keyboard input)
             - Physics updates for bird and pipes
             - Collision detection
             - Powerup system (invincibility)
             - Score tracking
             - Rendering all game elements
    """
    ## The player-controlled bird object
    bird = Bird()
    ## List of pipe objects currently on screen
    pipes = [Pipe(SCREEN_WIDTH)]
    ## Current player score (number of pipes passed)
    score = 0
    ## Current state of the game
    game_state = GAME_RUNNING
    
    # Powerup variables
    ## Flag indicating if bird is currently invincible
    invincible = False
    ## Timestamp when current powerup was activated
    powerup_start_time = 0
    ## Timestamp of last powerup use (for cooldown calculation)
    last_powerup_use = -POWERUP_COOLDOWN  # Allow immediate first use

    while True:
        ## Current time in milliseconds since pygame initialization
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
                # Remove off-screen pipes and add new ones
                if pipe.x + 50 < 0:
                    pipes.remove(pipe)
                    pipes.append(Pipe(SCREEN_WIDTH))
                    score += 1

            # Collision detection (skip if invincible)
            if not invincible:
                # Check collision with pipes
                for pipe in pipes:
                    if (bird.x + bird.radius > pipe.x and bird.x - bird.radius < pipe.x + 50 and
                        (bird.y - bird.radius < pipe.top_height or bird.y + bird.radius > SCREEN_HEIGHT - pipe.bottom_height)):
                        game_state = GAME_OVER

                # Check collision with screen boundaries
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
                ## Remaining invincibility time in seconds
                remaining_time = (POWERUP_DURATION - (current_time - powerup_start_time)) / 1000
                powerup_text = font_small.render(f"INVINCIBLE: {remaining_time:.1f}s", True, YELLOW)
                screen.blit(powerup_text, (10, 50))
            else:
                ## Remaining cooldown time in seconds
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

        ## Maintain consistent frame rate
        clock.tick(FPS)

if __name__ == "__main__":
    main()
