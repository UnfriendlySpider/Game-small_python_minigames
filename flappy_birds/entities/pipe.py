"""
Pipe entity for Flappy Birds game.
Represents a pair of pipes (top and bottom) that the bird must navigate through.
"""

import pygame
import random
from typing import Tuple, List

from config.settings import PHYSICS, GAMEPLAY, COLORS, DISPLAY


class Pipe:
    """
    Represents a pair of pipes (top and bottom) that the bird must navigate through.
    
    Features:
    - Configurable gap size and position
    - Collision detection methods
    - Visual rendering with optional variations
    - Movement and lifecycle management
    """
    
    def __init__(self, x: int, gap_size: int = None, gap_center: int = None):
        """
        Initialize a pipe pair.
        
        Args:
            x: X position of the pipe
            gap_size: Size of the gap between pipes (defaults to config value)
            gap_center: Y position of gap center (random if None)
        """
        self.x = x
        self.width = GAMEPLAY.PIPE_WIDTH
        self.gap_size = gap_size if gap_size is not None else GAMEPLAY.PIPE_GAP
        
        # Calculate gap position
        if gap_center is None:
            min_gap_center = self.gap_size // 2 + 50
            max_gap_center = DISPLAY.SCREEN_HEIGHT - self.gap_size // 2 - 50
            self.gap_center = random.randint(min_gap_center, max_gap_center)
        else:
            self.gap_center = gap_center
        
        # Calculate pipe heights
        self.top_height = self.gap_center - self.gap_size // 2
        self.bottom_y = self.gap_center + self.gap_size // 2
        self.bottom_height = DISPLAY.SCREEN_HEIGHT - self.bottom_y
        
        # State tracking
        self.passed = False  # Whether bird has passed this pipe
        self.scored = False  # Whether this pipe has contributed to score
        
        # Visual properties
        self.color = COLORS.GREEN
        self.border_color = (0, 150, 0)  # Darker green for borders
        self.border_width = 2
    
    def update(self, dt: float) -> None:
        """
        Update pipe position for one frame.
        
        Args:
            dt: Time since last frame in seconds
        """
        self.x -= PHYSICS.PIPE_SPEED * dt
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the pipe pair on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw top pipe
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        pygame.draw.rect(screen, self.color, top_rect)
        pygame.draw.rect(screen, self.border_color, top_rect, self.border_width)
        
        # Draw bottom pipe
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, self.bottom_height)
        pygame.draw.rect(screen, self.color, bottom_rect)
        pygame.draw.rect(screen, self.border_color, bottom_rect, self.border_width)
        
        # Optional: Draw pipe caps (wider rectangles at the gap edges)
        cap_width = self.width + 6
        cap_height = 20
        cap_x = self.x - 3
        
        # Top cap
        top_cap_rect = pygame.Rect(cap_x, self.top_height - cap_height, cap_width, cap_height)
        pygame.draw.rect(screen, self.color, top_cap_rect)
        pygame.draw.rect(screen, self.border_color, top_cap_rect, self.border_width)
        
        # Bottom cap
        bottom_cap_rect = pygame.Rect(cap_x, self.bottom_y, cap_width, cap_height)
        pygame.draw.rect(screen, self.color, bottom_cap_rect)
        pygame.draw.rect(screen, self.border_color, bottom_cap_rect, self.border_width)
    
    def get_collision_rects(self) -> List[pygame.Rect]:
        """
        Get collision rectangles for both pipes.
        
        Returns:
            List[pygame.Rect]: List containing top and bottom pipe rectangles
        """
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, self.bottom_height)
        return [top_rect, bottom_rect]
    
    def check_collision_with_bird(self, bird_pos: Tuple[int, int], bird_radius: int) -> bool:
        """
        Check if bird collides with this pipe.
        
        Args:
            bird_pos: (x, y) position of bird center
            bird_radius: Radius of bird collision circle
            
        Returns:
            bool: True if collision detected
        """
        bird_x, bird_y = bird_pos
        
        # Check if bird is horizontally aligned with pipe
        if not (self.x - bird_radius < bird_x < self.x + self.width + bird_radius):
            return False
        
        # Check collision with top pipe
        if bird_y - bird_radius < self.top_height:
            return True
        
        # Check collision with bottom pipe
        if bird_y + bird_radius > self.bottom_y:
            return True
        
        return False
    
    def check_bird_passed(self, bird_x: int) -> bool:
        """
        Check if bird has passed this pipe (for scoring).
        
        Args:
            bird_x: X position of bird
            
        Returns:
            bool: True if bird has passed this pipe
        """
        if not self.passed and bird_x > self.x + self.width:
            self.passed = True
            return True
        return False
    
    def is_off_screen(self) -> bool:
        """
        Check if pipe is completely off the left side of screen.
        
        Returns:
            bool: True if pipe is off screen
        """
        return self.x + self.width < 0
    
    def is_on_screen(self) -> bool:
        """
        Check if pipe is visible on screen.
        
        Returns:
            bool: True if pipe is at least partially visible
        """
        return self.x < DISPLAY.SCREEN_WIDTH and self.x + self.width > 0
    
    def get_gap_rect(self) -> pygame.Rect:
        """
        Get rectangle representing the gap between pipes.
        
        Returns:
            pygame.Rect: Rectangle of the gap area
        """
        return pygame.Rect(
            self.x,
            self.top_height,
            self.width,
            self.gap_size
        )
    
    def set_color(self, color: Tuple[int, int, int]) -> None:
        """
        Set the pipe color.
        
        Args:
            color: RGB color tuple
        """
        self.color = color
        # Automatically calculate darker border color
        self.border_color = tuple(max(0, c - 50) for c in color)
    
    def get_stats(self) -> dict:
        """
        Get pipe statistics for debugging or display.
        
        Returns:
            dict: Dictionary containing pipe stats
        """
        return {
            'position': self.x,
            'gap_center': self.gap_center,
            'gap_size': self.gap_size,
            'top_height': self.top_height,
            'bottom_y': self.bottom_y,
            'passed': self.passed,
            'scored': self.scored,
            'on_screen': self.is_on_screen()
        }


class PipeManager:
    """
    Manages multiple pipes for the game.
    Handles pipe creation, removal, and batch operations.
    """
    
    def __init__(self, initial_pipe_x: int = None):
        """
        Initialize pipe manager.
        
        Args:
            initial_pipe_x: X position for first pipe (defaults to screen width)
        """
        self.pipes: List[Pipe] = []
        self.pipe_spacing = 300  # Distance between pipes
        self.next_pipe_x = initial_pipe_x if initial_pipe_x is not None else DISPLAY.SCREEN_WIDTH
        
        # Add initial pipe
        self.add_pipe()
    
    def add_pipe(self, x: int = None) -> Pipe:
        """
        Add a new pipe to the manager.
        
        Args:
            x: X position for new pipe (uses next_pipe_x if None)
            
        Returns:
            Pipe: The newly created pipe
        """
        pipe_x = x if x is not None else self.next_pipe_x
        pipe = Pipe(pipe_x)
        self.pipes.append(pipe)
        self.next_pipe_x = pipe_x + self.pipe_spacing
        return pipe
    
    def update(self, dt: float) -> int:
        """
        Update all pipes and manage pipe lifecycle.
        
        Args:
            dt: Time since last frame in seconds
            
        Returns:
            int: Number of pipes that were removed
        """
        removed_count = 0
        
        # Update all pipes
        for pipe in self.pipes:
            pipe.update(dt)
        
        # Remove off-screen pipes and add new ones
        self.pipes = [pipe for pipe in self.pipes if not pipe.is_off_screen()]
        removed_count = len(self.pipes) - len([pipe for pipe in self.pipes if not pipe.is_off_screen()])
        
        # Add new pipes as needed
        while len(self.pipes) < 3:  # Keep at least 3 pipes
            self.add_pipe()
        
        return removed_count
    
    def draw_all(self, screen: pygame.Surface) -> None:
        """
        Draw all pipes on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        for pipe in self.pipes:
            if pipe.is_on_screen():
                pipe.draw(screen)
    
    def check_collisions(self, bird_pos: Tuple[int, int], bird_radius: int) -> bool:
        """
        Check if bird collides with any pipe.
        
        Args:
            bird_pos: (x, y) position of bird center
            bird_radius: Radius of bird collision circle
            
        Returns:
            bool: True if collision detected with any pipe
        """
        for pipe in self.pipes:
            if pipe.check_collision_with_bird(bird_pos, bird_radius):
                return True
        return False
    
    def check_scoring(self, bird_x: int) -> int:
        """
        Check for scoring opportunities and return score increment.
        
        Args:
            bird_x: X position of bird
            
        Returns:
            int: Score increment (number of pipes passed)
        """
        score_increment = 0
        for pipe in self.pipes:
            if pipe.check_bird_passed(bird_x) and not pipe.scored:
                pipe.scored = True
                score_increment += 1
        return score_increment
    
    def reset(self) -> None:
        """Reset pipe manager to initial state."""
        self.pipes.clear()
        self.next_pipe_x = DISPLAY.SCREEN_WIDTH
        self.add_pipe()
    
    def get_pipe_count(self) -> int:
        """Get current number of pipes."""
        return len(self.pipes)
