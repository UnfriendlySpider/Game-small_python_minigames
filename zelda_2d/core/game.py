"""
Core game coordinator for zelda_2d.
"""

import sys
import time
from typing import Dict, Optional

from config.settings import DISPLAY
from core.state_manager import StateManager, GameState

try:
    import pygame
except Exception:
    pygame = None


class Game:
    def __init__(self, headless: bool = False, seed: Optional[int] = None):
        self.headless = headless
        self.running = True
        self.state_manager = StateManager(GameState.MENU)
        self.scenes: Dict[GameState, object] = {}
        self.current_scene: Optional[object] = None
        self.clock = None
        self.screen = None
        if not headless and pygame:
            pygame.init()
            self.screen = pygame.display.set_mode((DISPLAY.SCREEN_WIDTH, DISPLAY.SCREEN_HEIGHT))
            pygame.display.set_caption(DISPLAY.WINDOW_TITLE)
            self.clock = pygame.time.Clock()
        self._setup_state_callbacks()

    def _setup_state_callbacks(self) -> None:
        for state in GameState:
            self.state_manager.add_enter_callback(state, lambda s=state: self._on_enter_state(s))
            self.state_manager.add_exit_callback(state, lambda s=state: self._on_exit_state(s))

    def register_scene(self, state: GameState, scene) -> None:
        self.scenes[state] = scene

    def _on_enter_state(self, state: GameState) -> None:
        if state == GameState.QUIT:
            self.quit()
            return
        new_scene = self.scenes.get(state)
        if new_scene is None:
            return
        if self.current_scene and self.current_scene != new_scene and hasattr(self.current_scene, 'exit'):
            try:
                self.current_scene.exit()
            except Exception:
                pass
        self.current_scene = new_scene
        if hasattr(self.current_scene, 'enter'):
            try:
                self.current_scene.enter()
            except Exception:
                pass

    def _on_exit_state(self, state: GameState) -> None:
        if self.current_scene and hasattr(self.current_scene, 'exit'):
            try:
                self.current_scene.exit()
            except Exception:
                pass

    def handle_events(self) -> None:
        if self.headless or not pygame:
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
                return
            if self.current_scene and hasattr(self.current_scene, 'handle_event'):
                try:
                    handled = self.current_scene.handle_event(event)
                    if handled:
                        continue
                except Exception:
                    pass

    def update(self, dt: float) -> None:
        if not self.current_scene or not hasattr(self.current_scene, 'update'):
            return
        try:
            new_state = self.current_scene.update(dt)
            if new_state and new_state != self.state_manager.current_state:
                self.state_manager.change_state(new_state)
        except Exception:
            pass

    def render(self) -> None:
        if self.headless or not pygame:
            return
        if self.current_scene and hasattr(self.current_scene, 'render'):
            try:
                self.current_scene.render()
            except Exception:
                pass
        pygame.display.flip()

    def step(self, dt: Optional[float] = None) -> None:
        if dt is None:
            dt = 1.0 / DISPLAY.FPS
        self.handle_events()
        self.update(dt)
        self.render()

    def run(self) -> None:
        try:
            while self.running:
                if self.clock:
                    dt = self.clock.tick(DISPLAY.FPS) / 1000.0
                else:
                    dt = 1.0 / DISPLAY.FPS
                    time.sleep(dt)
                self.handle_events()
                self.update(dt)
                self.render()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def quit(self) -> None:
        self.running = False

    def cleanup(self) -> None:
        if pygame:
            try:
                pygame.quit()
            except Exception:
                pass

    def get_current_state(self) -> GameState:
        return self.state_manager.current_state

    def change_state(self, new_state: GameState) -> bool:
        return self.state_manager.change_state(new_state)


def main():
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Game crashed with error: {e}")
        import traceback
        traceback.print_exc()

