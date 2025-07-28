"""
Game Over scene for Flappy Birds.
Displays final score and options to restart or return to menu.
"""

import pygame
from typing import Optional

from scenes.base_scene import BaseScene
from core.state_manager import GameState
from config.settings import DISPLAY, COLORS


class GameOverScene(BaseScene):
    """
    Game over scene.
    
    Features:
    - Final score display
    - High score tracking (if implemented)
    - Options to restart or return to menu
    - Game statistics display
    - Animated elements
    """
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        
        # Game over state
        self.final_score = 0
        self.high_score = 0  # TODO: Load from persistent storage
        self.is_new_high_score = False
        
        # Menu state
        self.selected_option = 0
        self.menu_options = [
            "Play Again",
            "Main Menu"
        ]
        
        # Fonts
        self.title_font = None
        self.score_font = None
        self.menu_font = None
        self.subtitle_font = None
        
        # Animation
        self.animation_time = 0.0
        self.fade_alpha = 0
        self.score_scale = 1.0
        
        # Colors
        self.selected_color = COLORS.YELLOW
        self.normal_color = COLORS.WHITE
        self.score_color = COLORS.WHITE
        self.high_score_color = COLORS.YELLOW
    
    def enter(self) -> None:
        """Initialize the game over scene."""
        super().enter()
        
        # Load fonts
        self.title_font = self.load_font("title", 48)
        self.score_font = self.load_font("score", 36)
        self.menu_font = self.load_font("menu", 32)
        self.subtitle_font = self.load_font("subtitle", 24)
        
        # Reset animation
        self.animation_time = 0.0
        self.fade_alpha = 0
        self.score_scale = 1.0
        self.selected_option = 0
        
        # TODO: Load high score from file
        # For now, just track session high score
        if self.final_score > self.high_score:
            self.high_score = self.final_score
            self.is_new_high_score = True
        else:
            self.is_new_high_score = False
        
        print(f"Game over scene entered - Final score: {self.final_score}")
    
    def exit(self) -> None:
        """Clean up the game over scene."""
        print("Game over scene exited")
        super().exit()
    
    def set_final_score(self, score: int) -> None:
        """Set the final score to display."""
        self.final_score = score
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update game over scene animations."""
        # Update animation timer
        self.animation_time += dt
        
        # Fade in effect
        if self.fade_alpha < 255:
            self.fade_alpha = min(255, self.fade_alpha + 300 * dt)
        
        # Score scale animation for new high score
        if self.is_new_high_score:
            import math
            self.score_scale = 1.0 + 0.1 * math.sin(self.animation_time * 4)
        
        return None
    
    def render(self) -> None:
        """Render the game over scene."""
        # Clear screen with background color
        self.screen.fill(COLORS.BLUE)
        
        # Draw background overlay
        self._draw_background_overlay()
        
        # Draw game over title
        self._draw_title()
        
        # Draw scores
        self._draw_scores()
        
        # Draw menu options
        self._draw_menu_options()
        
        # Draw instructions
        self._draw_instructions()
        
        # Draw statistics (optional)
        self._draw_statistics()
    
    def _draw_background_overlay(self) -> None:
        """Draw semi-transparent background overlay."""
        overlay = pygame.Surface((DISPLAY.SCREEN_WIDTH, DISPLAY.SCREEN_HEIGHT))
        overlay.set_alpha(min(128, self.fade_alpha // 2))
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
    
    def _draw_title(self) -> None:
        """Draw the game over title."""
        if not self.title_font:
            return
        
        # Main title
        title_color = (*COLORS.RED, min(255, int(self.fade_alpha)))
        title_text = self.title_font.render("GAME OVER", True, COLORS.RED)
        title_pos = self.center_text(title_text, -200)
        
        # Apply fade effect
        if self.fade_alpha < 255:
            title_surface = pygame.Surface(title_text.get_size())
            title_surface.set_alpha(self.fade_alpha)
            title_surface.blit(title_text, (0, 0))
            self.screen.blit(title_surface, title_pos)
        else:
            self.screen.blit(title_text, title_pos)
    
    def _draw_scores(self) -> None:
        """Draw the final score and high score."""
        if not self.score_font:
            return
        
        # Final score
        score_text = f"Final Score: {self.final_score}"
        score_color = self.high_score_color if self.is_new_high_score else self.score_color
        
        # Apply scale animation for new high score
        if self.is_new_high_score:
            # Create scaled font
            scaled_size = int(36 * self.score_scale)
            scaled_font = self.load_font("score_scaled", scaled_size)
            score_surface = scaled_font.render(score_text, True, score_color)
        else:
            score_surface = self.score_font.render(score_text, True, score_color)
        
        score_pos = self.center_text(score_surface, -100)
        self.screen.blit(score_surface, score_pos)
        
        # New high score indicator
        if self.is_new_high_score and self.subtitle_font:
            new_high_text = self.subtitle_font.render("NEW HIGH SCORE!", True, COLORS.YELLOW)
            new_high_pos = self.center_text(new_high_text, -60)
            self.screen.blit(new_high_text, new_high_pos)
        
        # High score display
        if self.subtitle_font and not self.is_new_high_score:
            high_score_text = f"High Score: {self.high_score}"
            high_score_surface = self.subtitle_font.render(high_score_text, True, self.high_score_color)
            high_score_pos = self.center_text(high_score_surface, -60)
            self.screen.blit(high_score_surface, high_score_pos)
    
    def _draw_menu_options(self) -> None:
        """Draw the menu options."""
        if not self.menu_font:
            return
        
        start_y = DISPLAY.SCREEN_HEIGHT // 2 + 50
        option_spacing = 50
        
        for i, option in enumerate(self.menu_options):
            # Choose color based on selection
            color = self.selected_color if i == self.selected_option else self.normal_color
            
            # Render text
            option_text = self.menu_font.render(option, True, color)
            
            # Calculate position
            y = start_y + i * option_spacing
            pos = self.center_text(option_text, y - DISPLAY.SCREEN_HEIGHT // 2)
            
            # Draw selection indicator
            if i == self.selected_option:
                indicator_x = pos[0] - 25
                indicator_y = pos[1] + option_text.get_height() // 2
                pygame.draw.polygon(self.screen, self.selected_color, [
                    (indicator_x, indicator_y - 8),
                    (indicator_x, indicator_y + 8),
                    (indicator_x + 12, indicator_y)
                ])
            
            # Draw option text
            self.screen.blit(option_text, pos)
    
    def _draw_instructions(self) -> None:
        """Draw control instructions."""
        if not self.subtitle_font:
            return
        
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Press ENTER to select",
            "Press R to restart quickly"
        ]
        
        start_y = DISPLAY.SCREEN_HEIGHT - 100
        for i, instruction in enumerate(instructions):
            text = self.subtitle_font.render(instruction, True, COLORS.WHITE)
            pos = self.center_text(text, start_y - DISPLAY.SCREEN_HEIGHT // 2 + i * 20)
            self.screen.blit(text, pos)
    
    def _draw_statistics(self) -> None:
        """Draw game statistics (optional)."""
        # TODO: Implement game statistics display
        # Could show things like:
        # - Total games played
        # - Average score
        # - Best streak
        # - Time played
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle game over input events."""
        if event.type == pygame.KEYDOWN:
            # Navigate menu
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                return True
            
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                return True
            
            # Select option
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self._handle_menu_selection()
            
            # Quick restart
            elif event.key == pygame.K_r:
                self.selected_option = 0  # Play Again
                return self._handle_menu_selection()
            
            # Quick menu
            elif event.key == pygame.K_m:
                self.selected_option = 1  # Main Menu
                return self._handle_menu_selection()
        
        return False
    
    def _handle_menu_selection(self) -> bool:
        """Handle menu option selection."""
        selected = self.menu_options[self.selected_option]
        
        if selected == "Play Again":
            # Signal to restart the game
            return False  # Let state manager handle transition to PLAYING
        
        elif selected == "Main Menu":
            # Signal to return to menu
            return False  # Let state manager handle transition to MENU
        
        return False
    
    def get_selected_option(self) -> str:
        """Get the currently selected menu option."""
        return self.menu_options[self.selected_option]
    
    def get_final_score(self) -> int:
        """Get the final score."""
        return self.final_score
    
    def get_high_score(self) -> int:
        """Get the high score."""
        return self.high_score
    
    def is_high_score(self) -> bool:
        """Check if the final score is a new high score."""
        return self.is_new_high_score


class ScoreManager:
    """
    Helper class to manage score persistence and statistics.
    Handles saving/loading high scores and game statistics.
    """
    
    def __init__(self, save_file: str = "flappy_bird_scores.json"):
        self.save_file = save_file
        self.high_score = 0
        self.total_games = 0
        self.total_score = 0
        self.best_streak = 0
        
        self.load_scores()
    
    def load_scores(self) -> None:
        """Load scores from file."""
        try:
            import json
            import os
            
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.high_score = data.get('high_score', 0)
                    self.total_games = data.get('total_games', 0)
                    self.total_score = data.get('total_score', 0)
                    self.best_streak = data.get('best_streak', 0)
        except Exception as e:
            print(f"Error loading scores: {e}")
    
    def save_scores(self) -> None:
        """Save scores to file."""
        try:
            import json
            
            data = {
                'high_score': self.high_score,
                'total_games': self.total_games,
                'total_score': self.total_score,
                'best_streak': self.best_streak
            }
            
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def update_score(self, score: int) -> bool:
        """
        Update scores with a new game result.
        
        Args:
            score: The score from the completed game
            
        Returns:
            bool: True if this is a new high score
        """
        self.total_games += 1
        self.total_score += score
        
        is_new_high = score > self.high_score
        if is_new_high:
            self.high_score = score
        
        self.save_scores()
        return is_new_high
    
    def get_average_score(self) -> float:
        """Get the average score across all games."""
        if self.total_games == 0:
            return 0.0
        return self.total_score / self.total_games
    
    def reset_statistics(self) -> None:
        """Reset all statistics."""
        self.high_score = 0
        self.total_games = 0
        self.total_score = 0
        self.best_streak = 0
        self.save_scores()
