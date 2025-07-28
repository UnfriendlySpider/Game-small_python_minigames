"""
Game state management for Text Adventure Game.
Handles different game states and transitions between them.
"""

from enum import Enum
from typing import Dict, List, Callable, Optional, Any
import time


class GameState(Enum):
    """Enumeration of possible game states."""
    MENU = "menu"
    PLAYING = "playing"
    INVENTORY = "inventory"
    PAUSED = "paused"
    SAVING = "saving"
    LOADING = "loading"
    QUIT = "quit"


class StateManager:
    """
    Manages game state transitions and callbacks.
    
    Responsibilities:
    - Track current game state
    - Handle state transitions with validation
    - Execute callbacks on state changes
    - Maintain state history for debugging
    """
    
    def __init__(self, initial_state: GameState = GameState.MENU):
        """Initialize the state manager."""
        self.current_state = initial_state
        self.previous_state: Optional[GameState] = None
        self.state_history: List[tuple] = []
        
        # Callbacks for state transitions
        self.enter_callbacks: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        self.exit_callbacks: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        
        # State transition rules
        self.valid_transitions: Dict[GameState, List[GameState]] = {
            GameState.MENU: [GameState.PLAYING, GameState.LOADING, GameState.QUIT],
            GameState.PLAYING: [GameState.INVENTORY, GameState.PAUSED, GameState.SAVING, GameState.MENU, GameState.QUIT],
            GameState.INVENTORY: [GameState.PLAYING],
            GameState.PAUSED: [GameState.PLAYING, GameState.MENU, GameState.QUIT],
            GameState.SAVING: [GameState.PLAYING],
            GameState.LOADING: [GameState.PLAYING, GameState.MENU],
            GameState.QUIT: []  # Terminal state
        }
        
        # Record initial state
        self._record_state_change(None, initial_state)
    
    def change_state(self, new_state: GameState) -> bool:
        """
        Change to a new game state.
        
        Args:
            new_state: The state to transition to
            
        Returns:
            bool: True if transition was successful, False otherwise
        """
        if not self.can_transition_to(new_state):
            print(f"Invalid state transition from {self.current_state.value} to {new_state.value}")
            return False
        
        old_state = self.current_state
        
        # Execute exit callbacks for current state
        self._execute_callbacks(self.exit_callbacks[old_state])
        
        # Change state
        self.previous_state = old_state
        self.current_state = new_state
        
        # Record the change
        self._record_state_change(old_state, new_state)
        
        # Execute enter callbacks for new state
        self._execute_callbacks(self.enter_callbacks[new_state])
        
        return True
    
    def can_transition_to(self, target_state: GameState) -> bool:
        """
        Check if transition to target state is valid.
        
        Args:
            target_state: The state to check transition to
            
        Returns:
            bool: True if transition is valid
        """
        return target_state in self.valid_transitions.get(self.current_state, [])
    
    def add_enter_callback(self, state: GameState, callback: Callable) -> None:
        """
        Add a callback to execute when entering a state.
        
        Args:
            state: The state to add callback for
            callback: Function to call when entering the state
        """
        self.enter_callbacks[state].append(callback)
    
    def add_exit_callback(self, state: GameState, callback: Callable) -> None:
        """
        Add a callback to execute when exiting a state.
        
        Args:
            state: The state to add callback for
            callback: Function to call when exiting the state
        """
        self.exit_callbacks[state].append(callback)
    
    def remove_callback(self, state: GameState, callback: Callable, callback_type: str = "enter") -> bool:
        """
        Remove a callback from a state.
        
        Args:
            state: The state to remove callback from
            callback: The callback function to remove
            callback_type: "enter" or "exit"
            
        Returns:
            bool: True if callback was found and removed
        """
        callback_list = (self.enter_callbacks if callback_type == "enter" 
                        else self.exit_callbacks)[state]
        
        if callback in callback_list:
            callback_list.remove(callback)
            return True
        return False
    
    def get_state_name(self) -> str:
        """Get the current state name as a string."""
        return self.current_state.value
    
    def get_previous_state_name(self) -> Optional[str]:
        """Get the previous state name as a string."""
        return self.previous_state.value if self.previous_state else None
    
    def is_in_state(self, state: GameState) -> bool:
        """Check if currently in the specified state."""
        return self.current_state == state
    
    def get_valid_transitions(self) -> List[str]:
        """Get list of valid transitions from current state."""
        return [state.value for state in self.valid_transitions.get(self.current_state, [])]
    
    def get_state_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent state history.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of state change records
        """
        return self.state_history[-limit:] if limit > 0 else self.state_history
    
    def _execute_callbacks(self, callbacks: List[Callable]) -> None:
        """Execute a list of callbacks safely."""
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error executing state callback: {e}")
    
    def _record_state_change(self, old_state: Optional[GameState], new_state: GameState) -> None:
        """Record a state change in history."""
        record = {
            "timestamp": time.time(),
            "from_state": old_state.value if old_state else None,
            "to_state": new_state.value,
            "transition_valid": old_state is None or self.can_transition_to(new_state)
        }
        self.state_history.append(record)
        
        # Keep history manageable
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-50:]
    
    def reset_to_menu(self) -> bool:
        """Reset state manager to menu state."""
        # Force transition to menu regardless of current state
        old_state = self.current_state
        
        # Execute exit callbacks for current state
        if old_state != GameState.MENU:
            self._execute_callbacks(self.exit_callbacks[old_state])
        
        # Change state
        self.previous_state = old_state
        self.current_state = GameState.MENU
        
        # Record the change
        self._record_state_change(old_state, GameState.MENU)
        
        # Execute enter callbacks for menu state
        self._execute_callbacks(self.enter_callbacks[GameState.MENU])
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get state manager statistics.
        
        Returns:
            Dictionary containing state manager stats
        """
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "total_transitions": len(self.state_history),
            "valid_transitions": self.get_valid_transitions(),
            "callback_counts": {
                state.value: {
                    "enter": len(self.enter_callbacks[state]),
                    "exit": len(self.exit_callbacks[state])
                }
                for state in GameState
            }
        }


# Convenience functions for common state checks
def is_playing_state(state_manager: StateManager) -> bool:
    """Check if the game is in a playing state."""
    return state_manager.is_in_state(GameState.PLAYING)


def is_menu_state(state_manager: StateManager) -> bool:
    """Check if the game is in menu state."""
    return state_manager.is_in_state(GameState.MENU)


def is_interactive_state(state_manager: StateManager) -> bool:
    """Check if the game is in an interactive state (not transitioning)."""
    return state_manager.current_state in [
        GameState.MENU, GameState.PLAYING, GameState.INVENTORY, GameState.PAUSED
    ]
