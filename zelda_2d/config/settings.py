"""
Configuration settings for zelda_2d.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DisplayConfig:
    SCREEN_WIDTH: int = 800
    SCREEN_HEIGHT: int = 600
    FPS: int = 60
    WINDOW_TITLE: str = "Zelda 2D"


@dataclass
class GameplayConfig:
    TILE_SIZE: int = 16
    PLAYER_START_X: int = 100
    PLAYER_START_Y: int = 100
    MAX_ENTITIES: int = 200


@dataclass
class SaveConfig:
    SAVE_DIR: str = "saves"
    SAVE_EXTENSION: str = ".json"
    MAX_SAVE_SIZE_BYTES: int = 10 * 1024 * 1024


@dataclass
class SecurityConfig:
    ASSET_MANIFEST: str = "assets_manifest.json"
    ALLOW_UNTRUSTED_ASSETS: bool = False


DISPLAY = DisplayConfig()
GAMEPLAY = GameplayConfig()
SAVE = SaveConfig()
SECURITY = SecurityConfig()


def validate_config() -> None:
    if DISPLAY.SCREEN_WIDTH <= 0 or DISPLAY.SCREEN_HEIGHT <= 0:
        raise ValueError("Screen dimensions must be positive")
    if DISPLAY.FPS <= 0:
        raise ValueError("FPS must be positive")
    if GAMEPLAY.TILE_SIZE <= 0:
        raise ValueError("Tile size must be positive")
    if SAVE.MAX_SAVE_SIZE_BYTES <= 0:
        raise ValueError("Max save size must be positive")
    save_path = Path(SAVE.SAVE_DIR)
    if any(part == ".." for part in save_path.parts):
        raise ValueError("Save directory must not contain parent references")


validate_config()
