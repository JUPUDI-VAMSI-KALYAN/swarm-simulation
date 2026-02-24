"""Flocking/Boids algorithm for bird swarms."""

from src.core.vector2d import Vector2D
from src.intelligence.behaviors import SteeringBehaviors


class FlockingBehavior:
    """Implements the Boids flocking algorithm."""

    def __init__(self, cohesion_weight=0.3, separation_weight=0.3, alignment_weight=0.4):
        """
        Initialize flocking parameters.

        Args:
            cohesion_weight: Weight for cohesion behavior
            separation_weight: Weight for separation behavior
            alignment_weight: Weight for alignment behavior
        """
        self.cohesion_weight = cohesion_weight
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight

    def calculate_flock_steering(self, agent, neighbors_list, perception_radius, max_force):
        """
        Calculate combined flocking steering force.

        Args:
            agent: The bird agent
            neighbors_list: List of (neighbor, distance) tuples
            perception_radius: How far to consider neighbors
            max_force: Maximum force magnitude

        Returns:
            Vector2D steering force
        """
        # Calculate individual behaviors
        cohesion = SteeringBehaviors.cohesion(
            agent.position, neighbors_list, perception_radius, max_force
        )
        separation = SteeringBehaviors.separation(
            agent.position, neighbors_list, perception_radius, max_force
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

        # Limit total force
        combined = combined.limit(max_force)

        return combined

    def update_flock_member(self, bird, neighbors_list, target, perception_radius, max_force):
        """
        Update a single bird's steering based on flock and environment.

        Args:
            bird: Bird agent to update
            neighbors_list: List of (neighbor, distance) tuples
            target: Current target (if any)
            perception_radius: How far to see
            max_force: Maximum force magnitude

        Returns:
            Vector2D total steering force
        """
        forces = []

        # 1. Separation (high priority to avoid collisions)
        sep = SteeringBehaviors.separation(
            bird.position, neighbors_list, perception_radius * 0.5, max_force
        )
        forces.append(sep * 1.2)

        # 2. Cohesion and Alignment
        coh = SteeringBehaviors.cohesion(
            bird.position, neighbors_list, perception_radius, max_force
        )
        forces.append(coh * self.cohesion_weight)

        ali = SteeringBehaviors.alignment(
            bird.velocity, neighbors_list, perception_radius, max_force
        )
        forces.append(ali * self.alignment_weight)

        # 3. Target seeking (if target exists and is close)
        if target and target.alive:
            target_dist = bird.distance_to(target)
            if target_dist < perception_radius * 2:  # Can see target
                seek = SteeringBehaviors.seek(
                    bird.position, target.position, bird.max_speed
                )
                forces.append(seek * 1.5)

        # Combine all forces
        total_force = Vector2D(0, 0)
        for force in forces:
            total_force = total_force + force

        # Limit combined force
        total_force = total_force.limit(max_force)

        return total_force
