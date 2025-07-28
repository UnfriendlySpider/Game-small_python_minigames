"""
Menu scene for Flappy Birds.
Displays the main menu with options to start game, view settings, etc.
"""

import pygame
from typing import Optional

from scenes.base_scene import BaseScene
from core.state_manager import GameState
from config.settings import DISPLAY, COLORS


class MenuScene(BaseScene):
    """
    Main menu scene.
    
    Features:
    - Title display
    - Menu options (Start Game, Settings, Quit)
    - Keyboard navigation
    - Background animation (optional)
    """
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        
        # Menu state
        self.selected_option = 0
        self.menu_options = [
            "Start Game",
            "Quit"
        ]
        
        # Fonts
        self.title_font = None
        self.menu_font = None
        self.subtitle_font = None
        
        # Animation
        self.animation_time = 0.0
        self.title_bounce_offset = 0
        
        # Colors
        self.selected_color = COLORS.YELLOW
        self.normal_color = COLORS.WHITE
        self.title_color = COLORS.WHITE
    
    def enter(self) -> None:
        """Initialize the menu scene."""
        super().enter()
        
        # Load fonts
        self.title_font = self.load_font("title", 72)
        self.menu_font = self.load_font("menu", 36)
        self.subtitle_font = self.load_font("subtitle", 24)
        
        # Reset animation
        self.animation_time = 0.0
        self.selected_option = 0
        
        print("Menu scene entered")
    
    def exit(self) -> None:
        """Clean up the menu scene."""
        print("Menu scene exited")
        super().exit()
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update menu logic and animations."""
        # Update animation timer
        self.animation_time += dt
        
        # Calculate title bounce effect
        import math
        self.title_bounce_offset = int(math.sin(self.animation_time * 2) * 10)
        
        return None
    
    def render(self) -> None:
        """Render the menu scene."""
        # Clear screen with background color
        self.screen.fill(COLORS.BLUE)
        
        # Draw animated background elements (optional)
        self._draw_background_elements()
        
        # Draw title
        self._draw_title()
        
        # Draw menu options
        self._draw_menu_options()
        
        # Draw instructions
        self._draw_instructions()
        
        # Draw version info
        self._draw_version_info()
    
    def _draw_background_elements(self) -> None:
        """Draw animated background elements."""
        # Draw some simple animated clouds or pipes in background
        import math
        
        # Animated background pipes (decorative)
        pipe_color = (0, 100, 0)  # Darker green
        for i in range(3):
            x = 50 + i * 150 + int(math.sin(self.animation_time + i) * 20)
            y_offset = int(math.sin(self.animation_time * 0.5 + i * 2) * 30)
            
            # Top pipe
            pipe_rect = pygame.Rect(x, 0 + y_offset, 40, 200)
            pygame.draw.rect(self.screen, pipe_color, pipe_rect)
            
            # Bottom pipe
            pipe_rect = pygame.Rect(x, DISPLAY.SCREEN_HEIGHT - 200 + y_offset, 40, 200)
            pygame.draw.rect(self.screen, pipe_color, pipe_rect)
    
    def _draw_title(self) -> None:
        """Draw the game title."""
        if not self.title_font:
            return
        
        # Main title
        title_text = self.title_font.render("Flappy Bird", True, self.title_color)
        title_pos = self.center_text(title_text, -150 + self.title_bounce_offset)
        self.screen.blit(title_text, title_pos)
        
        # Subtitle
        if self.subtitle_font:
            subtitle_text = self.subtitle_font.render("Enhanced Edition", True, COLORS.YELLOW)
            subtitle_pos = self.center_text(subtitle_text, -100 + self.title_bounce_offset // 2)
            self.screen.blit(subtitle_text, subtitle_pos)
    
    def _draw_menu_options(self) -> None:
        """Draw the menu options."""
        if not self.menu_font:
            return
        
        start_y = DISPLAY.SCREEN_HEIGHT // 2 - 50
        option_spacing = 60
        
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
                indicator_x = pos[0] - 30
                indicator_y = pos[1] + option_text.get_height() // 2
                pygame.draw.polygon(self.screen, self.selected_color, [
                    (indicator_x, indicator_y - 10),
                    (indicator_x, indicator_y + 10),
                    (indicator_x + 15, indicator_y)
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
            "Press ESC to quit"
        ]
        
        start_y = DISPLAY.SCREEN_HEIGHT - 120
        for i, instruction in enumerate(instructions):
            text = self.subtitle_font.render(instruction, True, COLORS.WHITE)
            pos = self.center_text(text, start_y - DISPLAY.SCREEN_HEIGHT // 2 + i * 25)
            self.screen.blit(text, pos)
    
    def _draw_version_info(self) -> None:
        """Draw version information."""
        if not self.subtitle_font:
            return
        
        version_text = self.subtitle_font.render("v2.0 - Enhanced Architecture", True, (150, 150, 150))
        self.screen.blit(version_text, (10, DISPLAY.SCREEN_HEIGHT - 30))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle menu input events."""
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
            
            # Quick start with any key (except ESC)
            elif event.key not in [pygame.K_ESCAPE, pygame.K_UP, pygame.K_DOWN]:
                if self.menu_options[0] == "Start Game":
                    self.selected_option = 0
                    return self._handle_menu_selection()
        
        return False
    
    def _handle_menu_selection(self) -> bool:
        """Handle menu option selection."""
        selected = self.menu_options[self.selected_option]
        
        if selected == "Start Game":
            # Request state change to playing
            return False  # Let the event bubble up to trigger state change
        
        elif selected == "Settings":
            # TODO: Implement settings scene
            print("Settings not implemented yet")
            return True
        
        elif selected == "Quit":
            # Send quit event
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
            return True
        
        return False
    
    def update(self, dt: float) -> Optional[GameState]:
        """Update menu logic and animations."""
        # Update animation timer
        self.animation_time += dt
        
        # Calculate title bounce effect
        import math
        self.title_bounce_offset = int(math.sin(self.animation_time * 2) * 10)
        
        # Check if we should transition to game state
        # This will be triggered by the menu selection
        return None
    
    def request_state_change(self) -> Optional[GameState]:
        """Request a state change based on current selection."""
        selected = self.menu_options[self.selected_option]
        
        if selected == "Start Game":
            return GameState.PLAYING
        
        return None
    
    def get_selected_option(self) -> str:
        """Get the currently selected menu option."""
        return self.menu_options[self.selected_option]
    
    def set_selected_option(self, option_index: int) -> None:
        """Set the selected menu option by index."""
        if 0 <= option_index < len(self.menu_options):
            self.selected_option = option_index


class MenuInputHandler:
    """
    Helper class to handle menu-specific input logic.
    Separates input handling from rendering logic.
    """
    
    def __init__(self, menu_scene: MenuScene):
        self.menu_scene = menu_scene
    
    def handle_keyboard_input(self, keys_pressed: dict) -> Optional[GameState]:
        """
        Handle continuous keyboard input (for held keys).
        
        Args:
            keys_pressed: Dictionary of currently pressed keys
            
        Returns:
            Optional[GameState]: New state to transition to, or None
        """
        # This could be used for continuous input like holding arrow keys
        # Currently not needed for menu, but useful for extensibility
        return None
    
    def handle_mouse_input(self, mouse_pos: tuple, mouse_buttons: tuple) -> Optional[GameState]:
        """
        Handle mouse input for menu navigation.
        
        Args:
            mouse_pos: (x, y) mouse position
            mouse_buttons: Tuple of mouse button states
            
        Returns:
            Optional[GameState]: New state to transition to, or None
        """
        # TODO: Implement mouse hover and click for menu options
        return None
