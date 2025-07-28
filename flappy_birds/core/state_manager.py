"""
Game state management system for Flappy Birds.
Handles transitions between different game states with validation and callbacks.
"""

from enum import Enum
from typing import Dict, Callable, Optional, List
import pygame


class GameState(Enum):
    """Enumeration of all possible game states."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SETTINGS = "settings"


class StateManager:
    """
    Manages game state transitions with validation and callbacks.
    
    Features:
    - State transition validation
    - Enter/exit callbacks for states
    - State history tracking
    - Event-driven state changes
    """
    
    def __init__(self, initial_state: GameState = GameState.MENU):
        self.current_state = initial_state
        self.previous_state: Optional[GameState] = None
        self.state_history: List[GameState] = [initial_state]
        
        # Callbacks for state transitions
        self.enter_callbacks: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        self.exit_callbacks: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        
        # Valid state transitions
        self.valid_transitions: Dict[GameState, List[GameState]] = {
            GameState.MENU: [GameState.PLAYING, GameState.SETTINGS],
            GameState.PLAYING: [GameState.PAUSED, GameState.GAME_OVER, GameState.MENU],
            GameState.PAUSED: [GameState.PLAYING, GameState.MENU],
            GameState.GAME_OVER: [GameState.MENU, GameState.PLAYING],
            GameState.SETTINGS: [GameState.MENU]
        }
    
    def change_state(self, new_state: GameState) -> bool:
        """
        Change to a new game state with validation.
        
        Args:
            new_state: The state to transition to
            
        Returns:
            bool: True if transition was successful, False otherwise
        """
        if not self.is_valid_transition(new_state):
            print(f"Invalid transition from {self.current_state} to {new_state}")
            return False
        
        # Execute exit callbacks for current state
        for callback in self.exit_callbacks[self.current_state]:
            callback()
        
        # Update state
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_history.append(new_state)
        
        # Keep history manageable
        if len(self.state_history) > 10:
            self.state_history.pop(0)
        
        # Execute enter callbacks for new state
        for callback in self.enter_callbacks[new_state]:
            callback()
        
        return True
    
    def is_valid_transition(self, new_state: GameState) -> bool:
        """Check if transition to new_state is valid from current state."""
        return new_state in self.valid_transitions.get(self.current_state, [])
    
    def go_back(self) -> bool:
        """Return to the previous state if possible."""
        if self.previous_state and self.is_valid_transition(self.previous_state):
            return self.change_state(self.previous_state)
        return False
    
    def add_enter_callback(self, state: GameState, callback: Callable):
        """Add a callback to be executed when entering a state."""
        self.enter_callbacks[state].append(callback)
    
    def add_exit_callback(self, state: GameState, callback: Callable):
        """Add a callback to be executed when exiting a state."""
        self.exit_callbacks[state].append(callback)
    
    def remove_enter_callback(self, state: GameState, callback: Callable):
        """Remove an enter callback for a state."""
        if callback in self.enter_callbacks[state]:
            self.enter_callbacks[state].remove(callback)
    
    def remove_exit_callback(self, state: GameState, callback: Callable):
        """Remove an exit callback for a state."""
        if callback in self.exit_callbacks[state]:
            self.exit_callbacks[state].remove(callback)
    
    def is_state(self, state: GameState) -> bool:
        """Check if currently in the specified state."""
        return self.current_state == state
    
    def get_state_name(self) -> str:
        """Get the current state name as a string."""
        return self.current_state.value
    
    def handle_common_events(self, event: pygame.event.Event) -> bool:
        """
        Handle common events that can trigger state changes.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if event.type == pygame.KEYDOWN:
            # ESC key handling
            if event.key == pygame.K_ESCAPE:
                if self.current_state == GameState.PLAYING:
                    return self.change_state(GameState.PAUSED)
                elif self.current_state == GameState.PAUSED:
                    return self.change_state(GameState.PLAYING)
                elif self.current_state in [GameState.SETTINGS, GameState.GAME_OVER]:
                    return self.change_state(GameState.MENU)
            
            # Pause key handling
            elif event.key == pygame.K_p:
                if self.current_state == GameState.PLAYING:
                    return self.change_state(GameState.PAUSED)
                elif self.current_state == GameState.PAUSED:
                    return self.change_state(GameState.PLAYING)
        
        return False
    
    def reset(self):
        """Reset state manager to initial state."""
        self.current_state = GameState.MENU
        self.previous_state = None
        self.state_history = [GameState.MENU]
