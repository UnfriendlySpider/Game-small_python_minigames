"""
Base entity for zelda_2d.
"""

from typing import Tuple, Dict, Any, Optional

try:
    import pygame
except Exception:
    pygame = None


class Entity:
    def __init__(self, entity_id: str, x: float = 0.0, y: float = 0.0, width: int = 16, height: int = 16):
        self.entity_id = entity_id
        self.x = float(x)
        self.y = float(y)
        self.width = int(width)
        self.height = int(height)
        self.vx = 0.0
        self.vy = 0.0
        self.tags = set()

    def get_rect(self) -> Optional['pygame.Rect']:
        if pygame:
            return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        return (int(self.x), int(self.y), self.width, self.height)

    def set_position(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)

    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

    def serialize(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "vx": self.vx,
            "vy": self.vy,
            "tags": list(self.tags)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        ent = cls(data.get("entity_id", "entity"), data.get("x", 0.0), data.get("y", 0.0), data.get("width", 16), data.get("height", 16))
        ent.vx = data.get("vx", 0.0)
        ent.vy = data.get("vy", 0.0)
        ent.tags = set(data.get("tags", []))
        return ent

    def get_stats(self) -> Dict[str, Any]:
        return {
            "id": self.entity_id,
            "pos": (self.x, self.y),
            "vel": (self.vx, self.vy),
            "size": (self.width, self.height)
        }
