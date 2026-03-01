"""Base Entity class for all simulation objects."""

from typing import Any, Optional
from src.core.vector2d import Vector2D


class Entity:
    """Base class for all entities in the simulation."""

    _entity_counter = 0

    DRAG_COEFFICIENT = 0.02

    def __init__(
        self,
        position: Optional[Vector2D] = None,
        velocity: Optional[Vector2D] = None,
        radius: float = 5.0
    ) -> None:
        """
        Initialize an entity.

        Args:
            position: Vector2D position (default: origin)
            velocity: Vector2D velocity (default: zero)
            radius: Collision radius in pixels
        """
        self.id = Entity._entity_counter
        Entity._entity_counter += 1

        self.position = position if position is not None else Vector2D(0, 0)
        self.velocity = velocity if velocity is not None else Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)

        self.radius = radius
        self.max_speed = 300.0
        self.max_force = 100.0
        self.mass = 1.0

        self.alive = True
        self.creation_time = 0.0

    def apply_force(self, force: Vector2D) -> None:
        """Add a force to this entity's acceleration (F=ma)."""
        if isinstance(force, Vector2D):
            self.acceleration = self.acceleration + (force / self.mass)

    def apply_drag(self) -> None:
        """Apply aerodynamic/ hydrodynamic drag force."""
        speed = self.velocity.magnitude()
        if speed > 0:
            drag_magnitude = self.DRAG_COEFFICIENT * speed * speed
            drag_force = self.velocity.normalize() * -drag_magnitude
            self.apply_force(drag_force)

    def update(self, delta_time: float) -> None:
        """
        Update entity physics using frame-rate independent delta time.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self.alive:
            return

        self.apply_drag()

        self.velocity = self.velocity + (self.acceleration * delta_time)

        self.velocity = self.velocity.limit(self.max_speed)

        self.position = self.position + (self.velocity * delta_time)

        self.acceleration = Vector2D(0, 0)

        self.creation_time += delta_time

    def wrap_edges(self, width: float, height: float) -> None:
        """Wrap entity around screen edges."""
        if self.position.x < 0:
            self.position.x = width
        elif self.position.x > width:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = height
        elif self.position.y > height:
            self.position.y = 0

    def clamp_position(self, width: float, height: float) -> None:
        """Clamp entity position within bounds."""
        if self.position.x < self.radius:
            self.position.x = self.radius
        elif self.position.x > width - self.radius:
            self.position.x = width - self.radius

        if self.position.y < self.radius:
            self.position.y = self.radius
        elif self.position.y > height - self.radius:
            self.position.y = height - self.radius

    def distance_to(self, other: Any) -> float:
        """Calculate distance to another entity."""
        if isinstance(other, Entity):
            return self.position.distance(other.position)
        return float('inf')

    def distance_squared_to(self, other: Any) -> float:
        """Calculate squared distance to another entity."""
        if isinstance(other, Entity):
            return self.position.distance_squared(other.position)
        return float('inf')

    def is_colliding_with(self, other: Any) -> bool:
        """Check if this entity is colliding with another."""
        if isinstance(other, Entity):
            dist = self.distance_to(other)
            return dist < (self.radius + other.radius)
        return False

    def get_direction_to(self, other: Any) -> Vector2D:
        """Get normalized direction vector to another entity."""
        if isinstance(other, Entity):
            direction = other.position - self.position
            return direction.normalize()
        return Vector2D(0, 0)

    def destroy(self) -> None:
        """Mark entity as destroyed."""
        self.alive = False

    def __repr__(self) -> str:
        return f"Entity(id={self.id}, pos={self.position}, vel={self.velocity})"
