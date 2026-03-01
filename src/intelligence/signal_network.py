"""Digital signal network system for bot communication."""

import numpy as np
import math
from src.core.vector2d import Vector2D


class SignalNetworkMap:
    """Grid-based digital signal map for mesh-networked bot communication."""

    def __init__(self, grid_width=1280, grid_height=720, cell_size=10):
        """
        Initialize signal map.

        Args:
            grid_width: Map width in pixels
            grid_height: Map height in pixels
            cell_size: Size of each grid cell
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size

        self.cols = grid_width // cell_size
        self.rows = grid_height // cell_size

        # Grids for different network signals
        self.path_signals = np.zeros((self.rows, self.cols), dtype=np.float32)
        self.base_signals = np.zeros((self.rows, self.cols), dtype=np.float32)
        self.alert_signals = np.zeros((self.rows, self.cols), dtype=np.float32)

        self.decay_rate = 0.99
        self.broadcast_rate = 0.1
        self.emission_strength = 1.0

    def get_grid_pos(self, world_pos):
        """
        Convert world position to grid coordinates.

        Args:
            world_pos: Vector2D world position

        Returns:
            Tuple (grid_x, grid_y)
        """
        grid_x = int(world_pos.x // self.cell_size)
        grid_y = int(world_pos.y // self.cell_size)
        grid_x = max(0, min(self.cols - 1, grid_x))
        grid_y = max(0, min(self.rows - 1, grid_y))
        return grid_x, grid_y

    def emit_signal(self, position, strength=1.0):
        """Emit a path tracking signal at position."""
        x, y = self.get_grid_pos(position)
        self.path_signals[y, x] = min(255, self.path_signals[y, x] + strength)

    def emit_base_signal(self, position, strength=1.0):
        """Emit a base station signal at position."""
        x, y = self.get_grid_pos(position)
        self.base_signals[y, x] = min(255, self.base_signals[y, x] + strength)

    def emit_alert_signal(self, position, strength=1.0):
        """Emit a danger/alert signal at position."""
        x, y = self.get_grid_pos(position)
        self.alert_signals[y, x] = min(255, self.alert_signals[y, x] + strength)

    def get_signal_strength(self, position):
        """Get path signal strength at position."""
        x, y = self.get_grid_pos(position)
        return self.path_signals[y, x]

    def get_base_strength(self, position):
        """Get base signal strength at position."""
        x, y = self.get_grid_pos(position)
        return self.base_signals[y, x]

    def get_alert_strength(self, position):
        """Get alert signal strength at position."""
        x, y = self.get_grid_pos(position)
        return self.alert_signals[y, x]

    def get_signal_gradient(self, position):
        """
        Get gradient direction toward strongest path signal.

        Args:
            position: Vector2D position

        Returns:
            Vector2D direction toward stronger signal
        """
        x, y = self.get_grid_pos(position)

        # Sample 4 neighbors
        directions = [
            (0, -1, Vector2D(0, -1)),
            (0, 1, Vector2D(0, 1)),
            (-1, 0, Vector2D(-1, 0)),
            (1, 0, Vector2D(1, 0))
        ]

        max_strength = self.path_signals[y, x]
        best_dir = Vector2D(0, 0)

        for dx, dy, direction in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                strength = self.path_signals[ny, nx]
                if strength > max_strength:
                    max_strength = strength
                    best_dir = direction

        return best_dir

    def update(self):
        """Update signal decay and network mesh broadcast."""
        # Decay over time (limited memory of nodes)
        self.path_signals *= self.decay_rate
        self.base_signals *= self.decay_rate
        self.alert_signals *= self.decay_rate

        # Broadcast (spread to neighbor nodes in grid)
        for signal_grid in [self.path_signals, self.base_signals, self.alert_signals]:
            diffused = np.zeros_like(signal_grid)

            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    shifted = np.roll(np.roll(signal_grid, dx, axis=1), dy, axis=0)
                    diffused += shifted * (self.broadcast_rate / 8)

            # Apply broadcast
            if signal_grid is self.path_signals:
                self.path_signals += diffused
            elif signal_grid is self.base_signals:
                self.base_signals += diffused
            else:
                self.alert_signals += diffused

    def get_visualization_grid(self):
        """Get signal grid for HUD visualization."""
        return self.path_signals.copy()
