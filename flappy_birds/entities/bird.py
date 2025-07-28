"""
Bird entity for Flappy Birds game.
Represents the player-controlled bird character with physics-based movement.
"""

import pygame
from typing import Tuple

from config.settings import PHYSICS, GAMEPLAY, COLORS, DISPLAY


class Bird:
    """
    Represents the player-controlled bird character.

    The bird has physics-based movement with gravity and jumping mechanics.
    It can be rendered in different colors based on powerup status.
    """
    
    def __init__(self, x: int = None, y: int = None):
        """
        Initialize the bird.
        
        Args:
            x: Starting x position (defaults to config value)
            y: Starting y position (defaults to screen center)
        """
        self.x = x if x is not None else GAMEPLAY.BIRD_START_X
        self.y = y if y is not None else DISPLAY.SCREEN_HEIGHT // 2
        self.radius = GAMEPLAY.BIRD_RADIUS
        self.velocity = 0.0
        
        # Visual properties
        self.normal_color = COLORS.WHITE
        self.invincible_color = COLORS.YELLOW
        
        # State tracking
        self.is_invincible = False
        self.jump_count = 0  # For potential multi-jump mechanics
    
    def update(self, dt: float) -> None:
        """
        Update bird physics for one frame.
        
        Args:
            dt: Time since last frame in seconds
        """
        # Apply gravity
        self.velocity += PHYSICS.GRAVITY * dt
        
        # Update position
        self.y += self.velocity * dt
        
        # Clamp position to screen bounds (with some tolerance for collision detection)
        self.y = max(-self.radius, min(DISPLAY.SCREEN_HEIGHT + self.radius, self.y))
    
    def jump(self) -> None:
        """Make the bird jump by setting upward velocity."""
        self.velocity = PHYSICS.BIRD_JUMP
        self.jump_count += 1
    
    def draw(self, screen: pygame.Surface, invincible: bool = False) -> None:
        """
        Draw the bird on the screen.
        
        Args:
            screen: Pygame surface to draw on
            invincible: Whether to draw in invincible color
        """
        color = self.invincible_color if invincible else self.normal_color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Optional: Draw a simple eye
        eye_offset_x = self.radius // 3
        eye_offset_y = -self.radius // 4
        eye_radius = max(2, self.radius // 5)
        eye_pos = (int(self.x + eye_offset_x), int(self.y + eye_offset_y))
        pygame.draw.circle(screen, COLORS.WHITE if not invincible else COLORS.RED, eye_pos, eye_radius)
    
    def get_rect(self) -> pygame.Rect:
        """
        Get the bird's bounding rectangle for collision detection.
        
        Returns:
            pygame.Rect: Rectangle representing bird's bounds
        """
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
    
    def get_collision_circle(self) -> Tuple[Tuple[int, int], int]:
        """
        Get the bird's collision circle (center and radius).
        
        Returns:
            Tuple[Tuple[int, int], int]: ((x, y), radius) for circle collision
        """
        return ((int(self.x), int(self.y)), self.radius)
    
    def is_off_screen(self) -> bool:
        """
        Check if bird is completely off screen (for game over detection).
        
        Returns:
            bool: True if bird is off screen
        """
        return (self.y + self.radius < 0 or 
                self.y - self.radius > DISPLAY.SCREEN_HEIGHT)
    
    def is_touching_ground(self) -> bool:
        """
        Check if bird is touching the ground.
        
        Returns:
            bool: True if touching ground
        """
        return self.y + self.radius >= DISPLAY.SCREEN_HEIGHT
    
    def is_touching_ceiling(self) -> bool:
        """
        Check if bird is touching the ceiling.
        
        Returns:
            bool: True if touching ceiling
        """
        return self.y - self.radius <= 0
    
    def reset(self, x: int = None, y: int = None) -> None:
        """
        Reset bird to initial state.
        
        Args:
            x: Reset x position (defaults to config value)
            y: Reset y position (defaults to screen center)
        """
        self.x = x if x is not None else GAMEPLAY.BIRD_START_X
        self.y = y if y is not None else DISPLAY.SCREEN_HEIGHT // 2
        self.velocity = 0.0
        self.is_invincible = False
        self.jump_count = 0
    
    def set_invincible(self, invincible: bool) -> None:
        """
        Set the bird's invincibility status.
        
        Args:
            invincible: Whether the bird should be invincible
        """
        self.is_invincible = invincible
    
    def get_stats(self) -> dict:
        """
        Get bird statistics for debugging or display.
        
        Returns:
            dict: Dictionary containing bird stats
        """
        return {
            'position': (self.x, self.y),
            'velocity': self.velocity,
            'jump_count': self.jump_count,
            'is_invincible': self.is_invincible,
            'on_ground': self.is_touching_ground(),
            'on_ceiling': self.is_touching_ceiling()
        }
