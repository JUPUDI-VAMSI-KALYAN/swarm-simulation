"""Tactical formation algorithm for drone swarms."""

from src.core.vector2d import Vector2D
from src.intelligence.behaviors import SteeringBehaviors


class TacticalFormationBehavior:
    """Implements rigid grid alignment for military drone swarms."""

    def __init__(self, cohesion_weight=0.1, separation_weight=0.6, alignment_weight=0.6):
        """
        Initialize tactical formation parameters.

        Args:
            cohesion_weight: Weight for cohesion behavior (low for drones)
            separation_weight: Weight for separation behavior (high for collision avoidance)
            alignment_weight: Weight for rigid grid alignment (high for formation tightness)
        """
        self.cohesion_weight = cohesion_weight
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight

    def update_formation_member(self, drone, neighbors_list, target, perception_radius, max_force):
        """
        Update a single drone's steering based on tactical block formation and environment.

        Args:
            drone: Drone agent to update
            neighbors_list: List of (neighbor, distance) tuples
            target: Current target (if any)
            perception_radius: How far to see
            max_force: Maximum force magnitude

        Returns:
            Vector2D total steering force
        """
        forces = []

        # 1. Separation (Extremely high priority to avoid catastrophic drone collisions)
        sep = SteeringBehaviors.separation(
            drone.position, neighbors_list, perception_radius * 0.4, max_force
        )
        forces.append(sep * self.separation_weight * 1.5)

        # 2. Cohesion (Low priority, drones shouldn't clump)
        coh = SteeringBehaviors.cohesion(
            drone.position, neighbors_list, perception_radius, max_force
        )
        forces.append(coh * self.cohesion_weight)

        # 3. Grid Alignment (The core of the tactical formation)
        # Using the new grid_alignment we built in behaviors.py
        grid_align = SteeringBehaviors.grid_alignment(
            drone.velocity, neighbors_list, perception_radius, max_force
        )
        forces.append(grid_align * self.alignment_weight)

        # 4. Target seeking (if target exists and is close)
        if target and target.alive:
            target_dist = drone.distance_to(target)
            if target_dist < perception_radius * 2:  # Can see target
                seek = SteeringBehaviors.seek(
                    drone.position, target.position, drone.max_speed
                )
                forces.append(seek * 1.8) # Strong pull toward target

        # Combine all forces
        total_force = Vector2D(0, 0)
        for force in forces:
            total_force = total_force + force

        # Limit combined force
        total_force = total_force.limit(max_force)

        return total_force
