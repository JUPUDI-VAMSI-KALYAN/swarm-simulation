"""Base Entity class for all simulation objects."""

import uuid
from src.core.vector2d import Vector2D


class Entity:
    """Base class for all entities in the simulation."""

    _entity_counter = 0

    def __init__(self, position=None, velocity=None, radius=5.0):
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
        self.max_speed = 5.0
        self.max_force = 1.0

        self.alive = True
        self.creation_time = 0

    def apply_force(self, force):
        """Add a force to this entity's acceleration."""
        if isinstance(force, Vector2D):
            self.acceleration = self.acceleration + force

    def update(self, delta_time):
        """
        Update entity physics using frame-rate independent delta time.

        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        if not self.alive:
            return

        # Update velocity with acceleration
        self.velocity = self.velocity + (self.acceleration * delta_time)

        # Limit speed
        self.velocity = self.velocity.limit(self.max_speed)

        # Update position with velocity
        self.position = self.position + (self.velocity * delta_time)

        # Reset acceleration for next frame
        self.acceleration = Vector2D(0, 0)

        # Update creation time
        self.creation_time += delta_time

    def wrap_edges(self, width, height):
        """Wrap entity around screen edges."""
        if self.position.x < 0:
            self.position.x = width
        elif self.position.x > width:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = height
        elif self.position.y > height:
            self.position.y = 0

    def clamp_position(self, width, height):
        """Clamp entity position within bounds."""
        if self.position.x < self.radius:
            self.position.x = self.radius
        elif self.position.x > width - self.radius:
            self.position.x = width - self.radius

        if self.position.y < self.radius:
            self.position.y = self.radius
        elif self.position.y > height - self.radius:
            self.position.y = height - self.radius

    def distance_to(self, other):
        """Calculate distance to another entity."""
        if isinstance(other, Entity):
            return self.position.distance(other.position)
        return float('inf')

    def distance_squared_to(self, other):
        """Calculate squared distance to another entity."""
        if isinstance(other, Entity):
            return self.position.distance_squared(other.position)
        return float('inf')

    def is_colliding_with(self, other):
        """Check if this entity is colliding with another."""
        if isinstance(other, Entity):
            dist = self.distance_to(other)
            return dist < (self.radius + other.radius)
        return False

    def get_direction_to(self, other):
        """Get normalized direction vector to another entity."""
        if isinstance(other, Entity):
            direction = other.position - self.position
            return direction.normalize()
        return Vector2D(0, 0)

    def destroy(self):
        """Mark entity as destroyed."""
        self.alive = False

    def __repr__(self):
        return f"Entity(id={self.id}, pos={self.position}, vel={self.velocity})"
