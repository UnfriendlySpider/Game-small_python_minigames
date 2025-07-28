"""
Game configuration settings for Text Adventure Game.
Contains all game constants and configuration values.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class GameConfig:
    """General game configuration."""
    GAME_TITLE: str = "Text Adventure Game"
    VERSION: str = "2.0.0"
    AUTHOR: str = "Game Developer"
    MAX_SAVE_SLOTS: int = 5
    AUTO_SAVE: bool = True
    AUTO_SAVE_INTERVAL: int = 300  # seconds


@dataclass
class PlayerConfig:
    """Player-related configuration."""
    MAX_INVENTORY_SIZE: int = 10
    STARTING_HEALTH: int = 100
    STARTING_ENERGY: int = 100
    STARTING_LOCATION: str = "start_room"


@dataclass
class GameplayConfig:
    """Gameplay mechanics configuration."""
    COMMAND_HISTORY_SIZE: int = 50
    MAX_COMMAND_LENGTH: int = 100
    CASE_SENSITIVE_COMMANDS: bool = False
    ENABLE_SHORTCUTS: bool = True
    ENABLE_HINTS: bool = True


@dataclass
class DisplayConfig:
    """Display and text formatting configuration."""
    LINE_WIDTH: int = 80
    SEPARATOR_CHAR: str = "="
    PROMPT_SYMBOL: str = "> "
    ERROR_PREFIX: str = "[ERROR] "
    INFO_PREFIX: str = "[INFO] "
    SUCCESS_PREFIX: str = "[SUCCESS] "


@dataclass
class FileConfig:
    """File and directory configuration."""
    SAVE_DIR: str = "saves"
    SAVE_EXTENSION: str = ".json"
    CONFIG_FILE: str = "game_config.json"
    LOG_FILE: str = "game.log"


# Global configuration instances
GAME = GameConfig()
PLAYER = PlayerConfig()
GAMEPLAY = GameplayConfig()
DISPLAY = DisplayConfig()
FILES = FileConfig()

# Command shortcuts mapping
COMMAND_SHORTCUTS: Dict[str, str] = {
    "n": "go north",
    "s": "go south",
    "e": "go east",
    "w": "go west",
    "ne": "go northeast",
    "nw": "go northwest",
    "se": "go southeast",
    "sw": "go southwest",
    "u": "go up",
    "d": "go down",
    "l": "look",
    "i": "inventory",
    "inv": "inventory",
    "q": "quit",
    "h": "help",
    "?": "help"
}

# Available directions
DIRECTIONS = [
    "north", "south", "east", "west",
    "northeast", "northwest", "southeast", "southwest",
    "up", "down", "in", "out"
]

# Direction aliases
DIRECTION_ALIASES: Dict[str, str] = {
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "ne": "northeast",
    "nw": "northwest",
    "se": "southeast",
    "sw": "southwest",
    "u": "up",
    "d": "down"
}


def validate_config():
    """Validate configuration values for consistency."""
    if PLAYER.MAX_INVENTORY_SIZE <= 0:
        raise ValueError("Max inventory size must be positive")
    
    if PLAYER.STARTING_HEALTH <= 0:
        raise ValueError("Starting health must be positive")
    
    if PLAYER.STARTING_ENERGY <= 0:
        raise ValueError("Starting energy must be positive")
    
    if GAMEPLAY.COMMAND_HISTORY_SIZE <= 0:
        raise ValueError("Command history size must be positive")
    
    if DISPLAY.LINE_WIDTH <= 0:
        raise ValueError("Line width must be positive")


def get_all_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary."""
    return {
        "game": GAME.__dict__,
        "player": PLAYER.__dict__,
        "gameplay": GAMEPLAY.__dict__,
        "display": DISPLAY.__dict__,
        "files": FILES.__dict__,
        "shortcuts": COMMAND_SHORTCUTS,
        "directions": DIRECTIONS,
        "direction_aliases": DIRECTION_ALIASES
    }


# Validate configuration on import
validate_config()
