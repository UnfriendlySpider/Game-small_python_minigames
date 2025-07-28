"""
Main game class for Flappy Birds.
Coordinates all game systems and manages the main game loop.
"""

import pygame
import sys
from typing import Dict, Optional

from core.state_manager import StateManager, GameState
from scenes.base_scene import BaseScene
from scenes.game_scene import GameScene
from scenes.menu_scene import MenuScene
from scenes.game_over_scene import GameOverScene
from config.settings import DISPLAY


class Game:
    """
    Main game coordinator class.
    
    Responsibilities:
    - Initialize pygame and create window
    - Manage game loop and timing
    - Coordinate scene transitions
    - Handle global events
    - Manage resources and cleanup
    """
    
    def __init__(self):
        """Initialize the game."""
        # Initialize pygame
        pygame.init()
        
        # Create display
        self.screen = pygame.display.set_mode((DISPLAY.SCREEN_WIDTH, DISPLAY.SCREEN_HEIGHT))
        pygame.display.set_caption(DISPLAY.WINDOW_TITLE)
        
        # Initialize clock for frame rate control
        self.clock = pygame.time.Clock()
        
        # Initialize state manager
        self.state_manager = StateManager(GameState.MENU)
        
        # Initialize scenes
        self.scenes: Dict[GameState, BaseScene] = {}
        self._initialize_scenes()
        
        # Game state
        self.running = True
        self.current_scene: Optional[BaseScene] = None
        
        # Setup state change callbacks
        self._setup_state_callbacks()
        
        # Start with initial scene
        self._change_to_scene(self.state_manager.current_state)
    
    def _initialize_scenes(self) -> None:
        """Initialize all game scenes."""
        self.scenes[GameState.MENU] = MenuScene(self.screen)
        self.scenes[GameState.PLAYING] = GameScene(self.screen)
        self.scenes[GameState.GAME_OVER] = GameOverScene(self.screen)
        # Note: PAUSED state uses the same scene as PLAYING
        # Note: SETTINGS scene not implemented yet
    
    def _setup_state_callbacks(self) -> None:
        """Setup callbacks for state transitions."""
        # Add enter callbacks for each state
        for state in GameState:
            self.state_manager.add_enter_callback(
                state, 
                lambda s=state: self._on_enter_state(s)
            )
            self.state_manager.add_exit_callback(
                state,
                lambda s=state: self._on_exit_state(s)
            )
    
    def _on_enter_state(self, state: GameState) -> None:
        """Called when entering a new state."""
        print(f"Entering state: {state.value}")
        
        # Handle special state entry logic
        if state == GameState.GAME_OVER:
            # Pass the final score from game scene to game over scene
            game_scene = self.scenes.get(GameState.PLAYING)
            game_over_scene = self.scenes.get(GameState.GAME_OVER)
            
            if game_scene and game_over_scene and hasattr(game_scene, 'get_score'):
                final_score = game_scene.get_score()
                if hasattr(game_over_scene, 'set_final_score'):
                    game_over_scene.set_final_score(final_score)
        
        self._change_to_scene(state)
    
    def _on_exit_state(self, state: GameState) -> None:
        """Called when exiting a state."""
        print(f"Exiting state: {state.value}")
        if self.current_scene:
            self.current_scene.exit()
    
    def _change_to_scene(self, state: GameState) -> None:
        """Change to the scene associated with the given state."""
        # Handle special cases
        if state == GameState.PAUSED:
            # Paused state uses the same scene as playing, just paused
            if self.current_scene:
                self.current_scene.pause()
            return
        
        # Get the scene for this state
        new_scene = self.scenes.get(state)
        if new_scene is None:
            print(f"Warning: No scene found for state {state.value}")
            return
        
        # Exit current scene if it exists
        if self.current_scene and self.current_scene != new_scene:
            self.current_scene.exit()
        
        # Enter new scene
        self.current_scene = new_scene
        self.current_scene.enter()
    
    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            # Handle quit event
            if event.type == pygame.QUIT:
                self.quit()
                return
            
            # Let state manager handle common events first
            if self.state_manager.handle_common_events(event):
                continue
            
            # Let current scene handle the event
            if self.current_scene:
                if not self.current_scene.handle_event(event):
                    # Scene didn't handle the event, check for state transitions
                    self._handle_scene_state_transitions(event)
            
            # Handle global events that weren't handled by scene
            self._handle_global_event(event)
    
    def _handle_scene_state_transitions(self, event: pygame.event.Event) -> None:
        """Handle state transitions triggered by scene events."""
        if event.type == pygame.KEYDOWN:
            current_state = self.state_manager.current_state
            
            # Menu scene transitions
            if current_state == GameState.MENU:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if hasattr(self.current_scene, 'get_selected_option'):
                        selected = self.current_scene.get_selected_option()
                        if selected == "Start Game":
                            self.state_manager.change_state(GameState.PLAYING)
            
            # Game over scene transitions
            elif current_state == GameState.GAME_OVER:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_r]:
                    if hasattr(self.current_scene, 'get_selected_option'):
                        selected = self.current_scene.get_selected_option()
                        if selected == "Play Again" or event.key == pygame.K_r:
                            self.state_manager.change_state(GameState.PLAYING)
                        elif selected == "Main Menu":
                            self.state_manager.change_state(GameState.MENU)
            
            # Paused state transitions
            elif current_state == GameState.PAUSED:
                if event.key == pygame.K_q:
                    self.state_manager.change_state(GameState.MENU)
    
    def _handle_global_event(self, event: pygame.event.Event) -> None:
        """Handle global events not handled by scenes."""
        if event.type == pygame.KEYDOWN:
            # Global quit key
            if event.key == pygame.K_F4 and pygame.key.get_pressed()[pygame.K_LALT]:
                self.quit()
    
    def update(self, dt: float) -> None:
        """Update game logic."""
        if not self.current_scene:
            return
        
        # Update current scene
        new_state = self.current_scene.update(dt)
        
        # Handle state change request from scene
        if new_state and new_state != self.state_manager.current_state:
            self.state_manager.change_state(new_state)
    
    def render(self) -> None:
        """Render the game."""
        if self.current_scene:
            self.current_scene.render()
        
        # Update display
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop."""
        print("Starting Flappy Birds game...")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(DISPLAY.FPS) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update game logic
            self.update(dt)
            
            # Render
            self.render()
        
        # Cleanup
        self.cleanup()
    
    def quit(self) -> None:
        """Quit the game."""
        print("Quitting game...")
        self.running = False
    
    def cleanup(self) -> None:
        """Clean up resources before exit."""
        # Exit current scene
        if self.current_scene:
            self.current_scene.exit()
        
        # Clean up all scenes
        for scene in self.scenes.values():
            if hasattr(scene, 'cleanup_resources'):
                scene.cleanup_resources()
        
        # Quit pygame
        pygame.quit()
        sys.exit()
    
    def get_current_state(self) -> GameState:
        """Get the current game state."""
        return self.state_manager.current_state
    
    def change_state(self, new_state: GameState) -> bool:
        """
        Request a state change.
        
        Args:
            new_state: State to change to
            
        Returns:
            bool: True if state change was successful
        """
        return self.state_manager.change_state(new_state)
    
    def get_stats(self) -> dict:
        """
        Get game statistics for debugging.
        
        Returns:
            dict: Dictionary containing game stats
        """
        return {
            'current_state': self.state_manager.get_state_name(),
            'fps': self.clock.get_fps(),
            'running': self.running,
            'current_scene': type(self.current_scene).__name__ if self.current_scene else None,
            'scene_count': len(self.scenes)
        }


def main():
    """Entry point for the game."""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Game crashed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure pygame is properly closed
        if pygame.get_init():
            pygame.quit()


if __name__ == "__main__":
    main()
