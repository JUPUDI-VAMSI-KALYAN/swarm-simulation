"""Base environment class."""

from src.core.vector2d import Vector2D


class Environment:
    """Base environment class."""

    def __init__(self, env_type="air", width=1280, height=720):
        """
        Initialize environment.

        Args:
            env_type: Type of environment ("ground", "water", "air")
            width: Environment width
            height: Environment height
        """
        self.env_type = env_type
        self.width = width
        self.height = height
        self.obstacles = []
        self.color = (200, 200, 200)
        self.environmental_force = Vector2D(0, 0)

    def get_environmental_force(self, position):
        """
        Get environmental force at position (wind, current, etc).

        Args:
            position: Vector2D position

        Returns:
            Vector2D force
        """
        return self.environmental_force.copy()

    def add_obstacle(self, obstacle):
        """Add obstacle to environment."""
        self.obstacles.append(obstacle)

    def remove_obstacle(self, obstacle):
        """Remove obstacle from environment."""
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)

    def get_obstacles(self):
        """Get all obstacles."""
        return self.obstacles

    def update(self, delta_time):
        """Update environment state."""
        pass

    def __repr__(self):
        return f"Environment(type={self.env_type}, obstacles={len(self.obstacles)})"
