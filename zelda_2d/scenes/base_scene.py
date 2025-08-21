"""
Base scene for zelda_2d.
"""

from abc import ABC, abstractmethod
from typing import Optional

try:
    import pygame
except Exception:
    pygame = None


class BaseScene(ABC):
    def __init__(self, screen: Optional['pygame.Surface'] = None):
        self.screen = screen
        self.is_active = False
        self.fonts = {}
        self.sounds = {}
        self.images = {}

    def enter(self) -> None:
        self.is_active = True

    def exit(self) -> None:
        self.is_active = False
        self.cleanup_resources()

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def handle_event(self, event) -> bool:
        return False

    def pause(self) -> None:
        return None

    def resume(self) -> None:
        return None

    def cleanup_resources(self) -> None:
        self.fonts.clear()
        self.sounds.clear()
        self.images.clear()

    def load_font(self, name: str, size: int, font_path: Optional[str] = None):
        if not pygame:
            return None
        key = f"{name}_{size}"
        if key not in self.fonts:
            self.fonts[key] = pygame.font.Font(font_path, size)
        return self.fonts[key]

    def center_text(self, text_surface, y_offset: int = 0):
        screen_rect = self.screen.get_rect()
        text_rect = text_surface.get_rect()
        x = screen_rect.centerx - text_rect.width // 2
        y = screen_rect.centery - text_rect.height // 2 + y_offset
        return (x, y)

    def draw_centered_text(self, text: str, font, color, y_offset: int = 0) -> None:
        if not font:
            return
        text_surface = font.render(text, True, color)
        pos = self.center_text(text_surface, y_offset)
        self.screen.blit(text_surface, pos)
