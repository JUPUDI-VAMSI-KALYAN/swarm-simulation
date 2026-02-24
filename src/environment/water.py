"""Water environment with current forces."""

import math
from src.environment.environment import Environment
from src.core.vector2d import Vector2D
from config.settings import COLOR_WATER


class WaterEnvironment(Environment):
    """Water environment with currents."""

    def __init__(self, width=1280, height=720):
        """Initialize water environment."""
        super().__init__("water", width, height)
        self.color = COLOR_WATER
        self.current_strength = 0.2
        self.current_angle = 0
        self.current_change_speed = 0.3

    def update(self, delta_time):
        """Update current patterns."""
        # Slowly change current direction
        self.current_angle += self.current_change_speed * delta_time
        current_x = math.cos(self.current_angle) * self.current_strength
        current_y = math.sin(self.current_angle) * self.current_strength
        self.environmental_force = Vector2D(current_x, current_y)

    def __repr__(self):
        return f"WaterEnvironment(current={self.current_strength:.2f}, obstacles={len(self.obstacles)})"
