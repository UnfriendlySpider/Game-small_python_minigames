"""
State manager for zelda_2d.
"""

from enum import Enum
from typing import Dict, Callable, Optional, List
import time


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    GAME_OVER = "game_over"
    QUIT = "quit"


class StateManager:
    def __init__(self, initial_state: GameState = GameState.MENU):
        self.current_state = initial_state
        self.previous_state: Optional[GameState] = None
        self.state_history: List[Dict] = []
        self.enter_callbacks: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        self.exit_callbacks: Dict[GameState, List[Callable]] = {state: [] for state in GameState}
        self.valid_transitions: Dict[GameState, List[GameState]] = {
            GameState.MENU: [GameState.PLAYING, GameState.QUIT],
            GameState.PLAYING: [GameState.PAUSED, GameState.INVENTORY, GameState.GAME_OVER, GameState.MENU, GameState.QUIT],
            GameState.PAUSED: [GameState.PLAYING, GameState.MENU, GameState.QUIT],
            GameState.INVENTORY: [GameState.PLAYING],
            GameState.GAME_OVER: [GameState.MENU, GameState.PLAYING],
            GameState.QUIT: []
        }
        self._record_state_change(None, initial_state)

    def _record_state_change(self, old_state: Optional[GameState], new_state: GameState) -> None:
        record = {
            "timestamp": time.time(),
            "from_state": old_state.value if old_state else None,
            "to_state": new_state.value
        }
        self.state_history.append(record)
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-50:]

    def can_transition_to(self, target_state: GameState) -> bool:
        return target_state in self.valid_transitions.get(self.current_state, [])

    def change_state(self, new_state: GameState) -> bool:
        if not self.can_transition_to(new_state):
            return False
        old_state = self.current_state
        for cb in list(self.exit_callbacks.get(old_state, [])):
            try:
                cb()
            except Exception:
                pass
        self.previous_state = old_state
        self.current_state = new_state
        self._record_state_change(old_state, new_state)
        for cb in list(self.enter_callbacks.get(new_state, [])):
            try:
                cb()
            except Exception:
                pass
        return True

    def add_enter_callback(self, state: GameState, callback: Callable) -> None:
        self.enter_callbacks[state].append(callback)

    def add_exit_callback(self, state: GameState, callback: Callable) -> None:
        self.exit_callbacks[state].append(callback)

    def get_state_name(self) -> str:
        return self.current_state.value

    def reset_to_menu(self) -> None:
        self.change_state(GameState.MENU)

