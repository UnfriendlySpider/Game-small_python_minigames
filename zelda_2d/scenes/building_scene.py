"""
Building interior scene for zelda_2d.
Provides a simple room with walls, an entrance and an exit, and collision boundaries.
"""

from typing import Optional, List, Tuple

try:
    import pygame
except Exception:
    pygame = None

from scenes.base_scene import BaseScene
from entities.player import Player
from core.state_manager import GameState
from config.settings import DISPLAY


# Simple color definitions
COLOR_BG = (30, 30, 30)
COLOR_WALL = (100, 60, 40)
COLOR_DOOR = (160, 120, 80)
COLOR_EXIT = (50, 150, 50)


class BuildingScene(BaseScene):
    """
    A simple interior room with walls and an entrance/exit.

    Walls are represented as a list of rect tuples (x, y, w, h).
    The door/exit is an area in one wall. When the player enters the exit area
    and presses the interact key (E) or remains inside briefly, the scene will
    request a state change back to MENU.
    """

    def __init__(self, screen: Optional['pygame.Surface'] = None, player: Optional[Player] = None):
        super().__init__(screen)
        self.player = player
        self.walls: List[Tuple[int, int, int, int]] = []
        self.entrance_rect: Tuple[int, int, int, int] = (0, 0, 0, 0)
        self.exit_rect: Tuple[int, int, int, int] = (0, 0, 0, 0)
        self._exit_timer = 0.0
        self._exit_hold_seconds = 0.6

    def enter(self) -> None:
        super().enter()
        # Initialize player if not provided
        if not self.player:
            self.player = Player()

        # Build walls around the perimeter with a door on the right wall
        sw = DISPLAY.SCREEN_WIDTH
        sh = DISPLAY.SCREEN_HEIGHT
        wall_thickness = 24

        # Top wall
        self.walls.append((0, 0, sw, wall_thickness))
        # Bottom wall
        self.walls.append((0, sh - wall_thickness, sw, wall_thickness))
        # Left wall
        self.walls.append((0, 0, wall_thickness, sh))
        # Right wall with door gap: we'll create two wall segments
        door_w = 48
        door_h = 80
        door_y = sh // 2 - door_h // 2
        # right wall top
        self.walls.append((sw - wall_thickness, 0, wall_thickness, door_y))
        # right wall bottom
        self.walls.append((sw - wall_thickness, door_y + door_h, wall_thickness, sh - (door_y + door_h)))

        # entrance (where player spawns) — left side center
        self.entrance_rect = (wall_thickness + 8, sh // 2 - 16, 32, 32)
        self.player.set_position(self.entrance_rect[0], self.entrance_rect[1])

        # exit area (door) on right wall
        self.exit_rect = (sw - wall_thickness - (door_w // 2), door_y + (door_h // 2) - 16, door_w, 32)
        self._exit_timer = 0.0

    def exit(self) -> None:
        super().exit()

    def _get_obstacles(self) -> List[Tuple[int, int, int, int]]:
        # Return wall rects as obstacle list
        return self.walls.copy()

    def update(self, dt: float) -> Optional[GameState]:
        # Handle movement via keyboard state if pygame present
        if pygame:
            keys = pygame.key.get_pressed()
            up = keys[pygame.K_w] or keys[pygame.K_UP]
            down = keys[pygame.K_s] or keys[pygame.K_DOWN]
            left = keys[pygame.K_a] or keys[pygame.K_LEFT]
            right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
            self.player.handle_input(up, down, left, right)

        obstacles = self._get_obstacles()
        self.player.update(dt, obstacles)

        # Check for exit overlap
        px = int(self.player.x)
        py = int(self.player.y)
        pw = self.player.width
        ph = self.player.height
        pr = (px, py, pw, ph)

        if self._rects_overlap(pr, self.exit_rect):
            self._exit_timer += dt
        else:
            self._exit_timer = 0.0

        # If player holds in exit or presses interact, request state change
        if self._exit_timer >= self._exit_hold_seconds:
            return GameState.MENU

        return None

    def render(self) -> None:
        if not pygame or not self.screen:
            return
        # Clear background
        self.screen.fill(COLOR_BG)

        # Draw walls
        for w in self.walls:
            rect = pygame.Rect(w[0], w[1], w[2], w[3])
            pygame.draw.rect(self.screen, COLOR_WALL, rect)

        # Draw entrance and exit markers
        er = pygame.Rect(self.entrance_rect)
        pygame.draw.rect(self.screen, COLOR_DOOR, er)
        xr = pygame.Rect(self.exit_rect)
        pygame.draw.rect(self.screen, COLOR_EXIT, xr)

        # Draw player
        self.player.draw(self.screen)

    def handle_event(self, event) -> bool:
        # Interact key to exit when in exit rect
        if pygame and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                # check overlap
                px = int(self.player.x)
                py = int(self.player.y)
                pw = self.player.width
                ph = self.player.height
                if self._rects_overlap((px, py, pw, ph), self.exit_rect):
                    return_value = True
                    # return state change by setting exit timer high so update will transition
                    self._exit_timer = self._exit_hold_seconds
                    return True
        return False

    @staticmethod
    def _rects_overlap(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> bool:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return (ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by)
