"""Air environment with wind forces."""

import math
from src.environment.environment import Environment
from src.core.vector2d import Vector2D
from config.settings import COLOR_AIR


class AirEnvironment(Environment):
    """Air environment with wind."""

    def __init__(self, width=1280, height=720):
        """Initialize air environment."""
        super().__init__("air", width, height)
        self.color = COLOR_AIR
        self.wind_strength = 0.3
        self.wind_angle = 0
        self.wind_change_speed = 0.5

    def update(self, delta_time):
        """Update wind patterns."""
        # Slowly change wind direction
        self.wind_angle += self.wind_change_speed * delta_time
        wind_x = math.cos(self.wind_angle) * self.wind_strength
        wind_y = math.sin(self.wind_angle) * self.wind_strength * 0.5
        self.environmental_force = Vector2D(wind_x, wind_y)

    def __repr__(self):
        return f"AirEnvironment(wind={self.wind_strength:.2f}, obstacles={len(self.obstacles)})"
