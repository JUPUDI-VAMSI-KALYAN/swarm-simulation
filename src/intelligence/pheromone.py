"""Pheromone system for ant communication."""

import numpy as np
import math
from src.core.vector2d import Vector2D


class PheromoneMap:
    """Grid-based pheromone map for ant communication."""

    def __init__(self, grid_width=1280, grid_height=720, cell_size=10):
        """
        Initialize pheromone map.

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

        # Separate grids for different pheromone types
        self.food_pheromones = np.zeros((self.rows, self.cols), dtype=np.float32)
        self.home_pheromones = np.zeros((self.rows, self.cols), dtype=np.float32)
        self.danger_pheromones = np.zeros((self.rows, self.cols), dtype=np.float32)

        self.evaporation_rate = 0.99
        self.diffusion_rate = 0.1
        self.deposit_strength = 1.0

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

    def deposit_food_pheromone(self, position, strength=1.0):
        """Deposit food pheromone at position."""
        x, y = self.get_grid_pos(position)
        self.food_pheromones[y, x] = min(255, self.food_pheromones[y, x] + strength)

    def deposit_home_pheromone(self, position, strength=1.0):
        """Deposit home pheromone at position."""
        x, y = self.get_grid_pos(position)
        self.home_pheromones[y, x] = min(255, self.home_pheromones[y, x] + strength)

    def deposit_danger_pheromone(self, position, strength=1.0):
        """Deposit danger pheromone at position."""
        x, y = self.get_grid_pos(position)
        self.danger_pheromones[y, x] = min(255, self.danger_pheromones[y, x] + strength)

    def get_food_strength(self, position):
        """Get food pheromone strength at position."""
        x, y = self.get_grid_pos(position)
        return self.food_pheromones[y, x]

    def get_home_strength(self, position):
        """Get home pheromone strength at position."""
        x, y = self.get_grid_pos(position)
        return self.home_pheromones[y, x]

    def get_danger_strength(self, position):
        """Get danger pheromone strength at position."""
        x, y = self.get_grid_pos(position)
        return self.danger_pheromones[y, x]

    def get_food_gradient(self, position):
        """
        Get gradient direction toward strongest food pheromone.

        Args:
            position: Vector2D position

        Returns:
            Vector2D direction toward stronger pheromone
        """
        x, y = self.get_grid_pos(position)

        # Sample 4 neighbors
        strengths = {}
        directions = [
            (0, -1, Vector2D(0, -1)),
            (0, 1, Vector2D(0, 1)),
            (-1, 0, Vector2D(-1, 0)),
            (1, 0, Vector2D(1, 0))
        ]

        max_strength = self.food_pheromones[y, x]
        best_dir = Vector2D(0, 0)

        for dx, dy, direction in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                strength = self.food_pheromones[ny, nx]
                if strength > max_strength:
                    max_strength = strength
                    best_dir = direction

        return best_dir

    def update(self):
        """Update pheromone decay and diffusion."""
        # Evaporation
        self.food_pheromones *= self.evaporation_rate
        self.home_pheromones *= self.evaporation_rate
        self.danger_pheromones *= self.evaporation_rate

        # Diffusion (spread to neighbors)
        for pheromone_grid in [self.food_pheromones, self.home_pheromones, self.danger_pheromones]:
            diffused = np.zeros_like(pheromone_grid)

            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    shifted = np.roll(np.roll(pheromone_grid, dx, axis=1), dy, axis=0)
                    diffused += shifted * (self.diffusion_rate / 8)

            # Apply diffusion
            if pheromone_grid is self.food_pheromones:
                self.food_pheromones += diffused
            elif pheromone_grid is self.home_pheromones:
                self.home_pheromones += diffused
            else:
                self.danger_pheromones += diffused

    def get_visualization_grid(self):
        """Get pheromone grid for visualization."""
        return self.food_pheromones.copy()
