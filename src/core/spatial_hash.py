"""Spatial hash grid for fast neighbor queries."""

from collections import defaultdict


class SpatialHashGrid:
    """Spatial partitioning for efficient neighbor detection."""

    def __init__(self, cell_size=50, grid_width=1280, grid_height=720):
        """
        Initialize spatial hash grid.

        Args:
            cell_size: Size of each grid cell
            grid_width: Grid width in pixels
            grid_height: Grid height in pixels
        """
        self.cell_size = cell_size
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = defaultdict(list)

    def get_cell_key(self, position):
        """
        Get grid cell key for a position.

        Args:
            position: Vector2D position

        Returns:
            Tuple (grid_x, grid_y)
        """
        grid_x = int(position.x // self.cell_size)
        grid_y = int(position.y // self.cell_size)
        return (grid_x, grid_y)

    def add_entity(self, entity):
        """
        Add entity to grid.

        Args:
            entity: Entity to add
        """
        key = self.get_cell_key(entity.position)
        self.grid[key].append(entity)

    def clear(self):
        """Clear all entities from grid."""
        self.grid.clear()

    def get_neighbors(self, entity, radius):
        """
        Get all entities within radius of given entity.

        Args:
            entity: Query entity
            radius: Search radius

        Returns:
            List of (neighbor_entity, distance) tuples
        """
        neighbors = []
        entity_key = self.get_cell_key(entity.position)

        # Check current cell and surrounding cells
        cells_to_check = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_key = (entity_key[0] + dx, entity_key[1] + dy)
                if check_key in self.grid:
                    cells_to_check.append(check_key)

        # Check all entities in nearby cells
        for cell_key in cells_to_check:
            for other_entity in self.grid[cell_key]:
                if other_entity is not entity and other_entity.alive:
                    distance = entity.distance_to(other_entity)
                    if distance < radius:
                        neighbors.append((other_entity, distance))

        return neighbors

    def rebuild(self, all_entities):
        """
        Rebuild grid with new entities.

        Args:
            all_entities: List of all entities to add
        """
        self.clear()
        for entity in all_entities:
            if entity.alive:
                self.add_entity(entity)
