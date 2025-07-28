"""
Game scene for Flappy Birds.
Contains the main gameplay logic and rendering.
"""

import pygame
from typing import Optional

from scenes.base_scene import BaseScene
from core.state_manager import GameState
from entities.bird import Bird
from entities.pipe import PipeManager
from config.settings import DISPLAY, COLORS, GAMEPLAY


class GameScene(BaseScene):
    """
    Main gameplay scene.
    
    Handles:
    - Bird physics and movement
    - Pipe management and collision detection
    - Powerup system
    - Score tracking
    - Game over detection
    """
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        
        # Game entities
        self.bird: Optional[Bird] = None
        self.pipe_manager: Optional[PipeManager] = None
        
        # Game state
        self.score = 0
        self.is_paused = False
        
        # Powerup system
        self.invincible = False
        self.powerup_start_time = 0
        self.last_powerup_use = -GAMEPLAY.POWERUP_COOLDOWN
        
        # Fonts
        self.score_font = None
        self.ui_font = None
    
    def enter(self) -> None:
        """Initialize the game scene."""
        super().enter()
        
        # Initialize entities
        self.bird = Bird()
        self.pipe_manager = PipeManager()
        
        # Reset game state
        self.score = 0
        self.is_paused = False
        
        # Reset powerup system
        self.invincible = False
        self.powerup_start_time = 0
        self.last_powerup_use = -GAMEPLAY.POWERUP_COOLDOWN
        
        # Load fonts
        self.score_font = self.load_font("score", 36)
        self.ui_font = self.load_font("ui", 24)
        
        print("Game scene entered - starting new game")
    
    def exit(self) -> None:
        """Clean up the game scene."""
        print("Game scene exited")
        super().exit()
    
    def pause(self) -> None:
        """Pause the game scene."""
        self.is_paused = True
        print("Game paused")
    
    def resume(self) -> None:
        """Resume the game scene."""
        self.is_paused = False
        print("Game resumed")
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update game logic."""
        if self.is_paused:
            return None
        
        current_time = pygame.time.get_ticks()
        
        # Update powerup system
        if self.invincible and current_time - self.powerup_start_time >= GAMEPLAY.POWERUP_DURATION:
            self.invincible = False
            self.bird.set_invincible(False)
        
        # Update bird
        if self.bird:
            self.bird.update(dt)
            
            # Check for ground/ceiling collision
            if not self.invincible and (self.bird.is_touching_ground() or self.bird.is_touching_ceiling()):
                return GameState.GAME_OVER
        
        # Update pipes
        if self.pipe_manager:
            self.pipe_manager.update(dt)
            
            # Check for scoring
            if self.bird:
                score_increment = self.pipe_manager.check_scoring(int(self.bird.x))
                self.score += score_increment
            
            # Check for pipe collisions
            if not self.invincible and self.bird:
                bird_pos = (int(self.bird.x), int(self.bird.y))
                if self.pipe_manager.check_collisions(bird_pos, self.bird.radius):
                    return GameState.GAME_OVER
        
        return None
    
    def render(self) -> None:
        """Render the game scene."""
        # Clear screen with background color
        self.screen.fill(COLORS.BLUE)
        
        # Draw pipes
        if self.pipe_manager:
            self.pipe_manager.draw_all(self.screen)
        
        # Draw bird
        if self.bird:
            self.bird.draw(self.screen, self.invincible)
        
        # Draw UI
        self._draw_ui()
        
        # Draw pause overlay if paused
        if self.is_paused:
            self._draw_pause_overlay()
    
    def _draw_ui(self) -> None:
        """Draw the user interface elements."""
        current_time = pygame.time.get_ticks()
        
        # Draw score
        if self.score_font:
            score_text = self.score_font.render(f"Score: {self.score}", True, COLORS.WHITE)
            self.screen.blit(score_text, (10, 10))
        
        # Draw powerup status
        if self.ui_font:
            if self.invincible:
                remaining_time = (GAMEPLAY.POWERUP_DURATION - (current_time - self.powerup_start_time)) / 1000
                powerup_text = self.ui_font.render(f"INVINCIBLE: {remaining_time:.1f}s", True, COLORS.YELLOW)
                self.screen.blit(powerup_text, (10, 50))
            else:
                cooldown_remaining = max(0, (GAMEPLAY.POWERUP_COOLDOWN - (current_time - self.last_powerup_use)) / 1000)
                if cooldown_remaining > 0:
                    cooldown_text = self.ui_font.render(f"Powerup cooldown: {cooldown_remaining:.1f}s", True, COLORS.RED)
                    self.screen.blit(cooldown_text, (10, 50))
                else:
                    ready_text = self.ui_font.render("Press A for invincibility!", True, COLORS.WHITE)
                    self.screen.blit(ready_text, (10, 50))
        
        # Draw controls hint
        if self.ui_font:
            controls_text = self.ui_font.render("SPACE: Jump | A: Powerup | ESC: Pause", True, COLORS.WHITE)
            text_rect = controls_text.get_rect()
            self.screen.blit(controls_text, (DISPLAY.SCREEN_WIDTH - text_rect.width - 10, DISPLAY.SCREEN_HEIGHT - text_rect.height - 10))
    
    def _draw_pause_overlay(self) -> None:
        """Draw the pause overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((DISPLAY.SCREEN_WIDTH, DISPLAY.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        if self.score_font:
            self.draw_centered_text("PAUSED", self.score_font, COLORS.WHITE, -50)
        
        if self.ui_font:
            self.draw_centered_text("Press ESC or P to resume", self.ui_font, COLORS.WHITE, 0)
            self.draw_centered_text("Press Q to quit to menu", self.ui_font, COLORS.WHITE, 30)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            # Jump
            if event.key == pygame.K_SPACE and not self.is_paused:
                if self.bird:
                    self.bird.jump()
                return True
            
            # Powerup
            elif event.key == pygame.K_a and not self.is_paused:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_powerup_use >= GAMEPLAY.POWERUP_COOLDOWN:
                    self.invincible = True
                    self.powerup_start_time = current_time
                    self.last_powerup_use = current_time
                    if self.bird:
                        self.bird.set_invincible(True)
                return True
            
            # Quit to menu (when paused)
            elif event.key == pygame.K_q and self.is_paused:
                return False  # Let the state manager handle this
        
        return False
    
    def reset_game(self) -> None:
        """Reset the game to initial state."""
        # Reset entities
        if self.bird:
            self.bird.reset()
        
        if self.pipe_manager:
            self.pipe_manager.reset()
        
        # Reset game state
        self.score = 0
        self.is_paused = False
        
        # Reset powerup system
        self.invincible = False
        self.powerup_start_time = 0
        self.last_powerup_use = -GAMEPLAY.POWERUP_COOLDOWN
        
        print("Game reset")
    
    def get_score(self) -> int:
        """Get the current score."""
        return self.score
    
    def get_game_stats(self) -> dict:
        """Get game statistics for debugging or display."""
        stats = {
            'score': self.score,
            'is_paused': self.is_paused,
            'invincible': self.invincible,
            'bird_stats': self.bird.get_stats() if self.bird else None,
            'pipe_count': self.pipe_manager.get_pipe_count() if self.pipe_manager else 0
        }
        
        if self.invincible:
            current_time = pygame.time.get_ticks()
            stats['powerup_remaining'] = max(0, (GAMEPLAY.POWERUP_DURATION - (current_time - self.powerup_start_time)) / 1000)
        
        return stats
