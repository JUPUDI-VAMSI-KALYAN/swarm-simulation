"""Obstacle entities for the environment."""

from src.core.entity import Entity
from config.settings import COLOR_OBSTACLE


class Obstacle(Entity):
    """Static obstacle entity."""

    def __init__(self, position=None, width=20, height=20):
        """
        Initialize an obstacle.

        Args:
            position: Center position (Vector2D)
            width: Obstacle width
            height: Obstacle height
        """
        super().__init__(position=position, radius=max(width, height) // 2)

        self.width = width
        self.height = height
        self.color = COLOR_OBSTACLE
        self.velocity = None  # Obstacles don't move
        self.acceleration = None

    def update(self, delta_time):
        """Obstacles don't move."""
        pass

    def __repr__(self):
        return f"Obstacle(pos={self.position}, size={self.width}x{self.height})"
