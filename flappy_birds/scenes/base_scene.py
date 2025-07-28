"""
Base scene class for Flappy Birds game scenes.
Provides common interface and functionality for all game scenes.
"""

from abc import ABC, abstractmethod
from typing import Optional
import pygame

from core.state_manager import GameState


class BaseScene(ABC):
    """
    Abstract base class for all game scenes.
    
    Defines the standard interface that all scenes must implement
    and provides common functionality for scene management.
    """
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.is_active = False
        self.needs_cleanup = False
        
        # Scene-specific resources
        self.fonts = {}
        self.sounds = {}
        self.images = {}
    
    @abstractmethod
    def enter(self) -> None:
        """
        Called when entering this scene.
        Initialize scene-specific resources and state.
        """
        self.is_active = True
        self.needs_cleanup = False
    
    @abstractmethod
    def exit(self) -> None:
        """
        Called when exiting this scene.
        Clean up scene-specific resources.
        """
        self.is_active = False
        self.cleanup_resources()
    
    @abstractmethod
    def update(self, dt: float) -> Optional[GameState]:
        """
        Update scene logic for one frame.
        
        Args:
            dt: Time since last frame in seconds
            
        Returns:
            Optional[GameState]: New state to transition to, or None to stay in current state
        """
        pass
    
    @abstractmethod
    def render(self) -> None:
        """
        Render the scene to the screen.
        Should not modify game state, only draw.
        """
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        pass
    
    def pause(self) -> None:
        """
        Called when scene is paused (but not exited).
        Override in subclasses if needed.
        """
        pass
    
    def resume(self) -> None:
        """
        Called when scene is resumed from pause.
        Override in subclasses if needed.
        """
        pass
    
    def cleanup_resources(self) -> None:
        """
        Clean up scene-specific resources.
        Called automatically on exit, but can be called manually.
        """
        # Clear fonts
        for font in self.fonts.values():
            if hasattr(font, 'quit'):
                font.quit()
        self.fonts.clear()
        
        # Clear sounds (pygame handles sound cleanup automatically)
        self.sounds.clear()
        
        # Clear images (pygame handles surface cleanup automatically)
        self.images.clear()
        
        self.needs_cleanup = False
    
    def load_font(self, name: str, size: int, font_path: Optional[str] = None) -> pygame.font.Font:
        """
        Load and cache a font.
        
        Args:
            name: Name to cache the font under
            size: Font size
            font_path: Path to font file, or None for default font
            
        Returns:
            pygame.font.Font: The loaded font
        """
        font_key = f"{name}_{size}"
        if font_key not in self.fonts:
            self.fonts[font_key] = pygame.font.Font(font_path, size)
        return self.fonts[font_key]
    
    def get_font(self, name: str, size: int) -> Optional[pygame.font.Font]:
        """
        Get a previously loaded font.
        
        Args:
            name: Name the font was cached under
            size: Font size
            
        Returns:
            Optional[pygame.font.Font]: The font if found, None otherwise
        """
        font_key = f"{name}_{size}"
        return self.fonts.get(font_key)
    
    def center_text(self, text_surface: pygame.Surface, y_offset: int = 0) -> tuple:
        """
        Calculate position to center text horizontally on screen.
        
        Args:
            text_surface: The rendered text surface
            y_offset: Vertical offset from center
            
        Returns:
            tuple: (x, y) position to center the text
        """
        screen_rect = self.screen.get_rect()
        text_rect = text_surface.get_rect()
        x = screen_rect.centerx - text_rect.width // 2
        y = screen_rect.centery - text_rect.height // 2 + y_offset
        return (x, y)
    
    def draw_centered_text(self, text: str, font: pygame.font.Font, color: tuple, y_offset: int = 0) -> None:
        """
        Draw text centered horizontally on the screen.
        
        Args:
            text: Text to draw
            font: Font to use
            color: Text color
            y_offset: Vertical offset from center
        """
        text_surface = font.render(text, True, color)
        pos = self.center_text(text_surface, y_offset)
        self.screen.blit(text_surface, pos)
    
    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        if not self.needs_cleanup:
            self.cleanup_resources()
