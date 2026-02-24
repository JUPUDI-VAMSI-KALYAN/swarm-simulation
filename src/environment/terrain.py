"""Ground terrain environment."""

from src.environment.environment import Environment
from config.settings import COLOR_GROUND


class TerrainEnvironment(Environment):
    """Ground terrain environment."""

    def __init__(self, width=1280, height=720):
        """Initialize terrain environment."""
        super().__init__("ground", width, height)
        self.color = COLOR_GROUND
        self.friction = 0.9  # Ants experience friction

    def get_friction(self):
        """Get friction coefficient."""
        return self.friction

    def __repr__(self):
        return f"TerrainEnvironment(friction={self.friction}, obstacles={len(self.obstacles)})"
