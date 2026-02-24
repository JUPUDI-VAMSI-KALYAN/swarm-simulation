"""Schooling behaviors for fish swarms."""

from src.core.vector2d import Vector2D
from src.intelligence.behaviors import SteeringBehaviors


class SchoolingBehavior:
    """Implements fish schooling behavior."""

    def __init__(self, cohesion_weight=0.25, separation_weight=0.4, alignment_weight=0.35):
        """
        Initialize schooling parameters.

        Args:
            cohesion_weight: Weight for cohesion
            separation_weight: Weight for separation
            alignment_weight: Weight for alignment
        """
        self.cohesion_weight = cohesion_weight
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight

    def calculate_schooling_steering(self, agent, neighbors_list, perception_radius, max_force):
        """
        Calculate schooling steering force.

        Args:
            agent: Fish agent
            neighbors_list: List of (neighbor, distance) tuples
            perception_radius: How far to consider neighbors
            max_force: Maximum force magnitude

        Returns:
            Vector2D steering force
        """
        # Fish school is tighter than birds, so separation is higher
        cohesion = SteeringBehaviors.cohesion(
            agent.position, neighbors_list, perception_radius, max_force
        )
        separation = SteeringBehaviors.separation(
            agent.position, neighbors_list, perception_radius * 0.7, max_force
        )
        alignment = SteeringBehaviors.alignment(
            agent.velocity, neighbors_list, perception_radius, max_force
        )

        # Combine with weights
        combined = (
            cohesion * self.cohesion_weight +
            separation * self.separation_weight +
            alignment * self.alignment_weight
        )

        combined = combined.limit(max_force)
        return combined
