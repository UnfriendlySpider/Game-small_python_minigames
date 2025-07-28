"""
Game configuration settings for Flappy Birds.
Contains all game constants and configuration values.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class DisplayConfig:
    """Display and rendering configuration."""
    SCREEN_WIDTH: int = 400
    SCREEN_HEIGHT: int = 600
    FPS: int = 60
    WINDOW_TITLE: str = "Flappy Bird"


@dataclass
class ColorConfig:
    """Color definitions for game elements."""
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    BLUE: Tuple[int, int, int] = (135, 206, 250)
    GREEN: Tuple[int, int, int] = (0, 200, 0)
    YELLOW: Tuple[int, int, int] = (255, 255, 0)
    RED: Tuple[int, int, int] = (255, 0, 0)


@dataclass
class PhysicsConfig:
    """Physics and movement configuration."""
    GRAVITY: float = 800.0          # pixels per second squared
    BIRD_JUMP: float = -300.0       # pixels per second (initial jump velocity)
    PIPE_SPEED: float = 180.0       # pixels per second


@dataclass
class GameplayConfig:
    """Gameplay mechanics configuration."""
    PIPE_GAP: int = 150
    PIPE_WIDTH: int = 50
    BIRD_RADIUS: int = 15
    BIRD_START_X: int = 50
    
    # Powerup configuration
    POWERUP_DURATION: int = 5000    # milliseconds
    POWERUP_COOLDOWN: int = 10000   # milliseconds


@dataclass
class GameStates:
    """Game state definitions."""
    RUNNING: str = "running"
    GAME_OVER: str = "game_over"
    MENU: str = "menu"
    PAUSED: str = "paused"


# Global configuration instances
DISPLAY = DisplayConfig()
COLORS = ColorConfig()
PHYSICS = PhysicsConfig()
GAMEPLAY = GameplayConfig()
STATES = GameStates()


def validate_config():
    """Validate configuration values for consistency."""
    if DISPLAY.SCREEN_WIDTH <= 0 or DISPLAY.SCREEN_HEIGHT <= 0:
        raise ValueError("Screen dimensions must be positive")
    
    if DISPLAY.FPS <= 0:
        raise ValueError("FPS must be positive")
    
    if GAMEPLAY.PIPE_GAP <= 0:
        raise ValueError("Pipe gap must be positive")
    
    if GAMEPLAY.BIRD_RADIUS <= 0:
        raise ValueError("Bird radius must be positive")
    
    if PHYSICS.GRAVITY <= 0:
        raise ValueError("Gravity must be positive")


# Validate configuration on import
validate_config()
