"""
Player entity for zelda_2d with movement, collision detection, and sprite handling.
"""

from typing import List, Tuple, Optional, Dict, Any
import math

from entities.entity import Entity
from config.settings import GAMEPLAY

try:
    import pygame
except Exception:
    pygame = None


class Player(Entity):
    def __init__(self, entity_id: str = "player", x: float = None, y: float = None, speed: float = 120.0, width: int = None, height: int = None, sprite_path: Optional[str] = None):
        start_x = x if x is not None else GAMEPLAY.PLAYER_START_X
        start_y = y if y is not None else GAMEPLAY.PLAYER_START_Y
        w = width if width is not None else GAMEPLAY.TILE_SIZE
        h = height if height is not None else GAMEPLAY.TILE_SIZE
        super().__init__(entity_id, start_x, start_y, w, h)
        self.speed = float(speed)
        self.facing = "down"
        self.moving = False
        self.sprite_path = sprite_path
        self.sprite_sheet = None
        self.frames: Dict[str, List['pygame.Surface']] = {}
        self.current_frame = 0
        self.frame_time = 0.15
        self._frame_timer = 0.0
        if sprite_path and pygame:
            try:
                self._load_sprite(sprite_path)
            except Exception:
                self.sprite_sheet = None

    def _load_sprite(self, path: str, frame_w: Optional[int] = None, frame_h: Optional[int] = None, directions: Optional[List[str]] = None) -> None:
        if not pygame:
            return
        image = pygame.image.load(path).convert_alpha()
        self.sprite_sheet = image
        sheet_w, sheet_h = image.get_size()
        fw = frame_w if frame_w else self.width
        fh = frame_h if frame_h else self.height
        cols = max(1, sheet_w // fw)
        rows = max(1, sheet_h // fh)
        frames = []
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(c * fw, r * fh, fw, fh)
                frames.append(image.subsurface(rect))
        if directions:
            per_dir = max(1, len(frames) // len(directions))
            for i, d in enumerate(directions):
                self.frames[d] = frames[i * per_dir:(i + 1) * per_dir]
        else:
            self.frames["down"] = frames

    def handle_input(self, up: bool, down: bool, left: bool, right: bool) -> None:
        dx = 0
        dy = 0
        if up:
            dy -= 1
        if down:
            dy += 1
        if left:
            dx -= 1
        if right:
            dx += 1
        length = math.hypot(dx, dy)
        if length > 0:
            nx = dx / length
            ny = dy / length
            self.vx = nx * self.speed
            self.vy = ny * self.speed
            self.moving = True
            if abs(nx) > abs(ny):
                self.facing = "left" if nx < 0 else "right"
            else:
                self.facing = "up" if ny < 0 else "down"
        else:
            self.vx = 0.0
            self.vy = 0.0
            self.moving = False

    def update(self, dt: float, obstacles: Optional[List[Tuple[int, int, int, int]]] = None) -> None:
        if not obstacles:
            super().update(dt)
            if self.moving:
                self._advance_animation(dt)
            return
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        rect_x = (int(new_x), int(self.y), self.width, self.height)
        if not self._check_collision(rect_x, obstacles):
            self.x = new_x
        else:
            self.vx = 0.0
        rect_y = (int(self.x), int(new_y), self.width, self.height)
        if not self._check_collision(rect_y, obstacles):
            self.y = new_y
        else:
            self.vy = 0.0
        if self.moving:
            self._advance_animation(dt)

    def _check_collision(self, rect: Tuple[int, int, int, int], obstacles: List[Tuple[int, int, int, int]]) -> bool:
        rx, ry, rw, rh = rect
        for o in obstacles:
            ox, oy, ow, oh = o
            if (rx < ox + ow and rx + rw > ox and ry < oy + oh and ry + rh > oy):
                return True
        return False

    def _advance_animation(self, dt: float) -> None:
        if not self.frames:
            return
        self._frame_timer += dt
        if self._frame_timer >= self.frame_time:
            self._frame_timer -= self.frame_time
            self.current_frame = (self.current_frame + 1) % max(1, len(self.frames.get(self.facing, [])))

    def draw(self, surface) -> None:
        if not pygame or surface is None:
            return
        frame_list = self.frames.get(self.facing)
        if frame_list:
            frame = frame_list[self.current_frame % len(frame_list)]
            surface.blit(frame, (int(self.x), int(self.y)))
        elif self.sprite_sheet:
            surface.blit(self.sprite_sheet, (int(self.x), int(self.y)))
        else:
            pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(int(self.x), int(self.y), self.width, self.height))

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({
            "speed": self.speed,
            "facing": self.facing,
            "moving": self.moving
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        p = cls(data.get("entity_id", "player"), data.get("x", 0), data.get("y", 0), data.get("speed", 120.0), data.get("width", GAMEPLAY.TILE_SIZE), data.get("height", GAMEPLAY.TILE_SIZE))
        p.vx = data.get("vx", 0.0)
        p.vy = data.get("vy", 0.0)
        p.facing = data.get("facing", "down")
        p.moving = data.get("moving", False)
        return p

    def get_stats(self) -> Dict[str, Any]:
        s = super().get_stats()
        s.update({
            "speed": self.speed,
            "facing": self.facing,
            "moving": self.moving
        })
        return s
