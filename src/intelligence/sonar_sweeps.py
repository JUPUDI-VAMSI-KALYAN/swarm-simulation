"""Sonar array sweeping behaviors for pod sub-surface swarms."""

from src.core.vector2d import Vector2D
from src.intelligence.behaviors import SteeringBehaviors


class SonarSweepBehavior:
    """Implements sub-surface sonar grid search behavior."""

    def __init__(self, sweep_weight=0.5, separation_weight=0.4, alignment_weight=0.2):
        """
        Initialize sonar sweep parameters.

        Args:
            sweep_weight: Weight for the scanning sweep
            separation_weight: Weight for collision avoidance
            alignment_weight: Weight for group movement
        """
        self.sweep_weight = sweep_weight
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight

    def calculate_sweep_steering(self, agent, sweep_angle, neighbors_list, perception_radius, max_force):
        """
        Calculate methodical scanning steering force.

        Args:
            agent: Pod agent
            sweep_angle: Current sweeping arc angle
            neighbors_list: List of (neighbor, distance) tuples
            perception_radius: How far to consider neighbors
            max_force: Maximum force magnitude

        Returns:
            Tuple (Vector2D steering force, new_sweep_angle)
        """
        # 1. Separation to maintain acoustic array gaps
        separation = SteeringBehaviors.separation(
            agent.position, neighbors_list, perception_radius * 0.7, max_force
        )
        
        # 2. Alignment to travel generally together
        alignment = SteeringBehaviors.alignment(
            agent.velocity, neighbors_list, perception_radius, max_force
        )
        
        # 3. Sonar Sweep (replaces completely random wandering or intense cohesion)
        sweep, new_sweep_angle = SteeringBehaviors.sonar_sweep(
            agent.position, agent.velocity, sweep_angle, 40, max_force
        )

        # Combine with weights
        combined = (
            sweep * self.sweep_weight +
            separation * self.separation_weight +
            alignment * self.alignment_weight
        )

        combined = combined.limit(max_force)
        return combined, new_sweep_angle
